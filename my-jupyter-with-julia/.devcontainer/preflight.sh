#!/usr/bin/env bash
# Host-side check (devcontainer.json `initializeCommand`): print obvious warnings (without failing)
# if a Git-controlled Copilot source mounted by docker-compose.yml is missing or empty.
# Generated from preflight.sh.mustache by render.js; the families come from `instruction_families` and `skill_families` in data.json.
set -euo pipefail

ROOT="${HOME}/projects/my-agents/copilot"


# - if `/tmp/shared` already exists as root:root, running mkdir -p -m 1777 /tmp/shared in preflight.sh silently does nothing.
# - `-m 1777` gives the folder sticky world-writable permissions—just like standard /tmp—so any container running under any UID (root, jovyan, vscode) can read and write to it without conflict.
# - Linux distros inside WSL2 only wipe /tmp when the WSL2 VM itself restarts (e.g., Windows reboot or wsl --shutdown).
# - If you are on native Linux or macOS, /tmp is wiped on every standard OS reboot as expected.
mkdir -p -m 1777 /tmp/shared
echo "/tmp/shared created (will wipe out on OS reboot)"


WARNINGS=0

warn() {
    echo "" >&2
    echo "##########################################################" >&2
    echo "!!! WARNING: $1" >&2
    echo "##########################################################" >&2
    echo "" >&2
    WARNINGS=$((WARNINGS + 1))
}

check() {
    local dir="$1" pattern="$2"
    if [[ ! -d "$dir" ]]; then
        warn "missing directory: $dir"
    elif ! find "$dir" -name "$pattern" -print -quit | grep -q .; then
        warn "no '$pattern' found in: $dir"
    fi
}

check "$ROOT/agents" '*.agent.md'
for family in common julia quarto typst logseq-dev-notes shell; do
    check "$ROOT/instructions/$family" '*.instructions.md'
done
for family in common typst quarto julia dvc logseq; do
    check "$ROOT/skillsets/$family" 'SKILL.md'
done

if [[ "$WARNINGS" -gt 0 ]]; then
    echo "!!! $WARNINGS warning(s): some Copilot sources are missing or empty under $ROOT (continuing anyway)" >&2
else
    echo "Copilot sources OK: $ROOT"
fi

