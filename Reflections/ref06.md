# Reflection 6 — Module 6a: The Analytical Engine (DuckDB)

<!-- DRAFT written from my Module 6a notes (duckdb-notes.md, race-results.txt, memo.md). Check every sentence and fill in the [TODO] parts before the checkpoint. -->

[← Reflection 5](ref05.md) · [Module 6a README](../Module06a/README.md) · [Next: Reflection 7 →](ref07.md)

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

My take-away is that there is no "best" database, only the right engine for the right job. On the same 2,000,000 rows, DuckDB ran the dashboard aggregate in about 22 ms while SQLite needed about 281 ms, so almost 13 times faster. But when I tried the opposite kind of work, many small single-row inserts, SQLite did them in 1.8 ms and DuckDB needed almost 4 seconds. The fast engine for reading a big report is the slow engine for writing one row at a time.

What I want to remember: before comparing speed, prove that both sides contain the same data. My honesty check gave 2,000,000 rows and a `SUM(part_price)` of 21,000,000.0 on both sides, so I know the race was fair.

My advice: report the median of several interleaved runs, not your best lucky run.

- What was good?

The `EXPLAIN ANALYZE` output was good because it showed me why DuckDB is fast: it read only the 4 columns the query needs instead of all 7, scanned the 2,000,000 rows, and grouped them down to 350 rows, with the hash group-by as the most expensive step. I also liked writing the memo to Lea and Yasmin, because it forced me to turn my numbers into a real recommendation.

- What was difficult, where did you struggle?

I think I got a hand of it, and now the work is more fluid and becomes easier.  

- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The monthly query was an interesting surprise: there DuckDB was about 44 times faster, while for the dashboard it was "only" about 13 times faster. 

- How was your interaction with peers/instructors?

It was pretty individual; we worked on our laptops and exchanged some advice, but not more than that. 

