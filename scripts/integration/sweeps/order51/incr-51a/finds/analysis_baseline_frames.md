# The analysis's own debug-profile stack baseline under the walk (incr-51a, Order 51)

Read with gdb at the overflow of `deep_nesting::a_thirty_level_chain_still_fits_libtests_own_two_mib_thread`
on the v0.48.0 base (ca407da0), dev profile, `VILAN_CANARY_STACK_KIB=1536`:

    T=$(ls -t target/debug/deps/deep_nesting-* | grep -v '\.d$' | head -1)
    cat > frames.gdb <<'G'
    set pagination off
    handle SIGSEGV stop print
    run
    set $i = 0
    while $i < 128
      frame $i
      printf "SP %d 0x%lx\n", $i, $sp
      set $i = $i + 1
    end
    kill
    quit
    G
    VILAN_CANARY_STACK_KIB=1536 gdb -q -batch -x frames.gdb --args $T a_thirty_level_chain_still_fits --test-threads 1

Frame sizes (bytes, the SP delta to the caller), bottom of the thread up to the first walk level:

| frame | bytes |
|---|---:|
| the test's closure | 19,408 |
| `analyze_source` | 19,056 |
| `analyze_source_reclaimable` | 9,712 |
| `catch_unwind` + `do_call` (AnalyzedEntry, 9,480 B) | 28,608 + 28,528 |
| `analyze_source_unfenced` | 79,152 |
| `catch_unwind` + `do_call` (Option<Program>, Program = 9,408 B) | 28,448 + 28,336 |
| `analyze_source_unfenced::{closure#4}` | 47,280 |
| `analyze_cancellable` | 48,400 |
| `analyze_inner` | **214,336** |
| `analyze_over_world` | 83,152 |
| `walk_module_items` -> `walk_expr_nodes` -> iterator layers | ~1,200 |
| total under the first walk level | **~636 KB** |

The walk's 33 levels were 0.89 MiB of the 1.5 MiB; after N169 they are 0.26 MiB and the baseline is
now 70% of what the canary measures. The four `catch_unwind` frames are the Program / AnalyzedEntry
moved by value through each layer (~3 copies each at opt-level 0). Optimized, the same path is a
small fraction (the release walk-frame is 640 B a level).
