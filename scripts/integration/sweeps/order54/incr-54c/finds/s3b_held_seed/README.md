# B?1 - S3b's cold async seed counted a value a HOT module assigned into a cold binding

`src/views.vl` (hot, the open/edited file) assigns an `async || i32` FIELD READ into `lib`'s
`export mut hook`; `lib::call_hook` calls `hook()`. Before incr-54c's M138 commit the post-pass
record's cold async result (S3b, `PostRecord::async_cold`) asked `hook`'s held values without
asking where they came from, so `call_hook` entered the cold seed; the keystroke that deletes
`hook = holder.run;` was then served a seed a monotone fixpoint cannot shrink from, and the
emitted JS kept `call_hook` async where a clean analysis made it synchronous.

Pinned by the edit-replay differential's `s3b_held` fixture (red on the classes and layered legs
with the cold view's held-value filter reverted). `vilan check .` / `vilan run src/main.vl` print 2.
