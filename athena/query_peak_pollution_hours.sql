-- Query 2: Phân tích khung giờ cao điểm ô nhiễm trong ngày
-- Mục đích: Xác định thời điểm nồng độ bụi PM2.5 và PM10 đạt đỉnh

SELECT 
    hour,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(us_aqi), 2) AS avg_aqi,
    COUNT(*) AS sample_count
FROM weather_aqi_db.weather_airquality_records
GROUP BY hour
ORDER BY hour ASC;
