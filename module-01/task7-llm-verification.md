# Task 7 — LLM-assisted SQL profiling

## Prompt given to the LLM

"Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending."

## LLM-generated SQL

```sql
SELECT machine, AVG(spindle_load) AS avg_load
FROM readings
WHERE ts LIKE '%18%'
GROUP BY machine
ORDER BY avg_load DESC;
```

## My corrected / verified SQL

```sql
SELECT machine, AVG(spindle_load) AS avg_load
FROM readings
WHERE ts > '2026-01-05 18:00:00'
GROUP BY machine
ORDER BY avg_load DESC;
```

## What the LLM got right

The overall query shape was correct: `SELECT ... AVG(...) ... GROUP BY machine ... ORDER BY ... DESC`. The aggregate function and the ordering direction were both correct.

## What the LLM got wrong

The **time filter** was wrong. The LLM used `ts LIKE '%18%'`, which matches any occurrence of "18" anywhere in the timestamp string:

- ✅ includes rows from 18:00 to 18:59
- ❌ wrongly includes rows from **any hour on the 18th day of a month** (e.g. `2026-01-18 05:00:00`)
- ❌ wrongly includes rows where "18" appears in the seconds (e.g. `12:18:30`)
- ❌ **misses** all rows from 19:00 to 23:59

Since `ts` is stored as ISO-8601 text (`YYYY-MM-DD HH:MM:SS`), the correct comparison is `ts > '2026-01-05 18:00:00'`.

## How I verified

1. Ran both queries and compared the `avg_load` values — they differ.
2. Ran `EXPLAIN QUERY PLAN` on the corrected query. It showed `SCAN readings`, which is expected because there is no index on `ts` or `machine`.
3. Tested an edge case: a row with `ts = '2026-01-18 05:00:00'` is wrongly included by `LIKE '%18%'` but correctly excluded by `ts > '2026-01-05 18:00:00'`.

## One-paragraph verification

The model got the **shape** of the query right — SELECT, AVG, GROUP BY, ORDER BY DESC — but got the **filter** wrong. Using `LIKE '%18%'` on a timestamp is a classic string-vs-datetime mistake: it matches any occurrence of "18" anywhere in the string, not just the hour 18:00, and it misses all rows from 19:00 to 23:59. The correct comparison is `ts > '2026-01-05 18:00:00'`, which relies on ISO-8601 timestamps comparing lexicographically in the same order as chronologically. I verified this by running both queries, comparing the results, testing an edge case, and profiling with `EXPLAIN QUERY PLAN`. **Generated SQL is a hypothesis, not an answer** — always run it, profile it, and try to break it before trusting it.