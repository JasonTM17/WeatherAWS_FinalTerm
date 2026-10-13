-- Tạo Athena View: vietnam_weather_aqi
-- Cho phép truy vấn song song và hoán đổi trong suốt giữa 2 tên bảng:
-- 'vietnam_weather_aqi' và 'weather_airquality_records'
-- Database: weather_aqi_db

CREATE OR REPLACE VIEW weather_aqi_db.vietnam_weather_aqi AS
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
FROM weather_aqi_db.weather_airquality_records;
