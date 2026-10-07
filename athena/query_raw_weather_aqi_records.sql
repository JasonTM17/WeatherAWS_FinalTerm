-- Query 5: Trích xuất toàn bộ bản ghi dữ liệu thô (Raw Weather & AQI Records)
-- Mục đích: Xuất toàn bộ 156 bản ghi đo đạc từ AWS Athena ra định dạng CSV qua AWS CLI

SELECT 
    record_id,
    city,
    latitude,
    longitude,
    timestamp_utc,
    timestamp_vn,
    temperature_2m,
    relative_humidity_2m,
    surface_pressure,
    wind_speed_10m,
    pm2_5,
    pm10,
    carbon_monoxide,
    nitrogen_dioxide,
    sulphur_dioxide,
    ozone,
    us_aqi,
    aqi_category,
    hour,
    collected_at,
    year,
    month,
    day
FROM weather_aqi_db.weather_airquality_records
ORDER BY timestamp_utc DESC;
