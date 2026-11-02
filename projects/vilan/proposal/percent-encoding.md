# `std::url`: percent-encoding on both backends (M181)

- status: BUILT 2026-11-02 (lane std-56 a5df8059; merged to next 79a620f9; rides v0.54.0; M181 closed; Q1 built as recommended)
- item: M181 — `percent_decode` is browser-only (in `std::web::router`), and
  there is no encoder

## 1. The fault

`std::web::router::percent_decode` is the total decoder (a malformed escape
decodes to itself), but `router.vl` is `[platform("browser")]`, so code that
also runs on node (kolt's `code_links.vl`, tested under `vilan test`; its
server's upload filenames) cannot call it. There is no encoder at all. Kolt
keeps two externs (`decode_uri_component`, `encode_uri_component`) every app
writing URLs will repeat.

## 2. The surface

A new platform-neutral module, `std::url`:

```
/// `encodeURIComponent`'s set: every byte of the UTF-8 encoding is escaped as
/// `%XX` except the unreserved `A-Z a-z 0-9 - _ . ! ~ * ' ( )`.
export fun percent_encode(text: str): str

/// The TOTAL decoder: `%XX` pairs decode to their bytes and the result is read
/// as UTF-8; a malformed escape (`%G1`, a lone `%`) and an escape sequence that
/// is not valid UTF-8 decode to themselves, byte for byte, never fail.
export fun percent_decode(text: str): str
```

`std::web::router` re-exports `percent_decode` from `std::url` (its existing
callers keep working, the browser-only extern goes).

## 3. One implementation on both backends

On JS, `percent_encode` is `encodeURIComponent`; `percent_decode` is the router's
present extern (try `decodeURIComponent` on each `%`-run, fall back to the run
itself) moved to `url.vl`. Natively both are hand-written in `vilan-rt` (the
crate is dependency-free, Order 37 R8): the encoder over the UTF-8 bytes; the
decoder a byte loop that decodes maximal `%XX` runs and validates each run as
UTF-8, keeping the written text where it is not. The native differential
proves the two answer the same bytes on the same inputs (ASCII, spaces, the
reserved set, multi-byte UTF-8, a lone `%`, `%G1`, `%FF` alone, a `%`-run whose
bytes are not UTF-8, an empty string).

## 4. Pins

- `std_surface::m181_*` on node: the encoder's set exactly (every unreserved
  character kept, space → `%20`, `/` → `%2F`, `é` → `%C3%A9`), the decoder's
  totality (each malformed shape decodes to itself), round trips.
- The native differential `native/url.vl`: the table above, byte-identical.
- The router's re-export: a browser program calling
  `std::web::router::percent_decode` compiles as before (an existing router pin
  covers it; if none, add one).

## 5. Docs

`docs/std/strings.md` or a new `docs/std/url.md` (the lane picks the page the
std table already groups string encoders on — `encoding.md` holds base64);
SUMMARY/README's std table; CHANGELOG feature entry (M181), one bold head.

## 6. Owner questions

- Q1: a module `std::url` (rec) vs `str` methods (`text.percent_encode()`).
  Rec: the module; `str` methods on a shown need.

## 7. As built (lane std-56, 2026-11-02)

As §2–§3, two deviations: (1) the JS decoder decodes per maximal `%XX` RUN (as §3 says and as native must), not the router's old whole-text fallback — `"%zz%20"` now decodes to `"%zz "` where it used to stay as written; a run that is not valid UTF-8 as a whole (`%41%FF`) stays as written, matching `decodeURIComponent` on that run; (2) the JS encoder is a `__percent_encode` helper rather than bare `encodeURIComponent`, because a lone surrogate is reachable on JS (`"😀".substring(0, 1)`) and the host function throws on it — the helper retries with U+FFFD (pinned). The router's extern became a one-line re-export (the split golden's `router.vl:<line>` labels moved up 6). Docs landed on std/encoding.md (beside base64) and browser.md. Pins: `std_surface::m181_*` ×6, the native differential (26 inputs, byte-identical), vilan-rt url units ×4. Find filed from the probe: B695 (a substring splitting a surrogate pair diverges between backends).

