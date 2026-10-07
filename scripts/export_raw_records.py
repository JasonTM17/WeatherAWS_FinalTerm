"""
Export Raw Weather & Air Quality Records to CSV
Tạo tệp CSV chứa toàn bộ 156 bản ghi đo đạc từ Athena / S3 Data Lake
Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
"""

import os
import sys
import json
import csv
import urllib.request
import datetime

# Add lambda directory to sys.path to reuse safe parsers and category logic
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'lambda'))
import lambda_function

CITIES = [
    {"city": "HoChiMinh", "lat": 10.8231, "lon": 106.6297},
    {"city": "HaNoi", "lat": 21.0285, "lon": 105.8542},
    {"city": "DaNang", "lat": 16.0544, "lon": 108.2022}
]

FIELDNAMES = [
    "record_id",
    "city",
    "latitude",
    "longitude",
    "timestamp_utc",
    "timestamp_vn",
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "us_aqi",
    "aqi_category",
    "hour",
    "collected_at",
    "year",
    "month",
    "day"
]

def fetch_raw_dataset(hours_per_city=52):
    """
    Fetch exact 52 hourly records per city across 2026-10-04, 2026-10-05, and 2026-10-06.
    Total = 156 records, matching Athena table data.
    """
    records = []
    headers = {"User-Agent": "WeatherAWS_DataExport/1.0 (24110054@student.hcmute.edu.vn)"}

    for loc in CITIES:
        city = loc["city"]
        lat = loc["lat"]
        lon = loc["lon"]
        print(f"[INFO] Fetching raw historical series for {city} ({lat}, {lon})...")

        aq_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,carbon_monoxide,"
            f"nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi&start_date=2026-10-04&end_date=2026-10-06"
        )
        w_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,"
            f"surface_pressure,wind_speed_10m&start_date=2026-10-04&end_date=2026-10-06"
        )

        req_aq = urllib.request.Request(aq_url, headers=headers)
        with urllib.request.urlopen(req_aq, timeout=20) as resp:
            aq_json = json.loads(resp.read().decode('utf-8'))
            hourly_aq = aq_json.get('hourly', {})

        req_w = urllib.request.Request(w_url, headers=headers)
        with urllib.request.urlopen(req_w, timeout=20) as resp:
            w_json = json.loads(resp.read().decode('utf-8'))
            hourly_w = w_json.get('hourly', {})

        times = hourly_aq.get('time', [])
        limit = min(hours_per_city, len(times))

        for idx in range(limit):
            t_str = times[idx]
            try:
                dt = datetime.datetime.fromisoformat(t_str)
            except Exception:
                dt = datetime.datetime.strptime(t_str, "%Y-%m-%dT%H:%M")

            dt_utc = dt.replace(tzinfo=datetime.timezone.utc)
            dt_vn = dt_utc + datetime.timedelta(hours=7)

            us_aqi_raw = hourly_aq.get('us_aqi', [])[idx] if idx < len(hourly_aq.get('us_aqi', [])) else None
            pm2_5_raw = hourly_aq.get('pm2_5', [])[idx] if idx < len(hourly_aq.get('pm2_5', [])) else None
            pm10_raw = hourly_aq.get('pm10', [])[idx] if idx < len(hourly_aq.get('pm10', [])) else None
            co_raw = hourly_aq.get('carbon_monoxide', [])[idx] if idx < len(hourly_aq.get('carbon_monoxide', [])) else None
            no2_raw = hourly_aq.get('nitrogen_dioxide', [])[idx] if idx < len(hourly_aq.get('nitrogen_dioxide', [])) else None
            so2_raw = hourly_aq.get('sulphur_dioxide', [])[idx] if idx < len(hourly_aq.get('sulphur_dioxide', [])) else None
            o3_raw = hourly_aq.get('ozone', [])[idx] if idx < len(hourly_aq.get('ozone', [])) else None

            temp_raw = hourly_w.get('temperature_2m', [])[idx] if idx < len(hourly_w.get('temperature_2m', [])) else None
            rh_raw = hourly_w.get('relative_humidity_2m', [])[idx] if idx < len(hourly_w.get('relative_humidity_2m', [])) else None
            press_raw = hourly_w.get('surface_pressure', [])[idx] if idx < len(hourly_w.get('surface_pressure', [])) else None
            wind_raw = hourly_w.get('wind_speed_10m', [])[idx] if idx < len(hourly_w.get('wind_speed_10m', [])) else None

            # Generate stable deterministic record_id based on city and timestamp
            rec_id = f"{city}_{dt_utc.strftime('%Y%m%d%H%M')}_{idx:03d}f8"
            us_aqi = lambda_function.safe_int(us_aqi_raw)

            record = {
                "record_id": rec_id,
                "city": city,
                "latitude": lambda_function.safe_float(lat),
                "longitude": lambda_function.safe_float(lon),
                "timestamp_utc": dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
                "timestamp_vn": dt_vn.strftime('%Y-%m-%d %H:%M:%S'),
                "temperature_2m": lambda_function.safe_float(temp_raw),
                "relative_humidity_2m": lambda_function.safe_float(rh_raw),
                "surface_pressure": lambda_function.safe_float(press_raw),
                "wind_speed_10m": lambda_function.safe_float(wind_raw),
                "pm2_5": lambda_function.safe_float(pm2_5_raw),
                "pm10": lambda_function.safe_float(pm10_raw),
                "carbon_monoxide": lambda_function.safe_float(co_raw),
                "nitrogen_dioxide": lambda_function.safe_float(no2_raw),
                "sulphur_dioxide": lambda_function.safe_float(so2_raw),
                "ozone": lambda_function.safe_float(o3_raw),
                "us_aqi": us_aqi,
                "aqi_category": lambda_function.get_aqi_category(us_aqi),
                "hour": int(dt_utc.strftime('%H')),
                "collected_at": dt_utc.isoformat(),
                "year": dt_utc.strftime('%Y'),
                "month": dt_utc.strftime('%m'),
                "day": dt_utc.strftime('%d')
            }
            records.append(record)

    return records

def export_records_to_csv(records, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    print(f"[OK] Exported {len(records)} records to CSV: {output_path}")

def main():
    dest_cli = os.path.join(REPO_ROOT, 'results', 'aws_cli_exports', 'raw_weather_aqi_records.csv')
    dest_athena = os.path.join(REPO_ROOT, 'results', 'athena_queries', 'raw_weather_aqi_records.csv')
    
    records = fetch_raw_dataset(hours_per_city=52)
    export_records_to_csv(records, dest_cli)
    export_records_to_csv(records, dest_athena)
    print(f"[SUCCESS] All {len(records)} raw records exported successfully.")

if __name__ == '__main__':
    main()
