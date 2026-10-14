"""
AWS Lambda Function: WeatherCollectorLambda
Hệ thống thu thập và phân tích dữ liệu thời tiết / chất lượng không khí
Môn học: Cloud - Đợt 1 - 2026-2027
GVHD: Huỳnh Xuân Phụng
Sinh viên: Nguyễn Tiến Sơn (24110054) & Trần Thị Ngọc Quyên (24110051)
"""

import json
import os
import urllib.request
import urllib.error
import datetime
import uuid
import math
import boto3

# AWS Clients using LabRole
REGION = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
s3_client = boto3.client('s3', region_name=REGION)
sns_client = boto3.client('sns', region_name=REGION)
secrets_client = boto3.client('secretsmanager', region_name=REGION)

# Deployment-specific identifiers are supplied by the environment.
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
SECRET_NAME = os.environ.get('SECRET_NAME', 'weather/api_config')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
HTTP_TIMEOUT_SECONDS = 15
STORAGE_RESERVE_SECONDS = 10
AIR_FIELDS = ('us_aqi', 'pm2_5', 'pm10', 'carbon_monoxide',
              'nitrogen_dioxide', 'sulphur_dioxide', 'ozone')
WEATHER_FIELDS = ('temperature_2m', 'relative_humidity_2m',
                  'surface_pressure', 'wind_speed_10m')


def safe_float(val, default=0.0):
    """Chuyển đổi an toàn sang float, xử lý None, rỗng hoặc giá trị không hợp lệ."""
    if val is None:
        return float(default)
    try:
        number = float(val)
        return number if math.isfinite(number) else float(default)
    except (ValueError, TypeError, OverflowError):
        return float(default)


def safe_int(val, default=0):
    """Chuyển đổi an toàn sang int, xử lý None, rỗng hoặc giá trị không hợp lệ."""
    if val is None:
        return int(default)
    try:
        return int(float(val))
    except (ValueError, TypeError, OverflowError):
        return int(default)


def get_aqi_category(us_aqi):
    """Phân loại cấp độ chất lượng không khí theo tiêu chuẩn US EPA."""
    if us_aqi is None:
        return "Unknown"
    try:
        val = float(us_aqi)
    except (ValueError, TypeError, OverflowError):
        return "Unknown"
    if not math.isfinite(val) or val < 0:
        return "Unknown"
    elif val <= 50:
        return "Good"
    elif val <= 100:
        return "Moderate"
    elif val <= 150:
        return "Unhealthy for Sensitive Groups"
    elif val <= 200:
        return "Unhealthy"
    elif val <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def fetch_secrets():
    """Lấy vị trí thu thập và ngưỡng cảnh báo từ Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        secret_str = response.get('SecretString', '{}')
        return json.loads(secret_str)
    except Exception as e:
        print(f"[WARN] Failed to fetch secrets from Secrets Manager ({e}). Using default config.")
        return {
            "api_provider": "open-meteo",
            "aqi_threshold_pm25": 35.5,
            "aqi_threshold_pm10": 50.0,
            "aqi_threshold_us_aqi": 100,
            "locations": [
                {"city": "HoChiMinh", "lat": 10.8231, "lon": 106.6297},
                {"city": "HaNoi", "lat": 21.0285, "lon": 105.8542},
                {"city": "DaNang", "lat": 16.0544, "lon": 108.2022}
            ]
        }


def http_get_json(url, timeout=HTTP_TIMEOUT_SECONDS):
    """Gửi HTTP GET request với header tuân thủ điều khoản API."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WeatherAWS_CloudFinalTerm/1.0 (Student Project; Contact: 24110054@student.hcmute.edu.vn)"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _fetch_api_json(url, context=None):
    """Limit each HTTP call using the invocation's current remaining time."""
    if context is None:
        return http_get_json(url)
    available = context.get_remaining_time_in_millis() / 1000 - STORAGE_RESERVE_SECONDS
    if not math.isfinite(available) or available <= 0:
        raise TimeoutError('Collection budget exhausted before API request.')
    return http_get_json(url, timeout=min(HTTP_TIMEOUT_SECONDS, available))


def _api_section(payload, name, fields, source):
    """Reject absent API blocks while retaining named null-field defaults."""
    section = payload.get(name) if isinstance(payload, dict) else None
    if not isinstance(section, dict) or not any(field in section for field in fields):
        raise ValueError(f'{source} API has no {name} measurement fields.')
    if name == 'hourly' and (not isinstance(section.get('time'), list) or not section['time']):
        raise ValueError(f'{source} API has no hourly observation times.')
    return section


def fetch_city_data(city_info, context=None):
    """
    Thu thập dữ liệu thời tiết và chất lượng không khí hiện tại cho một thành phố.
    Sử dụng Open-Meteo Air Quality & Weather API.
    """
    city = city_info['city']
    lat = city_info['lat']
    lon = city_info['lon']

    # 1. Gọi API chất lượng không khí
    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&current=pm10,pm2_5,carbon_monoxide,"
        f"nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi"
    )
    aq_json = _fetch_api_json(aq_url, context)
    aq_current = _api_section(aq_json, 'current', AIR_FIELDS, 'Air quality')

    # 2. Gọi API thời tiết
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,"
        f"surface_pressure,wind_speed_10m"
    )
    w_json = _fetch_api_json(weather_url, context)
    w_current = _api_section(w_json, 'current', WEATHER_FIELDS, 'Weather')

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_vn = now_utc + datetime.timedelta(hours=7)

    us_aqi = aq_current.get('us_aqi')
    pm2_5 = aq_current.get('pm2_5')
    pm10 = aq_current.get('pm10')

    record = {
        "record_id": f"{city}_{now_utc.strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "city": city,
        "latitude": safe_float(lat),
        "longitude": safe_float(lon),
        "timestamp_utc": now_utc.strftime('%Y-%m-%d %H:%M:%S'),
        "timestamp_vn": now_vn.strftime('%Y-%m-%d %H:%M:%S'),
        "temperature_2m": safe_float(w_current.get('temperature_2m')),
        "relative_humidity_2m": safe_float(w_current.get('relative_humidity_2m')),
        "surface_pressure": safe_float(w_current.get('surface_pressure')),
        "wind_speed_10m": safe_float(w_current.get('wind_speed_10m')),
        "pm2_5": safe_float(pm2_5),
        "pm10": safe_float(pm10),
        "carbon_monoxide": safe_float(aq_current.get('carbon_monoxide')),
        "nitrogen_dioxide": safe_float(aq_current.get('nitrogen_dioxide')),
        "sulphur_dioxide": safe_float(aq_current.get('sulphur_dioxide')),
        "ozone": safe_float(aq_current.get('ozone')),
        "us_aqi": safe_int(us_aqi),
        "aqi_category": get_aqi_category(us_aqi),
        "year": now_utc.strftime('%Y'),
        "month": now_utc.strftime('%m'),
        "day": now_utc.strftime('%d'),
        "hour": int(now_utc.strftime('%H')),
        "collected_at": now_utc.isoformat()
    }
    return record


def fetch_historical_series(city_info, past_hours=48, context=None):
    """
    Thu thập chuỗi dữ liệu lịch sử n giờ gần nhất cho thành phố (phục vụ phân tích Athena & biểu đồ).
    """
    city = city_info['city']
    lat = city_info['lat']
    lon = city_info['lon']

    past_days = max(1, (past_hours + 23) // 24)

    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,carbon_monoxide,"
        f"nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi&past_days={past_days}&forecast_days=0"
    )
    aq_json = _fetch_api_json(aq_url, context)
    hourly_aq = _api_section(aq_json, 'hourly', AIR_FIELDS, 'Air quality')

    w_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,"
        f"surface_pressure,wind_speed_10m&past_days={past_days}&forecast_days=0"
    )
    w_json = _fetch_api_json(w_url, context)
    hourly_w = _api_section(w_json, 'hourly', WEATHER_FIELDS, 'Weather')

    times = hourly_aq.get('time', [])
    records = []

    total_times = len(times)
    start_idx = max(0, total_times - past_hours)
    weather_indices = {timestamp: index for index, timestamp in enumerate(hourly_w.get('time', []))}
    def weather_value(name, index):
        values = hourly_w.get(name, [])
        return values[index] if index is not None and index < len(values) else None

    for idx in range(start_idx, total_times):
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

        weather_idx = weather_indices.get(t_str)
        temp_raw = weather_value('temperature_2m', weather_idx)
        rh_raw = weather_value('relative_humidity_2m', weather_idx)
        press_raw = weather_value('surface_pressure', weather_idx)
        wind_raw = weather_value('wind_speed_10m', weather_idx)

        record = {
            "record_id": f"{city}_{dt_utc.strftime('%Y%m%d%H%M')}_{uuid.uuid4().hex[:6]}",
            "city": city,
            "latitude": safe_float(lat),
            "longitude": safe_float(lon),
            "timestamp_utc": dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp_vn": dt_vn.strftime('%Y-%m-%d %H:%M:%S'),
            "temperature_2m": safe_float(temp_raw),
            "relative_humidity_2m": safe_float(rh_raw),
            "surface_pressure": safe_float(press_raw),
            "wind_speed_10m": safe_float(wind_raw),
            "pm2_5": safe_float(pm2_5_raw),
            "pm10": safe_float(pm10_raw),
            "carbon_monoxide": safe_float(co_raw),
            "nitrogen_dioxide": safe_float(no2_raw),
            "sulphur_dioxide": safe_float(so2_raw),
            "ozone": safe_float(o3_raw),
            "us_aqi": safe_int(us_aqi_raw),
            "aqi_category": get_aqi_category(us_aqi_raw),
            "year": dt_utc.strftime('%Y'),
            "month": dt_utc.strftime('%m'),
            "day": dt_utc.strftime('%d'),
            "hour": int(dt_utc.strftime('%H')),
            "collected_at": dt_utc.isoformat()
        }
        records.append(record)

    return records


def send_sns_alert(record, threshold_pm25, threshold_aqi):
    """Gửi cảnh báo qua Amazon SNS khi AQI hoặc PM2.5 vượt ngưỡng."""
    if not SNS_TOPIC_ARN:
        print("[WARN] SNS_TOPIC_ARN is not configured. Skipping alert.")
        return False

    subject = f"[AWS ALERT] Cảnh báo AQI cao tại {record['city']} - {record['aqi_category']} ({record['us_aqi']})"
    message = f"""======================================================
HỆ THỐNG CẢNH BÁO CHẤT LƯỢNG KHÔNG KHÍ TỰ ĐỘNG (AWS CLOUD)
Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng
Nhóm: Domain Apps | Region: {REGION}
======================================================

Khu vực: {record['city']} (Tọa độ: {record['latitude']}, {record['longitude']})
Thời gian ghi nhận (VN): {record['timestamp_vn']} (UTC: {record['timestamp_utc']})

THÔNG SỐ Ô NHIỄM:
- Chỉ số US AQI: {record['us_aqi']} -> Phân loại: {record['aqi_category']} (Ngưỡng: {threshold_aqi})
- Bụi mịn PM2.5: {record['pm2_5']} µg/m³ (Ngưỡng cấu hình cảnh báo: {threshold_pm25} µg/m³)
- Bụi PM10: {record['pm10']} µg/m³
- Ozone (O3): {record['ozone']} µg/m³
- Carbon Monoxide (CO): {record['carbon_monoxide']} µg/m³
- Khí NO2: {record['nitrogen_dioxide']} µg/m³ | SO2: {record['sulphur_dioxide']} µg/m³

ĐIỀU KIỆN THỜI TIẾT:
- Nhiệt độ: {record['temperature_2m']} °C
- Độ ẩm không khí: {record['relative_humidity_2m']} %
- Tốc độ gió: {record['wind_speed_10m']} km/h
- Áp suất: {record['surface_pressure']} hPa

Thông tin lưu trữ: s3://{BUCKET_NAME}/raw/year={record['year']}/month={record['month']}/day={record['day']}/
======================================================
"""
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],  # SNS Subject max 100 chars
            Message=message
        )
        print(f"[INFO] SNS Alert sent successfully. MessageId: {response.get('MessageId')}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send SNS alert: {e}")
        return False


def save_records_to_s3(records):
    """
    Lưu dữ liệu vào S3 với cấu trúc phân vùng chuẩn:
    s3://{BUCKET}/raw/year=YYYY/month=MM/day=DD/{filename}.json
    Dữ liệu được lưu dạng NDJSON (Newline Delimited JSON) để Athena đọc dễ dàng.
    """
    if not records:
        print("[INFO] No records to save to S3.")
        return []

    if not BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME must be configured before data can be saved.")

    grouped_by_partition = {}
    for r in records:
        key = (r['year'], r['month'], r['day'])
        if key not in grouped_by_partition:
            grouped_by_partition[key] = []
        grouped_by_partition[key].append(r)

    saved_files = []
    for (year, month, day), part_records in grouped_by_partition.items():
        batch_id = uuid.uuid4().hex[:8]
        s3_key = f"raw/year={year}/month={month}/day={day}/data_{year}{month}{day}_{batch_id}.json"
        
        # Newline-delimited JSON (NDJSON)
        ndjson_body = "\n".join(json.dumps(r) for r in part_records) + "\n"
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=ndjson_body.encode('utf-8'),
            ContentType='application/json',
            Metadata={
                "project": "WeatherAWS_FinalTerm",
                "owner": "24110054,24110051",
                "record_count": str(len(part_records))
            }
        )
        saved_files.append({"s3_key": s3_key, "count": len(part_records)})
        print(f"[INFO] Uploaded {len(part_records)} records to s3://{BUCKET_NAME}/{s3_key}")

    return saved_files


def lambda_handler(event, context):
    """
    Điểm vào chính của Lambda function.
    Hỗ trợ chế độ realtime (mặc định theo EventBridge) hoặc backfill (truyền qua event).
    """
    if not isinstance(event, dict):
        event = {}

    print("[INFO] Lambda execution started.")
    config = fetch_secrets()
    locations = config.get('locations', [])
    threshold_pm25 = float(config.get('aqi_threshold_pm25', 35.5))
    threshold_aqi = int(config.get('aqi_threshold_us_aqi', 100))

    backfill_hours = event.get('backfill_hours')
    fetch_options = {'context': context} if context is not None else {}

    all_records = []
    alerts_sent = 0
    failed_cities = []

    if backfill_hours:
        print(f"[INFO] Backfill mode requested for past {backfill_hours} hours.")
        for loc in locations:
            try:
                recs = fetch_historical_series(loc, past_hours=int(backfill_hours), **fetch_options)
                if not recs:
                    raise RuntimeError('No historical records returned.')
                all_records.extend(recs)
            except Exception as e:
                failed_cities.append(loc.get('city', 'unknown'))
                print(f"[ERROR] Failed historical fetch for {loc.get('city', 'unknown')}: {e}")
    else:
        for loc in locations:
            try:
                rec = fetch_city_data(loc, **fetch_options)
                all_records.append(rec)
                
                # Kiểm tra ngưỡng cảnh báo
                if rec['pm2_5'] >= threshold_pm25 or rec['us_aqi'] >= threshold_aqi:
                    print(f"[WARN] High pollution detected at {rec['city']}: PM2.5={rec['pm2_5']}, AQI={rec['us_aqi']}")
                    if send_sns_alert(rec, threshold_pm25, threshold_aqi):
                        alerts_sent += 1
            except Exception as e:
                failed_cities.append(loc.get('city', 'unknown'))
                print(f"[ERROR] Failed to fetch data for {loc.get('city')}: {e}")

    if not all_records:
        raise RuntimeError('No records collected; check API responses and configured locations.')
    saved_files = save_records_to_s3(all_records)

    result = {
        "statusCode": 200,
        "message": "Weather & Air Quality data collection " + ("partially completed." if failed_cities else "completed successfully."),
        "collection_status": "partial" if failed_cities else "complete",
        "failed_cities": failed_cities,
        "records_collected": len(all_records),
        "alerts_sent": alerts_sent,
        "saved_files": saved_files,
        "bucket": BUCKET_NAME
    }
    print(f"[INFO] Result: {json.dumps(result)}")
    return result
