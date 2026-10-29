# Module 1
## Learning goals
1. Explain how this class works — the CBL/PBL philosophy, the portfolio-based project work assessment, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a .gitignore that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with uv — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.
4. Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.



## Task Inspirations
By the end of this module, you can:
Explain how this class works — the CBL/PBL philosophy, the portfolio-based project work assessment, and the "moving bar" of a first-time course.
-         This class uses Challenge-Based Learning (CBL) and Project-Based Learning (PBL); we learn by investigating a real problem and building a real solution
-          The professor starts from stories because people learn best when the problem is meaningful and connected to something real.
-          The assessment is portfolio-based. We do not take a written exam. Instead, we build and maintain one GitHub repository that contains all our work.  At the end of every 4th module, we demonstrate that we have reached the learning goals in a short checkpoint presentation with the professor. The professor checks whether you can prove that you reached the goals.
-          The phrase "moving bar" refers to the fact that this is the first time the course is being taught in this form. The syllabus, the tasks, and even the tools may change during the semester as the professor learns what works and what does not.
-          We work in Task Pods, small teams of three people. For the final project, two pods merge into a Project Team of six people.
-          What I did to reach this goal: I read the syllabus and the module index, I formed my Task Pod with Jonathan and Aron, and I understood that the portfolio is the main artefact you are building.
Set up your personal GitHub portfolio from the course template, with a clean first commit and a .gitignore that keeps databases and secrets out of Git.
-          I learned how to clone the repository to your computer and open it in VS Code
-          The most important technical lesson in this goal is the .gitignore file. Git is designed to track everything in your repository, but some files should never be committed: database files (*.db, *.duckdb), because they are large and can be rebuilt from scripts; environment files (.venv/), because they are machine-specific; secrets (.env), because they contain passwords and API keys; and generated files like telemetry.csv, because they are reproducible. The .gitignore tells Git to ignore these files, so they stay on your computer but never appear on GitHub.
-          What you did to reach this goal: you created databases-portfolio from the template, made it public, added the professor as a collaborator, created module-01/README.md with the learning goals, and I made a mistake: I pushed tour.db and telemetry.csv to GitHub before the .gitignore was in place. I then fixed it by creating the .gitignore and running git rm --cached to untrack the files without deleting them from your disk.

Set up the entire toolchain reproducibly with uv — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.

uv downloads the Python version you need and the libraries (DuckDB, Datasette, sqlite-utils, pydantic, SQLAlchemy). It installs them in a separate folder called .venv/ inside the project, so they do not conflict with other projects on your computer. uv.lock pins the exact versions, so anyone who clones your repository gets the same setup. Finally, uv-check.py verifies that everything is installed correctly.

-          What I did to reach this goal: I installed uv (and solved the PATH problem by restarting the terminal), I ran uv init, uv python install 3.14, uv python pin 3.14, and uv add duckdb datasette sqlite-utils pydantic sqlalchemy. I installed sqlite3 with winget install SQLite.SQLite. I installed litecli, datasette, and sqlite-utils as global tools. I created uv-check.py and ran it with uv run uv-check.py, confirming that everything was installed correctly.
Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
An embedded database is a file inside my program. A client/server database is a separate program that I connect to over a network. For a local app, the file is enough — the server is just extra complication.
-	I created generate_telemetry.py, which generates two days of machine-shop telemetry from three CNC machines, one reading every three seconds, for a total of 172,800 rows. I then loaded this data into SQLite with load_telemetry.py, which uses Python's built-in sqlite3 module with bound parameters. After loading the data, I measured the result.

Load real rows into SQLite and query them from Python using bound parameters.
-          Get real data (not fake, hand-typed numbers)
-          Put that data into SQLite using Python (not by typing SQL by hand)
o   Opened the CSV
o   Opened (or created) a SQLite database file
o   Created a table called readings
o   Copied every row from the CSV into the table
-          Ask questions of that data (query it) — and do it safely using a technique called "bound parameters"
o   I learned that inserting data into SQLite by concatenating strings is dangerous; it allows SQL injection. The safe way is to use bound parameters: ? placeholders with values passed separately, so the database always treats them as data, never as code. I proved this with a demo that shows a malicious input destroying a table in the unsafe version but being stored literally in the safe version."

Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.
I asked an LLM for a query on my readings table. It worked, but when I tried to break it I found that it used LIKE '%18%' for the time filter, which matches any '18' anywhere in the timestamp, not just the hour 18:00. I corrected it to ts > '2026-01-05 18:00:00', compared the results, and confirmed the difference 


## Reflection 1
[Reflection 1](/Reflections/ref01.md)
