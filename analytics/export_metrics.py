"""
Run Athena Analytical Queries and Export Results & Execution Metrics
Môn học: Cloud - Đợt 1 - 2026-2027
GVHD: Huỳnh Xuân Phụng
Sinh viên: 24110054
Account: 873674852386 | Region: us-east-1
"""

import boto3
import time
import os
import json
import csv
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
athena = boto3.client('athena', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)

DATABASE = os.environ.get('ATHENA_DATABASE', 'weather_aqi_db')
try:
    sts = boto3.client('sts', region_name=REGION)
    _acc = sts.get_caller_identity()['Account']
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', f'weather-aqi-{_acc}')
except Exception:
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'weather-aqi-873674852386')

OUTPUT_LOCATION = f"s3://{BUCKET_NAME}/athena-results/"
RESULTS_DIR = os.path.abspath('results/athena_queries')
os.makedirs(RESULTS_DIR, exist_ok=True)

QUERIES = [
    {
        "name": "avg_aqi_by_city",
        "description": "Thống kê chỉ số ô nhiễm và thời tiết trung bình theo từng thành phố",
        "sql": """
            SELECT 
                city,
                COUNT(*) AS total_records,
                ROUND(AVG(us_aqi), 2) AS avg_aqi,
                MIN(us_aqi) AS min_aqi,
                MAX(us_aqi) AS max_aqi,
                ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
                ROUND(AVG(pm10), 2) AS avg_pm10,
                ROUND(AVG(temperature_2m), 2) AS avg_temp,
                ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity
            FROM weather_aqi_db.weather_airquality_records
            GROUP BY city
            ORDER BY avg_aqi DESC;
        """
    },
    {
        "name": "peak_pollution_hours",
        "description": "Phân tích khung giờ ô nhiễm trong ngày",
        "sql": """
            SELECT 
                hour,
                ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
                ROUND(AVG(pm10), 2) AS avg_pm10,
                ROUND(AVG(us_aqi), 2) AS avg_aqi,
                COUNT(*) AS sample_count
            FROM weather_aqi_db.weather_airquality_records
            GROUP BY hour
            ORDER BY hour ASC;
        """
    },
    {
        "name": "aqi_category_distribution",
        "description": "Phân bố cấp độ chất lượng không khí",
        "sql": """
            SELECT 
                city,
                aqi_category,
                COUNT(*) AS occurrence_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS percentage
            FROM weather_aqi_db.weather_airquality_records
            GROUP BY city, aqi_category
            ORDER BY city, occurrence_count DESC;
        """
    },
    {
        "name": "weather_correlation",
        "description": "Tương quan giữa Nhiệt độ, Độ ẩm và Bụi mịn PM2.5",
        "sql": """
            SELECT 
                city,
                ROUND(corr(temperature_2m, pm2_5), 4) AS corr_temp_pm25,
                ROUND(corr(relative_humidity_2m, pm2_5), 4) AS corr_humidity_pm25,
                ROUND(corr(wind_speed_10m, pm2_5), 4) AS corr_wind_pm25
            FROM weather_aqi_db.weather_airquality_records
            GROUP BY city;
        """
    }
]

def run_query(q):
    print(f"\n[INFO] Running query: {q['name']} ({q['description']})...")
    resp = athena.start_query_execution(
        QueryString=q['sql'].strip(),
        QueryExecutionContext={'Database': DATABASE},
        ResultConfiguration={'OutputLocation': OUTPUT_LOCATION}
    )
    qid = resp['QueryExecutionId']
    print(f"  -> QueryExecutionId: {qid}")

    # Wait for completion
    while True:
        status_resp = athena.get_query_execution(QueryExecutionId=qid)
        status = status_resp['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(1)

    if status != 'SUCCEEDED':
        reason = status_resp['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
        print(f"  [ERROR] Query failed: {reason}")
        return None

    stats = status_resp['QueryExecution']['Statistics']
    exec_time_ms = stats.get('EngineExecutionTimeInMillis', 0)
    bytes_scanned = stats.get('DataScannedInBytes', 0)
    print(f"  -> Execution Time: {exec_time_ms} ms | Data Scanned: {bytes_scanned} bytes")

    # Download result CSV from S3
    s3_path = status_resp['QueryExecution']['ResultConfiguration']['OutputLocation']
    # s3_path format: s3://bucket/key
    bucket = s3_path.replace("s3://", "").split("/")[0]
    key = "/".join(s3_path.replace("s3://", "").split("/")[1:])
    
    local_csv = os.path.join(RESULTS_DIR, f"{q['name']}.csv")
    s3.download_file(bucket, key, local_csv)
    print(f"  -> Downloaded CSV: {local_csv}")

    # Read rows
    rows = []
    with open(local_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    return {
        "name": q['name'],
        "description": q['description'],
        "query_id": qid,
        "status": status,
        "execution_time_ms": exec_time_ms,
        "bytes_scanned": bytes_scanned,
        "row_count": len(rows),
        "rows": rows
    }

def main():
    results = []
    for q in QUERIES:
        res = run_query(q)
        if res:
            results.append(res)

    summary_file = os.path.join(RESULTS_DIR, "summary_metrics.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Saved summary metrics to {summary_file}")

if __name__ == '__main__':
    main()
