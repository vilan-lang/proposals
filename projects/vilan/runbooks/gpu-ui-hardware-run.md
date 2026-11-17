# The GPU UI on real hardware: Windows and macOS runbook (F187)

Prepared by lane hw-58 on 2026-11-17. The report switch is on `next` from commit
`eba9c211` (pushed 2026-11-17): use a checkout of `next` at or after it.
Tracker item F187. A sample of the report's output from Linux is in
[gpu-ui-hardware-run-sample-report.txt](gpu-ui-hardware-run-sample-report.txt).

## Read this first: what could not be checked from Linux

Everything below was written on Linux (WSL2) with Mesa's software Vulkan under a
virtual X display. These parts are checked here:

- The report switch works on Linux, and its sample output is below.
- The GPU crate (`crates/vilan-rt-gfx`) passes `cargo clippy -D warnings` for
  `x86_64-pc-windows-msvc`, `aarch64-apple-darwin` and `x86_64-apple-darwin`.
- A generated project (`ui-counter`) passes `cargo check` for
  `x86_64-pc-windows-msvc` and `aarch64-apple-darwin`.
- `vilan run --backend rust` needs no `node` (checked with `node` removed from
  `PATH`).

These parts are NOT checked. Treat each one as a question the run answers:

- That anything links, starts or draws on Windows or macOS. Nothing has ever
  run there.
- Every PowerShell command. They are written from the documentation, not run.
- Every macOS command. They are written from the documentation, not run.
- That `vilan run` finds `main.exe` on Windows. The compiler prints the binary's
  path without `.exe`. Rust's process launcher should add it, but this was not
  tried.
- First-build times and disk use on your machines. The only numbers come from
  this Linux box.
- How the window behaves when launched from a terminal on macOS: whether it
  comes to the front, and whether the Dock shows it. It is not an app bundle.
- Whether `WGPU_BACKEND=gl` gives an adapter on Windows.
- Everything in the Narrator and VoiceOver section.

## 1. What this run is for

The GPU UI (`std::gfx`, `std::ui`) has only ever run on a software renderer on Linux.
This run finds out whether it draws correctly on DirectX 12, Vulkan and Metal, and how fast its frames really are.
It also finds out which missing feature a real user meets first: input methods, focus scopes, or a second window.

## 2. Prerequisites

### Both systems

- About 15 GB of free disk for one shared build directory. That covers the
  compiler, the examples in debug, and one release build. On Linux, one
  example's debug build directory was 5.3 GB and its release directory 1.0 GB.
  The rest of the space is for the compiler's own build.
- Git.
- Rust through rustup, with the toolchain this repository pins.
  `rust-toolchain.toml` says `1.98.1`. Rustup obeys that file in every
  directory under the checkout. The generated example projects
  (`vilan/examples/<name>/dist/native/main/`) are inside the checkout, so they
  build with 1.98.1 too. A generated project OUTSIDE a checkout pins nothing.
  It would build with your default toolchain.
- Node is NOT needed. `vilan run --backend rust` only calls `cargo`. Node is
  only for JavaScript builds, the editor extension, and
  `scripts/install-dev.sh`.
- No C compiler is needed beyond the platform's linker. Nothing in the
  compiler or the GPU stack compiles C for these targets.

### Windows

- Visual Studio Build Tools 2022 with the "Desktop development with C++"
  workload. It brings the MSVC linker and a Windows SDK.
- Rust from rustup-init.exe, on the default host `x86_64-pc-windows-msvc`.
- PowerShell 7 (`pwsh`) is the easier shell for saving the report to a file.
  See section 4.

Install the pinned toolchain once:

```powershell
rustup toolchain install 1.98.1
```

### macOS

- The Xcode command line tools. They bring the linker and the SDK.

```zsh
xcode-select --install
```

- Rust from rustup (`curl https://sh.rustup.rs -sSf | sh`).

Then install the pinned toolchain:

```zsh
rustup toolchain install 1.98.1
```

### Time

Unmeasured on Windows and macOS. On Linux (this box, 6 build jobs, other
builds running):

- The first example, from cold: 85 s.
- A second example sharing the build directory: 26 s.
- A release build of one example, from cold: 77 s.

On your Linux machine, the survey recorded 25 to 37 s for a clean debug build
of the stack alone, and 36 to 44 s for `ui-todo`. Building the compiler in
release mode comes on top of that, and was not measured here.

## 3. Getting the code and building the compiler

Use a checkout of `next` at or after the commit that carries the report switch.
Look for the changelog entry "`VILAN_GFX_REPORT=1` ... (F187)".

From the checkout's root, build the compiler.

Windows (PowerShell):

```powershell
cargo build --release -p vilan-cli
```

macOS (zsh):

```zsh
cargo build --release -p vilan-cli
```

Do not use `scripts/install-dev.sh`. It is POSIX shell, so it cannot run on
Windows. On macOS it refuses to start without `npm`, and it installs the VS Code
extension too. The plain cargo command is enough. Use the compiler from
`target/release` directly, so nothing else on the machine changes.

Only AFTER the compiler is built, point every example at ONE shared build
directory. Otherwise each example builds the whole GPU stack again, which costs
about 5 GB and a minute or more each time. Set this in the shell you run the
examples from.

Windows:

```powershell
$env:CARGO_TARGET_DIR = "$HOME\vilan-hw\target"
```

macOS:

```zsh
export CARGO_TARGET_DIR="$HOME/vilan-hw/target"
```

Make a folder for what you send back.

Windows:

```powershell
New-Item -ItemType Directory -Force "$HOME\vilan-hw\reports"
```

macOS:

```zsh
mkdir -p "$HOME/vilan-hw/reports"
```

## 4. The run, example by example

Run every command from the checkout's root. Each one builds the example in
debug and opens its window. `vilan run` prints nothing on success until the
window closes. The report goes to stderr. The commands below save it to a file
and still show the window.

Turn the report on once per shell.

Windows:

```powershell
$env:VILAN_GFX_REPORT = "1"
```

macOS:

```zsh
export VILAN_GFX_REPORT=1
```

If PowerShell's `2>` writes error-record text around the report (Windows
PowerShell 5.1 does this to native programs), use PowerShell 7. Or run the same
line inside `cmd /c "..."`. Or copy the text out of the terminal instead.

On Windows the program is a console program. Launched from the terminal it uses
that terminal and opens no second window. Launched by double-clicking the .exe,
it would also open a console window. The compiler emits no
`windows_subsystem` attribute (checked in `crates/vilan-rust/src/lib.rs`). Do
not double-click; this is only so you know.

The reference images in the repository use a test font (Noto Mono). Your runs
use the system's fonts, so text will look different and take different widths.
That is expected.

### Things to try in EVERY example

Do each of these and note anything wrong:

1. Drag-resize the window from a corner, slowly and then fast. Watch for
   stretching, flicker, a black or stale frame, or lag behind the pointer.
2. Move the window to a monitor with a different scale factor, if you have one
   (for example a 4K display at 150% next to a 1080p one at 100%, or a Retina
   laptop screen next to an external 1x display). Everything should re-render
   sharp at the new scale. The report prints a `scale factor:` line.
3. Minimise and restore. The window should come back drawn.
4. Sleep the machine with the window open, wake it, and look at the window.
   The report may print `surface: lost` or `outdated` lines. The window should
   still draw afterwards.
5. Close the window with the title bar's close button. The program should end
   and the report's exit section should appear.

The examples that take text (`ui-todo`, `ui-notes`) have more to try in their
own sections.

### 4.1 `gfx`: the drawing layer alone

A counter drawn with `std::gfx` primitives: a card with a shadow, a gradient
bar, the text "Count: 0" with an underline, and an "Add one" button with a plus
icon (a stroked path). It looks like `crates/vilan-cli/tests/gfx/counter-100.png`.
Hover over the button: it changes colour. Click it: the count goes up. A click
anywhere else does nothing.

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\gfx 2> "$HOME\vilan-hw\reports\gfx-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/gfx 2> "$HOME/vilan-hw/reports/gfx-macos.txt"
```

### 4.2 `ui-counter`: `std::ui` elements and keys

The same counter built from `std::ui` elements, with two buttons, "Add one" and
"Reset". Their hovered, pressed and focused looks come from the app. Try
clicks, then Tab and Shift+Tab to move focus, then Enter and Space on the
focused button. Make the window shorter than about 300 dp: the count's text
gets smaller.

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-counter 2> "$HOME\vilan-hw\reports\ui-counter-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/ui-counter 2> "$HOME/vilan-hw/reports/ui-counter-macos.txt"
```

### 4.3 `ui`: layout

A documentation page: a dark header with "vilan" and three links, a sidebar
with "Elements" highlighted, a heading, wrapped paragraphs, and a picture card
with a red "NEW" badge in its top-right corner. It looks like
`crates/vilan-cli/tests/ui/screen-100.png`. Resize it narrower: the paragraphs
re-wrap and the text column beside the picture gives up its width first. This is
the best example for the resize and scale tests.

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui 2> "$HOME\vilan-hw\reports\ui-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/ui 2> "$HOME/vilan-hw/reports/ui-macos.txt"
```

### 4.4 `ui-todo`: the kit's controls and text input

A text input with a placeholder and an "Add" button. Enter or the button adds
an item. Each item has a checkbox (a check icon) and a remove button.

Try:

1. Type a few words and press Enter. Add three items.
2. Select by dragging across the text, past the field's edge and past the
   window's edge. Double-click to select a word. Triple-click to select all.
3. Use Shift+arrows, Ctrl+arrows to step by word (Option+arrows on macOS),
   Home and End.
4. Undo and redo: Ctrl+Z and Ctrl+Shift+Z (Cmd on macOS).
5. Copy text from the input and paste it into another application, such as
   Notepad or TextEdit. Then copy text in the other application and paste it
   into the input.
6. Type with an input method on: on Windows the Microsoft Japanese IME or
   Pinyin; on macOS a Japanese or Chinese input source. This is EXPECTED NOT
   TO WORK: input-method composition is not built. Note exactly what happens.
   Possible outcomes: nothing is typed; the raw Latin letters are typed; or a
   candidate window appears, and you note where. Also note whether committed
   text arrives at all.
7. Check, uncheck, and remove items with the mouse. Then do the same with Tab
   and Space.

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-todo 2> "$HOME\vilan-hw\reports\ui-todo-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/ui-todo 2> "$HOME/vilan-hw/reports/ui-todo-macos.txt"
```

### 4.5 `ui-notes`: multi-line text

A notes pad: a multi-line text area that wraps softly, scrolls, and has undo.
Do the same text checks as in `ui-todo`, with line breaks. Also try Up and Down
across wrapped lines (the caret should keep its column) and a selection over
several lines. Paste a long text, a few hundred lines, and type at its end.
Typing in long text is known to be slow (F180). Note how slow it is, not just
that it is slow.

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-notes 2> "$HOME\vilan-hw\reports\ui-notes-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/ui-notes 2> "$HOME/vilan-hw/reports/ui-notes-macos.txt"
```

### 4.6 `ui-virtual-list`: 100,000 rows

A list of 100,000 keyed rows, of which only the visible ones exist. Scroll fast
with the wheel or touchpad, drag the touchpad hard, and click rows far down.
Watch for blank rows, rows jumping, or the scroll lagging behind your hand. Then
run it once more with rows of differing heights (`-- --varied`).

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-virtual-list 2> "$HOME\vilan-hw\reports\ui-virtual-list-windows.txt"
```

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-virtual-list -- --varied 2> "$HOME\vilan-hw\reports\ui-virtual-list-varied-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/ui-virtual-list 2> "$HOME/vilan-hw/reports/ui-virtual-list-macos.txt"
```

```zsh
./target/release/vilan run --backend rust vilan/examples/ui-virtual-list -- --varied 2> "$HOME/vilan-hw/reports/ui-virtual-list-varied-macos.txt"
```

Optional: `vilan/examples/ui-list` is the same idea with 10,000 real rows and
no virtualisation. Run it the same way if you want the comparison.

### 4.7 `ui-icons`: paths

A few rows of Lucide icons from the generated icon package at
`vilan/packages/lucide`: "Saved" with a check; three icons at 16, 24 and 32 dp;
a blue "Menu" button with a chevron; a filled red heart and a ring with an
even-odd hole. It looks like `crates/vilan-cli/tests/ui/icons-100.png`. Look
closely at thin strokes at 100% and at 150% or 200%. The scale test matters most
here.

Windows:

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-icons 2> "$HOME\vilan-hw\reports\ui-icons-windows.txt"
```

macOS:

```zsh
./target/release/vilan run --backend rust vilan/examples/ui-icons 2> "$HOME/vilan-hw/reports/ui-icons-macos.txt"
```

### 4.8 Other backends, once per system

Windows uses DirectX 12 by default. Run `ui` and `ui-virtual-list` once more on
Vulkan and once on OpenGL. Compare what they draw and their frame times. If a
backend has no adapter, the program prints a "no window" line; note it.

```powershell
$env:WGPU_BACKEND = "vulkan"
```

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui 2> "$HOME\vilan-hw\reports\ui-windows-vulkan.txt"
```

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-virtual-list 2> "$HOME\vilan-hw\reports\ui-virtual-list-windows-vulkan.txt"
```

```powershell
$env:WGPU_BACKEND = "gl"
```

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui 2> "$HOME\vilan-hw\reports\ui-windows-gl.txt"
```

```powershell
.\target\release\vilan.exe run --backend rust vilan\examples\ui-virtual-list 2> "$HOME\vilan-hw\reports\ui-virtual-list-windows-gl.txt"
```

```powershell
Remove-Item Env:WGPU_BACKEND
```

macOS has only Metal. The build has no Vulkan driver (MoltenVK) and no OpenGL
layer (ANGLE), so there is nothing to compare there.

## 5. Release mode, for two examples

There is no `--release` flag. A debug run has already written the cargo
project, so build that project in release yourself. Debug rendering is known to
be 5 to 10 times slower. This measures by how much on real hardware.

Windows, `ui` then `ui-virtual-list`:

```powershell
cargo build --release --manifest-path vilan\examples\ui\dist\native\main\Cargo.toml
```

```powershell
& "$env:CARGO_TARGET_DIR\release\main.exe" 2> "$HOME\vilan-hw\reports\ui-windows-release.txt"
```

```powershell
cargo build --release --manifest-path vilan\examples\ui-virtual-list\dist\native\main\Cargo.toml
```

```powershell
& "$env:CARGO_TARGET_DIR\release\main.exe" 2> "$HOME\vilan-hw\reports\ui-virtual-list-windows-release.txt"
```

macOS:

```zsh
cargo build --release --manifest-path vilan/examples/ui/dist/native/main/Cargo.toml
```

```zsh
"$CARGO_TARGET_DIR/release/main" 2> "$HOME/vilan-hw/reports/ui-macos-release.txt"
```

```zsh
cargo build --release --manifest-path vilan/examples/ui-virtual-list/dist/native/main/Cargo.toml
```

```zsh
"$CARGO_TARGET_DIR/release/main" 2> "$HOME/vilan-hw/reports/ui-virtual-list-macos-release.txt"
```

Every example's binary is named `main`, so with the shared build directory each
release build replaces the last. Run each one straight after building it, as
above. The report's `crate:` line says `(release build)`.

## 6. Accessibility: five minutes

Use `ui-todo` with one item added. Check three things:

1. Tab to the "Add" button. The screen reader announces it as a button named
   "Add".
2. Tab to an item's checkbox. It reads the state (checked or not checked).
   Press Space and listen for the new state.
3. Tab to the text input after typing something. It reads what you typed.

Windows Narrator: Win+Ctrl+Enter turns it on, and the same keys turn it off.

macOS VoiceOver: Cmd+F5 turns it on, and the same keys turn it off. The first
time, a welcome dialog appears: choose "Use VoiceOver". If nothing is
announced, use VO+Right Arrow (VO is Control+Option) to move through the
window.

Note what is read, word for word, and anything not read.

## 7. What to send back

The `$HOME/vilan-hw/reports` folder (one report file per run). And these:

- One screenshot of each example at each scale factor you tried. Name them
  `<example>-<system>-<scale>.png`, for example `ui-windows-150.png`.
- This table, filled in. One line per thing that looked or behaved wrong; add
  rows as needed.

| System | Example | Backend | Scale(s) | Report saved | Looked right? | What went wrong (one line each) |
|---|---|---|---|---|---|---|
| Windows | gfx | dx12 | | | | |
| Windows | ui-counter | dx12 | | | | |
| Windows | ui | dx12 | | | | |
| Windows | ui-todo | dx12 | | | | |
| Windows | ui-notes | dx12 | | | | |
| Windows | ui-virtual-list | dx12 | | | | |
| Windows | ui-icons | dx12 | | | | |
| Windows | ui, ui-virtual-list | vulkan | | | | |
| Windows | ui, ui-virtual-list | gl | | | | |
| Windows | ui, ui-virtual-list | dx12, release | | | | |
| macOS | gfx | metal | | | | |
| macOS | ui-counter | metal | | | | |
| macOS | ui | metal | | | | |
| macOS | ui-todo | metal | | | | |
| macOS | ui-notes | metal | | | | |
| macOS | ui-virtual-list | metal | | | | |
| macOS | ui-icons | metal | | | | |
| macOS | ui, ui-virtual-list | metal, release | | | | |

Also note, once per system: the OS version (Windows: `winver`; macOS: Apple menu,
About This Mac), the GPU and its driver version, and the input method you tried.

## 8. Known limits: do not report these as findings

- No input-method composition. Typing through an IME is expected to fail (see
  4.4). What it does instead is still worth one line.
- One window per program. No menus, no dialogs, no file pickers.
- The system's text-size setting is ignored. Text follows the display's scale
  factor only, and the report says `text scale: 1`.
- Debug builds draw 5 to 10 times slower than release builds. Judge smoothness
  in the release pass.
- Fonts are the system's, so text differs from the reference images.
- Typing in a very long text in `ui-notes` is slow (F180).
- Closing the window cannot be refused by the program, and a stopped program
  prints no exit report if it is killed outright.

## The report, as it looks here

From `ui-counter` in debug, under xvfb on Mesa's software Vulkan. Your
adapter, backend, present modes, monitor and times will differ. The full file is
`~/.vilan/gates/hw-58/sample-report.txt`.

```text
--- vilan gfx report: start ---
window: 1
crate: vilan-rt-gfx 0.56.1 (debug build)
os: linux x86_64
WGPU_BACKEND: (unset)
WGPU_DEBUG: (unset)
adapter: llvmpipe (LLVM 19.1.7, 256 bits)
adapter vendor: 0x10005 (Mesa)
adapter device: 0x0000
adapter type: CPU (a software renderer)
backend: Vulkan
driver: llvmpipe
driver info: Mesa 25.0.7-2+deb13u1 (LLVM 19.1.7)
max texture side: 16384 (adapter 16384; the device asks WebGL2's limits, raised to the adapter's texture size)
surface format: Bgra8UnormSrgb (supported: Bgra8UnormSrgb, Bgra8Unorm)
present mode: AutoVsync (supported: Immediate, Mailbox, Fifo, FifoRelaxed)
alpha mode: Opaque (supported: Opaque, Inherit)
frame latency: 2 frames at most
surface size: 360x240 px
window inner size: 360x240 px
scale factor: 1
text scale: 1 (the system's text size setting is not read)
monitor: screen, 1280x1024 px, refresh unknown, scale factor 1
--- end ---
--- vilan gfx report: exit ---
run time: 1.2 s
frames presented: 12
...
interval: count 9, median 2951 us, p95 3368 us, max 3368 us (between presents); counted only between frames asked for back to back (...): 9 of 11 intervals
...
--- end ---
```

Lines that can appear while it runs, one per event:

```text
vilan gfx report: window 1 scale factor: 1.5 (inner size 1080x900 px; monitor ...)
vilan gfx report: window 1 surface: resized to 1024x768 px (resize 7)
vilan gfx report: window 1 surface: outdated (skipped, configured again) at 1024x768 px, 1 so far
```

How to read the times: they are wall time on the program's main thread, in
microseconds. `acquire` is where a frame waits for the display under vsync, so
on real hardware expect it near one refresh period when frames come back to
back. `interval` counts only frames asked for back to back, so an idle window
does not look slow.
