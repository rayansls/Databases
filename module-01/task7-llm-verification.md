# Task 7 — LLM-assisted SQL profiling

## Prompt given to the LLM
"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending."

## LLM-generated SQL
```sql
<incolla la query dell'LLM>
```

## My corrected/verified SQL
```sql
SELECT machine, AVG(spindle_load) AS avg_load
FROM readings
WHERE ts > '2026-01-05 18:00:00'
GROUP BY machine
ORDER BY avg_load DESC;
```

## What the LLM got right
<es: struttura SELECT/GROUP BY/ORDER BY corretta>

## What the LLM got wrong (or could get wrong)
<es: usa LIKE '%18%' invece di ts > '...' — matcha "18" anche in altri contesti>

## How I verified
<es: ho eseguito EXPLAIN QUERY PLAN e ho confrontato con la query corretta>

## One-paragraph verification
The model got X right. It got Y wrong. I verified by Z.