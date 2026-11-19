# Module 1 — Introduction & Local-First Foundations

[← Back to my portfolio](../README.md) · [Reflection 1](../Reflections/ref01.md) · [Next: Module 2 →](../module02/README.md)

This was my very first contact with databases, and in a way it was also my first contact with this way of studying. Before I could write a single query I had to understand how the class works, build my own portfolio on GitHub and set up a toolchain on my laptop. Only at the end of the session did I load real data into a database and ask it questions. Below I go through the learning goals one by one and explain, in my own words, what I understood and what I did to reach each of them.

## Learning goals

1. Explain how this class works — the CBL/PBL philosophy, the portfolio-based project work assessment, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a `.gitignore` that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with `uv` — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.
4. Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.

---

## 1. How this class works

The first thing I understood is that this is not a class where you listen to a lecture and then write an exam. It uses Challenge-Based and Project-Based Learning (CBL/PBL), which means that we learn by investigating a real problem and building a real solution for it, and the professor deliberately starts from stories, because people learn best when the problem connects to something real and meaningful.

There is no written exam. Instead, each of us builds and maintains one GitHub repository, this portfolio, which contains all of our work, and at the checkpoints we show the professor, together with our pod, that we have reached the learning goals of each module. The professor does not check whether we followed every task exactly, but whether we can *prove* that we reached the goals. That is why every README in this portfolio is organized around the learning goals.

The "moving bar" took me a moment to understand. It means that this is the first time the course is taught in this form, so the syllabus, the tasks and even the tools can change during the semester as the professor learns what works and what does not. The learning goals stay fixed; the way we reach them can move.

We work in Task Pods of three people, and for the final project two pods merge into a Project Team. To reach this goal I read the syllabus and the module index, I formed my Task Pod with [Jonathan Behring](https://github.com/Jonathan-T-B/databasesclass) and [Aron Grudaj](https://github.com/AronGrudaj/Databases-Portfolio), and I understood that the portfolio is the main thing we are building all semester.

## 2. My GitHub portfolio and the `.gitignore`

I created this repository from the course template, made it public, added the professor as a collaborator, cloned it to my computer and opened it in VS Code.

The most important lesson of this goal was the [`.gitignore`](../.gitignore) file. Git is designed to track everything in a repository, but some files should never go online: database files (`*.db`, `*.duckdb`), because they are large and can always be rebuilt from my scripts; the `.venv/` folder, because it is specific to my machine; secrets such as `.env`, because they contain passwords and API keys; and generated files like `telemetry.csv`, because anyone can reproduce them. The `.gitignore` tells Git to ignore these files, so they stay on my computer but never appear on GitHub.

I learned this the honest way, by making the mistake first: I pushed `tour.db` and `telemetry.csv` to GitHub before the `.gitignore` was in place. I fixed it by creating the `.gitignore` and running `git rm --cached`, which tells Git to stop tracking the files without deleting them from my disk.

## 3. A reproducible toolchain with `uv`

`uv` is the tool that builds the whole environment for me. It downloads the Python version the course needs and the libraries (DuckDB, Datasette, sqlite-utils, Pydantic, SQLAlchemy), and it installs them in a separate `.venv/` folder inside the project, so they never conflict with other projects on my computer. The file `uv.lock` pins the exact versions, so anyone who clones my repository gets exactly the same setup, which is what "reproducible" means here.

What I did: I installed `uv` (and solved a PATH problem simply by restarting the terminal), then I ran `uv init`, `uv python install 3.14`, `uv python pin 3.14` and `uv add duckdb datasette sqlite-utils pydantic sqlalchemy`. I installed the `sqlite3` shell with `winget install SQLite.SQLite`, and `litecli`, `datasette` and `sqlite-utils` as global tools. Finally I wrote [`uv-check.py`](../uv-check.py) and ran it with `uv run uv-check.py` to confirm that everything was installed; the result is in [`uv-check-output.txt`](../uv-check-output.txt), and my project settings are in [`pyproject.toml`](../pyproject.toml).

[TODO: the saved output currently shows Python 3.13.5 from a `.venv` in my user folder, not 3.14 from the project. Re-run `uv run uv-check.py` inside the project folder and save the new output.]

Before moving on to Python, I also took a short tour of the `sqlite3` shell ([`shell-tour.txt`](shell-tour.txt), [`tour.sql`](tour.sql), [my notes](shell-tour-notes.txt)). My favourite command was `.schema`, because it prints the exact `CREATE` statement that built a table, which is the fastest way to understand a database you did not design yourself. That turned out to be the main skill of Module 2.

## 4. Embedded vs. client/server — with a measurement

The simplest way I can put it: an **embedded** database is a file that lives inside my program, while a **client/server** database is a separate program, often on another machine, that my program has to connect to over a network. For a local app the file is enough, and the server is just extra complication: something to install, run, secure and pay for.

The course asked me to show this with a measurement rather than a slide, so I wrote [`generate_telemetry.py`](generate_telemetry.py), which generates two days of telemetry from three CNC machines, one reading every three seconds, and [`load_telemetry.py`](load_telemetry.py), which loads it into SQLite. Then I measured the result ([`task6-db-size.txt`](task6-db-size.txt), [`task6-queries-with-timings.txt`](task6-queries-with-timings.txt)):

| What I measured | Result |
|---|---|
| Rows loaded | 172,800 (57,600 per machine) |
| Size of the whole database | about 10 MB, one single file |
| Count readings per machine | about 56 ms |
| Peak vibration per machine | about 54 ms |
| Count readings above a threshold | about 14 ms |

Two days of a small machine shop fit in a 10 MB file, and every question I asked came back in a few hundredths of a second, on my own laptop, with no server, no administrator and no monthly bill. For a local dashboard or a weekly shift report, that is all that is needed, and this is why most local apps should not run a server.

## 5. Real rows into SQLite, with bound parameters

In `load_telemetry.py` I opened the CSV, opened (or created) a SQLite database file, created a table called `readings` and copied every row from the CSV into it, using Python instead of typing SQL by hand.

The important part is *how* the rows go in. I learned that building an SQL statement by gluing strings together is dangerous, because if a value contains a quote or a piece of SQL, the database might execute it as code; this is called SQL injection. The safe way is to use **bound parameters**: `?` placeholders in the SQL, with the values passed separately, so the database always treats them as data and never as code. My loader does exactly that, with five `?` for five columns:

```python
conn.executemany("INSERT INTO readings VALUES (?, ?, ?, ?, ?)", rows)
```

I proved the difference with a small demo, [`bound-parameters-demo.py`](bound-parameters-demo.py), explained in [`bound-parameters.md`](bound-parameters.md): the same malicious input breaks the unsafe version, which tries to run a `DROP TABLE`, while the safe version simply stores it as a strange but harmless piece of text, and the table is still there.

## 6. My first LLM-generated query: verify before you trust

I asked an LLM for a query on my `readings` table: the average spindle load per machine for readings taken overnight, after 18:00 ([full write-up](task7-llm-verification.md), [output](task7-output.txt), [SQL](task7-queries.sql)). The query ran and looked perfectly reasonable, and the shape was right: `AVG`, `GROUP BY machine`, `ORDER BY ... DESC`.

But when I tried to break it, I found the problem in the time filter. The model used `ts LIKE '%18%'`, which matches *any* "18" anywhere in the timestamp: the 18th day of a month, or 18 seconds past any minute, while it completely misses the hours from 19:00 to 23:59. I corrected it to `ts > '2026-01-05 18:00:00'`, which works because ISO timestamps sort as text in the same order as in time, then I ran both versions, compared the results, tested an edge case and checked the plan with `EXPLAIN QUERY PLAN`.

This was a small example, but it gave me the sentence I keep for the rest of the course: **generated SQL is a hypothesis, not an answer**. It has to be run, checked and broken before I trust it.

---

## Pictures

[Screenshots from this module](pictures/README.md)

## Reflection 1

What I took away from this first session, and how it felt, is in [Reflection 1](../Reflections/ref01.md).

**Where this leads:** in this module I built a database from scratch, with data I generated myself. In [Module 2](../module02/README.md) the situation is reversed: I inherit a database that somebody else built, without any documentation, and I have to find out what it really means and what is wrong with it.
