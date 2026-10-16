"""Read AWS project evidence and export SELECT results into a new snapshot.

No deployment, invocation, resource configuration or Secret values are requested.
Athena SELECT executions create only their normal result objects in S3.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from athena_export import AthenaExporter, AthenaQueryError

ROOT = Path(__file__).resolve().parents[2]
FUNCTION = "WeatherCollectorLambda"
PROFILES = {"default": "Sinh viên Tiến Sơn", "quyen": "Sinh viên Ngọc Quyên"}
QUERIES = (
    "raw_all",
    "raw_week2",
    "city_week2",
    "category_week2",
    "hour_city_week2",
    "partition_all",
    "quality_all",
)


def write_csv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def file_manifest(folder):
    return [
        {
            "path": path.relative_to(folder).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        }
        for path in sorted(folder.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    ]


def collect_profile(profile, output, region):
    folder = output / profile
    folder.mkdir()
    session = boto3.Session(profile_name=profile, region_name=region)
    config = Config(connect_timeout=10, read_timeout=30, retries={"max_attempts": 2})
    clients = {}

    def client(service):
        if service not in clients:
            clients[service] = session.client(service, config=config)
        return clients[service]

    observed = datetime.now(timezone.utc).isoformat()
    checks = []
    details = {
        "profile": profile,
        "student": PROFILES[profile],
        "region": region,
        "observed_at_utc": observed,
    }

    def check(name, action):
        try:
            result = action()
            details[name] = result
            checks.append(
                {
                    "profile": profile,
                    "service_check": name,
                    "status": "PASS",
                    "error_code": "",
                }
            )
            return result
        except (
            ClientError,
            BotoCoreError,
            OSError,
            ValueError,
            KeyError,
            zipfile.BadZipFile,
        ) as error:
            # Public evidence exposes only the SDK error class/code, not raw responses.
            code = (
                error.response["Error"]["Code"]
                if isinstance(error, ClientError)
                else type(error).__name__
            )
            checks.append(
                {
                    "profile": profile,
                    "service_check": name,
                    "status": "UNAVAILABLE",
                    "error_code": code,
                }
            )
            return None

    identity = check(
        "identity",
        lambda: {"account_id": client("sts").get_caller_identity()["Account"]},
    )
    if not identity:
        (folder / "services.json").write_text(
            json.dumps(details, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (folder / "queries.json").write_text("[]\n", encoding="utf-8")
        write_csv(
            folder / "service_checks.csv",
            checks,
            ["profile", "service_check", "status", "error_code"],
        )
        return details, checks, []
    bucket = "weather-aqi-" + identity["account_id"]

    def lambda_config():
        result = client("lambda").get_function_configuration(FunctionName=FUNCTION)
        keys = [
            "FunctionName",
            "Runtime",
            "Handler",
            "MemorySize",
            "Timeout",
            "State",
            "LastModified",
            "LastUpdateStatus",
            "CodeSha256",
        ]
        return {key: result.get(key) for key in keys}

    check("lambda", lambda_config)

    def deployed_source():
        function = client("lambda").get_function(FunctionName=FUNCTION)
        request = urllib.request.Request(function["Code"]["Location"])
        with urllib.request.urlopen(request, timeout=30) as response:
            blob = response.read()
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            names = [
                name for name in archive.namelist() if name == "lambda_function.py"
            ]
            if len(names) != 1:
                raise ValueError("Expected one root collector module")
            deployed = archive.read(names[0])
        local = (ROOT / "tuan_2/lambda/lambda_function.py").read_bytes()
        return {
            "deployed_module_sha256": hashlib.sha256(deployed).hexdigest(),
            "repository_module_sha256": hashlib.sha256(local).hexdigest(),
            "matches_repository": deployed == local,
        }

    check("deployed_source", deployed_source)

    def schedules():
        items = []
        for page in (
            client("events")
            .get_paginator("list_rules")
            .paginate(NamePrefix="WeatherCollection")
        ):
            for rule in page.get("Rules", []):
                targets = client("events").list_targets_by_rule(Rule=rule["Name"])[
                    "Targets"
                ]
                items.append(
                    {
                        "name": rule["Name"],
                        "state": rule["State"],
                        "schedule": rule.get("ScheduleExpression"),
                        "collector_targets": sum(
                            t.get("Arn", "").endswith(":function:" + FUNCTION)
                            for t in targets
                        ),
                    }
                )
        return items

    check("eventbridge", schedules)

    def policy():
        doc = json.loads(client("lambda").get_policy(FunctionName=FUNCTION)["Policy"])
        return {
            "eventbridge_invoke_statements": sum(
                s.get("Effect") == "Allow"
                and s.get("Principal", {}).get("Service") == "events.amazonaws.com"
                and s.get("Action") == "lambda:InvokeFunction"
                for s in doc.get("Statement", [])
            )
        }

    check("lambda_policy", policy)
    check(
        "s3_public_access",
        lambda: client("s3").get_public_access_block(Bucket=bucket)[
            "PublicAccessBlockConfiguration"
        ],
    )
    check(
        "s3_encryption",
        lambda: {
            "algorithms": [
                r["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
                for r in client("s3").get_bucket_encryption(Bucket=bucket)[
                    "ServerSideEncryptionConfiguration"
                ]["Rules"]
            ]
        },
    )

    def objects():
        rows = []
        for page in (
            client("s3")
            .get_paginator("list_objects_v2")
            .paginate(Bucket=bucket, Prefix="raw/")
        ):
            rows.extend(
                {
                    "key": r["Key"],
                    "bytes": r["Size"],
                    "last_modified_utc": r["LastModified"].isoformat(),
                }
                for r in page.get("Contents", [])
                if r["Size"] > 0
            )
        write_csv(
            folder / "s3_objects.csv", rows, ["key", "bytes", "last_modified_utc"]
        )
        return {
            "prefix": "raw/",
            "objects": len(rows),
            "bytes": sum(r["bytes"] for r in rows),
        }

    check("s3_raw", objects)

    def table():
        item = client("glue").get_table(
            DatabaseName="weather_aqi_db", Name="weather_airquality_records"
        )["Table"]
        return {
            "database": "weather_aqi_db",
            "name": item["Name"],
            "columns": item["StorageDescriptor"]["Columns"],
            "partition_keys": item["PartitionKeys"],
            "serde": item["StorageDescriptor"]
            .get("SerdeInfo", {})
            .get("SerializationLibrary"),
        }

    check("glue_table", table)

    def partitions():
        values = [
            p["Values"]
            for page in client("glue")
            .get_paginator("get_partitions")
            .paginate(
                DatabaseName="weather_aqi_db", TableName="weather_airquality_records"
            )
            for p in page.get("Partitions", [])
        ]
        return {"count": len(values), "values": sorted(values)}

    check("glue_partitions", partitions)

    def sns():
        topics = [
            t["TopicArn"]
            for page in client("sns").get_paginator("list_topics").paginate()
            for t in page.get("Topics", [])
            if t["TopicArn"].endswith(":weather-airquality-alerts")
        ]
        subscriptions = [
            s
            for arn in topics
            for page in client("sns")
            .get_paginator("list_subscriptions_by_topic")
            .paginate(TopicArn=arn)
            for s in page.get("Subscriptions", [])
        ]
        return {
            "project_topics": len(topics),
            "confirmed_email_subscriptions": sum(
                s["Protocol"] == "email"
                and s["SubscriptionArn"] not in ("PendingConfirmation", "Deleted")
                for s in subscriptions
            ),
            "pending_subscriptions": sum(
                s["SubscriptionArn"] == "PendingConfirmation" for s in subscriptions
            ),
        }

    check("sns", sns)

    def alarms():
        rows = client("cloudwatch").describe_alarms(AlarmNamePrefix="WeatherCollector")[
            "MetricAlarms"
        ]
        return [
            {
                key: row.get(key)
                for key in [
                    "AlarmName",
                    "StateValue",
                    "MetricName",
                    "Namespace",
                    "Threshold",
                    "ComparisonOperator",
                    "Period",
                    "EvaluationPeriods",
                ]
            }
            for row in rows
        ]

    check("cloudwatch_alarms", alarms)

    def metrics():
        start = datetime(2026, 10, 11, 17, tzinfo=timezone.utc)
        end = min(
            datetime.now(timezone.utc), datetime(2026, 10, 18, 17, tzinfo=timezone.utc)
        )
        rows = []
        for metric, stat in [
            ("Invocations", "Sum"),
            ("Errors", "Sum"),
            ("Duration", "Average"),
        ]:
            response = client("cloudwatch").get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName=metric,
                Dimensions=[{"Name": "FunctionName", "Value": FUNCTION}],
                StartTime=start,
                EndTime=end,
                Period=86400,
                Statistics=[stat],
            )
            rows.extend(
                {
                    "metric": metric,
                    "statistic": stat,
                    "timestamp_utc": p["Timestamp"].isoformat(),
                    "value": p[stat],
                    "unit": p["Unit"],
                    "period_seconds": 86400,
                }
                for p in sorted(response["Datapoints"], key=lambda x: x["Timestamp"])
            )
        write_csv(
            folder / "cloudwatch_metrics.csv",
            rows,
            ["metric", "statistic", "timestamp_utc", "value", "unit", "period_seconds"],
        )
        return {
            "namespace": "AWS/Lambda",
            "dimension": "FunctionName=" + FUNCTION,
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "period_seconds": 86400,
            "invocations": sum(
                r["value"] for r in rows if r["metric"] == "Invocations"
            ),
            "errors": sum(r["value"] for r in rows if r["metric"] == "Errors"),
            "points": len(rows),
        }

    check("cloudwatch_metrics", metrics)
    exporter = AthenaExporter(
        client("athena"),
        client("s3"),
        "weather_aqi_db",
        f"s3://{bucket}/athena-results/repository-review/",
        timeout=120,
    )
    queries = []
    for name in QUERIES:
        sql = (ROOT / "tuan_2/athena/week2_analysis" / (name + ".sql")).read_text(
            encoding="utf-8"
        )
        if not sql.lstrip().upper().startswith("SELECT "):
            raise ValueError("Only saved SELECT statements can be exported")
        try:
            result = exporter.export(name, sql, folder / (name + ".csv"))
            result.pop("rows")
            result.update(
                {
                    "profile": profile,
                    "student": PROFILES[profile],
                    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                    "sql_path": f"tuan_2/athena/week2_analysis/{name}.sql",
                    "csv_sha256": hashlib.sha256(
                        (folder / (name + ".csv")).read_bytes()
                    ).hexdigest(),
                }
            )
        except (ClientError, BotoCoreError, AthenaQueryError, TimeoutError) as error:
            code = (
                error.response["Error"]["Code"]
                if isinstance(error, ClientError)
                else type(error).__name__
            )
            result = {
                "name": name,
                "profile": profile,
                "status": "UNAVAILABLE",
                "error_code": code,
            }
        queries.append(result)
        print(
            json.dumps(
                {
                    "profile": profile,
                    "query": name,
                    "status": result["status"],
                    "rows": result.get("row_count"),
                }
            ),
            flush=True,
        )
    (folder / "services.json").write_text(
        json.dumps(details, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (folder / "queries.json").write_text(
        json.dumps(queries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(
        folder / "service_checks.csv",
        checks,
        ["profile", "service_check", "status", "error_code"],
    )
    return details, checks, queries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, required=True, help="A new empty snapshot directory"
    )
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    # Exclusive creation prevents replacing historic results, even on a rerun.
    output.mkdir(parents=True, exist_ok=False)
    summaries = []
    for profile in PROFILES:
        details, checks, queries = collect_profile(profile, output, args.region)
        summaries.append(
            {
                "profile": profile,
                "student": PROFILES[profile],
                "service_pass": sum(c["status"] == "PASS" for c in checks),
                "service_total": len(checks),
                "query_pass": sum(q["status"] == "SUCCEEDED" for q in queries),
                "query_total": len(queries),
            }
        )
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    manifest = {
        "mode": "live-read-and-select",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_base_commit": head,
        "collector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "region": args.region,
        "summary": summaries,
        "files": file_manifest(output),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summaries))


if __name__ == "__main__":
    main()
