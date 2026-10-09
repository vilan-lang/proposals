E266's other half (not built by layout-48): `infer_platform` reads only `std::`
imports. Open `lib/src/measure.vl` in the editor: the `[library]` path has no
platform and infers one from the file's own imports; `pkg::paint` declares
`[platform("browser")] mod self;`, but a `pkg::` (or `<dependency>::`) import is
not evidence, so the file is analyzed under the node default and its `Region`
is the PROCESS twin's — where `paint.vl` itself is analyzed under browser
(the status line reads "analyzed as: node — default" for measure.vl).
