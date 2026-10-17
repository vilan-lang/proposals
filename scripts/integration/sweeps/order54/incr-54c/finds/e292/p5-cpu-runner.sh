#!/bin/bash
# N157/P5's instrument: a nextest target runner recording each test process's
# CPU (user+sys of the test binary and every process it spawns). `times` runs
# in THIS shell (a pipe or a substitution would ask a subshell, whose children
# are none).
"$@"
status=$?
scratch=$(mktemp)
times > "$scratch"
children=$(tail -1 "$scratch")
rm -f "$scratch"
name=""
previous=""
for argument in "$@"; do
    if [ "$previous" = "--exact" ]; then name="$argument"; fi
    previous="$argument"
done
printf '%s\t%s\t%s\n' "$(basename "$1")" "$name" "$children" >> "${CPU_RUNNER_LOG:?}"
exit $status
