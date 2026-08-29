# Database migrations — an ordered, recorded schema history (kolt.local 036)

> Status: PROPOSED 2026-08-29 (cycle 38, work order 20, lane
> `migrations`), **BUILT in the same order** — the paper settled the
> semantics, §11 records what shipped. Tracker:
> `../../kolt.local/tracker/items/036.md`.
>
> Scope: the v1 shape the order ruled — steps as `(name, sql)` pairs
> applied in list order, an applied-set table the migrator owns, one
> transaction per step, two loud drift refusals. This paper's job is to
> settle the details that ruling left open (§8 is the determinations
> table) and to state precisely what v1 does **not** do (§9).
>
> Governing records this paper builds on rather than re-decides:
> `kolt-migration.md` §2.2 (`std::db` as the server-only storage seam,
> minimal by design); `destruction.md` (`Database` as a `resource`, no
> public `close()`); `platform-coloring.md` (this is the process layer —
> the client physically cannot reach it); `const-eval.md` §(the asset
> channel) and `filesystem.md` §(`read_dir`) for how a deployed app
> carries its SQL, which §7 treats as a **neighbouring** concern this
> surface deliberately does not depend on.

## 1. The exhibit

kolt's `open_database()` runs, at module load:

```sql
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at INTEGER NOT NULL
)
```

This is an idempotent schema **ensure**, and it is exactly right until the
first schema **change**. Add a `description` column to `task` and the
`IF NOT EXISTS` clause does nothing at all: the table exists, so the
statement is a no-op, and the running database keeps the old shape while
the code that queries it has the new one. There is no spelling for "this
file was created under the old shape; carry it forward". The choices left
are hand-run SQL against production, or delete the file.

Every framework with a database answers this — Rails has
`db/migrate`, Prisma has `prisma migrate`, sqlx has `sqlx migrate`. This
one does not, and `std::db` is batteries-included by doctrine
(`kolt-migration.md` §2.2: the storage seam ships with the language, so
an app does not reach for a package manager to talk to its own disk).
The gap is not an ergonomic one. It is the difference between an app that
can be deployed twice and an app that can be deployed once.

## 2. Where this lands, and where it does not

This is **not** a build-system concern, which is why it fell out of the
027 discussion as a redirect rather than as a manifest key. The database
exists at RUN time, with the deployment, on a machine the build never
sees. No manifest key, no const channel, no build hook and no build
program can reach it: the build produces `dist/`, and `dist/` is then
copied to a host whose database file the compiler has never observed and
must never assume the shape of.

So the migrator is a **runtime surface in `std::db`**, server-coloured,
beside `Database`. It runs when the server boots, against the database
the server just opened, and it is the first thing that happens to that
database — before a single query.

The SQL sources are a separate question with a separate answer (§7): they
ride the const channel into the bundle like every other asset, so the
deployed artifact is still `dist/` and nothing else. The two halves are
independent on purpose. The surface takes *values*; how an app collects
them is the const channel's business, and this paper's build does not
depend on that lane's code.

## 3. The surface

```vilan
struct Migration {
    name: str,
    sql: str,
}

impl Database {
    fun migrate(self, migrations: List<Migration>): List<str>
}
```

A call site, in full:

```vilan
let db = Database::open("app.db");
let applied = db.migrate([
    Migration { name = "001-create-task", sql = asset::read("migrations/001-create-task.sql") },
    Migration { name = "002-task-description", sql = asset::read("migrations/002-task-description.sql") },
]);
print(i"applied {applied.len()} migrations");
```

**Why a method on `Database` and not a `Migrator` type.** `std::db`'s
entire surface is methods on three types — `Database`, `Statement`, `Row`
— and a `Migrator` would be a fourth whose only state is the database it
wraps. It would also fight the memory model: `Database` is a `resource`,
so a `Migrator` holding one either *moves* it (leaving the caller without
the database it just opened, which is absurd for a boot-time call) or
becomes a loan-carrying struct, which is a real cost to pay for a type
with no state. `migrate` is a database operation. It belongs on the
database, spelled the way `exec` and `prepare` are.

**Why it returns `List<str>`.** The names applied, in the order they were
applied. An empty list is the normal steady state — a re-run applies
nothing — which makes idempotence *observable at the call site* rather
than merely asserted in a doc comment. It gives a server a one-line boot
log worth having, and it is what the pins (§10) assert.

## 4. The applied table

The migrator owns exactly one table:

```sql
CREATE TABLE IF NOT EXISTS vilan_migrations (
    name TEXT PRIMARY KEY NOT NULL,
    applied_at_ms INTEGER NOT NULL
)
```

- **`vilan_migrations`**, prefixed, because the table is the language's
  and not the app's: the prefix says which component owns it and keeps it
  out of the app's own namespace. This name is part of the **on-disk
  contract** from the moment the first database records a row in it, so
  it is fixed here and cannot change later without the migrator
  migrating its own table.
- **`name` is the primary key.** A step's identity is its name; its
  position is not stored, and its SQL is not stored (see below).
- **`applied_at_ms`** is epoch milliseconds from `std::time::now()`,
  sampled per step at the moment that step commits. It is an audit
  value — nothing in the algorithm reads it. It is stored at i53 width
  because epoch millis outgrew i32 in 1970 plus 25 days, and read back
  through `Row.big_integer`.
- **No ordinal column.** Application order is not the contract; the
  *source list's* order is (§5), so an ordinal in the table would be a
  second, redundant, potentially disagreeing authority. SQLite gives the
  insertion order back through the implicit rowid for anyone doing a
  human audit, without it being something the migrator promises.
- **No checksum of the SQL.** Considered, and deferred to §9: a hash
  column would let the migrator refuse a step whose *body* changed after
  it was applied, which is a real third drift. It is a strictly additive
  column and a strictly additive refusal, and adding it now would mean
  designing the "yes, I meant to edit that" escape hatch in the same
  breath. v1 records what was applied, not what it said.

The migrator creates this table with the very `CREATE TABLE IF NOT
EXISTS` idiom §1 exists to replace. That is legitimate **here and only
here**: the migrator owns the table's shape, so for this one table
"ensure" and "migrate" coincide, and if the shape ever changes the
migrator is the thing that knows how to change it.

## 5. The algorithm

In order, and the order matters:

1. **Validate the list.** Every `name` must be non-empty and no two may
   be equal (§8 D4, D5). This is a check on the *argument*, before the
   database is touched at all.
2. **Ensure `vilan_migrations`.** Unguarded — a failure here is not a
   step failure and has no step to name.
3. **Read the recorded set**: `SELECT name FROM vilan_migrations`, into a
   `Set<str>`.
4. **Drift refusal (a)** — the database is ahead of the code.
5. **Drift refusal (b)** — a step was inserted into the past.
6. **Apply**, in list order, every step whose name is not recorded.

Nothing is applied before both refusals have passed. A drifted database
is therefore never *touched* — the migrator reads it, refuses, and the
boot stops with the schema exactly as it found it.

Steps 4 and 5 run in that order deliberately: (a) is the more
fundamental condition, and its diagnosis is unambiguous, whereas (b)'s
notion of "the last applied step" is only meaningful once every recorded
name is known to be *in* the list.

### 5.1 Drift refusal (a): the database is ahead of the code

Every recorded name must appear in the source list. If one does not, the
database has been migrated by a build this one does not contain:

> `std::db migrate: the database has migration 'X' applied, but it is not in the 2 migrations given — this database was migrated by a newer build`

This is the deploy-rollback case, and it is the one that quietly
destroys data if it is allowed through: an older binary, whose queries
predate migration `X`, running against a schema that has it. It is also
the "somebody deleted a migration file" case. Either way the code and
the database disagree about history, and the only safe move is to stop.

### 5.2 Drift refusal (b): a step was inserted into the past

Let `last` be the highest index whose step is recorded. Every step before
`last` must also be recorded. If one is not, a step has been added
*behind* history:

> `std::db migrate: migration 'X' is not applied, but 'Y' after it in the list is — a migration was inserted before the applied history`

This is the two-branches-merged case: two developers each add a
migration, the merge orders them, and one of them is now numbered before
a step the shared database has already run. Applying it out of order
would produce a schema that no single ordering of the list can reproduce
— which is to say, a schema no fresh database will ever have. Stop.

Note what this refusal makes redundant: an "names must be strictly
ascending" rule (§8 D6). On a database with history, (b) catches every
misordering such a rule would catch. On a fresh database, any list order
is by construction self-consistent — it *is* the history. The ascending
rule would add no safety and would refuse a legitimate hand-written list.

### 5.3 Applying a step

Each step, in its own transaction:

```
BEGIN
  <the step's sql>
  INSERT INTO vilan_migrations (name, applied_at_ms) VALUES (?, ?)
COMMIT
```

The record INSERT is **inside the step's transaction**. That is the
whole design in one line, and it buys the invariant everything else
rests on:

> **A step is recorded if and only if its SQL committed.**

There is no window in which the schema moved and the record did not, or
the record landed and the schema did not. A process killed mid-migration
— `SIGKILL`, power loss — leaves a database whose recorded set exactly
describes its schema, and the next boot resumes from there.

`node:sqlite` was probed to confirm DDL is transactional there
(§10.1 records the probe verbatim): `BEGIN; CREATE TABLE a (x TEXT);
ROLLBACK;` leaves no table, and a `CREATE TABLE` that fails mid-way
through a multi-statement `exec` is undone along with the statements
before it in the same transaction. SQLite has no implicit commit for
DDL, which is what makes this work and is not true of every SQL engine
(MySQL, notably, commits implicitly on DDL — a host binding added later
would have to say so).

**One transaction per step, not per run.** A per-run transaction sounds
safer and is worse. It makes a five-step migration all-or-nothing, so a
failure in step 5 re-runs steps 1–4 on the next boot — and a step 1 that
is not re-runnable (a `DROP`, a data backfill that doubles) then cannot
recover at all. Per-step, a failed run leaves the successful prefix
applied *and recorded*; the operator fixes the failing SQL, re-runs, and
it resumes exactly at the failure.

### 5.4 A failing step

Nothing is recorded for it, the transaction is rolled back, and the boot
**stops loudly with the step named**:

> `std::db migrate: migration '003-add-index' failed and was not applied: no such table: taks`

The host's own message is quoted — it is the only thing that says *what*
was wrong with the SQL — and the step's name is prepended, because it is
the only thing that says *which file to open*. A server that boots over a
half-migrated schema is the torn-JSON lesson again: the failure is
loud at the moment it happens or it is silent until it corrupts
something.

The rollback is itself guarded and its own failure ignored. SQLite
aborts the transaction by itself for a handful of error classes
(`SQLITE_FULL`, `SQLITE_IOERR`, `SQLITE_BUSY`, `SQLITE_NOMEM`), after
which `ROLLBACK` reports `cannot rollback - no transaction is active`.
That message means the rollback already happened; treating it as a
second failure would replace the real error message with a meaningless
one.

### 5.5 Steps must not manage transactions

A step's SQL may contain any number of statements. It may **not** contain
`BEGIN`, `COMMIT` or `ROLLBACK`, and it may not contain a statement
SQLite refuses inside a transaction (`VACUUM`; `PRAGMA journal_mode`).

This is the one way to break §5.3's invariant, and it is worth being
precise about how. A step that commits itself commits *the migrator's*
transaction under it: the DDL lands permanently, the record INSERT has
not run yet, and the migrator's own `COMMIT` then fails with `cannot
commit - no transaction is active`. The step is reported failed while its
effect is permanent and unrecorded — the exact state everything above is
designed to make unreachable.

**Considered and refused: scanning the SQL for those keywords.**
Substring scanning SQL is not parsing SQL. `-- COMMIT the design doc`,
`'commit'` as a string literal, and a column named `commit_sha` are all
false refusals, and the check is evaded by a line break. A refusal that
is both wrong sometimes and bypassable always is worse than a documented
requirement, so this is a documented requirement.

## 6. The guard, and why it is internal

`vilan` has no `try`/`catch` (`fs.vl` states the same constraint at its
own boundary). Naming the failing step therefore requires catching the
host throw, which is host-side glue: two `__db_*` helpers,
`__db_exec_guarded` and `__db_run_guarded`, each returning
`Option<str>` — the host's message on failure, `None` on success — in
the same Option-array convention `__db_get` and `__fs_stat` already use
at this boundary.

They are **not public surface**. Whether `std::db` should offer a
`Result`-returning `try_exec` is a real question about the module's
error posture — everything else in it throws — and it deserves to be
answered on its own, with its own error type, not smuggled in as a
side effect of the migration surface. Two private helpers is the small
answer; a public one is a different paper.

## 7. Where the steps come from

The surface takes `List<Migration>`. It does not read the filesystem, and
it does not know what a `migrations/` directory is. That is deliberate:
the migrator's job is to apply an ordered list correctly, and how the
list was built is the const channel's business.

Today, an explicit list of `asset::read` calls spells it:

```vilan
db.migrate([
    Migration { name = "001-create-task", sql = asset::read("migrations/001-create-task.sql") },
    Migration { name = "002-task-description", sql = asset::read("migrations/002-task-description.sql") },
]);
```

`asset::read` is const-evaluated, so each `.sql` file's *text* is
compiled into the bundle. The deployed app is still `dist/` and nothing
else, every migration edit is a tracked build input, and there is no
runtime path that can be wrong on the deployment machine.

Once the `read_dir` recipe lands, the same thing is written once and
stays correct as files are added — a const `read_dir` over `migrations/`,
sorted, each entry `read` and turned into a `Migration` named after its
file. That is the **intended idiom**, and the docs say so. It is not a
dependency: this surface builds and ships with an explicit list, and
gains the loop for free when the sibling ships.

The naming convention the docs recommend is `NNN-slug.sql`
(`001-create-task.sql`), because a name-sorted directory listing is then
the migration order. The surface does not require it (§8 D6) — it is the
convention that makes the `read_dir` idiom's sort mean the right thing.

## 8. Determinations

| # | Question | Determination |
|---|---|---|
| D1 | `Migrator` type or a `Database` method? | **`Database.migrate(migrations)`.** std::db is three types and their methods; a `Migrator` adds a fourth with no state, and holding a `resource` would either move the caller's database or make it loan-carrying (§3). |
| D2 | The step type | **`struct Migration { name: str, sql: str }`** — plain data, constructed at the call site, no const requirement on the fields. |
| D3 | The applied table | **`vilan_migrations (name TEXT PRIMARY KEY NOT NULL, applied_at_ms INTEGER NOT NULL)`.** Prefixed because it is the language's table, not the app's. No ordinal column, no SQL checksum (§4). |
| D4 | Duplicate names | **Refused**, before the database is touched. Two steps with one name map to one record, which makes §5.3's invariant unstatable. |
| D5 | Empty names | **Refused.** The name is the record's key and the subject of every refusal message; an empty one is neither. |
| D6 | Must names be strictly ascending? | **No.** List order is the sole authority. Drift (b) already catches every misordering the rule would catch on a database with history, and on a fresh database any order is self-consistent (§5.2). The `NNN-slug` convention is a docs recommendation, not a refusal. |
| D7 | Transaction granularity | **Per step**, with the record INSERT inside it. Per-run was considered and rejected: it re-runs a non-re-runnable prefix after a late failure (§5.3). |
| D8 | Does the applied set or the source list define order? | **The source list.** The table stores a *set* of names; every ordering question is answered against the list the caller passed (§4, §5.2). |
| D9 | A failing step | **`panic`**, naming the step and quoting the host's message, after a guarded rollback whose own failure is ignored (§5.4). |
| D10 | Steps containing `BEGIN`/`COMMIT` | **Documented as forbidden, not checked.** Substring-scanning SQL is not parsing SQL: false refusals on comments, string literals and `commit_sha`; evaded by a line break (§5.5). |
| D11 | The guard's visibility | **Internal.** `__db_exec_guarded` / `__db_run_guarded`, `Option<str>`. A public `try_exec` is a separate question about std::db's error posture (§6). |
| D12 | Return value | **`List<str>`** — the names applied, in order. Empty on a no-op re-run, which makes idempotence observable rather than merely asserted (§3). |
| D13 | Check-then-apply, or interleaved? | **Both refusals run over the whole list before anything is applied**, so a drifted database is never modified (§5). |
| D14 | The migrator's own table creation | **`CREATE TABLE IF NOT EXISTS`** — the idiom this paper replaces, legitimate for this one table because the migrator owns its shape (§4). |

## 9. Deliberately absent from v1

- **Down-migrations.** The alpha posture is roll forward. A `down` half
  doubles the surface, doubles what every step's author must write, and
  is — in practice, in every framework that has one — either untested or
  unrunnable by the time it is wanted. The recovery story for a bad
  migration is a *new* migration that undoes it, which is the story
  production actually uses.
- **Locking beyond the host's own.** SQLite's file lock is the lock: two
  processes racing to migrate the same file serialize on it, and the
  loser finds the steps recorded and applies nothing. A client/server
  engine would need an advisory lock; that is a question for the binding
  that introduces one, not for this one.
- **Diff generation** — "automatic" in the strong sense: compare a
  declared schema against the live one and mint the step. This is real
  and separable, and it wants the declared-schema design question
  answered first (what *is* the declaration, and where does it live?).
  Nothing here forecloses it: a generator's output is a `Migration`, and
  this is the thing that applies one.
- **SQL checksums** (§4). A strictly additive column and a strictly
  additive third refusal, wanting an "yes, I meant that" escape hatch
  designed alongside it.
- **A step that cannot run inside a transaction** (§5.5). `VACUUM` and
  `PRAGMA journal_mode` are out of a step's reach. If a real call site
  needs one, the answer is a step *kind* that opts out of the
  transaction and accepts the weaker invariant — stated as a shape, not
  built on speculation.

## 10. Pins

Every pin runs a real `vilan` program against a real SQLite file in a
per-test temp directory, through the CLI, the way
`crates/vilan-cli/tests/database.rs` already drives `Database`.

1. **Fresh apply-all** — an empty database, two steps: both applied, both
   recorded, the return list is both names in order.
2. **Re-run is a no-op** — `migrate` called twice with the same list: the
   second returns empty and the table is unchanged.
3. **The tail only** — a third step appended: only it is applied, and the
   return list is that one name.
4. **A failing step stops loudly and records nothing** — step 2 of 3 has
   bad SQL: the process fails, the message names `002`, step 1 is applied
   and recorded, steps 2 and 3 are not, and step 2's partial DDL is
   absent (the rollback worked).
5. **Drift (a)** — a database recording a name the list does not contain:
   refused, naming it, with the schema untouched.
6. **Drift (b)** — a step inserted before an applied one: refused, naming
   both, with the schema untouched.
7. **The applied table's exact rows** — after a run, `name` values in
   order and `applied_at_ms` non-zero.

### 10.1 The host probe

Recorded because §5.3's design rests on it (`node:sqlite`, node v24.2.0):

| Probe | Result |
|---|---|
| `BEGIN; CREATE TABLE a (x TEXT); ROLLBACK;` | no table — **DDL is transactional** |
| duplicate `CREATE TABLE` inside a transaction | throws `table b already exists`; the transaction stays open; the explicit `ROLLBACK` succeeds |
| multi-statement `exec` whose 2nd statement fails | the 1st statement's effect is undone by the explicit `ROLLBACK` |
| `ROLLBACK` with no transaction | throws `cannot rollback - no transaction is active` — must be guarded and ignored |
| a step containing its own `COMMIT` | succeeds; the migrator's `COMMIT` then throws `cannot commit - no transaction is active` (§5.5) |
| `exec("")` | succeeds |
| the error's message | `error.message` |

## 11. Ship record

BUILT 2026-08-29 in the same work order, on `origin/next` at `ce281993`
(v0.39.0). The surface is `Migration` + `Database.migrate` in
`vilan/std/src/process/db.vl`, the guard is two helpers in
`crates/vilan-core/src/transformer.rs`, the pins are in
`crates/vilan-cli/tests/database.rs`, and the docs are
`vilan/docs/guide/persistence.md` (the task-oriented recipe, including
§7's const channel) and `vilan/docs/std/process.md` (the reference
surface). The two new headings moved `markdown_anchors.golden`, which was
regenerated deliberately and carries exactly those two lines.

Nothing in §§3–9 changed under construction. Three notes worth keeping:

- **The rollback's failure genuinely must be ignored**, not merely
  "should be": pin 4 exercises a failing `CREATE TABLE` after a
  successful one in the same step, where the transaction is still open
  and the rollback succeeds — but the guarded form is what keeps the
  aborted-transaction classes (§5.4) from replacing the real message.
- **`applied_at_ms` is sampled per step**, inside the transaction's
  scope but before `COMMIT`, so a long-running step records when it
  started applying rather than when it finished. Either is defensible;
  this one is what a step that never finishes would have recorded, which
  is the more useful of the two for reading a stalled boot's table.
- **The drift refusals had to be plant-proved with an always-false
  condition, not an early `return`.** The obvious plant — returning from
  the refusal before its loop — does not compile in that position, and a
  plant that fails to BUILD takes the whole test binary red, which proves
  nothing about the pin. Both were redone as `&& false` on the refusal's
  own condition, which leaves the module compiling and takes exactly the
  one pin down. Worth writing down: a non-vacuity plant has to be a
  BEHAVIOURAL change, or the red it produces is the compiler's, not the
  pin's.
