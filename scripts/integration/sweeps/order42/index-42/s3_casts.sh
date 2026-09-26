#!/usr/bin/env bash
# S3's measurement: the emitted main.rs of every native-copy-census program,
# base toolchain (d65d4e759, installed) vs the migrated worktree binary.
set -u
B="$1"; W="$2"
out="$B/s3-casts.tsv"
printf 'program\tbefore-lines\tbefore-len-as-i32\tbefore-as-i64\tafter-lines\tafter-len-as-i32\tafter-as-i64\n' > "$out"
for p in $(awk -F'\t' '!/^#/{print $1}' "$W/crates/vilan-cli/tests/native-copy-census.tsv"); do
  [ -f "$W/vilan/test/$p.vl" ] || continue
  for d in before after; do
    mkdir -p "$B/$d/$p"; printf '[package]\nname = "p"\n' > "$B/$d/$p/vilan.toml"
    if [ $d = before ]; then
      git -C "$W" show "d65d4e75:vilan/test/$p.vl" > "$B/$d/$p/$p.vl" 2>/dev/null || continue
      (cd "$B/$d/$p" && timeout 120 vilan build --backend rust --stdout "$p.vl" > main.rs 2>/dev/null)
    else
      cp "$W/vilan/test/$p.vl" "$B/$d/$p/"
      (cd "$B/$d/$p" && timeout 120 "$W/target/debug/vilan" build --backend rust --stdout "$p.vl" > main.rs 2>/dev/null)
    fi
  done
  b="$B/before/$p/main.rs"; a="$B/after/$p/main.rs"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$p" "$(wc -l < "$b")" "$(grep -o 'len() as i32' "$b" | wc -l)" "$(grep -o ') as i64' "$b" | wc -l)" "$(wc -l < "$a")" "$(grep -o 'len() as i32' "$a" | wc -l)" "$(grep -o ') as i64' "$a" | wc -l)" >> "$out"
done
