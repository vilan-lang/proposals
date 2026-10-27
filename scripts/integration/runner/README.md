# The Linux CI runner (self-hosted, Docker)

What it is: one GitHub Actions runner in a container on the owner's machine, labelled
`vilan-linux`, that `ci.yml` routes the **ubuntu test legs** to for TRUSTED events only — a push
to `next`/`main`, or a pull request whose head repository is `vilan-lang/vilan` itself (Dependabot
included). A fork's PR never reaches it: it stays on `ubuntu-latest`. `perf` (its ceilings are
adopted on GitHub's runners) and `release.yml` (the publish secrets) stay GitHub-hosted.

## Start it (the owner; once)

```bash
cp .env.example .env            # then paste the registration token into .env
docker compose build
docker compose up -d
docker compose logs -f runner-1 # "Listening for Jobs" ends the first start
```

Repository setting to pair with it: Settings > Actions > General > "Fork pull request workflows
from outside collaborators" = **Require approval for all outside collaborators**. The routing
already keeps forks off the runner; the setting keeps them from spending GitHub minutes unasked.

## Then land the routing

`ci-routing.patch` beside this file is the `ci.yml` change (apply with `git apply` in the
integration worktree after the seal): the `changes` job gains a `trusted` output, the test job's
`runs-on` picks `vilan-linux` for trusted ubuntu legs, and the rust-cache step runs only on
GitHub-hosted runners (the container's `_work` keeps `target/` warm by itself).

## What to know

- The runner is NOT ephemeral: one container runs job after job, so `target/` and the npm cache
  carry over (that is the speed). The isolation is the container plus the routing; with forks kept
  off, only the repository's own code runs here.
- Caps: 8 CPUs, 12 GB. Both shards of an ubuntu leg queue on the one runner; uncomment `runner-2`
  in compose.yaml if that waits too long.
- The image pins `actions-runner:2.329.0`; the runner self-updates inside the container. To take a
  new base image: `docker compose build --pull && docker compose up -d` (the registration survives
  in the volume).
- To retire it: `docker compose down -v` after removing the runner on GitHub (Settings > Actions >
  Runners), or run `./config.sh remove --token <removal token>` inside the container first.
- Phase 2 (ruled 2026-10-05): a native Windows runner on the WSL host for the windows legs, after
  this one has proved out.

## When Docker Desktop itself is down (seen 2026-10-13, 2026-10-27)

`docker.exe` answers `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`
and `tasklist.exe` lists no `Docker Desktop.exe`. Launch it from WSL through PowerShell (a `cmd.exe /c start`
from a WSL cwd did NOT start it on 2026-10-27):

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command 'Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"'
```

The engine answers `docker.exe info` within ~10-20 s; the container came up on its own with the engine on
2026-10-27 (`docker.exe start vilan-runner-1` is harmless if it did), and `gh api repos/vilan-lang/vilan/actions/runners`
shows `vilan-linux-1 online` within a minute. The queued ubuntu legs then run.

## After a host reboot (seen 2026-10-08)

Docker Desktop came back but the container stayed `Exited (143)`: `restart: unless-stopped` was not
honoured across the reboot. Start it by hand, from WSL through the host CLI if this distro's
integration socket is missing:

```bash
"/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe" start vilan-runner-1
```

Then confirm on GitHub (Settings > Actions > Runners) that `vilan-linux-1` is online; queued ubuntu
legs pick up within a minute. If `docker` inside WSL says the socket is missing, re-enable this
distro under Docker Desktop > Settings > Resources > WSL integration.
