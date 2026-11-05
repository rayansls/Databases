# Reflection 1 in Module 1

- What is your take-away, what do you want to remember, what would be your advice?
  Take-away can be small summary, but better outstanding points.

The big idea of this module is simple: at the edge, there is no DBA to save you. The database has to be paranoid. So we make SQLite refuse garbage on its own, instead of trusting the application.

The three golden rules I want to remember:

1. Constraints are only real if you have seen them reject something. If you never saw the exact error message, you don't actually know the constraint works.

2. PRAGMA foreign_keys = ON is per-connection and OFF by default. Every new connection starts with foreign keys disabled. If a tool forgets this, orphan rows slip in silently.

3. CHECK does not stop NULLs. A CHECK constraint only rejects when the condition is FALSE. NULL is unknown, so the row goes through. You need NOT NULL for that.

My advice to past me: read the CREATE TABLE line by line like a sentence. Every clause is a rule in plain English. That makes the whole thing much less scary.
- What was good?

The best part was the acceptance test at the start. Running three junk INSERTs into an unconstrained table and seeing all three land without any complaint was a great "before" picture. It made the constrained version feel like it actually mattered.

I also liked the UPSERT task. Seeing the row count stay the same after running the Python script twice was very satisfying. It felt like I built something that actually survives a network outage, which is the whole point of the edge story.

The triggers were fun too. Watching the database insert an alarm row on its own, just because I wrote one reading with a high value, was cool.
- What was difficult, where did you struggle?

The FOREIGN KEY test gave me trouble. I ran the INSERT for sensor 99 and it just went through, no error. I thought I had broken my schema. Then I realized the PRAGMA foreign_keys = ON was only active in the connection where I set it. Every new sqlite3 command opens a fresh connection, and in that fresh connection foreign keys are back to OFF. So the orphan row landed, and I didn't even notice at first.

I also had a weird copy-paste issue in the setup script where the CHECK line got corrupted. The database still looked like it worked, but I had to double-check with .schema reading to make sure the constraint was actually there. Lesson: always verify the schema after creating a table.

The NULL + CHECK behavior was also confusing at first. I expected the CHECK to reject the NULL, but it was the NOT NULL that did the work. Once I understood that NULL is not FALSE, it clicked.
- Was there any good/fun “struggling”/exploration?
  Any show stoppers – anything where you should reach out to peers or instructors?

The FOREIGN KEY moment was the best "aha". I had read in the module notes that the pragma is per-connection, but reading it and seeing it happen are two different things. When I re-ran the test with the PRAGMA inside the same script, the FOREIGN KEY constraint failed error finally appeared. That felt like winning a small battle.

No real show stoppers. The setup mistake was annoying but fixable. The rest of the tasks went smoothly once I stopped trying to outsmart the shell (my first NULL test was run directly in bash and got a syntax error, because bash doesn't understand parentheses).

The benchmark was a nice surprise. The trigger only added a small overhead (a few hundredths of a second on 10,000 rows), which made me realize that triggers are not automatically "slow" — it depends on what they do. That changed how I think about them.
- How was your interaction with peers/instructors?

I mostly worked alone, but I used the pod discussion to compare notes. The most surprising thing other pods found was that a table with no constraints accepts text in a number column without complaining. We all had a good laugh at that.

When I got stuck on the FOREIGN KEY issue, I checked the module notes and the SQLite documentation page on foreign keys, which confirmed the per-connection behavior. I didn't need to ask the instructor, but knowing the answer was documented somewhere was reassuring.
- Who did you help, gave feedback to?

I helped a bit Jonathan

