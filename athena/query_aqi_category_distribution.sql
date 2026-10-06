-- Query 3: Phân bố cấp độ chất lượng không khí (Good vs Moderate vs Unhealthy)
-- Mục đích: Đánh giá tỉ lệ thời gian không khí đạt chuẩn an toàn

SELECT 
    city,
    aqi_category,
    COUNT(*) AS occurrence_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS percentage
FROM weather_aqi_db.weather_airquality_records
GROUP BY city, aqi_category
ORDER BY city, occurrence_count DESC;
