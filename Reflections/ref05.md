# Reflection 5 — Module 5: Normalization vs. Denormalization

[← Reflection 4](ref04.md) · [Module 5 README](../Module05/README.md) · [Next: Reflection 6 →](ref06.md)

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

My main take-away is that normalization is not a rule you simply obey, but a trade-off you have to measure. When I split the flat 200,000-row table into four clean tables, nothing was lost: joining them back together gave exactly 200,000 rows again, and the `part` table shrank to only 10 rows, because every price was now stored once instead of thousands of times. The denormalized report table is supposed to be faster to read, but it pays for that every time a fact changes, and, as I found out in this module, it is not even guaranteed to be faster.

What I want to remember is that the number that really matters is not the milliseconds, but the rows touched. Moving one machine to another site changed 1 row in the normalized design and 4,000 rows in the report table. That is the update anomaly from the "break it" round, only now with a price tag.

The second take-away has nothing to do with SQL. It was a strange day, because my usual team was not there, so I formed a new pod with people I had never worked with before, and it worked well. I learned that being flexible and working with people you don't know is not something negative but something positive, because everyone brings a different way of thinking about the same problem.

My advice: keep the transactional tables in 3NF, and if you add a fast reporting copy, decide from the start how it stays up to date. And change teams from time to time: if it is done well, it can only help you grow.

- What was good?

The price-it round was good because the numbers were so clear. On my run, the update took about 0.6 ms on the normalized side and about 25 ms on the report table, and the report table used about 11 MB against about 4 MB for the four normalized tables, so almost three times the storage for exactly the same information.

- What was difficult, where did you struggle?

The hardest part was not technical. At the beginning, it was difficult to come up with a strategy with teammates I did not know yet: getting to know each other, understanding everyone's strengths, and deciding who would take which task. It was slow at the start, but in the end we split the work well and it turned out very well.

- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The index experiment was the most surprising part. With the index `ix_report_machine`, the plan showed `SCAN report_jobpart USING INDEX ix_report_machine`, and after dropping it the plan became a plain `SCAN report_jobpart`, and the query actually got faster, as the module predicted: the median went from about 166 ms with the index to about 108 ms without it. Because the dashboard reads the whole table anyway, the index only adds extra jumps, the same lesson I had already learned in Module 3.

The bigger surprise was that our denormalized dashboard was not faster at all: in our pod's measurement, the normalized dashboard took about 133 ms, while the indexed report table took about 163 ms. The whole idea of denormalizing was to make reading faster, so this result made me question the shortcut instead of just accepting it.

- How was your interaction with peers/instructors?

During class, I worked with my new pod: Isa Babayev ([portfolio](https://github.com/isa-babayev-ibabayev/databases-portfolio)), Arshia Ziaee ([GitHub](https://github.com/Arshia-zi)) and Asmin Metin ([portfolio](https://github.com/asminmetin/databases-portfolio)). We worked through the functional dependencies and the anomalies together; Isa wrote down the dependencies, Asmin and Arshia drew the two ER sketches, and Isa ran the price-it round. That part of the work is in my teammates' portfolios.

After class I talked with the professor about our results, because my denormalized version was actually slower than the normalized one, which is the opposite of what we expected.

- Who did you help, gave feedback to?

In the pod I took care of asking an LLM for its list of functional dependencies and comparing it with ours, and I built the normalized tables and the race; these parts are in my portfolio ([Module 5](../Module05/README.md)).
