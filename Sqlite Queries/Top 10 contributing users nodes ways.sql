SELECT combined.user, count(*) as "Total Count" 
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) combined 
Group BY combined.user 
ORDER BY "Total Count" DESC LIMIT 10;