"""
AWS Lambda Function: WeatherCollectorLambda
Hệ thống thu thập và phân tích dữ liệu thời tiết / chất lượng không khí
Môn học: Cloud - Đợt 1 - 2026-2027
GVHD: Huỳnh Xuân Phụng
Sinh viên: 24110054
Role: arn:aws:iam::873674852386:role/LabRole
"""

import json
import os
import urllib.request
import urllib.error
import datetime
import uuid
import boto3

# AWS Clients using LabRole
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
secrets_client = boto3.client('secretsmanager')

# Environment / Defaults
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'weather-aqi-873674852386')
SECRET_NAME = os.environ.get('SECRET_NAME', 'weather/api_config')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts')


def get_aqi_category(us_aqi):
    """Phân loại cấp độ chất lượng không khí theo tiêu chuẩn US EPA."""
    if us_aqi is None:
        return "Unknown"
    val = float(us_aqi)
    if val <= 50:
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
    """Lấy cấu hình và API key từ AWS Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        secret_str = response.get('SecretString', '{}')
        return json.loads(secret_str)
    except Exception as e:
        print(f"[WARN] Failed to fetch secrets from Secrets Manager ({e}). Using default config.")
        return {
            "api_provider": "open-meteo",
            "api_key": "sec_demo_weather_api_key_873674852386",
            "aqi_threshold_pm25": 35.5,
            "aqi_threshold_pm10": 50.0,
            "aqi_threshold_us_aqi": 100,
            "locations": [
                {"city": "HoChiMinh", "lat": 10.8231, "lon": 106.6297},
                {"city": "HaNoi", "lat": 21.0285, "lon": 105.8542},
                {"city": "DaNang", "lat": 16.0544, "lon": 108.2022}
            ]
        }


def http_get_json(url):
    """Gửi HTTP GET request với header tuân thủ điều khoản API."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WeatherAWS_CloudFinalTerm/1.0 (Student Project; Contact: 24110054@student.hcmute.edu.vn)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_city_data(city_info):
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
    aq_json = http_get_json(aq_url)
    aq_current = aq_json.get('current', {})

    # 2. Gọi API thời tiết
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,"
        f"surface_pressure,wind_speed_10m"
    )
    w_json = http_get_json(weather_url)
    w_current = w_json.get('current', {})

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_vn = now_utc + datetime.timedelta(hours=7)

    us_aqi = aq_current.get('us_aqi', 0)
    pm2_5 = aq_current.get('pm2_5', 0.0)
    pm10 = aq_current.get('pm10', 0.0)

    record = {
        "record_id": f"{city}_{now_utc.strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "timestamp_utc": now_utc.strftime('%Y-%m-%d %H:%M:%S'),
        "timestamp_vn": now_vn.strftime('%Y-%m-%d %H:%M:%S'),
        "temperature_2m": float(w_current.get('temperature_2m', 0.0)),
        "relative_humidity_2m": float(w_current.get('relative_humidity_2m', 0.0)),
        "surface_pressure": float(w_current.get('surface_pressure', 0.0)),
        "wind_speed_10m": float(w_current.get('wind_speed_10m', 0.0)),
        "pm2_5": float(pm2_5 if pm2_5 is not None else 0.0),
        "pm10": float(pm10 if pm10 is not None else 0.0),
        "carbon_monoxide": float(aq_current.get('carbon_monoxide', 0.0) or 0.0),
        "nitrogen_dioxide": float(aq_current.get('nitrogen_dioxide', 0.0) or 0.0),
        "sulphur_dioxide": float(aq_current.get('sulphur_dioxide', 0.0) or 0.0),
        "ozone": float(aq_current.get('ozone', 0.0) or 0.0),
        "us_aqi": int(us_aqi if us_aqi is not None else 0),
        "aqi_category": get_aqi_category(us_aqi),
        "year": now_utc.strftime('%Y'),
        "month": now_utc.strftime('%m'),
        "day": now_utc.strftime('%d'),
        "hour": int(now_utc.strftime('%H')),
        "collected_at": now_utc.isoformat()
    }
    return record


def fetch_historical_series(city_info, past_hours=48):
    """
    Thu thập chuỗi dữ liệu lịch sử n giờ gần nhất cho thành phố (phục vụ phân tích Athena & biểu đồ).
    """
    city = city_info['city']
    lat = city_info['lat']
    lon = city_info['lon']

    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,carbon_monoxide,"
        f"nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi&past_days=2&forecast_days=0"
    )
    aq_json = http_get_json(aq_url)
    hourly_aq = aq_json.get('hourly', {})

    w_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,"
        f"surface_pressure,wind_speed_10m&past_days=2&forecast_days=0"
    )
    w_json = http_get_json(w_url)
    hourly_w = w_json.get('hourly', {})

    times = hourly_aq.get('time', [])
    records = []

    for i, t_str in enumerate(times[-past_hours:]):
        idx = len(times) - past_hours + i
        if idx < 0 or idx >= len(times):
            continue
        try:
            dt = datetime.datetime.fromisoformat(t_str)
        except Exception:
            dt = datetime.datetime.strptime(t_str, "%Y-%m-%dT%H:%M")

        dt_utc = dt.replace(tzinfo=datetime.timezone.utc)
        dt_vn = dt_utc + datetime.timedelta(hours=7)

        us_aqi = hourly_aq.get('us_aqi', [])[idx] if idx < len(hourly_aq.get('us_aqi', [])) else 0
        pm2_5 = hourly_aq.get('pm2_5', [])[idx] if idx < len(hourly_aq.get('pm2_5', [])) else 0.0
        pm10 = hourly_aq.get('pm10', [])[idx] if idx < len(hourly_aq.get('pm10', [])) else 0.0
        co = hourly_aq.get('carbon_monoxide', [])[idx] if idx < len(hourly_aq.get('carbon_monoxide', [])) else 0.0
        no2 = hourly_aq.get('nitrogen_dioxide', [])[idx] if idx < len(hourly_aq.get('nitrogen_dioxide', [])) else 0.0
        so2 = hourly_aq.get('sulphur_dioxide', [])[idx] if idx < len(hourly_aq.get('sulphur_dioxide', [])) else 0.0
        o3 = hourly_aq.get('ozone', [])[idx] if idx < len(hourly_aq.get('ozone', [])) else 0.0

        temp = hourly_w.get('temperature_2m', [])[idx] if idx < len(hourly_w.get('temperature_2m', [])) else 0.0
        rh = hourly_w.get('relative_humidity_2m', [])[idx] if idx < len(hourly_w.get('relative_humidity_2m', [])) else 0.0
        press = hourly_w.get('surface_pressure', [])[idx] if idx < len(hourly_w.get('surface_pressure', [])) else 0.0
        wind = hourly_w.get('wind_speed_10m', [])[idx] if idx < len(hourly_w.get('wind_speed_10m', [])) else 0.0

        record = {
            "record_id": f"{city}_{dt_utc.strftime('%Y%m%d%H%M')}_{uuid.uuid4().hex[:6]}",
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "timestamp_utc": dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp_vn": dt_vn.strftime('%Y-%m-%d %H:%M:%S'),
            "temperature_2m": float(temp or 0.0),
            "relative_humidity_2m": float(rh or 0.0),
            "surface_pressure": float(press or 0.0),
            "wind_speed_10m": float(wind or 0.0),
            "pm2_5": float(pm2_5 or 0.0),
            "pm10": float(pm10 or 0.0),
            "carbon_monoxide": float(co or 0.0),
            "nitrogen_dioxide": float(no2 or 0.0),
            "sulphur_dioxide": float(so2 or 0.0),
            "ozone": float(o3 or 0.0),
            "us_aqi": int(us_aqi or 0),
            "aqi_category": get_aqi_category(us_aqi),
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
    subject = f"[AWS ALERT] Cảnh báo AQI cao tại {record['city']} - {record['aqi_category']} ({record['us_aqi']})"
    message = f"""======================================================
HỆ THỐNG CẢNH BÁO CHẤT LƯỢNG KHÔNG KHÍ TỰ ĐỘNG (AWS CLOUD)
Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng
Mã SV: 24110054 | Account ID: 873674852386 | Region: us-east-1
======================================================

Khu vực: {record['city']} (Tọa độ: {record['latitude']}, {record['longitude']})
Thời gian ghi nhận (VN): {record['timestamp_vn']} (UTC: {record['timestamp_utc']})

THÔNG SỐ Ô NHIỄM:
- Chỉ số US AQI: {record['us_aqi']} -> Phân loại: {record['aqi_category']} (Ngưỡng: {threshold_aqi})
- Bụi mịn PM2.5: {record['pm2_5']} µg/m³ (Ngưỡng cho phép: {threshold_pm25} µg/m³)
- Bụi PM10: {record['pm10']} µg/m³
- Ozone (O3): {record['ozone']} µg/m³
- Carbon Monoxide (CO): {record['carbon_monoxide']} µg/m³
- Khí NO2: {record['nitrogen_dioxide']} µg/m³ | SO2: {record['sulphur_dioxide']} µg/m³

ĐIỀU KIỆN THỜI TIẾT:
- Nhiệt độ: {record['temperature_2m']} °C
- Độ ẩm không khí: {record['relative_humidity_2m']} %
- Tốc độ gió: {record['wind_speed_10m']} km/h
- Áp suất: {record['surface_pressure']} hPa

KHUYẾN CÁO SỨC KHỎE:
- Nhóm nhạy cảm (trẻ em, người cao tuổi, người có bệnh hô hấp) nên hạn chế hoạt động ngoài trời.
- Đeo khẩu trang chống bụi mịn PM2.5 khi ra đường.

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
                "owner": "24110054",
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
    print(f"[INFO] Lambda execution started. Event: {json.dumps(event)}")
    config = fetch_secrets()
    locations = config.get('locations', [])
    threshold_pm25 = float(config.get('aqi_threshold_pm25', 35.5))
    threshold_aqi = int(config.get('aqi_threshold_us_aqi', 100))

    backfill_hours = event.get('backfill_hours') if isinstance(event, dict) else None

    all_records = []
    alerts_sent = 0

    if backfill_hours:
        print(f"[INFO] Backfill mode requested for past {backfill_hours} hours.")
        for loc in locations:
            recs = fetch_historical_series(loc, past_hours=int(backfill_hours))
            all_records.extend(recs)
    else:
        for loc in locations:
            try:
                rec = fetch_city_data(loc)
                all_records.append(rec)
                
                # Kiểm tra ngưỡng cảnh báo
                if rec['pm2_5'] >= threshold_pm25 or rec['us_aqi'] >= threshold_aqi:
                    print(f"[WARN] High pollution detected at {rec['city']}: PM2.5={rec['pm2_5']}, AQI={rec['us_aqi']}")
                    if send_sns_alert(rec, threshold_pm25, threshold_aqi):
                        alerts_sent += 1
            except Exception as e:
                print(f"[ERROR] Failed to fetch data for {loc.get('city')}: {e}")

    saved_files = save_records_to_s3(all_records)

    result = {
        "statusCode": 200,
        "message": "Weather & Air Quality data collection completed successfully.",
        "records_collected": len(all_records),
        "alerts_sent": alerts_sent,
        "saved_files": saved_files,
        "bucket": BUCKET_NAME
    }
    print(f"[INFO] Result: {json.dumps(result)}")
    return result
