# Module 2 — Data Contracts & Reading Legacy Schemas (ERD Audits)

[← Module 1](../module-01/README.md) · [Back to my portfolio](../README.md) · [Reflection 2](../Reflections/ref02.md) · [Next: Module 3 →](../Module03/README.md)

In Module 1 I built a small database myself, so I knew exactly what every column meant. This module turned the situation around. Real engineers rarely start from an empty page: they inherit a database that somebody else built years ago, usually without a diagram and without documentation, and they have to work out what it was *meant* to say before they can trust it. That is what I did here, with the maintenance database of a fictional plastics plant, Kortmann Kunststofftechnik GmbH.

## Learning goals

1. Reconstruct an **ER/EER model** (entities, attributes, keys, relationships, cardinalities) from an undocumented SQL schema. [evidence 1](#1-reconstructing-the-er-model)
2. Identify **integrity defects** — missing foreign keys, orphan rows, redundant data, normalization violations — with queries, not intuition. [evidence 2](#2-proving-the-integrity-defects-with-queries)
3. Distinguish an **entity relationship** from an attribute, and a **surrogate key** from a natural key, and justify the choice. [evidence 3](#3-entity-or-attribute-natural-or-surrogate-key)
4. Express a schema as a **code-first data contract** (Pydantic / SQLAlchemy) that an application can enforce. [evidence 4](#4-the-data-contract-in-code)
5. Write the **requirements the schema forgot**: the business rules nobody encoded. [evidence 5](#5-the-requirements-the-schema-forgot)

My evidence for this module: [`setup.sql`](setup.sql) (rebuilds `legacy.db`), [`er-audit.md`](er-audit.md) (the full audit), [`contract.py`](contract.py) and [`corrected-schema.sql`](corrected-schema.sql) (the contract), and [`study-log.md`](study-log.md) (the pod study).

---

## Before the lab: studying in the pod

Since everything in this module was new to me, I started with the theory together with my pod. I read the basic pages on the [ER model](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model) and on the [enhanced ER model](https://en.wikipedia.org/wiki/Enhanced_entity%E2%80%93relationship_model), and the first thing I had to google was simply: what is a surrogate key, and what is a natural key? I then asked an LLM to explain the difference and to give me a real case where the wrong choice causes a bug, and instead of just believing the answer, I checked it against the legacy database (more on that below). Everything is collected in my [study log](study-log.md), including my [four sketches from words to diagrams](study-log.md#task-b-from-words-to-sketch) (1:1, 1:n, m:n, and entity vs. relationship) with a `CREATE TABLE` + `COUNT` proof, and the points we agreed on with another pod in Task C.

## 1. Reconstructing the ER model

`legacy.db` has only three tables: `machine`, `part` and `maint_job`. When I read their `CREATE TABLE` statements, I noticed very quickly how much is missing: there are no primary keys, no foreign keys and no UNIQUE rules, prices and dates are stored as plain text (one machine even has `'unknown'` as its installation date), and the parts used in a maintenance job are written as a comma-separated list inside one column.

So instead of drawing the schema as it *is*, I tried to reconstruct the model the designer probably *meant*:

| Entity | Attributes | Intended primary key |
|---|---|---|
| **Machine** | serial_no, site, installed | `serial_no` (natural) + surrogate `machine_id` |
| **Part** | part_no, description, unit_price | `part_no` (natural) |
| **MaintenanceJob** | job_id, done_on | `job_id` (surrogate) |
| **Technician** | name | `technician_id` (surrogate) — *not modelled in the legacy schema* |
| **JobPart** | job_id, part_no | composite `(job_id, part_no)` — *not modelled, hidden in `parts_used`* |

Two of these five entities do not exist in the database at all, and that was the most interesting discovery. The technician was "demoted" to a simple text column, and the many-to-many relationship between jobs and parts was squeezed into the `parts_used` list, so the junction table that should hold it was never created. The three relationships I ended up with are: one machine has many maintenance jobs, one technician does many maintenance jobs, and many jobs use many parts (through `JobPart`). The diagram and my sketches are in the [pictures for this module](pictures/README.md).

To check the cardinality with data and not only with intuition, I followed the module's tip, *count distinct values*, and counted how many parts each job lists:

```sql
SELECT job_id, parts_used,
       LENGTH(parts_used) - LENGTH(REPLACE(parts_used, ',', '')) + 1 AS n_parts
FROM maint_job;
```

Job 1 lists two parts, and parts are also shared between jobs, so `parts_used` really is a many-to-many list hidden in a text column. Job 1 is the proof.

## 2. Proving the integrity defects with queries

The module insisted that I should not *describe* defects but *prove* them, and this is the part where I felt like a database detective. For each defect I wrote a query, saved the result and wrote down what would go wrong in production. The full queries are in [`er-audit.md`](er-audit.md); here is the story they tell:

| Defect | What the query showed | What breaks in production |
|---|---|---|
| 1. Orphan jobs | Job 3 refers to machine `cnc-05`, which does not exist | Reports per machine or per site silently lose or misattribute the job |
| 2. Duplicate natural key | `P-1003` appears twice | Every sum or count over parts counts it twice, with no error |
| 3. Price stored as text | `unit_price < '15'` returns only `P-1001` | The cheapest part (9.90) disappears, because as text `'9.90'` comes after `'15'`; invoices and price reports are wrong |
| 4. Dates that are not dates | `RANDOM-NAME` was "installed" on `'unknown'` | Any filter or age calculation on dates breaks or skips this machine |
| 5. Joining on the list | The JOIN on `parts_used` returns only jobs 2 and 3, and job 2 even twice | Job 1 (two parts) and job 4 (no parts) silently vanish, and the duplicated `P-1003` counts job 2 double |

Defect 3 was my favourite moment of the module, because I expected three parts and got one, and it took me a while to understand that the database was comparing characters, not numbers. Defect 5, on the other hand, was the most worrying: the query did not crash, it just returned fewer rows. That is the main lesson of this goal for me: a silent wrong answer is worse than an error, and only a query can show it. It also showed me that defects do not stay alone: the duplicate part from Defect 2 made job 2 appear twice in the Defect 5 join.

## 3. Entity or attribute? Natural or surrogate key?

The technician is my clearest example of the entity-versus-attribute question. In the legacy schema it is just a name in a text column, which works as long as nobody needs to know anything else about technicians. But a technician performs many jobs and has an identity of their own, and as soon as two technicians share a name, or one of them changes their name, a text column cannot tell them apart. That is why I modelled `Technician` as its own entity.

For keys, my study told me that a **natural key** comes from the real world (a serial number, a part number), while a **surrogate key** is an ID the database invents, which has no meaning outside it. I made my choices like this:

- For **Part**, the part number is stable and already used by everyone in the plant, so `part_no` stays the key, but only if it is declared UNIQUE. The duplicated `P-1003` proved what the LLM had told me in the pod study: *without a UNIQUE constraint, a natural key is not actually a key.*
- For **Machine**, the name is clearly not stable (one machine is literally called `RANDOM-NAME`), so I added a surrogate `machine_id` as the primary key and kept `serial_no` as a UNIQUE natural key next to it.
- For **MaintenanceJob** and **Technician**, there is no natural identifier at all, so they get surrogate keys.

## 4. The data contract in code

An ER diagram is documentation, but a contract is something a program can *enforce*. In [`contract.py`](contract.py) I wrote the corrected schema twice, on purpose, for two different layers:

- **Pydantic** is the contract the *application* checks before it sends anything to the database. This is where business rules live, for example that a serial number must start with `SN-` and that `machine_id` must be positive; the database itself has no idea what a serial number is supposed to look like.
- **SQLAlchemy** is the contract the *database* enforces for every client, not only for my application: primary keys, foreign keys, `UNIQUE(serial_no)`, `NOT NULL`, and a real `NUMERIC(9,2)` type for prices, plus the new `job_part` junction table that repairs the comma-separated list.

Running the script prints the corrected DDL, which I saved in [`corrected-schema.sql`](corrected-schema.sql). Seeing the old text columns turn into strict rules felt like actually fixing the problem instead of just talking about it.

## 5. The requirements the schema forgot

The last goal asked me to write down the business rules that nobody ever encoded. Looking back at my defects, each one is really a forgotten requirement:

- Every maintenance job must belong to a machine that exists (Defect 1 → a foreign key).
- A part number identifies exactly one part (Defect 2 → UNIQUE).
- A price is an amount of money, not a piece of text, and it should never be negative (Defect 3 → a numeric type).
- Every machine has a real installation date (Defect 4 → a date type, NOT NULL).
- A job can use several parts, and each part can appear only once per job (Defect 5 → a junction table with a composite key).
- A technician is a person with an identity, not just a name, and a serial number always starts with `SN-`.

---

## Reflection 2

How this module felt, what I struggled with (mostly PowerShell) and what I want to remember is in [Reflection 2](../Reflections/ref02.md).

**Where this leads:** now that I can read a schema and prove what is wrong with it, the next step is to write queries against a bigger database. In [Module 3](../Module03/README.md) an LLM writes the SQL for me, and my job is to check whether it is correct, fast and safe.
