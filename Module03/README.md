# Module 3 — LLM-Assisted SQL & Query Profiling

[← Module 2](../module02/README.md) · [Back to my portfolio](../README.md) · [Reflection 3](../Reflections/ref03.md) · [Next: Module 4 →](../module04/README.md)

In Module 2 I learned to read a database I did not build. In this module I started asking it real questions, but with a twist: an LLM writes the SQL, and my job is to decide whether I can trust it. "It ran and gave a number" is not enough. I had to check if the answer was correct, if it was fast, and if it was safe, and for that I learned to read the query plan, which shows what the database engine is actually going to do. I worked on `warehouse.db`, a shop database with customers, products, orders and about 240,000 order lines, built by [`setup.sql`](setup.sql). All my notes, predictions and numbers are collected in [`sql-notes.md`](sql-notes.md).

## Learning goals

1. Build complex **DQL** queries: joins, aggregation with `GROUP BY`/`HAVING`, subqueries, and window functions. [evidence 1](#1-building-complex-queries)
2. Read **`EXPLAIN QUERY PLAN`** as primary evidence: say what the engine will do for a given query, tell a `SCAN` from a `SEARCH`, and a table lookup from a covering index. [evidence 2](#2-reading-the-query-plan)
3. **Benchmark** the effect of an index and explain when the planner ignores one. [evidence 3](#3-benchmarking-an-index-and-when-it-does-not-help)
4. Generate a query with an **LLM**, then **verify** it: correctness, performance, and edge cases. [evidence 4](#4-verifying-the-llms-query)
5. **Prevent SQL injection** with bound parameters and demonstrate why string concatenation is exploitable. [evidence 5](#5-sql-injection-and-bound-parameters)

---

## 1. Building complex queries

The main query of this module was a small sales dashboard: for each city, how many different customers ordered something in 2025, and how much revenue they produced. To answer it, the query has to join four tables (customer → orders → order lines → product), filter by date, group by city and sort by revenue. It looks long, but once I read it clause by clause it is simply a chain of questions.

Two things made it click for me. The first was learning *why* the clauses run in the order they do: SQL first needs to know which rows exist (`FROM`, `JOIN`, `WHERE`) before it can group them and pick the columns, which is also why an aggregate like `COUNT()` cannot go into `WHERE` and needs `HAVING` instead; I verified this by getting the error `misuse of aggregate: COUNT()` on purpose. The second was the relational algebra check, where I wrote the same query as `σ` (filter rows), `π` (keep columns) and `⋈` (glue tables) and compared it with the LLM's version. They had the same meaning; the LLM only added renames for the table aliases.

In the stretcher I wrote the same question ("late orders per customer") in three different ways: with `GROUP BY`, with a correlated subquery and with a window function (`COUNT(*) OVER (PARTITION BY ...)`). They looked like three ways to say the same thing, but they were not:

| Version | Median time | Rows returned |
|---|---:|---:|
| `GROUP BY` | ~6 ms | 400 |
| Correlated subquery | ~3,900 ms | 2,000 |
| Window function | ~14 ms | 400 |

The subquery was hundreds of times slower, because it scanned the orders table once for every customer, and it also returned 2,000 rows instead of 400, including the 1,600 customers with zero late orders, so it was answering a slightly different question. The window version needed a `DISTINCT`, otherwise it returns one row per order. The simple `GROUP BY` was both the most readable and the fastest.

## 2. Reading the query plan

`EXPLAIN QUERY PLAN` became my most useful tool in this module. The two words I learned to look for are `SCAN`, which means the engine reads the whole table row by row, and `SEARCH`, which means it uses an index (or the primary key) to jump directly to the rows it needs. A **covering index** is a special case: when the index already contains every column the query needs, the engine never has to open the table at all.

In the plan safari, I wrote my prediction first and then compared it with the real plan:

| Query | My prediction | Actual plan |
|---|---|---|
| `technician = 'Beier'` (no index) | scanning for a specific name | `SCAN maint_job` |
| same, after creating `ix_job_tech` | finding the specific result | `SEARCH maint_job USING INDEX ix_job_tech` |
| `technician LIKE '%ei%'` (with index) | more filtered results | still `SCAN maint_job` |
| `lower(technician) = 'beier'` (with index) | finds it in the sorted list | still `SCAN maint_job` |

I was wrong more than once, and that is how I really learned it. An index is sorted from the left, like a phone book, so a pattern that starts with `%` gives it nowhere to start, and a function like `lower()` wrapped around the column hides the column from the index. My plan for the dashboard query is saved in [`task1_plan.txt`](task1_plan.txt). It also surprised me: even without any extra index, the engine starts from the biggest table (`order_line`) and reaches the other three through their primary keys.

## 3. Benchmarking an index, and when it does not help

I asked the LLM how to make the dashboard faster, and it suggested three indexes: on `orders(ordered_on)`, `order_line(order_id)` and `order_line(product_id)`. Instead of adding all three at once, I added them one at a time and measured the median of five runs after each step ([`bench.py`](bench.py), [`bench_output.txt`](bench_output.txt)):

| Index added | What happened to the dashboard plan | Dashboard time |
|---|---|---|
| none (baseline) | `SCAN ol` first | ~100–118 ms |
| `ix_orders_ordered_on` | unchanged, the index is not used | ~100–120 ms |
| `ix_orderline_order` | the plan flips to two index searches | ~340–370 ms, **slower** |
| `ix_orderline_product` | unchanged, not used | ~330–340 ms |

This negative result was the most important thing I learned in the module. The second index really did change the plan, and the planner really did use it, but it made the dashboard about three times slower. The reason is that the 2025 filter keeps about two thirds of all orders, and when you need most of the table, thousands of small jumps through an index cost more than one simple scan from start to end. (When I re-ran `bench.py` later, the gap was even bigger: about 124 ms against about 1,075 ms.)

The same indexes were not useless, though; they just help *other* queries. A lookup for one single day went from about 2 ms to about 0.1 ms with the date index, and a filter on one product went from about 7 ms to about 0.6 ms. So the LLM's list was not wrong, it was incomplete: an index helps a specific query, and you only know which one by measuring. I also noticed that two identical runs gave me 100 ms and 118 ms, so the plan is better evidence than the clock.

## 4. Verifying the LLM's query

For the dashboard I gave the LLM the exact schema and asked for the query in plain English (the full prompt and SQL are in [`sql-notes.md`](sql-notes.md#task-1)). It returned Bielefeld, Gütersloh, Münster and Paderborn, each with 500 customers and their revenue. To check whether that was true, I did three things:

- **Correctness:** I recomputed the same four cities independently in Python and got identical customers and revenue. I also understood why `COUNT(DISTINCT ...)` is needed: the joins repeat each customer once per order line, so a plain `COUNT` would count the same person many times.
- **Edge cases:** the date filter uses `>= '2025-01-01' AND < '2026-01-01'`. A version with `BETWEEN '2025-01-01' AND '2026-01-01'` would wrongly include New Year's Day 2026, and I measured the difference: 40,686 orders instead of 40,575.
- **Performance:** I checked the plan, and I noted that a common LLM variant, `strftime('%Y', ordered_on) = '2025'`, would wrap the column in a function and stop any index from helping.

This time the LLM was right about the query, but its advice about indexes was only half right, and I would not have known either of these things without testing.

## 5. SQL injection and bound parameters

In [`injection_demo.py`](injection_demo.py) I built the classic mistake on purpose: a query made by gluing the user's input directly into the SQL string. With a normal input it returns one customer. With the input `' OR '1'='1`, the condition becomes always true and it returns all 2,000 customers. And the name `O'Brien`, a completely innocent input, crashes it with a syntax error, because the apostrophe ends the string too early. The safe version, with a `?` placeholder and the value passed separately, returned an empty list for both inputs, because the value is only ever treated as data ([`injection_output.txt`](injection_output.txt)).

The module also asked why escaping the quotes is not a real fix. My answer is that escaping means trying to predict every dangerous character in every single query: it does not work for table or column names, numbers do not even need a quote to be attacked (`WHERE id = 1 OR 1=1`), and different databases and encodings treat characters differently. With bound parameters the database receives the query and the value separately, so the value can never become SQL, and I do not have to be perfect on every call.

---

## Curiosities and questions I posted

Some things looked strange to me and I kept them, with their source, in [`sql-notes.md`](sql-notes.md#8-curiosities-with-sources): for example that SQLite accepts a `SELECT` alias inside `WHERE`, which the class says is an error, and that `date(ordered_on) = ...` turns into a scan of the covering index once an index exists. I posted both questions in `#sql-questions`.

## Reflection 3

What I took away from this module, and what was hard, is in [Reflection 3](../Reflections/ref03.md).

**Where this leads:** in this module I checked whether the *queries* were right. In [Module 4](../module04/README.md) the question becomes whether the *data* is right, and how to make the database itself refuse bad data, without trusting the application to do it.
