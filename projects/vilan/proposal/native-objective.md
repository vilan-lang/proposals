# The native objective: a Rust web server, then a Rust desktop app

Status: RULED 2026-11-09 - the owner accepted every recommendation in §3 (S1-S7, D1-D8) as a ruling. §5 (Kolt) is HELD: the git tracker stays the only planning surface; the project switches when Kolt is ready for the whole project (§5's gap list is the checklist). Reads with
`native-apps.md` (F1), F15, F17, F27. This paper is the plan and the question
list; it builds nothing.

## 1. Where we are (measured 2026-11-09, vilan 0.55.0)

- The Rust backend (`--backend rust`) builds the language, `std::http`,
  `std::rpc::server` (WebSocket upgrade, mirrors), `std::db`, json, crypto, fs,
  the executor, graceful stop. Native differential: 330/330 identical or
  refused by name.
- kolt's server does NOT build natively: it stops at the first of kolt's own
  JS host bindings (`now_seconds`, `src/tracker_import.vl:238`). kolt carries
  138 `[extern]` snippets; most are browser-side, a handful are reached by the
  server (store, accounts, files, mcp, dictionary). The build stops at the
  first refusal, so the full list needs a census (chunk 0).
- The native HTTP server has no keep-alive, no TLS, no HTTP/2, no head or body
  timeout (F152); a native rpc CLIENT (ws:// dial) is planned, unbuilt (F1 S1b
  note, Order 56).
- Nothing of the native UI exists: F1 S2-S5 unstarted, all behind F17.

## 2. Milestones

**M1 - kolt's server as a Rust binary, in production shape.** Done means:
kolt's server builds with `--backend rust` from kolt's own tree; kolt's e2e
suite passes against the native binary; it runs behind a reverse proxy with
keep-alive and timeouts; RSS and request cost are measured against node and
recorded.

**M2 - a Rust desktop app by the short road: a webview shell.** One Rust
binary: the native server in-process plus the OS webview showing the browser
client that already exists. It replaces Electron for kolt's desktop build. No
new UI layer, no renderer. Done means: kolt desktop starts from one binary on
Linux, macOS and Windows with deep links, menu, notifications and secure
token storage at parity with today's Electron shell.

**M3 - GPU-rendered native UI (F1 S2-S5).** The third `std::ui` twin over a
retained scene tree. Done means, first: `examples/todo` and `board.vl` in a
native window from the same source as the web build. kolt's client is NOT
M3's first exhibit: its editor leans on contenteditable, the DOM Range and
clipboard APIs (about 130 browser bindings).

M1 needs no design ruling except TLS. M2 needs one dependency ruling. M3 needs
F17.

## 3. Rulings (each recommendation below is RULED as written, 2026-11-09)

### Server (M1)

- **S1. TLS.** Rec: none in v1. The native server is deployed behind a proxy
  (caddy/nginx), as node servers usually are; `wss://` on the native CLIENT
  waits with it. Revisit with a `rustls` dependency ruling when a deployment
  needs it.
- **S2. kolt's host bindings.** Rec: two doors, by kind. A binding that is
  general (the clock in seconds, base64, a uuid) moves into std with both
  arms. A binding that is the app's own gains a second arm on the attribute:
  `[extern(js = "..", rust = "..")]`, refused natively by name when the rust
  arm is absent (today's behavior). The census decides which is which.
- **S3. Keep-alive and timeouts.** Rec: build both (HTTP/1.1 keep-alive; head
  60 s and body 300 s defaults, as node, configurable on the builder). HTTP/2
  stays out.
- **S4. Status reason phrases (F151).** Rec: node's phrases on both backends,
  so the wire differential stays byte-for-byte.
- **S5. NULL column reads (F149).** Rec: the typed readers refuse a NULL on
  both backends (a panic naming the column); `Option` readers are the door.
  BREAKING where an app read NULL as 0 or "" - census kolt first.
- **S6. What `any` holds natively (A176/F150/M195).** Rec: M175's `SqlValue`
  (paper ready, Order 56 Q8) retires `List<any>` at the db boundary, which is
  where kolt meets it; `Any` gains the BLOB arm.
- **S7. The dev loop.** Rec: JS stays the dev backend (`--watch`, hot swap);
  native is the release build. CI builds both and runs the e2e on both.

### Desktop (M2, M3)

- **D1. Which desktop first?** Rec: M2 (webview shell) before M3. It gives a
  real Rust desktop app within about two orders of M1 and removes Electron;
  M3 is several orders and is not blocked by it.
- **D2. The webview dependency (M2).** Rec: `wry` + `tao` (the Tauri crates),
  in their own runtime crate linked only by a desktop entry - the same rule
  as sqlite and ctrlc. This is the one new-dependency ruling M2 needs.
- **D3. F17 - one UI source for native and web.** Rec: the DOM-shaped `View`
  as the shared surface (the F1 paper's position): one `std::ui`, three twins
  (browser DOM, process SSR, native scene). No second retained-tree API.
- **D4. The exception mechanism.** Rec: F27's R3 as already ruled (2026-09-21):
  platform-fenced items in one file. Window chrome and the title bar live in
  a native-only `std::window` module; shared code never names it.
- **D5. F15 - the three-layer rule.** Rec: rule it now. A `ui` member is
  declared by every twin in the same commit or the parity gate refuses; the
  gate becomes N-way; SSR differential compares resolved structure.
- **D6. The render stack (M3).** Rec: `winit` + `wgpu` + `vello` + `parley` +
  `taffy`, in a separate crate S3 introduces. Layout is flexbox and grid as
  taffy has them; the style mapping (S4) covers what A95's condition sets
  reach, and anything else is refused by name.
- **D7. M3's scope fences.** Rec: out of the first cut, by name: text EDITING
  past a single-line input, IME, accessibility trees, multiple windows. Each
  is its own later slice; saying so now keeps S3 at XL instead of unbounded.
- **D8. rpc for a desktop app.** Rec: M2 uses the real socket to the
  in-process server (nothing new). F1's S6 (rpc in-process, no socket) waits
  until M3 has an app that wants it.

## 4. Chunks, in order

| # | Chunk | Needs | Size |
|---|---|---|---|
| 0 | Census: drive kolt's server to a native build on a scratch copy; list every refusal by kind | nothing | S-M, one lane |
| 1 | HTTP hardening: keep-alive, head/body timeouts (F152), F151 | S3, S4 | M |
| 2 | Bindings: std homes + the two-arm `[extern]` | S2 + chunk 0 | M |
| 3 | Backend defects kolt meets (B699, B705, B708, F155, what the census adds) | chunk 0 | M-L |
| 4 | db boundary: M175 `SqlValue`, M195 BLOB, F149 | S5, S6 | M |
| 5 | kolt on native: its patch, e2e on both backends, measurements = M1 | 1-4 | M |
| 6 | Native ws:// client (the Order 56 plan) | nothing | M |
| 7 | Webview shell crate + `desktop` entry kind; kolt's shell ported = M2 | D1, D2, chunk 5 | L |
| 8 | F17/F15 paper section from D3-D5; then F1 S2 (`native` platform) | D3-D5 | M |
| 9 | F1 S3 render twin, S4 style, S5 input = M3 | D6, D7, chunk 8 | XL+L+M |

One chunk is one to three lanes and lands as one seal's worth of work. A chunk
closes with: merged to `next`, CI green, its items closed, this table stamped.

## 5. Managing it: Kolt, and how ready Kolt is (HELD 2026-11-09: no vilan organization now; switch when the whole project fits)

What Kolt has today (the `kolt` organization, read through its MCP on
2026-11-09): tasks with number, status (three columns), assignees, comments,
`requires` links, three fields (Area, Kind, Size) and admin-made fields;
documents; channels; search; code links to configured repositories; an MCP
that reads and writes all of it. 104 tasks live there now.

What the vilan tracker is: 174 open items and about 2,800 archive lines; ids
by section (`B713`, `E361`) that the vilan repo itself cites in changelog
entries, test names and comments; items carrying dated status logs up to
18 KB; 178 papers; tools that file, stamp and close in batches; all of it in
git beside the papers, so a ruling and its record are one commit.

Gaps, in the order they would hurt:

1. **Stable ids.** Kolt numbers tasks per organization. The lettered ids are
   load-bearing in the code. They can ride in the title today; a real answer
   is a per-organization id prefix or a unique text field shown as the key.
2. **Scale.** Kolt's own open tasks say it: search and filter on the server
   (#68), partial fetch of an organization (#69, XL), rendering only visible
   rows (#70). A few hundred open tasks plus an archive of thousands is past
   what the client loads comfortably now.
3. **Statuses.** Three columns. The tracker needs at least `Needs ruling`,
   `Ready`, `Blocked`, `In a lane`, `Landed`, `Shipped`. A choice field can
   stand in; real columns are better.
4. **History in git.** Today a ruling is diffable and travels with the paper.
   Kolt needs an export (markdown or JSON per task, on a schedule) before it
   can be the only record.
5. **Durability.** One alpha app on an alpha language holding the project's
   memory, with deployments (#19) and a server CLI (#96) still open. Backups
   first.
6. **Bulk operations over MCP.** A sweep closes 30 items and files 30; the
   MCP is one call per task. Workable, slow; a batch tool is small.
7. **Repositories.** Only `kolt` is configured for code links; `vilan`,
   `proposals` and `website` need adding.

Verdict: ready to run THIS OBJECTIVE now; not ready to be the whole project's
only record. Rec, in three steps:

- **Now:** a `vilan` organization in Kolt holding this objective only: one
  task per chunk and per question above, `requires` links for the order, the
  tracker id in each title, fields `Milestone` (M1/M2/M3) and `Needs`
  (Ruling/Lane/Owner). The git tracker stays the record; the integrator
  writes both at each sweep. Every friction met is filed as a Kolt task.
- **When #68, #70, an export and an id prefix exist:** import the open items
  (a script over `tracker/items/`), freeze INDEX.md as generated output.
- **When the archive imports and backups are routine:** the git tracker is
  retired to an export.

This also makes the objective its own dogfood: the app tracking the work is
the app M1 and M2 ship natively.
