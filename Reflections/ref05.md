# Reflection 5 — Module 5: Normalization vs. Denormalization

<!-- DRAFT written from my Module 5 files (row_counts.txt, price_it_results.txt, explain plans). Check every sentence and fill in the [TODO] parts before the checkpoint. -->

[← Reflection 4](ref04.md) · [Module 5 README](../Module05/README.md) · [Next: Reflection 6 →](ref06.md)

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

My take-away is that normalization is not a rule you obey but a trade-off you measure. When I split the flat 200,000-row table into four clean tables, nothing was lost: joining them back together gave exactly 200,000 rows again, and the `part` table shrank to only 10 rows, because every price was stored once instead of thousands of times. The denormalized report table is faster to read, but it pays for that every time a fact changes.

What I want to remember: the number that really matters is not the milliseconds but the rows touched. Moving one machine to another site changed 1 row in the normalized design and 4,000 rows in the report table. That is the update anomaly from the "break it" round, now with a price tag.

My advice: keep the transactional tables in 3NF, and if you add a fast reporting copy, decide from the start how it stays up to date.

- What was good?

The price-it round was good because the numbers were so clear: the update took about 0.6 ms on the normalized side and about 25 ms on the report table, and the report table used about 11 MB against about 4 MB for the four normalized tables, almost three times the storage for the same information.

- What was difficult, where did you struggle?

[TODO: what was hard for you in this module? For example, understanding functional dependencies, or the output files that came out with strange characters (my .txt results are saved in a format where "Gütersloh" looks broken).]

- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The index experiment was a nice surprise. With the index `ix_report_machine`, the plan showed `SCAN report_jobpart USING INDEX ix_report_machine`, and after dropping it the plan became a plain `SCAN report_jobpart`. [TODO: add whether the query got faster without the index, as the module predicted.]

- How was your interaction with peers/instructors?

During class I worked with my new pod, and we did tasks 1, 2 and 4 together; that part of the work is in my teammates' portfolios. [TODO: add their names and links, and what you learned from working with them.]

- Who did you help, gave feedback to?

I helped Jonathan a bit.
