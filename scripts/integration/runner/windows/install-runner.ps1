# The vilan Windows self-hosted runner (L24): installs the GitHub Actions runner as a Windows
# service on the host of the WSL VM, labelled `vilan-windows`, after checking the toolchain the
# windows legs need. Run in an elevated PowerShell:
#
#   .\install-runner.ps1 -Token <registration token>
#
# The token comes from GitHub: vilan-lang/vilan > Settings > Actions > Runners > New self-hosted
# runner > Windows x64 (it expires in one hour; the registration persists afterwards).
param(
  [Parameter(Mandatory = $true)] [string] $Token,
  [string] $Repo = "vilan-lang/vilan",
  [string] $Name = "vilan-windows-1",
  [string] $Root = "C:\actions-runner",
  [string] $Version = "2.329.0"
)
$ErrorActionPreference = "Stop"

# What the windows legs run: rustup with stable (the suite) and the pinned 1.98.1 (fmt/clippy),
# the MSVC build tools, Node 24 (setup-node installs its own copy into the tool cache, but the
# gate's npm steps want one on PATH), git, python 3.11+ (the release scripts' floor).
function Need($cmd, $hint) { if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "missing $cmd - $hint" } }
Need rustup "install from https://rustup.rs (choose the MSVC host)"
Need cargo  "rustup installs it"
Need cl     "install the Visual Studio Build Tools with the 'Desktop development with C++' workload and run this from a Developer PowerShell, or add the MSVC bin dir to PATH"
Need node   "install Node 24 (https://nodejs.org)"
Need git    "install Git for Windows"
Need python "install Python 3.12 (https://python.org) and tick 'add to PATH'"
$py = (python --version 2>&1) -replace 'Python ', ''
if ([version]$py -lt [version]'3.11') { throw "python $py is older than 3.11 (the release scripts' floor)" }
rustup toolchain install stable --profile minimal | Out-Null
rustup toolchain install 1.98.1 --profile minimal -c rustfmt -c clippy | Out-Null
if (-not (Get-Command cargo-nextest -ErrorAction SilentlyContinue)) { cargo install cargo-nextest --locked }

# The runner itself.
New-Item -ItemType Directory -Force -Path $Root | Out-Null
Set-Location $Root
$zip = "actions-runner-win-x64-$Version.zip"
if (-not (Test-Path $zip)) {
  Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v$Version/$zip" -OutFile $zip
}
if (-not (Test-Path ".\config.cmd")) {
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::ExtractToDirectory("$Root\$zip", $Root)
}
if (-not (Test-Path ".\.runner")) {
  .\config.cmd --unattended --replace --url "https://github.com/$Repo" --token $Token --name $Name --labels vilan-windows --work _work --runasservice
}
Write-Host "registered $Name with label vilan-windows; the service is installed and started."
Write-Host "check GitHub: Settings > Actions > Runners should show $Name online."
