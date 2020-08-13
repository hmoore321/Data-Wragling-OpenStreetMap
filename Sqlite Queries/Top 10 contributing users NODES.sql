SELECT user, count(user) as "Total Count" 
FROM nodes 
GROUP BY user 
ORDER BY "Total Count" DESC 
LIMIT 10;
