SELECT user, count(user) as "Total Count"
FROM ways 
GROUP BY user 
ORDER BY "Total Count" DESC 
LIMIT 10;
