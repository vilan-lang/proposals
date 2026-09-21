#!/bin/bash
# Build every corpus program from a COPY of vilan/test with the current debug
# binary and record what each prints. usage: capture-corpus.sh <label>
set -u
W=/home/reed/code/vilan-lang/vilan/.claude/worktrees/reactive-38
S=/tmp/claude-1000/-home-reed-code-vilan-lang/ae2b0352-743d-4446-aedf-1f52ad55831a/scratchpad/reactive-38
LABEL="$1"
STAGE="$S/stage-$LABEL"
OUT="$S/out-$LABEL"
rm -rf "$STAGE" "$OUT"; mkdir -p "$OUT"
cp -r "$W/vilan/test" "$STAGE"
rm -f "$STAGE"/*.mjs
NOT_RUN="time.vl crypto.vl db.vl process-env.vl nursery.vl"
cd "$STAGE" || exit 1
for f in *.vl; do
    case " $NOT_RUN " in *" $f "*) continue;; esac
    base="${f%.vl}"
    if ! "$W/target/debug/vilan" build "$f" > "$OUT/$base.build" 2>&1; then
        echo "BUILD-FAIL" > "$OUT/$base.out"; continue
    fi
    timeout 60 node "$base.mjs" > "$OUT/$base.out" 2> "$OUT/$base.err"
    echo "exit=$?" >> "$OUT/$base.out"
done
echo "captured $(ls "$OUT"/*.out | wc -l) programs into $OUT"
