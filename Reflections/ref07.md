# Reflection 7 — Module 6b: Polyglot Persistence & the Decision

[← Reflection 6](ref06.md) · [Module 6b README](../Module06b/README.md) · [All reflections](README.md)

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

My take-away is that a database engineer is not the person who knows the most engines, but the person who can explain why each workload lives where it does, and back it up with a number. After six modules of measuring, this module asked me to put everything together on one page, and I realized that almost every row of my decision record came from something I had already measured earlier: the ingest from Module 4, the report from Module 6a, and the JSON plans and session timings from today.

What I want to remember: an expression index only works for the exact expression it was built on. `json_extract(meta, '$.vendor')` used the index, while `meta ->> 'vendor'` scanned the whole table, even though both found the same 334 devices. It is the same trap as `lower(technician)` in Module 3, just in a new form.

My advice: "NoSQL" does not mean "no schema". A JSON column with `json_valid` and an index on the paths you filter on is still a schema; it is just a more flexible one.

- What was good?

The decision record was good because it forced me to connect the whole course. I liked that there was no single correct answer, only an answer I could defend, and my answer was that if Kortmann could run only one engine, it would be SQLite, and the first thing to break would be the month-end report.

- What was difficult, where did you struggle?

The hardest part was that I missed this session because of a doctor's appointment, so I had to work through the module alone. I could not try the shared PostgreSQL server, and above all I could not compare my ideas with my pod or defend my decision record in front of another pod, which is the part of the module where you usually notice your own mistakes. Without that discussion, it was also harder to be sure that I had really understood ACID, BASE and CAP, so I tried to connect each word to something I had actually run myself.

- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The key-value benchmark surprised me. I expected the key-value store to win easily, because a session lookup is exactly what it is made for, but SQLite was just as fast for reading and much faster for writing, and on top of that it could count how many sessions used each filter, which `shelve` cannot do at all. [TODO: add the numbers from your own laptop.]

- How was your interaction with peers/instructors?

This time there was almost no interaction, because I was not in class. Instead of the shared-server task I ran the SQLite fallback described in the module, with two writers on the same row, and instead of the defence with another pod I answered the four questions of the listening pod myself, in my [decision record](../Module06b/README.md#defence-notes).

- Who did you help, gave feedback to?

Since I worked on this module alone, I did not help anyone this time.
