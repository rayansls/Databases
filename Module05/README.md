# Module 5 — Normalization vs. Denormalization

[← Module 4](../module04/README.md) · [Back to my portfolio](../README.md) · [Reflection 5](../Reflections/ref05.md) · [Next: Module 6a →](../Module06a/README.md)

In Module 4 I made each row correct. In this module the question was about the shape of the whole database. The story: Kortmann's machine-health dashboard needs 40 seconds to answer, and the operations lead, Yasmin Kaya, suggests a shortcut — copy the site and the technician onto every job row, so the dashboard reads just one table. She is right that reading becomes faster, but copying the same fact into many places has a price. My task was to do both things, keep the schema correct *and* add a fast reporting table on purpose, and then measure what each choice costs, so the decision is made with numbers and not with opinions.

> **Note on teamwork:** during class I worked with my new pod, and we did tasks 1 (functional dependencies), 2 (the anomalies) and 4 (the race) together; that part of the work is in my teammates' portfolios: [TODO: add the links to my teammates' Module 5 folders]. Below I explain the whole module in my own words, with the evidence that is in my folder.

## Learning goals

1. Derive **functional dependencies** from a relation and identify candidate keys.
2. Normalize a relation to **1NF, 2NF, and 3NF**, explaining the anomaly each step removes.
3. **Denormalize deliberately** to speed up a hot read path, and predict what it costs on writes and storage.
4. **Measure** the trade-off: query latency, write cost, and database size — before and after.
5. Decide, and *defend*, where a schema should sit on the normalization spectrum for a given workload.

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

[TODO: add the dashboard query time for both designs, from the race we did in class.]

**Writing and storage.** This is where the price shows ([`price_it.sql`](price_it.sql), [`price_it_results.txt`](price_it_results.txt)):

| Design | Rows changed when one machine moves site | Time of that update | Storage |
|---|---:|---:|---:|
| Normalized (3NF, 4 tables) | 1 | ~0.6 ms | ~4.1 MB |
| Denormalized (`report_jobpart`) | 4,000 | ~25 ms | ~11.1 MB |

The number I find most important is not the milliseconds but the rows touched: **1 against 4,000**. That is exactly the update anomaly from the "break it" round, now with a price tag, and it grows with every job the plant records. On top of that, the report table needs almost three times the storage for the same information.

## 5. Deciding and defending

For this plant I would keep the operational tables, where jobs and parts are written every day, in 3NF, because there every fact must be stored once and every update must touch one row. The denormalized `report_jobpart` is worth having only as a *read-only copy* for the dashboard, and only if it is clear from the start how it stays fresh, for example by rebuilding it on a schedule or by keeping it in sync with a trigger like the ones from [Module 4](../module04/README.md); otherwise the dashboard will one day show a machine at the wrong site, and nobody will notice.

[TODO: write this as the short memo to the operations lead, with my own numbers, as the module asks.]

---

## Pictures

[Screenshots from this module](pictures/)

## Reflection 5

What I took away from this module is in [Reflection 5](../Reflections/ref05.md).

**Where this leads:** the reporting table made reading faster, but it is still SQLite, an engine built to read and write single rows. In [Module 6a](../Module06a/README.md) I move a much bigger version of this same report, 2,000,000 rows, into an engine designed only for analysis, DuckDB, and race the two.
