# A124 S2c in kolt: the edits for the owner (reactive-42, Order 42; R4, kolt migrates at the owner's word)

Base: kolt 9a057c6 (`wip`) plus the owner's uncommitted files as of 2026-09-25. Checked on a
scratch copy with the flipped compiler (reactive-42 rebased on next @eafd61ef). Before the
edits: 18 errors, 14 from the flip and the 4 A125 errors already there. After the edits: the
same 4 A125 errors (`Theme` and `Command` are not `Hashable`, plus their `EachValues` Slot
cascades at theme.vl:208/216 and command_palette.vl:240/248), and nothing else. Runtime is
UNVERIFIED because kolt's e2e was already red before this change.

Every edit adds `.cell()` where a derivation (now a cold node) meets a `SignalCell<U>` that
kolt names. The type is either a return type, a local annotation or a struct field. Where the
cell is shared or read hot, `.cell()` is also what the paper recommends (the §4.1 "shared"
sites and `Searchable.table`, §4.3). Where one reader pulls, the alternative is to drop the
`SignalCell<U>` from the signature and take a `Source<U>` bound. That is the owner's call, and
this list keeps every signature as written.

| # | site | edit |
|---|---|---|
| 1 | `src/lib/overlay.vl:447` (`has_scrim`) | `self.scrims.map(\|count\| count > 0)` → `….cell()` |
| 2 | `src/model.vl:84-85` (`Channel::name`) | after `.map(\|x\| x.unwrap_or_default())` add `.cell()` (a new line `\t\t\t.cell()`) |
| 3 | `src/model.vl:97-98` (`Channel::messages`) | the same: add `.cell()` after `.map(\|x\| x.unwrap_or_default())` |
| 4 | `src/model.vl:111` (`get_channels`) | `….map(\|x\| x.unwrap_or_default())` → `….map(\|x\| x.unwrap_or_default()).cell()` |
| 5 | `src/model.vl:121` (`Message::find`) | `.map(\|x\| x.flatten()))` → `.map(\|x\| x.flatten())` + new line `.cell())` |
| 6 | `src/model.vl:134` (`map_safe`) | `self.map(\|x\| x.map(transform)).flatten().map(\|x\| x.flatten())` → `….cell()` (or `self.and_then(\|client\| transform(client))`, A123's spelling, then `.cell()`) |
| 7 | `src/lib/storage.vl:120` (`StorageSignalCell::map`) | `self.signal.map(transform)` → `self.signal.map(transform).cell()` |
| 8 | `src/store.vl:190` (`[rpc] get_channels`) | `self.global_store.channels.map(\|x\| x.keys())` → `….cell()` |
| 9 | `src/store.vl:197` (`[rpc] get_channel`) | `….map(\|x\| x.get(channel).map(\|record\| Channel { id = record.id }))` → `….cell()` |
| 10 | `src/store.vl:249` (`[rpc] get_message`) | `self.global_store.messages.map(\|x\| x.get(message))` → `….cell()` |
| 11 | `src/channel.vl:27` (`divorce`) | `(source.map(\|(a, _)\| a), source.map(\|(_, b)\| b))` → `(source.map(\|(a, _)\| a).cell(), source.map(\|(_, b)\| b).cell())` |
| 12 | `src/client.vl:64-65` (`let route: SignalCell<Route>`) | `.map(\|path\| Route::from_segments(segments(path)));` → `.map(…)` + new line `.cell();` (inside `mount_root`'s body, so the cell goes with the root) |
| 13 | `src/lib/search.vl:14-18` (`Searchable::new`'s `table`) | `.to_list()),` → `.to_list())` + new line `.cell(),` |
| 14 | `src/lib/search.vl:22-36` (`Searchable::many`'s `table`) | `});` closing the `list.map(…)` → `}).cell();` |

Reactive-41's census counted 17 primary sites and 6 cascades. Three of those were the
`combine((..))` calls at `sidebar.vl:320`, `channel.vl:46` and `command_palette.vl:183`, and
together with their cascades they need NOTHING now. `combine` takes
`(U in T: dyn Source<U>)` since B398, so a node goes in beside a cell unchanged.

`kolt_edits.py <copy-of-kolt>` applies exactly these 14 edits, one exact-match replacement
each, and refuses any edit that does not match exactly once.

`src/lib/reactive2.vl` is the owner's sketch. It does not compile and was not touched.
`StorageSignalCell` implements `Signal<T>` in one block. Because of that, a blanket
(`.cell()`, `.switch`, `.distinct()`) is not found on it (B419). Its inherent `map` hides this
for `map`.
