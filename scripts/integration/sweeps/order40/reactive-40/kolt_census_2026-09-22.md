# Kolt's reactive census — the source data for `reactive-pipeline.md` §4

Read-only census of `/home/reed/code/kolt/src` at kolt `9a057c6`, 2026-09-22,
excluding the generated `src/lucide`. Nothing in kolt was modified.

**Counting rule for a "reactive map":** a `.map(` whose receiver is a signal, a
cell, a source, or the result of one. `Option::map`, `Result::map`, `List::map`,
`Iterator::map`, `map_or*` and occurrences inside comments are excluded.

## Derivations, classified

55 reactive maps in live code (a 56th is in the `lib/reactive2.vl` sketch).

| class | count | share |
|---|---:|---:|
| single-consumer (one reader) | 38 | 69 % |
| shared (two or more readers) | 8 | 15 % |
| stored (into a field or a module-level container) | 8 | 15 % |
| unclear (`model.vl:134`, `map_safe` — per-call-site fate) | 1 | 2 % |

| file | maps | single | shared | stored | unclear |
|---|---:|---:|---:|---:|---:|
| `views.vl` | 23 | 15 | 4 | 4 | 0 |
| `channel.vl` | 11 | 10 | 1 | 0 | 0 |
| `model.vl` | 6 | 2 | 2 | 1 | 1 |
| `theme.vl` | 5 | 4 | 1 | 0 | 0 |
| `store.vl` | 3 | 3 | 0 | 0 | 0 |
| `lib/overlay.vl` | 2 | 2 | 0 | 0 | 0 |
| `lib/search.vl` | 2 | 0 | 0 | 2 | 0 |
| `client.vl` | 1 | 0 | 0 | 1 | 0 |
| `comp/login.vl` | 1 | 1 | 0 | 0 | 0 |
| `lib/storage.vl` | 1 | 1 | 0 | 0 | 0 |

**The eight SHARED sites** (each needs an explicit `.cell()` under the
redesign): `views.vl:263` (read at `:286` and `:287`), `views.vl:441` (`:448`,
`:471`), `views.vl:702` (six readers: `:704`, `:707`, `:738`, `:749`, `:769`,
`:791`), `views.vl:705` (`:714`, `:770`), `channel.vl:21` (the `message` half of
`divorce`, read at `:46` and `:54`), `model.vl:85` (`views.vl:264`, `:296`),
`model.vl:111` (`views.vl:255`, `:257`), `theme.vl:125` (eight readers).

**The eight STORED sites:** `views.vl:581`, `:597`, `:629`, `:647` (all into
`Command.name`), `model.vl:121` (into the `message_handles` memo),
`client.vl:65` (into `AppContext.route`), `lib/search.vl:14` and `:23` (into
`Searchable.table`).

## Signal-typed struct fields — 19 across 10 structs (A124's count HOLDS)

| struct.field | file:line | stores |
|---|---|---|
| `Searchable.list` | `lib/search.vl:6` | root |
| `Searchable.table` | `lib/search.vl:7` | **derived, always** |
| `Account.fullname/.username/.nickname/.channels` | `account.vl:4–7` | root (×4) |
| `AppContext.route` | `app_context.vl:16` | **derived, always** |
| `AppContext.sidebar_tab/.drag_status` | `app_context.vl:17–18` | root (×2) |
| `ChannelRecord.name/.messages` | `store.vl:93–94` | root (×2) |
| `GlobalStore.channels/.messages` | `store.vl:102`, `:104` | root (×2) |
| `Command.name` | `views.vl:548` | **MIXED** — derived at `:581`, `:597`, `:629`, `:647`; root at `:613`, `:621`, `:663`, `:672`, `:681`; both kinds in ONE list literal |
| `Overlay.open/.point` | `lib/overlay.vl:187–188` | root (×2) |
| `OverlayDriver.scrims` | `lib/overlay.vl:418` | root |
| `StorageSignalCell.signal` | `lib/storage.vl:65` | root |
| `InputLayer.data` | `lib/input_system.vl:80` | root |

Three of the nineteen need `dyn Source<T>`: `Searchable.table`,
`AppContext.route`, `Command.name`. The other sixteen are always root cells.

Adjacent, not counted: `GlobalStore.users` (`store.vl:105`) is
`Memo<UserId, SignalCell<Option<User>>>` — a signal-typed VALUE in a table; and
`Prefs` (`prefs.vl:12–20`) holds nine `StorageSignalCell<..>` fields, a concrete
wrapper implementing `Signal<T>` — signal-behaving, not signal-typed.

## Bare-trait struct fields — ZERO

`Searchable<T>` (`lib/search.vl:5`) and `InputLayer<T>` (`lib/input_system.vl:77`)
are **struct declarations, not traits**, so A124's and `briefs40.md`'s naming of
them as kolt's bare-trait fields is a misidentification. No struct field in kolt
has a trait as its declared type. The only traits declared in kolt at all are
`Source<T>` and `Signal<T>` inside the `lib/reactive2.vl` sketch.

The closest real phenomenon is type-parameter erasure through `any`:
`StackedLayer.layer: InputLayer<any>` (`lib/input_system.vl:33`) and
`StorageKeyAllocator.keys: Set<StorageKey<any>>` (`lib/storage.vl:36`).

Bare-trait spellings do exist in kolt, all outside field position: parameters
`Signal<str>` (`comp/login.vl:72` ×2, `:174` ×2) and `Signal<Option<Channel>>`
(`channel.vl:280`, `:353`); locals in the sketch; and impl subjects
(`lib/scoped_effect.vl:4`, `lib/storage.vl:70`). R3 leaves all of them alone.

## A124's counts, checked

| claim | verdict | actual |
|---|---|---|
| 59 `.get()` reads | textual | 49 reactive (8 `Context::get`, 1 `StorageKey::get`, 1 comment) |
| 74 `.map(` | raw grep | 55 reactive |
| 15 `combine` | **wrong** | 5 — `channel.vl:40`, `theme.vl:217`, `views.vl:471`, `:704`, `:770` (the inflation is two ICON names in `src/lucide`) |
| 6 `flatten` | raw grep | 2 reactive — `channel.vl:35`, `model.vl:134` |
| 8 `effect` | **holds** | 8 |
| 19 fields / 10 structs | **holds** | 19 / 10 |
| 32 signal-typed parameters | **wrong** | 11 parameters (37 if the 26 signal-typed RETURN types are counted) |
| one memo table, `store.vl:105` | undercounts | **6** — `store.vl:105` plus `model.vl:42`, `:59`, `:60`, `:61`, `:115` |

## A123's two kolt sites (the owner's to edit; reported, not touched)

`channel.vl:35` today:

    let author = message.map(|x| x.map(|x| x.author.user())).flatten().map(|x| x.flatten());

after A123:

    let author = message.and_then(|m| m.author.user());

`model.vl:130–135` today:

    fun map_safe<T, S: Source<Option<T>>>(
        self,
        transform: |client: KoltClient<SocketTransport>| S,
    ): SignalCell<Option<T>> {
        self.map(|x| x.map(transform)).flatten().map(|x| x.flatten())
    }

`map_safe` IS `and_then` specialised to `SignalCell<Option<KoltClient<..>>>`; it
retires, and its seven call sites (`model.vl:36`, `:46`, `:76`, `:84`, `:97`,
`:111`, `:120`) become `and_then`. The impl block keeps `get_safe`. Concretely:

    model.vl:110-112   fun get_channels(): SignalCell<List<u53>> {
                           get_client().and_then(|client| client.get_channels())
                               .map(|x| x.unwrap_or_default())
                       }
    model.vl:118-122   fun find(id: u53): SignalCell<Option<Message>> {
                           message_handles.get_or(id, || get_client()
                               .and_then(|client| client.get_message(id)));
                       }

(the trailing `.map(|x| x.flatten())` disappears in both — that join is what
`and_then` absorbs.)
