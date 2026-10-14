-- Task 7 — LLM-assisted SQL profiling
-- Test query
SELECT COUNT(*) FROM readings;

-- Overnight average spindle load per machine (corrected version)
SELECT machine, AVG(spindle_load) AS avg_load
FROM readings
WHERE ts > '2026-01-05 18:00:00'
GROUP BY machine
ORDER BY avg_load DESC;

-- EXPLAIN QUERY PLAN of the same query
EXPLAIN QUERY PLAN
SELECT machine, AVG(spindle_load) AS avg_load
FROM readings
WHERE ts > '2026-01-05 18:00:00'
GROUP BY machine
ORDER BY avg_load DESC;