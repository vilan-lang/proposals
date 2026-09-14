# One row per DECLARATION SITE of a `Shared<..>` cell in std (field decl,
# module-level `let`, local `let`). Construction slots (`x = Shared::new(..)`)
# re-state a field decl and are not counted. Classes:
#   R root-scoped, O owner-scoped (a boundary: view/row/turn/request/connection),
#   E escaping (minted under one owner, read by another), F frame-scoped
#   (never outlives the call or builder that made it; no subscriber).
rows = [
 # file, owning entity, n, class
 ("reactive.vl","module next_subscriber_id",1,"R"),
 ("reactive.vl","module draining_turns",1,"R"),
 ("reactive.vl","module releasing_turns",1,"R"),
 ("reactive.vl","Turn (pending/queued/draining/settled/scheduled)",5,"O"),
 ("reactive.vl","Subscription (subscribers, release)",2,"O"),
 ("reactive.vl","Owner (cleanups, disposed)",2,"O"),
 ("reactive.vl","SignalCell (value, subscribers)",2,"E"),
 ("reactive.vl","Selector fields (cells, current)",2,"O"),
 ("reactive.vl","selector() locals (cells, current)",2,"O"),
 ("reactive.vl","flatten x2 inner_subscription",2,"O"),
 ("reactive.vl","Draft (synced/generation/debounce/pending)",4,"E"),
 ("reactive.vl","Optimistic (confirmed/generation/confirmed_gen)",3,"E"),
 ("memo.vl","Memo.entries",1,"E"),
 ("browser/ui.vl","Region (live, rows)",2,"O"),
 ("browser/ui.vl","Swap.armed x2",2,"O"),
 ("browser/ui.vl","when/show locals (live x2)",2,"O"),
 ("browser/ui.vl","swap locals (armed, generation)",2,"O"),
 ("browser/ui.vl","bind_when locals (live_row, live_owner)",2,"O"),
 ("browser/ui.vl","bind_some locals (last_value, live_row, live_owner)",3,"O"),
 ("browser/ui.vl","bind_each locals (keys/items/rows/owners)",4,"O"),
 ("browser/ui.vl","bind_each_cell locals (keys/items/cells/rows/owners)",5,"O"),
 ("process/ui.vl","View (attributes, children, text) + builder local",4,"O"),
 ("browser/router.vl","module wired",1,"R"),
 ("ws.vl","frame decoder state (buffer/opcode/payload/violated)",4,"O"),
 ("time.vl","Debouncer (pending, running, timer)",3,"O"),
 ("binary.vl","BinaryWriter (buffer, used)",2,"F"),
 ("binary.vl","BinaryReader (cursor, error)",2,"F"),
 ("json.vl","JsonWriter (out/comma/saved/arities)",4,"F"),
 ("json.vl","JsonReader (stack, error) + builder local",3,"F"),
 ("process/fs.vl","Reader.cursor",1,"F"),
 ("process/rpc_server.vl","module connections",1,"R"),
 ("process/rpc_server.vl","module next_connection",1,"R"),
 ("process/rpc_server.vl","server stats (live, handshakes)",2,"O"),
 ("process/rpc_server.vl","handshake locals (settled/expired/closed/greeted)",4,"F"),
 ("rpc.vl","module reactive_sessions",1,"R"),
 ("rpc.vl","module client_channels",1,"R"),
 ("rpc.vl","module next_channel",1,"R"),
 ("rpc.vl","Duplex (peer, me)",2,"O"),
 ("rpc.vl","DuplexEnd (inbound, early)",2,"O"),
 ("rpc.vl","duplex_pair/connect locals",5,"O"),
 ("rpc.vl","ReactiveClient (socket..on_terminal)",10,"O"),
 ("rpc.vl","ReactiveClient wiring locals",5,"O"),
 ("rpc.vl","serve-side handler/early cells",4,"O"),
 ("rpc.vl","Dispatcher (routes, handle_methods)",2,"O"),
 ("rpc.vl","ReactiveServer (sources, live)",2,"O"),
 ("rpc.vl","ClientChannel (routes, dynamic, replays)",3,"O"),
 ("rpc.vl","KeyedLog (positions/log/version/base/cursors)",5,"O"),
 ("rpc.vl","KeyedCursor.at + minted local",2,"O"),
 ("rpc.vl","mirror adapter locals (seeded/previous/held/...)",5,"O"),
 ("rpc.vl","connect handshake locals (connection, refused)",2,"F"),
 ("rpc.vl","subscribe fault local",1,"F"),
 ("rpc.vl","LiveForward.holds",1,"E"),
 ("rpc.vl","RemoteSource (channel/subscribe/count/closing/released/leased)",6,"E"),
 ("rpc.vl","KeyedRemoteSource (channel/count/closing/leases/positions/released/leased)",7,"E"),
 ("rpc.vl","KeyLease (count/closing/on_wire)",3,"E"),
 ("rpc.vl","channel_cell locals x2",2,"E"),
]
kolt = [
 ("store.vl","module next_channel_id / next_message_id",2,"R"),
 ("store.vl","KoltStore.next_channel_id / next_message_id (alias the module cells)",2,"R"),
 ("lib/input_system.vl","InputSystem (layers, next_id)",2,"R"),
 ("lib/overlay.vl","Overlay.driver",1,"E"),
 ("lib/overlay.vl","OverlayDriver (layers, next_id)",2,"R"),
 ("lib/overlay.vl","attach local live_panel",1,"O"),
 ("lib/overlay.vl","relayout local focused",1,"O"),
 ("lib/rotary.vl","Rotary (next_key, nodes)",2,"O"),
]
from collections import defaultdict
byclass=defaultdict(int); byfile=defaultdict(lambda: defaultdict(int)); total=0
for f,e,n,c in rows:
    byclass[c]+=n; byfile[f][c]+=n; total+=n
print("TOTAL declaration sites:", total)
for c in "ROEF":
    print(f"  {c}: {byclass[c]}  ({100*byclass[c]/total:.1f}%)")
print()
print(f"{'file':26} {'R':>3} {'O':>3} {'E':>3} {'F':>3} {'tot':>4}")
for f in sorted(byfile):
    d=byfile[f]; t=sum(d.values())
    print(f"{f:26} {d['R']:>3} {d['O']:>3} {d['E']:>3} {d['F']:>3} {t:>4}")

print()
print("=== kolt ===")
kc=defaultdict(int); kf=defaultdict(lambda: defaultdict(int)); kt=0
for f,e,n,c in kolt:
    kc[c]+=n; kf[f][c]+=n; kt+=n
print("TOTAL declaration sites:", kt)
for c in "ROEF":
    print(f"  {c}: {kc[c]}")
for f in sorted(kf):
    d=kf[f]; print(f"{f:26} R={d['R']} O={d['O']} E={d['E']} F={d['F']}  tot={sum(d.values())}")
