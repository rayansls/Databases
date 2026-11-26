# Module 5 — Normalization vs. Denormalization

[← Module 4](../module04/README.md) · [Back to my portfolio](../README.md) · [Reflection 5](../Reflections/ref05.md) · [Next: Module 6a →](../Module06a/README.md)

In Module 4 I made each row correct. In this module the question was about the shape of the whole database. The story: Kortmann's machine-health dashboard needs 40 seconds to answer, and the operations lead, Yasmin Kaya, suggests a shortcut — copy the site and the technician onto every job row, so the dashboard reads just one table. Her idea is that reading becomes faster, but copying the same fact into many places has a price, and as it turned out, the speed-up was not even guaranteed. My task was to do both things, keep the schema correct *and* add a fast reporting table on purpose, and then measure what each choice costs, so the decision is made with numbers and not with opinions.

> **Note on teamwork:** my usual pod was not there, so I worked with a new pod: [Isa Babayev](https://github.com/isa-babayev-ibabayev/databases-portfolio), [Arshia Ziaee](https://github.com/Arshia-zi) and [Asmin Metin](https://github.com/asminmetin/databases-portfolio). We did the first two rounds (the functional dependencies and the anomalies) together: Isa wrote down the dependencies, Asmin and Arshia drew the two ER sketches, and I asked an LLM for its list of dependencies and compared it with ours. I then built the tables and the race, which are in this folder, and Isa ran the full "price it" round; I use Isa's numbers below where mine are missing, and I always say so. Below I explain the whole module in my own words.

## Learning goals

1. Derive **functional dependencies** from a relation and identify candidate keys. [evidence 1](#1-functional-dependencies-and-the-candidate-key)
2. Normalize a relation to **1NF, 2NF, and 3NF**, explaining the anomaly each step removes. [evidence 2](#2-from-the-flat-table-to-3nf-and-the-anomalies-it-removes)
3. **Denormalize deliberately** to speed up a hot read path, and predict what it costs on writes and storage. [evidence 3](#3-denormalizing-on-purpose)
4. **Measure** the trade-off: query latency, write cost, and database size — before and after. [evidence 4](#4-measuring-the-trade-off)
5. Decide, and *defend*, where a schema should sit on the normalization spectrum for a given workload. [evidence 5](#5-deciding-and-defending)

---

## 1. Functional dependencies and the candidate key

We started from a flat table where every row mixes everything together: the job, the machine, the site, the technician, the part and its price. A **functional dependency** `X → Y` means that if two rows agree on `X`, they must also agree on `Y`. In this table:

- `job_id → technician` (and the machine and date): a job is done by one technician;
- `machine_id → site`: a machine stands in one place;
- `part_no → part_price`: a part has one price.

The **candidate key** is the smallest set of columns that determines all the others, and here it is `(job_id, part_no)`, because one row describes one part used in one job. What I found important is the difference between a dependency that is a real rule of the plant and one that just happens to be true in a few rows; an LLM easily turns an accident in five rows into a "rule", and deciding which is which is my job.

## 2. From the flat table to 3NF, and the anomalies it removes

Every one of those dependencies is also a place where the same fact is repeated many times, and that repetition causes three kinds of problems, which we caused on purpose in the "break it" round:

- **Update anomaly:** moving one machine to another site means changing many rows, and if one of them is missed, the database contradicts itself.
- **Insert anomaly:** I cannot record a new part until some job has used it, because a part only exists inside a job row.
- **Delete anomaly:** deleting the last job that used a part silently deletes the price of that part too.

Normalizing means splitting the table so that every fact lives in exactly one place. **1NF** means one value per cell (the comma-separated list from Module 2 breaks this). **2NF** removes facts that depend on only part of the key: the technician depends on `job_id` alone, and the price on `part_no` alone, so they move out to their own tables. **3NF** removes facts that depend on another non-key column: the site depends on the machine, not on the job, so it moves to `machine`.

In [`build.sql`](build.sql) I generated the flat table with 200,000 rows (20,000 jobs × 10 parts each) and split it into four tables. The row counts ([`row_counts.txt`](row_counts.txt)) tell the whole story:

| Table | Rows | What it stores |
|---|---:|---|
| `flat_jobpart` (the original) | 200,000 | everything, repeated |
| `machine` | 50 | each machine and its site, once |
| `part` | 10 | each part and its price, once |
| `job` | 20,000 | each job, its technician and date, once |
| `job_part` | 200,000 | only the links between jobs and parts |
| all four joined back together | 200,000 | proof that nothing was lost |

The `part` table has only 10 rows because there are only 10 different parts; in the flat table each of those 10 prices was written 20,000 times.

## 3. Denormalizing on purpose

Then I did what Yasmin asked, but deliberately and next to the clean tables, not instead of them. In [`report.sql`](report.sql) I built `report_jobpart`, a reporting table that joins the four tables once and stores the result, so the dashboard can read a single table instead of joining four, and I added an index on `machine_id`. Before measuring, my prediction was: reading becomes faster, but every change to a repeated fact becomes more expensive, and the table takes more space.

## 4. Measuring the trade-off

**Reading.** The query plans ([`explain_plan.txt`](explain_plan.txt), [`explain_plans.txt`](explain_plans.txt)) show the difference clearly: the normalized dashboard ([`benchmark.sql`](benchmark.sql)) scans `job_part` and then jumps to the three other tables through their keys, while the report version is a single scan of `report_jobpart`. I also tried the module's experiment of dropping the index: with it the plan was `SCAN report_jobpart USING INDEX ix_report_machine`, and without it a plain `SCAN report_jobpart`.

The times are where the surprise came. My own race only saved the plans and the results, not the times, so here I use the medians of seven runs from Isa's "price it" round, which measured all three versions on the same machine:

| Dashboard on… | Median time |
|---|---:|
| the four normalized tables (3NF) | 133.2 ms |
| `report_jobpart` with the index `ix_report_machine` | 162.7 ms |
| `report_jobpart` after dropping the index | 108.3 ms |

With its index, the denormalized table was actually **slower** than the normalized design, the opposite of what we expected. The reason is the same lesson as in [Module 3](../Module03/README.md#3-benchmarking-an-index-and-when-it-does-not-help): the dashboard reads the whole table anyway, so walking through it via the index only adds thousands of extra jumps. Only after dropping the index did the report table become faster, and even then only by about 25 ms.

**Writing and storage.** This is where the price shows ([`price_it.sql`](price_it.sql), [`price_it_results.txt`](price_it_results.txt)):

| Design | Rows changed when one machine moves site | Time of that update | Storage |
|---|---:|---:|---:|
| Normalized (3NF, 4 tables) | 1 | ~0.6 ms | ~4.1 MB |
| Denormalized (`report_jobpart`) | 4,000 | ~25 ms | ~11.1 MB |

The number I find most important is not the milliseconds but the rows touched: **1 against 4,000**. That is exactly the update anomaly from the "break it" round, now with a price tag, and it grows with every job the plant records. On top of that, the report table needs almost three times the storage for the same information. Isa's run showed the same picture: 1 row against 4,000 rows, and 0.85 ms against 13.9 ms for the update.

## 5. Deciding and defending

Putting the numbers side by side made the decision much easier than I expected. The shortcut promised faster reading, but in our measurement it saved at most about 25 ms per dashboard (and only without its index), while every change to a machine became 4,000 row updates instead of one and the data took almost three times the space. So I wrote this short memo to the operations lead:

> **To:** Yasmin Kaya · **From:** Rayan Slassi · **Re:** Copying site and technician onto every job row
>
> Keep jobs, machines and parts in 3NF: there every fact is stored once, so moving a machine changes 1 row instead of 4,000, and the data needs about 4 MB instead of about 11 MB. On our 200,000 rows the copied table did not make the dashboard clearly faster: 133 ms on the normalized tables, 163 ms on the copy with its index, and 108 ms on the copy without it. If we still want the copy for the dashboard, it must be read-only, without the `machine_id` index, and rebuilt from the 3NF tables on a schedule, so that it can never show a machine at the wrong site for longer than one rebuild. For the really slow reports, the answer is probably not more copies inside SQLite, but a different engine for big reads.

The last sentence of the memo is where I went next.

---

## Pictures

[Screenshots from this module](pictures/)

## Reflection 5

What I took away from this module is in [Reflection 5](../Reflections/ref05.md).

**Where this leads:** the reporting table hardly made reading faster, and it is still SQLite, an engine built to read and write single rows. In [Module 6a](../Module06a/README.md) I move a much bigger version of this same report, 2,000,000 rows, into an engine designed only for analysis, DuckDB, and race the two.
