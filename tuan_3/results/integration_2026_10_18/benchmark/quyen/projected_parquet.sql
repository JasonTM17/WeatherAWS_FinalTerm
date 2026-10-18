SELECT city, COUNT(*) AS samples, AVG(us_aqi) AS avg_aqi, AVG(pm2_5) AS avg_pm2_5 FROM w3_RUN_ID_projected_parquet WHERE year='2026' AND month='10' AND day='16' GROUP BY city ORDER BY city
