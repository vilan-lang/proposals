# The Windows CI runner (self-hosted, native, L24)

What it is: a GitHub Actions runner installed as a **Windows service on the host** of the WSL VM
(the Linux runner lives in Docker; this one runs natively because the windows legs need MSVC),
labelled `vilan-windows`. `ci.yml` routes the windows test shards of TRUSTED events to it, and
`release.yml` its windows gate and windows build, with the same rule as the Linux runner: a push to
`next`/`main`, or a pull request whose head repository is `vilan-lang/vilan`. A fork's PR stays on
`windows-latest`. macOS builds, the linux-arm build, `perf` and every publish job stay GitHub-hosted.

## Install (the owner; once, in an elevated PowerShell on the host)

1. Install the toolchain the script checks for: rustup (MSVC host), the Visual Studio Build Tools
   ("Desktop development with C++"), Node 24, Git for Windows, Python 3.12.
2. Get a registration token: vilan-lang/vilan > Settings > Actions > Runners > New self-hosted
   runner > Windows x64.
3. Run `install-runner.ps1 -Token <token>` (copy it to the host first, e.g. from
   `\\wsl$\<distro>\home\reed\code\vilan-lang\proposals\scripts\integration\runner\windows\`).
   It installs the runner under `C:\actions-runner` as a service (`--runasservice`), so it comes
   back after a reboot without any hand start.
4. Confirm `vilan-windows-1` shows online under Settings > Actions > Runners.

## Then land the routing

`ci-routing-windows.patch` beside this file changes `ci.yml`'s `runs-on` to pick `vilan-windows`
for trusted windows legs (the ubuntu rule already exists), and `release.yml`'s windows gate and
build the same way. Apply with `git apply` in the integration worktree once the runner is online.

## What to know

- Capacity: the host shares the machine with the WSL VM (30 GB of its memory). A windows shard
  builds the workspace once (~10 min cold) and runs a quarter of the suite; expect each shard to
  take 8-15 min against 16-34 on GitHub's runners, serially on one runner. Register a second
  (`-Name vilan-windows-2`, another `-Root`) if the four shards queue too long.
- The service's `_work` persists between jobs, so `target/` stays warm; the rust-cache step is
  GitHub-hosted only in both workflows.
- Updates: the runner self-updates. To move to a newer base version, stop the service, re-run the
  script with `-Version`.
- To retire: Settings > Actions > Runners > remove, then `.\config.cmd remove --token <removal token>`
  in `C:\actions-runner` and delete the folder.
