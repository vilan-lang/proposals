#!/bin/sh
# tooling-55 find: SIGTERM to `vilan run --watch` exits 130 and leaves the node round's child running.
# usage: watch_sigterm_orphan.sh /path/to/vilan   (kills what it started, by pid)
V=${1:-vilan}
D=$(mktemp -d); mkdir -p $D/src
printf '[package]\nname = "app"\n' > $D/vilan.toml
printf 'import std::io::print;\nimport std::time::sleep;\n\nfun main() {\n\tprint("up");\n\tsleep(60000);\n}\n' > $D/src/main.vl
$V run --watch $D > $D/out.log 2>&1 &
W=$!
for i in $(seq 1 100); do grep -q up $D/out.log 2>/dev/null && break; sleep 0.3; done
kids=$(cat /proc/$W/task/*/children)
echo "watcher=$W children=$kids"
kill -TERM $W; wait $W; echo "watcher exit=$?"
for k in $kids; do kill -0 $k 2>/dev/null && { echo "child $k STILL ALIVE (orphan)"; kill -KILL $k; }; done
rm -rf $D
