#!/usr/bin/env bash
# Host-side check (devcontainer.json `initializeCommand`): fail before Docker starts
# if a Git-controlled Copilot source mounted by docker-compose.yml is missing or empty.
# Generated from preflight.sh.mustache by render.js; the instruction families come from `instruction_families` in data.json.
set -euo pipefail

ROOT="${HOME}/projects/my-agents/copilot"


# - if `/tmp/shared` already exists as root:root, running mkdir -p -m 1777 /tmp/shared in preflight.sh silently does nothing.
# - `-m 1777` gives the folder sticky world-writable permissions—just like standard /tmp—so any container running under any UID (root, jovyan, vscode) can read and write to it without conflict.
# - Linux distros inside WSL2 only wipe /tmp when the WSL2 VM itself restarts (e.g., Windows reboot or wsl --shutdown).
# - If you are on native Linux or macOS, /tmp is wiped on every standard OS reboot as expected.
mkdir -p -m 1777 /tmp/shared
echo "/tmp/shared created (will wipe out on OS reboot)"


check() {
    local dir="$1" pattern="$2"
    if [[ ! -d "$dir" ]]; then
        echo "ERROR: missing directory: $dir" >&2
        exit 1
    fi
    if ! find "$dir" -name "$pattern" -print -quit | grep -q .; then
        echo "ERROR: no '$pattern' found in: $dir" >&2
        exit 1
    fi
}

check "$ROOT/agents" '*.agent.md'
for family in common julia typst logseq-dev-notes shell; do
    check "$ROOT/instructions/$family" '*.instructions.md'
done
check "$ROOT/skillsets/typst" 'SKILL.md'

echo "Copilot sources OK: $ROOT"

