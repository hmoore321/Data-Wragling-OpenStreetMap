SELECT key, value as Amenity, Count(*) AS "Total Count"
FROM Ways_tags
GROUP BY key, value
HAVING key='amenity' and "Total Count" > 5
ORDER BY "Total Count" DESC;
