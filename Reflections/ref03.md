# Reflection 3 — Module 3: LLM-Assisted SQL & Query Profiling

<!-- DRAFT written from my Module 3 notes (sql-notes.md, bench_output.txt). Check every sentence and fill in the [TODO] parts before the checkpoint. -->

[← Reflection 2](ref02.md) · [Module 3 README](../Module03/README.md) · [Next: Reflection 4 →](ref04.md)

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

My take-away from this module is that a query that runs and gives a number is only the beginning, not the end. The LLM wrote me a dashboard query that was actually correct, but I only know that because I recomputed the four cities myself in Python and got the same customers and the same revenue. The query plan taught me the same lesson from another side: it tells you what the engine is really going to do, and it is a more honest witness than the clock, because two identical runs gave me 100 ms and 118 ms.

What I want to remember:
- An index is not a magic speed button. It helps a specific query, and it can make another query slower. When I followed the LLM's advice and added an index on `order_line(order_id)`, the dashboard got about three times slower, because the 2025 filter keeps around two thirds of the orders, and thousands of small index lookups cost more than one simple scan.
- A function around a column hides it from the index: `date(ordered_on) = ...` still scans.
- An index is sorted from the left, so `LIKE '%ei%'` can never use it.
- Bound parameters are the real fix for SQL injection; escaping quotes is just guessing which character will be the dangerous one.

My advice to past me: always write down your prediction before you look at the plan. Being wrong on paper is how I actually learned what `SCAN` and `SEARCH` mean.

- What was good?

The prediction table in the plan safari was good, because it made me commit to an answer first and then compare it with reality. I also liked the injection drill: seeing `' OR '1'='1` return all 2,000 customers, and seeing the name `O'Brien` crash the unsafe query, made the danger very concrete, and the safe version just returned an empty list for both.

- What was difficult, where did you struggle?

The hardest part was understanding the negative result: why an index that the LLM recommended, and that the planner actually used, made the dashboard slower instead of faster. I had to think about how many rows the filter keeps before it made sense. [TODO: add anything else that was hard for you, for example setup problems or the relational algebra notation.]

- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The stretcher with the late orders was a fun exploration: the correlated subquery took about 3.9 seconds, while the GROUP BY version took about 6 ms, and on top of that the subquery returned 2,000 rows instead of 400, so it was not even answering the same question. I also found two curiosities that I posted in `#sql-questions`: why `date(ordered_on) = ...` turns into a scan of the covering index once an index exists, and why SQLite accepts a SELECT alias inside WHERE when the class says it should not.

- How was your interaction with peers/instructors?

[TODO: describe how you worked with your pod and with the other pod in Task C, and whether anyone answered your questions in #sql-questions.]

- Who did you help, gave feedback to?

[TODO]
