# The served keystroke's checks phase at C1, per pass (incr-53a, Order 53)

VILAN_COUNTERS=1 VILAN_PHASE_TIMING=passes scripts/lsp-latency.py --source <kolt copy, lucide carried> --runs 3, 'leaf keystroke, world mode' and 'leaf keystroke'. Base = fe19e1c1 (next after editor-53 + std-53), tip = 1256a9db, run back to back; LOAD 17-20 (four lanes' suites beside): CPU ms are ~2x the quiet-box figures, read the ratios. A quiet-box base at load 4 (b923bfc6): checks 163-190 ms world mode.

```
## /home/reed/code/vilan-lang/vilan/.claude/worktrees/incr-53a/target/incr-53a-scratch/pass-next/scratch/vilan-lsp.stderr single: 7 served analyses; checks 317.3, 307.5, 312.8, 339.5, 346.7, 304.9, 430.9; post 300.4, 295.2, 280.1, 279.9, 361.2, 298.0, 406.6
| analyzer.seal_frozen_ranges() | 2.3 | 2.2-4.1 |
| analyzer.seal_world_table_ranges(&reusable_sources, &replay_records) | 1.3 | 1.3-2.4 |
| analyzer.infer_borrows() | 3.1 | 2.4-3.5 |
| analyzer.infer_bumps() | 29.0 | 25.3-36.6 |
| analyzer.wrapped_view_captures = analyzer.compute_wrapped_view_captures() | 2.2 | 1.8-2.3 |
| analyzer.record_lazy_arguments() | 5.6 | 4.8-16.0 |
| analyzer.check_element_attribute_shadowing() | 2.2 | 1.6-4.4 |
| analyzer.check_view_escape() | 5.3 | 4.8-6.9 |
| analyzer.check_invalidation() | 5.4 | 4.9-7.7 |
| analyzer.check_wire_boundary() | 0.0 | 0.0-0.0 |
| analyzer.check_generic_bound_satisfaction() | 32.8 | 29.3-39.7 |
| analyzer.check_written_nominal_bounds() | 5.4 | 5.1-6.0 |
| analyzer.check_hmr_transfer_bounds() | 4.8 | 4.2-5.7 |
| analyzer.check_container_resource_arguments() | 7.8 | 7.2-9.4 |
| analyzer.check_resource_any_coercion() | 0.0 | 0.0-1.5 |
| analyzer.check_resource_moves() | 20.8 | 19.3-39.7 |
| analyzer.record_drop_sink_argument_types() | 1.6 | 1.5-3.1 |
| R11: the seed walk | 1.1 | 1.0-1.3 |
| R11: the whole-program sets | 13.3 | 12.6-18.3 |
| analyzer.check_resource_generic_instantiations() | 40.0 | 38.3-56.5 |
| analyzer.plan_resource_drops() | 9.1 | 8.0-13.2 |
| analyzer.check_trait_method_scope(global_scope_id) | 2.7 | 2.5-3.2 |
| analyzer.check_duplicate_inherent_members() | 0.0 | 0.0-1.8 |
| analyzer.build_drop_glue() | 2.3 | 1.8-2.9 |
| analyzer.rewrite_view_assignment_targets() | 1.2 | 1.0-1.8 |
| liveness::LastUse::compute | 23.0 | 20.2-30.8 |
| analyzer.collect_held_rows() | 2.1 | 1.8-2.5 |
| analyzer.compute_shared_read_bindings() | 8.6 | 7.9-13.2 |
| analyzer.compute_capture_clone_sites() | 0.7 | 0.5-1.7 |
| analyzer.compute_resource_types() | 3.5 | 3.0-5.3 |
| analyzer.compute_clone_sites() | 1.1 | 0.0-1.5 |
| the view, clone and hmr plans | 10.7 | 8.4-18.5 |
| analyzer.hint_labels() | 1.3 | 1.1-1.4 |
| the stage hints and auto fills | 2.9 | 2.4-4.7 |
| the label tables | 24.5 | 21.3-34.1 |
| analyzer.member_headers() | 1.1 | 1.0-1.4 |
| the class D partition and the records | 4.9 | 4.6-7.5 |
| the remaining tables, labels and records | 22.9 | 20.7-27.9 |
counters: {'records-served': '15', 'records-stale': '1', 'live-ranges': '22', 'live-entities': '12316', 'functions-checked': '195'}
## /home/reed/code/vilan-lang/vilan/.claude/worktrees/incr-53a/target/incr-53a-scratch/pass-next/scratch/vilan-lsp.stderr world: 6 served analyses; checks 362.0, 408.8, 370.6, 380.2, 354.9, 408.9; post 326.5, 360.8, 344.0, 288.2, 326.2, 298.5
| analyzer.seal_frozen_ranges() | 3.9 | 3.8-11.9 |
| analyzer.seal_world_table_ranges(&reusable_sources, &replay_records) | 4.7 | 2.9-7.6 |
| analyzer.infer_borrows() | 4.2 | 3.5-8.8 |
| analyzer.infer_bumps() | 34.9 | 33.2-36.3 |
| analyzer.wrapped_view_captures = analyzer.compute_wrapped_view_captures() | 2.4 | 2.0-5.2 |
| analyzer.record_lazy_arguments() | 8.7 | 6.8-11.6 |
| analyzer.check_element_attribute_shadowing() | 3.2 | 3.0-4.3 |
| analyzer.check_view_escape() | 7.1 | 5.7-9.7 |
| analyzer.check_invalidation() | 7.2 | 6.1-7.7 |
| analyzer.check_wire_boundary() | 0.0 | 0.0-0.1 |
| analyzer.check_generic_bound_satisfaction() | 36.1 | 31.4-37.8 |
| analyzer.check_written_nominal_bounds() | 6.9 | 5.2-8.3 |
| analyzer.check_hmr_transfer_bounds() | 5.8 | 4.8-9.3 |
| analyzer.check_container_resource_arguments() | 8.8 | 7.3-14.7 |
| analyzer.check_resource_moves() | 25.1 | 23.3-36.7 |
| analyzer.record_drop_sink_argument_types() | 2.3 | 2.0-5.8 |
| R11: the seed walk | 1.3 | 1.2-1.8 |
| R11: the whole-program sets | 14.7 | 13.3-17.5 |
| analyzer.check_resource_generic_instantiations() | 44.1 | 40.9-52.6 |
| analyzer.plan_resource_drops() | 10.8 | 8.6-14.3 |
| analyzer.check_trait_method_scope(global_scope_id) | 2.8 | 2.6-4.7 |
| analyzer.build_drop_glue() | 2.7 | 2.4-2.9 |
| analyzer.rewrite_view_assignment_targets() | 1.5 | 1.3-1.8 |
| liveness::LastUse::compute | 28.1 | 25.0-29.2 |
| analyzer.collect_held_rows() | 2.6 | 2.1-10.1 |
| analyzer.compute_shared_read_bindings() | 10.2 | 9.0-17.9 |
| analyzer.compute_capture_clone_sites() | 0.7 | 0.7-1.0 |
| analyzer.compute_resource_types() | 4.2 | 3.8-9.2 |
| analyzer.compute_clone_sites() | 1.5 | 1.3-1.8 |
| the view, clone and hmr plans | 12.6 | 11.1-14.0 |
| analyzer.hint_labels() | 1.4 | 1.2-1.8 |
| the stage hints and auto fills | 3.3 | 2.7-3.9 |
| the label tables | 11.8 | 8.8-14.0 |
| analyzer.member_headers() | 1.6 | 1.2-2.5 |
| the class D partition and the records | 8.2 | 7.6-10.3 |
| the remaining tables, labels and records | 23.8 | 22.0-28.4 |
| analyzer.check_must_use() | 0.0 | 0.0-2.8 |
| analyzer.record_lazy_bindings() | 0.0 | 0.0-13.7 |
| analyzer.resolve_hint_attributes() | 0.0 | 0.0-6.2 |
| analyzer.check_mut_captures_under_view_subjects() | 0.0 | 0.0-1.1 |
| the held fold | 0.0 | 0.0-1.7 |
| analyzer.check_view_arguments() | 0.0 | 0.0-1.7 |
| analyzer.check_resource_any_coercion() | 0.0 | 0.0-1.4 |
| analyzer.check_written_autofocus() | 0.0 | 0.0-1.3 |
counters: {'records-served': '43', 'records-stale': '3', 'live-ranges': '24', 'live-entities': '12550', 'functions-checked': '196'}
```

```
## /home/reed/code/vilan-lang/vilan/.claude/worktrees/incr-53a/target/incr-53a-scratch/pass-tip/scratch/vilan-lsp.stderr single: 7 served analyses; checks 497.2, 325.0, 300.5, 294.9, 356.9, 313.4, 328.5; post 345.9, 303.5, 317.8, 294.6, 343.7, 377.1, 435.2
| analyzer.seal_frozen_ranges() | 2.0 | 1.8-2.2 |
| analyzer.seal_world_table_ranges(&reusable_sources, &replay_records) | 1.4 | 1.3-10.3 |
| analyzer.infer_borrows() | 3.4 | 2.5-3.9 |
| analyzer.infer_bumps() | 30.8 | 28.3-57.3 |
| analyzer.wrapped_view_captures = analyzer.compute_wrapped_view_captures() | 2.3 | 2.0-11.3 |
| analyzer.check_mut_captures_under_view_subjects() | 0.0 | 0.0-1.9 |
| analyzer.check_element_attribute_shadowing() | 2.6 | 1.9-3.1 |
| analyzer.check_view_escape() | 5.7 | 4.6-15.6 |
| analyzer.check_invalidation() | 5.7 | 5.0-9.8 |
| analyzer.check_wire_boundary() | 0.0 | 0.0-0.1 |
| analyzer.check_generic_bound_satisfaction() | 35.2 | 28.9-51.3 |
| analyzer.check_written_nominal_bounds() | 1.5 | 1.3-1.9 |
| analyzer.check_container_resource_arguments() | 7.8 | 7.3-11.3 |
| analyzer.check_resource_moves() | 2.9 | 2.3-12.9 |
| analyzer.record_drop_sink_argument_types() | 2.7 | 2.3-3.9 |
| R11: the seed walk | 1.4 | 1.3-11.7 |
| R11: the whole-program sets | 12.5 | 11.0-21.4 |
| analyzer.check_resource_generic_instantiations() | 51.6 | 42.1-90.9 |
| analyzer.plan_resource_drops() | 9.1 | 6.9-16.7 |
| analyzer.check_trait_method_scope(global_scope_id) | 3.0 | 2.6-6.7 |
| analyzer.build_drop_glue() | 2.9 | 2.2-5.1 |
| analyzer.rewrite_view_assignment_targets() | 1.4 | 1.2-4.0 |
| liveness::LastUse::compute | 26.6 | 20.1-38.0 |
| analyzer.collect_held_rows() | 2.3 | 1.9-3.3 |
| analyzer.compute_shared_read_bindings() | 10.0 | 8.8-12.2 |
| analyzer.compute_capture_clone_sites() | 0.8 | 0.7-1.0 |
| analyzer.compute_resource_types() | 2.8 | 2.6-4.1 |
| analyzer.compute_clone_sites() | 1.6 | 1.1-2.1 |
| the view, clone and hmr plans | 13.1 | 11.6-16.6 |
| analyzer.hint_labels() | 1.3 | 1.2-2.5 |
| the stage hints and auto fills | 3.5 | 2.7-5.0 |
| the label tables | 25.4 | 22.4-32.7 |
| analyzer.member_headers() | 1.2 | 0.0-2.2 |
| the hover rows | 6.2 | 5.8-11.4 |
| the class D partition and the records | 3.1 | 2.9-5.1 |
| the remaining tables, labels and records | 20.3 | 18.4-22.8 |
| analyzer.check_mutable_arguments() | 0.0 | 0.0-1.8 |
| analyzer.check_lazy_arguments() | 0.0 | 0.0-1.7 |
| analyzer.record_lazy_bindings() | 0.0 | 0.0-1.1 |
| analyzer.check_resource_any_coercion() | 0.0 | 0.0-1.5 |
| analyzer.check_exposed_unexported_types() | 0.0 | 0.0-1.1 |
| analyzer.check_duplicate_inherent_members() | 0.0 | 0.0-1.2 |
| analyzer.check_view_value_reads() | 0.0 | 0.0-1.7 |
counters: {'records-served': '15', 'records-stale': '1', 'live-ranges': '22', 'live-entities': '12316', 'functions-checked': '195'}
## /home/reed/code/vilan-lang/vilan/.claude/worktrees/incr-53a/target/incr-53a-scratch/pass-tip/scratch/vilan-lsp.stderr world: 6 served analyses; checks 412.2, 298.6, 275.8, 335.6, 346.9, 359.7; post 415.1, 315.4, 555.6, 439.5, 376.9, 392.5
| analyzer.seal_frozen_ranges() | 3.6 | 3.3-4.8 |
| analyzer.seal_world_table_ranges(&reusable_sources, &replay_records) | 3.2 | 2.7-9.0 |
| analyzer.infer_borrows() | 3.9 | 3.1-4.3 |
| analyzer.infer_bumps() | 35.5 | 29.5-44.3 |
| analyzer.wrapped_view_captures = analyzer.compute_wrapped_view_captures() | 2.1 | 1.9-2.9 |
| analyzer.check_element_attribute_shadowing() | 2.6 | 2.2-3.8 |
| analyzer.check_view_escape() | 5.5 | 5.0-8.2 |
| analyzer.check_invalidation() | 6.4 | 5.2-11.7 |
| analyzer.check_wire_boundary() | 0.0 | 0.0-0.0 |
| analyzer.check_generic_bound_satisfaction() | 38.4 | 30.8-59.4 |
| analyzer.check_written_nominal_bounds() | 1.5 | 1.4-4.2 |
| analyzer.check_container_resource_arguments() | 8.6 | 7.2-12.6 |
| analyzer.check_resource_any_coercion() | 1.1 | 0.0-2.2 |
| analyzer.check_resource_moves() | 3.1 | 2.5-4.2 |
| analyzer.check_class_written_twice() | 0.0 | 0.0-1.9 |
| analyzer.record_drop_sink_argument_types() | 2.8 | 2.6-3.6 |
| R11: the seed walk | 1.6 | 1.4-1.8 |
| R11: the whole-program sets | 12.6 | 11.3-23.3 |
| analyzer.check_resource_generic_instantiations() | 51.2 | 44.1-59.3 |
| analyzer.plan_resource_drops() | 10.6 | 7.8-13.1 |
| analyzer.check_trait_method_scope(global_scope_id) | 2.9 | 2.5-3.7 |
| analyzer.check_duplicate_inherent_members() | 0.0 | 0.0-1.2 |
| analyzer.build_drop_glue() | 3.0 | 1.9-5.9 |
| analyzer.rewrite_view_assignment_targets() | 1.6 | 1.1-2.5 |
| liveness::LastUse::compute | 29.2 | 21.1-40.3 |
| analyzer.collect_held_rows() | 2.4 | 2.2-3.5 |
| analyzer.compute_shared_read_bindings() | 9.9 | 9.6-10.6 |
| analyzer.compute_capture_clone_sites() | 0.9 | 0.8-1.0 |
| analyzer.compute_resource_types() | 4.0 | 3.2-8.3 |
| analyzer.compute_clone_sites() | 1.6 | 1.1-2.3 |
| the view, clone and hmr plans | 13.9 | 8.7-16.6 |
| analyzer.hint_labels() | 1.8 | 1.3-2.3 |
| the stage hints and auto fills | 3.2 | 2.8-5.9 |
| the label tables | 7.5 | 6.0-10.4 |
| analyzer.member_headers() | 1.8 | 1.3-3.6 |
| the hover rows | 4.2 | 3.0-5.6 |
| the class D partition and the records | 6.7 | 4.7-8.7 |
| the remaining tables, labels and records | 20.4 | 17.2-30.8 |
| analyzer.plan_last_use_drop_extents() | 0.0 | 0.0-1.6 |
| analyzer.check_duplicate_module_declarations() | 0.0 | 0.0-1.3 |
| analyzer.check_mut_captures_under_view_subjects() | 0.0 | 0.0-1.1 |
| analyzer.resolve_hint_attributes() | 0.0 | 0.0-1.2 |
| analyzer.compute_return_clone_sites() | 0.0 | 0.0-1.0 |
| analyzer.check_duplicate_trait_impls() | 0.0 | 0.0-4.1 |
counters: {'records-served': '43', 'records-stale': '3', 'live-ranges': '24', 'live-entities': '12550', 'functions-checked': '196'}
```
