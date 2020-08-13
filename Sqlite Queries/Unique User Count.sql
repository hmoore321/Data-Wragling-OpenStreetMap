SELECT COUNT(DISTINCT(combined.uid)) as "Unique User Count"
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) combined;