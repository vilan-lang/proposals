# B?2 - a std namespace the import names was not part of the std prefix's key

    mkdir wc
    VILAN_STD_PREFIX=on VILAN_WORLD_CACHE=$PWD/wc vilan check empty.vl   # writes the prefix
    VILAN_STD_PREFIX=on VILAN_WORLD_CACHE=$PWD/wc vilan check dmo.vl     # loads it

With v0.51.1 (and C2 = 56fe0283) the second check reports
"`std::web` moved to `std::web::prelude`" where the canonical analysis (`VILAN_STD_PREFIX=off`)
reports "cannot find 'dmo' in the imported path": the two programs share one std module closure,
the closure skipped pure namespaces, and the world built for `empty.vl` holds no `web`
namespace. The same pair in one process over the in-process prefix (P1) answers the same wrong way.
Found by P5 (`std_surface::a154_the_old_web_prelude_path_is_refused_and_a_typo_under_the_namespace_is_not`
red over the suite's shared world cache); fixed in incr-54c (`std_closure` keys a namespace as
`name/`); pinned by `a_std_namespace_the_import_names_is_part_of_the_prefix_key`
(prefix_roundtrip_differential).
