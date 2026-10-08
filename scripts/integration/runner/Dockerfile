# The vilan Linux CI runner: GitHub's runner image plus what `scripts/ci-local.sh test` needs.
# Built and run by compose.yaml; registered once by entrypoint.sh (the registration persists in
# a volume, so the one-hour token is used once). Rust is preinstalled so dtolnay/rust-toolchain
# only has to `rustup default`, and setup-node's downloads land in the tool-cache volume.
FROM ghcr.io/actions/actions-runner:2.329.0

USER root
# gawk: the cut script's CHANGELOG rewrite (scripts/cut-release.sh) emits doubled `---` separators
# under 22.04's mawk 1.3.4-20200120 (N152); GitHub's runners and the owner's box have a newer awk.
# The runner image is Ubuntu 22.04, whose python3 is 3.10; `scripts/perf_gate.py` and the release
# scripts read TOML with `tomllib` (3.11+), as GitHub's ubuntu-latest (24.04, Python 3.12) does.
# deadsnakes supplies 3.12; a shim ahead of /usr/bin makes it the `python3` the scripts find and
# leaves the system's 3.10 for apt.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential pkg-config libssl-dev git curl ca-certificates jq gawk software-properties-common \
 && add-apt-repository -y ppa:deadsnakes/ppa \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3.12 python3.12-venv \
 && ln -s /usr/bin/python3.12 /usr/local/bin/python3 \
 && rm -rf /var/lib/apt/lists/*

USER runner
ENV RUSTUP_HOME=/home/runner/.rustup CARGO_HOME=/home/runner/.cargo
ENV PATH=/home/runner/.cargo/bin:$PATH
# stable is what the suite legs build with (ci.yml `RUSTUP_TOOLCHAIN: stable`); the pinned
# channel is what rust-toolchain.toml would resolve to if a job forgot the env.
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable \
 && rustup toolchain install 1.98.1 --profile minimal -c rustfmt -c clippy \
 && cargo install cargo-nextest --locked

COPY --chown=runner:runner entrypoint.sh /home/runner/entrypoint.sh
RUN chmod +x /home/runner/entrypoint.sh
ENTRYPOINT ["/home/runner/entrypoint.sh"]
