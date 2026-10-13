-- Query 1: Thống kê chỉ số ô nhiễm và thời tiết trung bình theo từng thành phố
-- Mục đích: So sánh mức độ ô nhiễm giữa TP.HCM, Hà Nội và Đà Nẵng

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
