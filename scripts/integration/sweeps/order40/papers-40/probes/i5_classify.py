#!/usr/bin/env python3
"""I5's index-kind classification (Order 40, lane papers-40).

Reads `i5_census`'s TSV and decides, for every std signature/field position
whose written type is an INTEGER, whether the position is INDEX-KIND.

The rule, as the paper states it:

  A position is index-kind when its value is a POSITION into a sequence, a
  LENGTH/COUNT/CAPACITY of one, or the ANSWER of a search for a position.
  It is not index-kind when the value is an identity (a channel, a connection,
  a subscriber id), an element VALUE (a byte, a character code, a colour
  channel), a protocol integer (the `Serialize`/`Deserialize` seam), a
  duration, a port, a status code, or an operand of the numeric type's own
  algebra (`number.vl`).

Everything the rule decides by NAME is listed here in the open, and every
site the name rule would get wrong is overridden by hand with a reason, so the
verdict table is auditable row by row.

Usage: i5_classify.py <census.tsv> > verdicts.tsv
"""

import sys

# Whole modules whose integer positions are the numeric algebra itself.
ALGEBRA_MODULES = {"number.vl"}

# Whole (module, function) pairs that are the Wire PROTOCOL seam: their
# integers are what the codec writes, not positions in a vilan collection.
# Keeping them `i32` is what holds the frames byte-identical (§6).
WIRE_SEAM_FUNCTIONS = {
    "begin_list", "begin_struct", "begin_variant", "end_list", "end_struct",
    "end_variant", "i32_value", "i53_value", "u32_value", "u53_value",
    "f64_value", "bool_value", "str_value", "null_value", "some_value",
    "variant_tag", "rebuild", "describe", "field", "fail", "failed",
}
WIRE_SEAM_MODULES = {"wire.vl", "binary.vl", "json.vl"}

# Position names that are index-kind wherever they appear.
INDEX_NAMES = {
    "index", "at", "from", "to", "start", "end", "offset", "position",
    "cursor", "length", "len", "count", "size", "capacity", "limit",
    "arity", "fields", "extra", "insertions", "first_line", "minimum",
}

# Position names that are never index-kind, with the reason.
NOT_INDEX_NAMES = {
    "channel": "a channel id",
    "connection": "a connection id",
    "identity": "an identity",
    "id": "an identity",
    "request": "a request id",
    "mine": "a subscriber id",
    "target": "a connection id",
    "arm": "a chunk arm id",
    "opcode": "a websocket opcode",
    "code": "a status / character code",
    "port": "a port number",
    "millis": "a duration",
    "ms": "a duration",
    "interval_ms": "a duration",
    "value": "an element value",
    "b": "the numeric algebra's operand",
    "m": "the numeric algebra's operand",
    "other": "the numeric algebra's operand",
    "exponent": "the numeric algebra's operand",
    "low": "a range bound of values",
    "high": "a range bound of values",
    "step": "a design-token step",
    "blue": "a colour channel",
    "green": "a colour channel",
    "red": "a colour channel",
    "gray": "a colour channel",
    "c": "a character code",
    "bits": "a key size in bits",
    "iterations": "a work factor",
    "unit": "a character code",
    "handler": "a closure",
    "rebinds": "a list of closures",
    "settle": "a closure",
    "pending_settle": "a closure",
    "attempts": "a rate limit in attempts",
    "level": "a heading level",
    "line": "a line number",
    "line_number": "a line number",
    "columns": "a dedent width in columns",
    "indent": "an indent width in columns",
    "fallback": "a fallback POSITION",  # overridden below
    "found": "a found POSITION",        # overridden below
}

# Returns (`<ret>`) decided by the FUNCTION's name.
INDEX_RETURNS = {
    "len", "count", "index_of", "raw_index_of", "last_index_of",
    "raw_last_index_of", "position", "splice_point", "leading_spaces",
    "list_item_content_offset", "entity_length", "skip_spaces",
    "skip_raw_text", "closing_point", "at", "held", "oldest", "past",
    "bytes_read", "bytes_written", "read_at", "write_at", "begin_list",
    "attributes_of", "locate", "demand",
}

# Per-site overrides: (module, owner-ish, function, position) -> (verdict, reason)
# Only where the name rules above are wrong.
OVERRIDES = {
    ("document.vl", "past", "fallback"): ("INDEX", "a fallback POSITION"),
    ("document.vl", "past", "found"): ("INDEX", "a found POSITION"),
    ("document.vl", "past", "offset"): ("INDEX", "a byte offset"),
    ("markdown.vl", "entity_length", "i"): ("INDEX", "a scan position"),
    ("markdown.vl", "same_char_line", "minimum"): ("INDEX", "a minimum RUN LENGTH"),
    ("markdown.vl", "heading_content", "level"): ("NOT", "a heading level"),
    ("markdown.vl", "parse_blocks", "first_line"): ("INDEX", "a line index"),
    ("bytes.vl", "fill", "value"): ("NOT", "the byte written"),
    ("bytes.vl", "set", "value"): ("NOT", "the byte written"),
    ("bytes.vl", "get", "<ret>"): ("NOT", "the byte read (I5 §2: a byte VALUE is not an index)"),
    ("bytes.vl", "alloc", "size"): ("INDEX", "a byte-length"),
    ("bytes.vl", "read_f64", "offset"): ("INDEX", "a byte offset"),
    ("bytes.vl", "write_f64", "offset"): ("INDEX", "a byte offset"),
    ("binary.vl", "expect", "count"): ("INDEX", "a byte count into the frame buffer"),
    ("binary.vl", "ensure", "extra"): ("INDEX", "a byte count of buffer capacity"),
    ("binary.vl", "read_length", "<ret>"): ("INDEX", "a wire length read back as a count"),
    ("binary.vl", "read_byte", "<ret>"): ("NOT", "the byte read"),
    ("binary.vl", "write_byte", "value"): ("NOT", "the byte written"),
    ("binary.vl", "read_i32", "<ret>"): ("NOT", "a protocol integer"),
    ("binary.vl", "write_i32", "value"): ("NOT", "a protocol integer"),
    ("db.vl", "run", "<ret>"): ("NOT", "rows affected — a database count, not a position"),
    ("db.vl", "statement_run", "<ret>"): ("NOT", "rows affected"),
    ("db.vl", "refuse_database_ahead", "count"): ("NOT", "a migration count, not a sequence position"),
    ("db.vl", "column_integer", "<ret>"): ("NOT", "a column VALUE"),
    ("db.vl", "column_big_integer", "<ret>"): ("NOT", "a column VALUE"),
    ("db.vl", "integer", "<ret>"): ("NOT", "a column VALUE"),
    ("db.vl", "big_integer", "<ret>"): ("NOT", "a column VALUE"),
    ("fs.vl", "raw_read", "position"): ("STREAM", "a FILE offset — see §2.1's open sub-question"),
    ("fs.vl", "raw_write", "position"): ("STREAM", "a FILE offset"),
    ("fs.vl", "read_at", "position"): ("STREAM", "a FILE offset"),
    ("fs.vl", "write_at", "position"): ("STREAM", "a FILE offset"),
    ("fs.vl", "seek", "position"): ("STREAM", "a FILE offset"),
    ("fs.vl", "position", "<ret>"): ("STREAM", "a FILE offset"),
    ("fs.vl", "truncate", "length"): ("STREAM", "a FILE length"),
    ("fs.vl", "size", "<ret>"): ("STREAM", "a FILE length"),
    ("fs.vl", "next", "size"): ("INDEX", "a read chunk length in memory"),
    ("fs.vl", "read_at", "<ret>"): ("INDEX", "bytes read into a buffer"),
    ("fs.vl", "write_at", "<ret>"): ("INDEX", "bytes written from a buffer"),
    ("fs.vl", "raw_read", "length"): ("INDEX", "a buffer length"),
    ("fs.vl", "raw_write", "length"): ("INDEX", "a buffer length"),
    ("fs.vl", "raw_read", "offset"): ("INDEX", "a BUFFER offset"),
    ("fs.vl", "raw_write", "offset"): ("INDEX", "a BUFFER offset"),
    ("http.vl", "set_timeout", "millis"): ("NOT", "a duration"),
    ("reactive.vl", "debounce", "millis"): ("NOT", "a duration"),
    ("reactive.vl", "cell_identity", "<ret>"): ("NOT", "an identity"),
    ("reactive.vl", "fresh_id", "<ret>"): ("NOT", "an identity"),
    ("rpc.vl", "arg", "index"): ("INDEX", "an argument position in a request"),
    ("rpc.vl", "fresh_channel", "<ret>"): ("NOT", "a channel id"),
    ("rpc.vl", "parse_announced", "<ret>"): ("NOT", "a channel id"),
    ("rpc.vl", "reindex", "from"): ("INDEX", "a list position"),
    ("rpc.vl", "locate", "<ret>"): ("INDEX", "a list position (in a tuple)"),
    ("rpc.vl", "index_of", "<ret>"): ("INDEX", "a list position"),
    ("rpc.vl", "demand", "<ret>"): ("NOT", "a channel id"),
    ("rpc_server.vl", "fresh_connection", "<ret>"): ("NOT", "a connection id"),
    ("rpc_server.vl", "max_connections", "limit"): ("NOT", "a connection budget, not a sequence"),
    ("delta.vl", "with_limit", "limit"): ("INDEX", "a log LENGTH bound"),
    ("delta.vl", "at", "<ret>"): ("SEQUENCE", "a delta SEQUENCE NUMBER — monotonic, not a position"),
    ("delta.vl", "held", "<ret>"): ("INDEX", "how many ops are held — a count"),
    ("delta.vl", "oldest", "<ret>"): ("SEQUENCE", "a delta sequence number"),
    ("string.vl", "code_at", "index"): ("INDEX", "a string position"),
    ("string.vl", "repeat", "count"): ("INDEX", "a repetition count"),
    ("iterator.vl", "take", "count"): ("INDEX", "an element count"),
    ("iterator.vl", "skip", "count"): ("INDEX", "an element count"),
    ("iterator.vl", "count", "<ret>"): ("INDEX", "an element count"),
    ("time.vl", "days", "count"): ("NOT", "a duration"),
    ("time.vl", "hours", "count"): ("NOT", "a duration"),
    ("time.vl", "minutes", "count"): ("NOT", "a duration"),
    ("time.vl", "seconds", "count"): ("NOT", "a duration"),
    ("time.vl", "millis", "count"): ("NOT", "a duration"),
    ("time.vl", "join_units", "count"): ("NOT", "a duration"),
    ("time.vl", "split_units", "millis"): ("NOT", "a duration"),
    ("crypto.vl", "random_bytes", "length"): ("INDEX", "a byte-length"),
    ("base64.vl", "char_at", "value"): ("NOT", "an alphabet code"),
    ("base64.vl", "digit", "<ret>"): ("NOT", "an alphabet code"),
    ("style.vl", "token_axis", "<ret>"): ("NOT", "a design-token step"),
    ("style.vl", "font_weight", "value"): ("NOT", "a CSS weight"),
    ("style.vl", "check_channel", "value"): ("NOT", "a colour channel"),
    ("ui.vl", "chunk_arm", "<ret>"): ("NOT", "a chunk arm id"),
    ("arena.vl", "len", "<ret>"): ("INDEX", "a length"),
    ("shared.vl", "identity", "<ret>"): ("NOT", "an identity"),
    ("option.vl", "parse_i32", "<ret>"): ("NOT", "a parsed VALUE"),
    ("range.vl", "new", "start"): ("NOT", "a range of VALUES, not positions (I5 §2)"),
    ("range.vl", "new", "end"): ("NOT", "a range of VALUES"),
    ("range.vl", "next", "<ret>"): ("NOT", "a range of VALUES"),
    ("random.vl", "range", "<ret>"): ("NOT", "a random VALUE"),
    ("dom.vl", "button", "<ret>"): ("NOT", "a mouse button code"),
    ("fetch.vl", "status", "<ret>"): ("NOT", "an HTTP status"),
    ("process.vl", "exit", "code"): ("NOT", "an exit code"),
    ("storage.vl", "key_at", "index"): ("INDEX", "a storage position"),
    ("storage.vl", "raw_key_at", "index"): ("INDEX", "a storage position"),
    ("storage.vl", "len", "<ret>"): ("INDEX", "a length"),
    ("document.vl", "spliced", "insertions"): ("INDEX", "positions inside a tuple list"),
    ("markdown.vl", "is_fence_close", "indent"): ("INDEX", "a column position"),
    ("markdown.vl", "dedent", "columns"): ("INDEX", "a column width"),
    ("markdown.vl", "leading_spaces", "<ret>"): ("INDEX", "a column width"),
    ("markdown.vl", "heading_level", "<ret>"): ("NOT", "a heading level"),
    ("markdown.vl", "parse_inline", "line"): ("NOT", "a line number carried for diagnostics"),
    ("markdown.vl", "parse_row", "line_number"): ("NOT", "a line number"),
    ("markdown.vl", "index_of", "<ret>"): ("INDEX", "a string position"),
    ("markdown.vl", "index_of", "from"): ("INDEX", "a string position"),
    ("markdown.vl", "same_char_line", "code"): ("NOT", "a character code"),
    ("compare.vl", "index_of", "<ret>"): ("INDEX", "a list position"),
    ("http.vl", "bound_port", "<ret>"): ("NOT", "a port"),
    ("http.vl", "port", "<ret>"): ("NOT", "a port"),
    ("http.vl", "port", "port"): ("NOT", "a port"),
    ("http.vl", "listen", "port"): ("NOT", "a port"),
    ("http.vl", "code", "code"): ("NOT", "an HTTP status"),
    ("http.vl", "set_status_code", "code"): ("NOT", "an HTTP status"),
    ("ws.vl", "encode_frame", "opcode"): ("NOT", "a websocket opcode"),
    ("rpc.vl", "nibble_char", "digit"): ("NOT", "a nibble value"),
}


# Struct FIELDS, decided by (module, owner, field). A field's verdict is what
# the field MEANS, which no name rule can reach: `count` on a mirror is the
# element count of the mirrored list (index-kind), `count` on a lease is a
# reference count (not).
FIELD_OVERRIDES = {
    ("arena.vl", "struct Handle", "index"): ("INDEX", "a slot position"),
    ("arena.vl", "struct Arena", "free"): ("INDEX", "free slot positions"),
    ("arena.vl", "struct Arena", "brand"): ("NOT", "an arena identity"),
    ("arena.vl", "struct Handle", "generation"): ("NOT", "a generation counter"),
    ("arena.vl", "struct Slot", "generation"): ("NOT", "a generation counter"),
    ("binary.vl", "struct BinaryReader", "cursor"): ("INDEX", "a byte position in the frame"),
    ("binary.vl", "struct BinaryWriter", "used"): ("INDEX", "bytes used of the buffer"),
    ("delta.vl", "struct DeltaCursor", "at"): ("SEQUENCE", "a delta sequence number"),
    ("delta.vl", "struct DeltaCursor", "id"): ("NOT", "a consumer identity"),
    ("delta.vl", "struct DeltaLog", "base"): ("SEQUENCE", "a delta sequence number"),
    ("delta.vl", "struct DeltaLog", "version"): ("SEQUENCE", "a delta sequence number"),
    ("delta.vl", "struct DeltaLog", "limit"): ("INDEX", "a bound on the log's LENGTH"),
    ("document.vl", "struct Document", "splice"): ("INDEX", "a byte position"),
    ("document.vl", "struct Tag", "start"): ("INDEX", "a byte position"),
    ("document.vl", "struct Tag", "end"): ("INDEX", "a byte position"),
    ("fs.vl", "struct Reader", "cursor"): ("STREAM", "a FILE offset"),
    ("fs.vl", "struct Stat", "size"): ("STREAM", "a FILE length"),
    ("http.vl", "struct Response", "status"): ("NOT", "an HTTP status"),
    ("http.vl", "struct ResponseBuilder", "status"): ("NOT", "an HTTP status"),
    ("http.vl", "struct Server", "port"): ("NOT", "a port"),
    ("http.vl", "struct ServerBuilder", "port"): ("NOT", "a port"),
    ("iterator.vl", "struct Enumerated", "index"): ("INDEX", "the enumerate counter"),
    ("iterator.vl", "struct ListIterator", "index"): ("INDEX", "a list position"),
    ("iterator.vl", "struct Skipped", "pending"): ("INDEX", "an element count"),
    ("iterator.vl", "struct Taken", "remaining"): ("INDEX", "an element count"),
    ("json.vl", "struct JsonReader", "list_marks"): ("INDEX", "per-depth element counts"),
    ("json.vl", "struct JsonWriter", "variant_arities"): ("WIRE", "the protocol's arities"),
    ("markdown.vl", "struct ParseError", "line"): ("NOT", "a line number"),
    ("range.vl", "struct Range", "current"): ("NOT", "a range of VALUES"),
    ("range.vl", "struct Range", "end"): ("NOT", "a range of VALUES"),
    ("reactive.vl", "struct Draft", "debounce_millis"): ("NOT", "a duration"),
    ("reactive.vl", "struct Draft", "generation"): ("NOT", "a generation counter"),
    ("reactive.vl", "struct Optimistic", "generation"): ("NOT", "a generation counter"),
    ("reactive.vl", "struct Optimistic", "confirmed_generation"): ("NOT", "a generation counter"),
    ("reactive.vl", "struct ReconcilePlan", "removed"): ("INDEX", "the positions removed"),
    ("reactive.vl", "struct Subscriber", "id"): ("NOT", "a subscriber identity"),
    ("reactive.vl", "struct Subscription", "id"): ("NOT", "a subscription identity"),
    ("rpc_server.vl", "struct Connection", "id"): ("NOT", "a connection identity"),
    ("rpc_server.vl", "struct Service", "authorize_timeout"): ("NOT", "a duration"),
    ("rpc_server.vl", "struct Service", "handshake_timeout"): ("NOT", "a duration"),
    ("rpc_server.vl", "struct Service", "handshake_rate"): ("NOT", "a rate"),
    ("rpc_server.vl", "struct Service", "max_connections"): ("NOT", "a connection budget"),
    ("rpc_server.vl", "struct Service", "live"): ("NOT", "live connections, not a sequence"),
    ("rpc_server.vl", "struct Service", "on_connect"): ("NOT", "a closure over a connection id"),
    ("rpc_server.vl", "struct Service", "on_disconnect"): ("NOT", "a closure over a connection id"),
    ("rpc.vl", "struct Capability", "identity"): ("NOT", "an identity"),
    ("rpc.vl", "struct KeyedCell", "positions"): ("INDEX", "where each key sits"),
    ("rpc.vl", "struct KeyedSource", "positions"): ("INDEX", "where each key sits"),
    ("rpc.vl", "struct KeyedSource", "channel"): ("NOT", "a channel id"),
    ("rpc.vl", "struct KeyedSource", "count"): ("INDEX", "the mirrored list's element count"),
    ("rpc.vl", "struct KeyedSource", "settle_id"): ("NOT", "a settle identity"),
    ("rpc.vl", "struct KeyLease", "count"): ("NOT", "a reference count"),
    ("rpc.vl", "struct KeyLease", "settle_id"): ("NOT", "a settle identity"),
    ("rpc.vl", "struct LiveForward", "channel"): ("NOT", "a channel id"),
    ("rpc.vl", "struct LiveForward", "holds"): ("NOT", "a reference count"),
    ("rpc.vl", "struct Origin", "reissue"): ("NOT", "a closure answering a channel id"),
    ("rpc.vl", "struct PendingCall", "request"): ("NOT", "a request id"),
    ("rpc.vl", "struct ReactiveClient", "routes"): ("NOT", "channel ids"),
    ("rpc.vl", "struct ReactiveServer", "sources"): ("NOT", "channel ids"),
    ("rpc.vl", "struct RemoteSource", "channel"): ("NOT", "a channel id"),
    ("rpc.vl", "struct RemoteSource", "count"): ("INDEX", "the mirrored list's element count"),
    ("rpc.vl", "struct RemoteSource", "settle_id"): ("NOT", "a settle identity"),
    ("rpc.vl", "struct RpcProtocol", "connection"): ("NOT", "a connection id"),
    ("rpc.vl", "struct RpcRequest", "connection"): ("NOT", "a connection id"),
    ("rpc.vl", "struct RpcRequest", "arity"): ("WIRE", "the protocol's arity"),
    ("rpc.vl", "struct SocketDuplex", "connection"): ("NOT", "a connection id"),
    ("rpc.vl", "struct SocketDuplex", "next_request"): ("NOT", "a request id"),
    ("rpc.vl", "struct SplitDuplex", "connection"): ("NOT", "a connection id"),
    ("style.vl", "struct Gradient", "stop_count"): ("INDEX", "the stop list's element count"),
    ("time.vl", "struct Duration", "millis"): ("NOT", "a duration"),
    ("time.vl", "struct Instant", "millis"): ("NOT", "a duration"),
    ("ws.vl", "struct WsParser", "fragment_opcode"): ("NOT", "an opcode"),
}


def classify(module, owner, function, position, type_text):
    if function == "" or owner.startswith("struct "):
        field_key = (module, owner, position)
        if field_key in FIELD_OVERRIDES:
            verdict, reason = FIELD_OVERRIDES[field_key]
            return verdict, reason + " [field]"
        if module in WIRE_SEAM_MODULES and position in WIRE_SEAM_FUNCTIONS:
            return "WIRE", "the Serialize/Deserialize protocol seam (\u00a76)"
    key = (module, function, position)
    if key in OVERRIDES:
        verdict, reason = OVERRIDES[key]
        return verdict, reason + " [override]"
    if module in ALGEBRA_MODULES:
        return "NOT", "the numeric type's own algebra"
    if module in WIRE_SEAM_MODULES and function in WIRE_SEAM_FUNCTIONS:
        return "WIRE", "the Serialize/Deserialize protocol seam (§6)"
    if position == "<ret>":
        if function in INDEX_RETURNS:
            return "INDEX", f"`{function}` answers a position or a count"
        return "NOT", f"`{function}` answers a value"
    if position in NOT_INDEX_NAMES:
        return "NOT", NOT_INDEX_NAMES[position]
    if position in INDEX_NAMES:
        return "INDEX", f"`{position}` is a position or a length"
    return "REVIEW", "no rule matched — decide by hand"


def main():
    rows = open(sys.argv[1], encoding="utf-8").read().splitlines()
    print("verdict\tkind\tmodule\tline\towner\tfunction\tposition\ttype\treason")
    for row in rows[1:]:
        parts = row.split("\t")
        if len(parts) < 8:
            continue
        kind, path, line, owner, function, position, text, scalars = parts[:8]
        if kind not in ("SIG", "FIELD"):
            continue
        if not any(s in scalars.split("+") for s in ("i32", "i53", "u53", "u32")):
            continue
        module = path.rsplit("/", 1)[-1]
        verdict, reason = classify(module, owner, function, position, text)
        print(f"{verdict}\t{kind}\t{module}\t{line}\t{owner}\t{function}\t{position}\t{text}\t{reason}")


if __name__ == "__main__":
    main()
