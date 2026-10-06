-- Tạo bảng ngoại (External Table) trên AWS Athena cho dữ liệu thời tiết và chất lượng không khí
-- Định dạng: JSON (phân vùng theo year, month, day)
-- Database: weather_aqi_db
-- Bucket: s3://weather-aqi-873674852386/raw/

CREATE EXTERNAL TABLE IF NOT EXISTS weather_aqi_db.weather_airquality_records (
    record_id STRING,
    city STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    timestamp_utc STRING,
    timestamp_vn STRING,
    temperature_2m DOUBLE,
    relative_humidity_2m DOUBLE,
    surface_pressure DOUBLE,
    wind_speed_10m DOUBLE,
    pm2_5 DOUBLE,
    pm10 DOUBLE,
    carbon_monoxide DOUBLE,
    nitrogen_dioxide DOUBLE,
    sulphur_dioxide DOUBLE,
    ozone DOUBLE,
    us_aqi INT,
    aqi_category STRING,
    hour INT,
    collected_at STRING
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
    'ignore.malformed.json' = 'true'
)
LOCATION 's3://weather-aqi-873674852386/raw/'
TBLPROPERTIES ('has_encrypted_data'='false');
