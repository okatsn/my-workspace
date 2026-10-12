#!/usr/bin/env bash
# Host-side check (devcontainer.json `initializeCommand`): fail before Docker starts
# if a Git-controlled Copilot source mounted by docker-compose.yml is missing or empty.
# Generated from preflight.sh.mustache by render.js; the instruction families come from `instruction_families` in data.json.
set -euo pipefail

ROOT="${HOME}/projects/my-agents/copilot"

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
