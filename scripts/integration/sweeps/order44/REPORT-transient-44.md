# transient-44 — FINAL report (2026-09-30; saved by the integrator — the lane's tool environment refused the report file). Branch rebased onto 280f7231 (twice: d3560fad, then 280f7231; never cherry-picked); last commit 68b71a21. Model Opus.

Phases: 1 (A141, A139, A140, A133), 1b (A143), 2 (A142 S3 + A145). The full-suite run editor-44's pkill invalidated was on the old base; the orphan (pid 1043004) killed and every gate re-run on the rebased tip.

| item | state | sha | pins |
|---|---|---|---|
| A141 (R-f) | LANDED | e1c26d99 (+ folds 9062fcc9, 024e890c) | socket + in-process reactive_channels; `inference::lifetimes::a141_*` ×2 |
| A139 | LANDED | 3ee24174 | in process + socket |
| A140 | LANDED | 04455309 | in process + socket |
| A133 (R-g door c) | LANDED as documentation; closes | 76643aa5 | the contract pin |
| A143 (door b) | LANDED | 450bb4a3 | mixed in process, mixed over a socket, the whole-lease hand-back |
| A142 S3 | LANDED | 8563a0ed (+ golden 68b71a21) | latest-task-wins (in process); a mirror as a transient, Absent vs Pending (socket) |
| A145 | LANDED | 30042dd7 | MemoCell handle return over a socket; two inference pins |

Rebase folds: 9062fcc9 moves the phase-1 pins to `.derive`, widens A141's steer to `.memo()` beside `.cell()`, re-keys A141's NEW row to `{label} stored on …`; 024e890c repairs the first fold's mis-re-key of ANOTHER lane's NEW row (the unsigned-literal row), restored from next.

## Premise checks
A141 held over a socket (connections 1 and 2 read `doubled=20` for 40 and 60). A139 held both transports. A140 held (correction: only `invalidate_dynamic`'s mirrors go to -1; a retired minted mirror keeps its withdrawn id, its route inert). A133 re-verified (`sees 7` twice over `duplex_pair`; an A92 stub mirror mints asynchronously and sees it once). A143 held over a socket; the fix also closes a pre-existing bug (a single minted mirror holding the whole collection AND a key revoked its own channel on releasing the whole lease — the Unsubscribe went first). A145 held (`MemoCell` returns refused 'not Wire'; stubs typed as the raw return). S3's ground held with two live bugs shaping the design: a superseded task is cancelled with its run; `dyn Pipe<T>` is consumable; `guarded_async(|| await task)` absorbs a cancelled task's abort (J7's stderr noise does not reach `.transient()`); **B475 live** (`.derive` over a `dyn Source` throws) → Q1; **B477 live** (declaration order between overlapping blankets) → Q3.

## What was built
- A141: `RpcProtocol::under_owner`, `RpcRequest.owner`; `Service::new` stamps a service-lifetime owner, `factory` unstamped; `under_connection` prefers the stamped owner, then the session's, then fresh. Door (a)'s warning (ledger NEW) fires on a `.cell()`/`.memo()` stored through `Shared::write` (assignment or a method on the view) or built in a `Shared<Option<T>>::get_or_insert` maker, inside an `[rpc]` handler found through the generated routes; row 576's key names whose owner holds the cell; A135's socket pin moved to `Service::factory`.
- A139: `MirrorRoute.key_snapshot`, `KeyedSource.join_key` after every per-key Subscribe, `seed_key_from_sibling`.
- A140: replays keyed by channel-cell identity (`List<(i32, || void)>`); route + replay pruned on the retire hook; a `revive` hook run first by `rebind`; `dispose` clears replays.
- A133: `duplex_pair`'s doc + the services guide state the inline-seed contract.
- A143: `WireDemand` (`ReactiveClient.wire`, a copy on every mirror) — one forward per channel at the union of demands, whole subsumes per-key, subscribes before unsubscribes; a covered demand sends nothing and seeds from a sibling (whole holders offer per-key snapshots); `KeyedSource::accept` fans out by demand; dropping the whole lease trims to held keys; `reset_wire()` first in the generated reconnect hook, also on `invalidate_dynamic`/`dispose`; `rebind` forgets its own demand; `release_unleased` guarded. No wire change.
- A142 S3 (new `std::transient`): `TransientState<T, E>` (five states + `ready`, `latest`, `is_pending`, `refreshed`, `failed`); `TransientSource<T, E> with Source<Option<T>>` — `state()` returns `MemoCell` (Q1), `latest()`/`is_pending()` a fresh `dyn Pipe` per call; `Transient<T, E>` the sealed type; `.transient()` on `Pipe<Task<Result<T, E>>>` and `Pipe<Task<T>>` — latest task wins via a generation claim (superseded task cancelled with its run, a late reply dropped); releasing the seal drops what is in flight; R36 (`Err(e)` → `Failed(e, stale)`; a bare task's panic → `Failed(message, stale)`, `E = str`); `TaskSource<T, E>` (`::new` a Result task, `::of` a bare one); `RemoteSource<T>` implements `TransientSource<T, RpcError>` via `transient_state()` (`state()` reports without leasing; `latest()`/`is_pending()` are `combine((mirror, mint))` pipes that lease while bound). Docs: new `docs/std/transient.md` + notes in std/rpc.md, std/reactive.md, the services guide.
- A145: `handle_element` admits `MemoCell`; `handle_is_memo` picks `reply_source_memo`/`reply_source_memo_option`; the analyzer's two handle descents and `macros.rs`'s `handle_spelling` accept the spelling (a non-Wire element refused at the element, row 411); A135's tail steer finds memo-returning handle methods; the guide's handle table gains two rows.

## Questions (OWNER)
1. `state()` returns `MemoCell<TransientState<T, E>>`, not the paper's `dyn Source` (B475 live: `x.state().derive(..)` over a `dyn Source` would crash) — (a) keep, fix the paper's §5; (b) widen after B475. Rec (a).
2. A mirror's own `get()` unchanged (reads its cache incl. the stale value after a failed re-mint) — conflicts with R5 only while Failed/Absent with a held value; a strict `get()` needs the observe path to wake on mint changes (moves notification-count pins). (a) strict `get()` as its own item; (b) keep + document (done). Rec (b) now, (a) in Order 45 if a program meets it.
3. R36's two `.transient()` arms depend on B477's declaration order (the `Result` arm first; both pinned) — B477's fix needs a specificity rule, not a refusal.
4. A panicking `Task<Result<T, E>>` has no `E` to become — re-raised as an unobserved failure; the transient stays. Rec keep.
5. Names unruled: `TaskSource::new`/`TaskSource::of`; the seal type `Transient<T, E>`.
6. `.transient()` is owner-tied like `.cell()`, with no `_global` twin; A130's module-binding refusal (row 575) names only `cell`/`memo`, so a module-level `.transient()` lives for the program. Rec: add to A130's refusal in Order 45 if wanted.

## Unfixed finds
A135's tail warning (row 576) hard-codes "builds with `.cell()`" even for `.memo()` (cosmetic). A keyed `rebind` always `cache.set(None)`s (one extra `-` per-key at mint; pre-existing; A143's pin records it). `KeyedSource` is not a `TransientSource` (not asked).

## Ledger: one NEW row (A141's warning, `{label} stored on …`), row 576 re-keyed — prose owed. ## Goldens/censuses: none of corpus/split/examples moved; anchor golden +7 (`std/transient.md`); shared_census 154 → 159 (rpc.vl +4, transient.vl +1).
## Gates (30042dd7 + 68b71a21): fmt/`vilan fmt`/clippy clean; nextest workspace 9051 run / 9050 passed / 1 failed (`markdown_golden`, fixed by 68b71a21, re-run 2/2) / 40 skipped, incl. native default, corpus, split, examples, censuses, scope, reactive_channels, service_layer, transport_robustness, ledger, docs; `VILAN_NATIVE_DIFFERENTIAL=1` 86/86; doc-tests green.
## Kolt: A141 changes nothing (factory service; `get_user` caches a root); A145 lets store.vl 196/205/257 return a stored `MemoCell` (`.memo_global()` keyed by args); S3 covers kolt's hand-rolled `shared.vl` `Transient<T>` + `RemoteSource::remote()` (`state()`: Loading→Pending, Gone→Absent; `latest()` the refreshing view) — migrating is the owner's choice; A139/A140/A143 need nothing in kolt.
