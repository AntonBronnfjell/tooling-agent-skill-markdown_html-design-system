# Install html-design-system into Claude Code, Codex, Cursor, Copilot, Gemini CLI, Windsurf, Cline, Kiro, Roo, OpenCode, ...
#   .\install.ps1 [install.py options]                    from a clone (e.g. .\install.ps1 --tools all)
#   irm https://raw.githubusercontent.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system/main/install.ps1 | iex
# Note: without Windows Developer Mode, symlinks fall back to copies (re-run to update).
$ErrorActionPreference = "Stop"

$py = $null
foreach ($c in @("py", "python3", "python")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) {
    $args0 = if ($c -eq "py") { @("-3") } else { @() }
    & $c @args0 -c "import sys; sys.exit(sys.version_info < (3, 8))" 2>$null
    if ($LASTEXITCODE -eq 0) { $py = $c; $pyArgs = $args0; break }
  }
}
if (-not $py) { throw "Python 3.8+ is required (the skill's scripts need it too)." }

$dir = if ($PSScriptRoot) { $PSScriptRoot } else { "" }
$tmp = $null
if (-not $dir -or -not (Test-Path (Join-Path $dir "install.py"))) {
  if (-not $env:HDS_REPO) { $env:HDS_REPO = "https://github.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system.git" }
  $tmp = Join-Path ([IO.Path]::GetTempPath()) ("hds-" + [guid]::NewGuid())
  git clone -q --depth 1 $env:HDS_REPO $tmp 2>$null | Out-Null
  $dir = $tmp
}
try { & $py @pyArgs (Join-Path $dir "install.py") @args; exit $LASTEXITCODE }
finally { if ($tmp) { Remove-Item -Recurse -Force $tmp } }
