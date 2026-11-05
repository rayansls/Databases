# Reflection 1 in Module 1

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

Take-away:
A database that works is not necessarily a database that is correct. The old legacy.db ran fine for years, but it was silently making mistakes. Defect 5 was the worst: the JOIN did not crash, it just returned fewer rows. A silent wrong answer is worse than an error.

What I want to remember:
- A natural key without the UNIQUE rule is not a key, it is just a normal column. For example, part_no was duplicated because the database did not know it had to be unique.
- SQLite does not check foreign keys by default. You have to turn it on with PRAGMA foreign_keys = ON. Otherwise it accepts links to things that do not exist.
- You prove a defect with a query, not by looking at the column name. machine_name looked like a link to another table, but it was just text.

My advice:
Do not trust the names of the columns. Use COUNT and JOIN to check if the data really matches.
- What was good?

The investigative part was good. Taking a broken schema and proving the defects with SQL queries felt like being a database detective. Writing the contract.py was also good: seeing the old text columns change into strict rules like NUMERIC, ForeignKey, and UNIQUE felt like really fixing the problem, not just talking about it.
- What was difficult, where did you struggle?

The hardest part was the setup. I had problems running SQLite commands in Windows PowerShell. The syntax I copied did not work, so I had to learn how to run a .sql file instead.
- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The fun moment was Defect 3. I ran the query to find prices less than 15. I expected three parts, but I only got one. I was confused, then I understood that 9.90 is smaller than 15 as a number, but as text it comes after 15 because the letter 9 is bigger than the letter 1. It was fun to find out why the cheapest part disappeared.
- How was your interaction with peers/instructors?

The interaction with my Task Pod was mostly individual for the technical part, because everyone needs to prove their own learning. But the Task C discussion with another pod was useful.
- Who did you help, gave feedback to?

I helped a bit Jonathan

