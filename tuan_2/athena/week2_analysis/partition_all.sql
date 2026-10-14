SELECT year, month, day, COUNT(*) AS record_count, COUNT(DISTINCT city) AS cities FROM weather_airquality_records GROUP BY year, month, day ORDER BY year, month, day;
