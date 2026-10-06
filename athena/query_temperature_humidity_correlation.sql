-- Query 4: Phân tích tương quan giữa Thời tiết (Nhiệt độ, Độ ẩm, Gió) và Ô nhiễm (PM2.5)
-- Mục đích: Khảo sát ảnh hưởng của yếu tố khí tượng đến nồng độ bụi mịn

SELECT 
    city,
    ROUND(corr(temperature_2m, pm2_5), 4) AS corr_temp_pm25,
    ROUND(corr(relative_humidity_2m, pm2_5), 4) AS corr_humidity_pm25,
    ROUND(corr(wind_speed_10m, pm2_5), 4) AS corr_wind_pm25
FROM weather_aqi_db.weather_airquality_records
GROUP BY city;
