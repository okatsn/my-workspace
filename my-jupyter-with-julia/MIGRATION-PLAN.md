# Migration plan

- [Migration plan](#migration-plan)
  - [Background Context](#background-context)
  - [Reviewed Plan](#reviewed-plan)
    - [Recommended structure](#recommended-structure)
    - [But `~/.copilot` also contains private/runtime data](#but-copilot-also-contains-privateruntime-data)
    - [If you clone directly to `~/.copilot`, use an allowlist `.gitignore`](#if-you-clone-directly-to-copilot-use-an-allowlist-gitignore)
    - [I would avoid making symlinks the foundation](#i-would-avoid-making-symlinks-the-foundation)
    - [Flattening your current `my-agents/*/agents` is also sensible](#flattening-your-current-my-agentsagents-is-also-sensible)
    - [Prompts need different treatment](#prompts-need-different-treatment)
    - [One subtle change from your investigation report](#one-subtle-change-from-your-investigation-report)
    - [My preferred migration](#my-preferred-migration)
    - [In other words](#in-other-words)
  - [Dev Containers setup](#dev-containers-setup)
    - [I would not make `~/.copilot` itself your Git repository](#i-would-not-make-copilot-itself-your-git-repository)
    - [For your Dev Container, I would change the Compose mounts](#for-your-dev-container-i-would-change-the-compose-mounts)
    - [Your read-only design is actually more valuable now](#your-read-only-design-is-actually-more-valuable-now)
    - [Your existing arbitrary mount will no longer be sufficient by itself](#your-existing-arbitrary-mount-will-no-longer-be-sufficient-by-itself)
    - [This also answers why Dev Containers still make sense](#this-also-answers-why-dev-containers-still-make-sense)
    - [One further change I'd make to your repository organization](#one-further-change-id-make-to-your-repository-organization)
    - [And prompts really should become skills](#and-prompts-really-should-become-skills)
    - [If you intend to use multiple harnesses](#if-you-intend-to-use-multiple-harnesses)
    - [So my recommendation for your setup](#so-my-recommendation-for-your-setup)
  - [Instruction Architecture](#instruction-architecture)
    - [The structure I would use](#the-structure-i-would-use)
    - [Think in three instruction scopes](#think-in-three-instruction-scopes)
    - [`applyTo` replaces a lot of the old manual selection](#applyto-replaces-a-lot-of-the-old-manual-selection)
    - [But `applyTo` does **not** replace your old project selector in every case](#but-applyto-does-not-replace-your-old-project-selector-in-every-case)
    - [I would use the container mounts as your new per-project selector](#i-would-use-the-container-mounts-as-your-new-per-project-selector)
    - [Use `applyTo` *inside* those selected sets too](#use-applyto-inside-those-selected-sets-too)
    - [I would be conservative with `description`](#i-would-be-conservative-with-description)
    - [Keep `~/.copilot/copilot-instructions.md` extremely small](#keep-copilotcopilot-instructionsmd-extremely-small)
    - [There is also an official environment-variable mechanism](#there-is-also-an-official-environment-variable-mechanism)
    - [Claude can follow essentially the same organization](#claude-can-follow-essentially-the-same-organization)
    - [Therefore I would slightly refine my previous recommendation](#therefore-i-would-slightly-refine-my-previous-recommendation)
  - [CHECKPOINT: Permission Handling for `~/.copilot` in the container setup](#checkpoint-permission-handling-for-copilot-in-the-container-setup)
  - [Docker-compose Architecture Refined and Explained](#docker-compose-architecture-refined-and-explained)
    - [1. Recommended architecture](#1-recommended-architecture)
    - [2. Recommended Docker Compose configuration](#2-recommended-docker-compose-configuration)
    - [3. What happens if `~/.copilot` doesn't exist?](#3-what-happens-if-copilot-doesnt-exist)
    - [4. Does the host username need to match `jovyan`?](#4-does-the-host-username-need-to-match-jovyan)
    - [5. Understanding `create_host_path: false`](#5-understanding-create_host_path-false)
    - [6. My recommended fail-fast verification](#6-my-recommended-fail-fast-verification)
    - [7. The subtle stale-instructions problem with named volumes](#7-the-subtle-stale-instructions-problem-with-named-volumes)
    - [8. When rebuilding or removing containers](#8-when-rebuilding-or-removing-containers)
    - [9. Final architecture recommendation](#9-final-architecture-recommendation)
  - [Docker-compose Architecture For Skill sets](#docker-compose-architecture-for-skill-sets)
    - [1. Why skills should be treated differently from instructions](#1-why-skills-should-be-treated-differently-from-instructions)
    - [2. Comparing the two approaches](#2-comparing-the-two-approaches)
    - [3. What I would implement in your `my-agent` repository](#3-what-i-would-implement-in-your-my-agent-repository)
    - [4. Docker Compose implementation](#4-docker-compose-implementation)
    - [5. When exposing all skills is preferable](#5-when-exposing-all-skills-is-preferable)
    - [6. Skill metadata matters more than aggressive filtering](#6-skill-metadata-matters-more-than-aggressive-filtering)
    - [7. How I would validate the arrangement](#7-how-i-would-validate-the-arrangement)
    - [Final recommendation for your architecture](#final-recommendation-for-your-architecture)



## Background Context

In VSCode 1.140, the local agent settings ("chat.agentSkillsLocations", "chat.instructionsFilesLocations", "chat.promptFilesLocations", "chat.agentFilesLocations") seems to be going to be deprecated. I got the message "This setting and the Local agent harness will be removed in a future release. Here is the investigation report for the latest structure so far in below. Currently, `my-agent` is tracked as a standalone github repo `okatsn/my-agent`, because I need version control for these text files. The question is, is it a good idea that I simply move all `my-agents/*/agents/*.md` (as well as the instructions) to a new repo named `okatsn/.copilot` instead and clone the ".copilot" folder to `~/`? Is this a good solution for migration (not only migrate local, but also tracked by git)?

```markdown
Read 
Completed with input: {
  "path": "/home/okatsn/projects/ProjectTIPTree/.vscode/settings.json"
}

Search Tools

Search code
Completed with input: {
  "query": "Local agent harness will be removed in a future release repo:microsoft/vscode"
}

Search issues
Completed with input: {
  "query": "Local agent harness removed migrations tab agent customizations",
  "owner": "microsoft",
  "repo": "vscode"
}

Ran terminal command: cd /tmp; jq -r '.items[]|"\(.path) \(.text_matches[0].fragment|.[0:300]|gsub("\n";" "))"' 1791346965956-copilot-tool-output-8ea02a1fbf8f45b19f50b9ca9ddc827a.txt; echo ----; jq -r '.items[:15][]|"#\(.number) \(.state) \(.title)"' 1791346967522-copilot-tool-output-835563a4731246ef9c9377fe3ed52ded.txt

Get issue details
Completed with input: {
  "method": "get",
  "owner": "microsoft",
  "repo": "vscode",
  "issue_number": 328121
}

Get issue details
Completed with input: {
  "method": "get",
  "owner": "microsoft",
  "repo": "vscode",
  "issue_number": 335654
}

Get issue details
Completed with input: {
  "method": "get",
  "owner": "microsoft",
  "repo": "vscode",
  "issue_number": 340074
}

Search code
Completed with input: {
  "query": "\"Local agent harness\" removed deprecationMessage repo:microsoft/vscode path:src/vs/workbench/contrib/chat"
}

Search code
Completed with input: {
  "query": "migrations customization editor local harness migrate repo:microsoft/vscode"
}

Get issue details
Completed with input: {
  "issue_number": 340074,
  "method": "get_comments",
  "owner": "microsoft",
  "repo": "vscode"
}

Get issue details
Completed with input: {
  "issue_number": 335654,
  "method": "get_comments",
  "owner": "microsoft",
  "repo": "vscode"
}

Ran terminal command: cd /tmp; jq -r '.items[]|.path' 1791346985976-copilot-tool-output-cc3a1807c37142578c1bdd38afb61760.txt

Get file or directory contents
Completed with input: {
  "owner": "microsoft",
  "repo": "vscode",
  "path": "extensions/copilot/assets/prompts/skills/migrate-customizations/references/migration-techniques.md"
}

Get file or directory contents
Completed with input: {
  "owner": "microsoft",
  "repo": "vscode",
  "path": "extensions/copilot/assets/prompts/skills/migrate-customizations"
}

Get file or directory contents
Completed with input: {
  "owner": "microsoft",
  "path": "extensions/copilot/assets/prompts/skills/migrate-customizations/SKILL.md",
  "repo": "vscode"
}

Search code
Completed with input: {
  "query": "COPILOT_USER_AGENTS_SOURCE_FOLDER repo:microsoft/vscode path:src/vs/workbench/contrib/chat/common/promptSyntax"
}

Ran terminal command: cd /tmp; sed -n 1,400p 1791347001230-copilot-tool-output-5657939f8aec4a13b4f70c1b3ec78dcc.txt | cut -c1-900

Get file or directory contents
Completed with input: {
  "owner": "microsoft",
  "path": "src/vs/workbench/contrib/chat/common/promptSyntax/config/promptFileLocations.ts",
  "repo": "vscode"
}

Read 
Completed with input: {
  "path": "/tmp/1791347001230-copilot-tool-output-5657939f8aec4a13b4f70c1b3ec78dcc.txt"
}

Search for `SOURCE_FOLDER|\.copilot|\.claude|\.agents`

Ran terminal command: cd /tmp; sed -n 12,200p 1791347001230-copilot-tool-output-5657939f8aec4a13b4f70c1b3ec78dcc.txt | cut -c1-700

Read tool output
Completed with input: {
  "path": "/tmp/1791347012951-copilot-tool-output-752183-a2f11b46-a27e-4e59-954e-3fc37e975f23.txt",
  "view_range": [
    1,
    120
  ]
}

Search code
Completed with input: {
  "query": "markdownDeprecationMessage migrationsTabLink repo:microsoft/vscode path:chat.shared.contribution.ts"
}

Ran terminal command: cd /tmp; curl -s https://raw.githubusercontent.com/microsoft/vscode/main/src/vs/workbench/contrib/chat/browser/chat.shared.contribution.ts | grep -n -E "migrationsTabLink|deprecated'|PromptsConfig\.[A-Z_]+_LOCATION_KEY\]" | cut -c1-420

Ran terminal command: cd /tmp; curl -s https://raw.githubusercontent.com/microsoft/vscode/main/src/vs/workbench/contrib/chat/browser/chat.shared.contribution.ts | sed -n '1970,1990p;2069,2085p;2181,2195p' | cut -c1-600

**Short answer:** No. Moving files under `~/.config/Code/User` would not complete the migration, and it is the location the new design excludes.

## What's changing

VS Code is replacing the old **Local agent harness** with Agent Host harnesses such as Copilot CLI. A harness is the runtime that loads your agents, skills and instructions.

From the current `microsoft/vscode` source (`chat.shared.contribution.ts`, `promptFileLocations.ts`, the `migrate-customizations` skill):

- **Setting descriptions:** `chat.agentFilesLocations`, `chat.instructionsFilesLocations` and `chat.agentSkillsLocations` now say they are "only observed by the Local agent harness". Other harnesses receive files from these extra locations in addition to their built-in ones.
- **Removal notice:** The "will be removed in a future release" text is on `chat.promptFilesLocations` and the legacy `chat.modeFilesLocations`. The migration guidance for the other three says custom locations "can continue to work" when another harness is connected. Moving files is a portability improvement, "not automatically required".
- **User data folder:** The profile folder is `~/.config/Code/User/prompts`. The migration docs say Agent Host "doesn't read the VS Code profile user data folder" and that it is Local-only. This matches the bug report in #340074, where agents in `AppData/Roaming/Code/User/prompts` disappeared.

## Where files should go now

| Type | Workspace | User-level (Copilot CLI harness) |
|---|---|---|
| Agents (`*.agent.md`) | `.github/agents`, `.claude/agents` | `~/.copilot/agents`, `~/.claude/agents` |
| Instructions | `.github/instructions`, `.claude/rules` | `~/.copilot/instructions`, `~/.claude/rules` |
| Skills (`<name>/SKILL.md`) | `.github/skills`, `.claude/skills`, `.agents/skills` | `~/.copilot/skills`, `~/.agents/skills`, `~/.claude/skills` |
| Prompts (`*.prompt.md`) | not supported by Agent Host harnesses | convert each one to a skill |
| Hooks | `.github/hooks` | `~/.copilot/hooks` |

The authoritative destinations are the ones the Migrations tab reports for your selected harness. Treat the table as a guide.

## What it means for your settings

- **`chat.promptFilesLocations`:** This is the one with a real deadline. Convert `general/prompts` and `markdown/prompts` into skills, such as `my-agents/general/skills/<name>/SKILL.md`. Add `disable-model-invocation: true` if a prompt should only run when you invoke it.
- **Agents and instructions in `my-agents`:** These will keep working through the settings for now. For a durable setup, symlink or copy them into the user folders (for example `~/.copilot/agents`). That keeps `my-agents` as the git source, and you would then drop the settings.
  - **Symlinks:** I haven't checked that the harness follows symlinks. Test that the files appear in the Agent Customizations editor.
  - **Sync:** The harness user folders might not take part in Settings Sync. Your git repo already covers that.
- **Skills:** The same applies, with `~/.copilot/skills` or `~/.agents/skills` as targets.
- **Tool names:** Front-matter `tools:` lists may not be valid for the new harness (#328121, open). Check migrated agents.
- **Instruction files in a shared folder:** Make sure each subfolder exists in the target folder with the exact name. For example, `~/.copilot/instructions` takes your four instruction folders' contents.

## Suggested next step

Open the **Migrations** entry in the Agent Customizations editor and use **Migrate with Agent**. It makes a backup bundle, asks before each group, and treats copying files, deleting sources and clearing settings as separate approvals. It looks like it was designed for exactly your case.

Some migration UX details are still open (#335654, #334567). The Migrations tab and docs are changing quickly, so re-check them on your VS Code build.

```


## Reviewed Plan

Yes, the **direction is correct**: move your personal agents/instructions/skills into the harness-native `~/.copilot/...` structure and stop depending on the VS Code `chat.*FilesLocations` settings. VS Code's current documentation now explicitly marks those settings deprecated and says Agent Host sessions use the harness's own locations instead. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/overview.md?utm_source=chatgpt.com)

I would change one part of your proposal, though: **don't treat the entirety of `~/.copilot` as an ordinary dotfiles repository unless you carefully allowlist what Git tracks.**

### Recommended structure

Your idea can work nicely as:

```text
~/.copilot/                       # git checkout: github.com/okatsn/.copilot
├── .git/
├── .gitignore
│
├── agents/
│   ├── foo.agent.md
│   ├── bar.agent.md
│   └── ...
│
├── instructions/
│   ├── general.instructions.md
│   ├── markdown.instructions.md
│   └── ...
│
├── skills/
│   ├── some-skill/
│   │   └── SKILL.md
│   └── ...
│
└── copilot-instructions.md       # optional global always-on instructions
```

These are now first-class supported personal locations:

| Customization          | Personal location                              |
| ---------------------- | ---------------------------------------------- |
| Agents                 | `~/.copilot/agents/*.agent.md`                 |
| Modular instructions   | `~/.copilot/instructions/**/*.instructions.md` |
| Always-on instructions | `~/.copilot/copilot-instructions.md`           |
| Skills                 | `~/.copilot/skills/<skill>/SKILL.md`           |

That matches both current VS Code Agent Host documentation and GitHub's Copilot CLI documentation. [Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions?utm_source=chatgpt.com)

So conceptually, this migration:

```text
my-agent/
├── general/
│   ├── agents/*.agent.md
│   └── instructions/*.instructions.md
├── markdown/
│   ├── agents/*.agent.md
│   └── instructions/*.instructions.md
...
```

→

```text
~/.copilot/
├── agents/
│   └── *.agent.md
├── instructions/
│   └── *.instructions.md
└── skills/
    └── */
        └── SKILL.md
```

is exactly where I would head.

### But `~/.copilot` also contains private/runtime data

This is the significant catch.

Current Copilot CLI documentation says the same directory also contains things such as:

```text
~/.copilot/
├── config.json
├── ide/
├── installed-plugins/
├── logs/
├── mcp-config.json
├── mcp-oauth-config/
├── mcp-secrets/
├── permissions-config.json
├── plugin-data/
├── session-state/
├── session-store.db
├── settings.json
└── ...
```

Some of that is generated state; some can contain authentication/configuration/security-sensitive information. [GitHub](https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-config-dir-reference.md?utm_source=chatgpt.com)

Therefore this would be a bad pattern:

```bash
cd ~/.copilot
git add .
git commit
```

You could accidentally version things that absolutely should not live in `okatsn/.copilot`.

### If you clone directly to `~/.copilot`, use an allowlist `.gitignore`

For example:

```gitignore
# Ignore everything by default
*

# Repository metadata/config
!.gitignore
!README.md

# Personal Copilot customizations
!agents/
!agents/**

!instructions/
!instructions/**

!skills/
!skills/**

# Optional always-on global instructions
!copilot-instructions.md
```

That gives you an important property:

```text
~/.copilot/
├── agents/                 tracked
├── instructions/           tracked
├── skills/                 tracked
├── copilot-instructions.md tracked
│
├── logs/                   ignored
├── session-state/          ignored
├── session-store.db        ignored
├── config.json             ignored
├── permissions-config.json ignored
├── mcp-secrets/            ignored
└── ...
```

With that safeguard, **cloning `okatsn/.copilot` directly as `~/.copilot` is a reasonable solution**.

I would actually prefer it to symlinking every customization into `~/.copilot`.

### I would avoid making symlinks the foundation

Your investigation report correctly expressed uncertainty here.

There is currently an open Copilot CLI issue specifically asking GitHub to document/support symlinks for this dotfiles use case. [GitHub](https://github.com/github/copilot-cli/issues/3264?utm_source=chatgpt.com) More importantly, there's also a reported bug where skills whose individual directories are symlinks under `~/.copilot/skills` were **not discovered**, while real directories were. [GitHub](https://github.com/github/copilot-cli/issues/1021?utm_source=chatgpt.com)

GitHub documentation explicitly discusses following a symlink for `~/.copilot/settings.json`, but does not give the same guarantee for agents/instructions/skills. [GitHub](https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-config-dir-reference.md?utm_source=chatgpt.com)

So I wouldn't choose:

```text
~/my-agent/skills/foo
        ↓ symlink
~/.copilot/skills/foo
```

as the long-term architecture right now.

A **real Git checkout at `~/.copilot`** avoids that uncertainty.

### Flattening your current `my-agents/*/agents` is also sensible

Suppose today you have:

```text
my-agents/
├── general/
│   ├── agents/
│   │   └── general.agent.md
│   └── instructions/
│       └── general.instructions.md
├── markdown/
│   ├── agents/
│   │   └── markdown.agent.md
│   └── instructions/
│       └── markdown.instructions.md
```

I would turn that into:

```text
.copilot/
├── agents/
│   ├── general.agent.md
│   └── markdown.agent.md
└── instructions/
    ├── general.instructions.md
    └── markdown.instructions.md
```

rather than trying to preserve:

```text
.copilot/
└── general/
    └── agents/
```

The harness's documented discovery root is specifically:

```text
~/.copilot/agents
```

and the analogous instruction root is:

```text
~/.copilot/instructions
```

Instructions can explicitly be organized recursively beneath that directory, so this is fine if you want grouping:

```text
~/.copilot/instructions/
├── general/
│   └── style.instructions.md
├── markdown/
│   └── markdown.instructions.md
└── typescript/
    └── typescript.instructions.md
```

VS Code documents recursive discovery for these instruction directories. [Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions?utm_source=chatgpt.com)

For agents, I would keep them directly under `agents/` unless/until nested-agent discovery is explicitly documented.

### Prompts need different treatment

This part of your earlier investigation remains important:

```text
*.prompt.md
```

should **not simply be copied to `~/.copilot/prompts`**.

The current direction is explicitly to migrate prompt files to skills. VS Code's migration documentation says prompt files from `chat.promptFilesLocations` aren't handled as ordinary moved customizations; use the prompt-file migration to convert them to skills. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/overview.md?utm_source=chatgpt.com)

So something like:

```text
my-agents/general/prompts/release.prompt.md
```

should become approximately:

```text
~/.copilot/skills/release/
└── SKILL.md
```

Potentially with supporting files alongside the `SKILL.md`.

GitHub currently documents personal skills as:

```text
~/.copilot/skills/<name>/SKILL.md
```

and also supports `~/.agents/skills`. [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills?plain=1\&utm_source=chatgpt.com)

### One subtle change from your investigation report

Your report says agents/instructions/skills custom-location settings "can continue to work" for another harness.

The current documentation has become stronger since that material was collected. VS Code now explicitly says:

> these settings are deprecated because Agent Host sessions don't use them

for the location migration flow, and its agent/instruction documentation says the settings are deprecated and **only used by the Local agent**. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/overview.md?utm_source=chatgpt.com)

So I would no longer architect around:

```json
"chat.agentFilesLocations": {...},
"chat.instructionsFilesLocations": {...},
"chat.agentSkillsLocations": {...}
```

at all.

Your Git repository should become your synchronization mechanism instead.

### My preferred migration

I would therefore do essentially this:

```bash
# Preserve old repo first
mv ~/path/to/my-agent ~/path/to/my-agent.backup

# Clone the new canonical repository into the native location
git clone git@github.com:okatsn/.copilot.git ~/.copilot
```

and keep **only these categories tracked**:

```text
agents/
instructions/
skills/
copilot-instructions.md   # if you have global instructions
README.md
.gitignore
```

Then your workflow on another machine becomes very simple:

```bash
git clone git@github.com:okatsn/.copilot.git ~/.copilot
```

Copilot/VS Code can create their runtime files around the checkout, and Git ignores them.

There is no extra VS Code location configuration, no copy script, and no dependency on undocumented symlink behavior.

### In other words

**Yes — `okatsn/.copilot` cloned to `~/.copilot` is a good migration architecture, provided you treat the repository as an allowlisted subset of `~/.copilot`, not as a repository containing everything Copilot puts there.**

I would rank the options:

1. **`~/.copilot` is the Git checkout + strict allowlist `.gitignore`** ← simplest and what I'd use.
2. Separate Git repo + copy/deploy script into `~/.copilot` ← safest separation, but more maintenance.
3. Separate Git repo + symlinks ← elegant, but currently less robust because symlink behavior isn't fully documented and there have been skill-discovery problems. [GitHub](https://github.com/github/copilot-cli/issues/3264?utm_source=chatgpt.com)

And importantly, this isn't merely a workaround for VS Code 1.140. It aligns your repository layout with the **Copilot Agent Host/CLI's native user customization structure**, which is much more likely to survive removal of the Local harness than keeping `my-agent` plus VS Code-specific location settings.

## Dev Containers setup

Yes — **keep the “one Git-controlled agent repository on the host, mounted read-only into every Dev Container” architecture.** That part of your design is still a very good fit for the Agent Host model.

What should change is **where you mount it**.

I would **not** clone a Git repo directly as `~/.copilot`. Instead, keep Git source and Copilot runtime state separate, and mount only the Git-controlled customization directories into the standard locations that the Copilot harness discovers.


### I would not make `~/.copilot` itself your Git repository

A repository named `okatsn/.copilot` is fine as a GitHub repository name. What I would avoid is:

```text
git clone git@github.com:okatsn/.copilot.git ~/.copilot
```

The reason is that `~/.copilot` isn't just a customization directory anymore. GitHub Copilot CLI uses it for both user-editable customizations **and runtime/application state**, including things such as:

```text
~/.copilot/
├── agents/                    # yours
├── instructions/              # yours
├── skills/                    # yours
├── copilot-instructions.md    # yours
│
├── config.json                # managed state/auth
├── settings.json
├── permissions-config.json
├── session-state/
├── session-store.db
├── command-history-state/
├── logs/
├── ide/
├── installed-plugins/
├── plugin-data/
└── ...
```

GitHub explicitly describes `~/.copilot` as containing configuration, session history, logs, application state, permissions, authentication information, and customizations. On systems without an appropriate credential store, credentials can even fall back to `~/.copilot/config.json`. [GitHub](https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-config-dir-reference.md?utm_source=chatgpt.com)

So technically you *could* put `.git` there and aggressively `.gitignore` everything except agents/instructions/skills, but it creates an unnecessary risk of accidentally committing runtime state or credentials.

A cleaner separation is:

```text
~/projects/my-agents/       <-- Git repository, durable source of truth

~/.copilot/                 <-- runtime/application directory
```

and expose selected portions of the first as selected portions of the second.

### For your Dev Container, I would change the Compose mounts

For example, reorganize your Git repo roughly as:

```text
my-agents/
├── copilot/
│   ├── agents/
│   │   ├── planner.agent.md
│   │   ├── reviewer.agent.md
│   │   └── ...
│   ├── instructions/
│   │   ├── julia.instructions.md
│   │   ├── python.instructions.md
│   │   └── ...
│   ├── skills/
│   │   ├── some-skill/
│   │   │   └── SKILL.md
│   │   └── ...
│   └── copilot-instructions.md
│
└── ...
```

Then replace the arbitrary mount:

```yaml
- ~/projects/my-agents:/home/jovyan/projects/my-agents:ro
```

with native-location mounts such as:

```yaml
volumes:
  - ..:/home/jovyan/workspace

  # Git-controlled Copilot custom agents
  - ${HOME}/projects/my-agents/copilot/agents:/home/jovyan/.copilot/agents:ro

  # Git-controlled personal instructions
  - ${HOME}/projects/my-agents/copilot/instructions:/home/jovyan/.copilot/instructions:ro

  # Optional always-on personal instructions
  - ${HOME}/projects/my-agents/copilot/copilot-instructions.md:/home/jovyan/.copilot/copilot-instructions.md:ro

  # Your own skills
  - ${HOME}/projects/my-agents/copilot/skills:/home/jovyan/.copilot/skills:ro

  # Third-party / off-the-shelf skills
  - ${HOME}/ai-skills:/home/jovyan/.agents/skills:ro
```

Copilot officially supports user skills in either `~/.copilot/skills` or `~/.agents/skills`, so your separate `ai-skills` repository maps especially nicely to `~/.agents/skills`. [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills?utm_source=chatgpt.com)

I slightly prefer `${HOME}` over `~` in Compose configuration because it makes the host-side expansion explicit.

The important detail is that **you do not mount `/home/jovyan/.copilot` itself read-only**. Only the customization subdirectories are read-only. Copilot remains free to maintain its writable state elsewhere underneath `.copilot`.

### Your read-only design is actually more valuable now

Your current security boundary makes sense:

```text
host Git repo
       │
       │ :ro
       ▼
Dev Container
       │
       ▼
Agent Host
```

The Agent Host documentation explicitly emphasizes that a Dev Container is an execution boundary: tools, file edits, and commands run inside the container. It also warns that whatever host paths you mount into that container form part of the effective security boundary. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agents/concepts/agent-host.md?utm_source=chatgpt.com)

So retaining:

```yaml
:ro
```

for your agent/instruction/skill repositories is a good idea.

It gives you a useful property:

> The agent can **consume its operating instructions**, but cannot silently rewrite the canonical instructions that govern future sessions.

If you intentionally want an agent to edit an agent/skill definition, you'd edit the host repo yourself or temporarily provide a writable workflow rather than making that capability available to every session.

One caveat is that a skill whose script expects to write files into its own skill directory will fail with a read-only mount. I would design skills to put temporary/output files in the workspace or `/tmp`, not next to `SKILL.md`.

### Your existing arbitrary mount will no longer be sufficient by itself

This is the major practical migration point.

Today you have:

```yaml
- ~/projects/my-agents:/home/jovyan/projects/my-agents:ro
- ~/ai-skills:/home/jovyan/ai-skills:ro
```

With the Local harness, you could then tell VS Code:

```json
"chat.agentFilesLocations": {
    "/home/jovyan/projects/my-agents/...": true
}
```

With Agent Host, that arbitrary path is no longer the normal discovery mechanism. The current docs explicitly say these settings are deprecated and only used by Local. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agents/reference/ai-settings.md?utm_source=chatgpt.com)

So merely making this available:

```text
/home/jovyan/projects/my-agents
```

doesn't mean the Copilot harness will discover it.

Make it appear as:

```text
/home/jovyan/.copilot/agents
/home/jovyan/.copilot/instructions
/home/jovyan/.copilot/skills
```

instead.

For skills and instructions, Copilot CLI does have additional mechanisms such as `COPILOT_SKILLS_DIRS` and `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, but I would not make those the foundation of this setup. Standard locations are simpler, work naturally with VS Code's customization UI, and avoid another layer of configuration. [GitHub](https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-command-reference.md?utm_source=chatgpt.com)

### This also answers why Dev Containers still make sense

You don't need to rethink your "human and agent should see exactly the same development environment" philosophy.

In fact, the new architecture formalizes it.

VS Code describes an Agent Host Dev Container session as one where:

```text
VS Code desktop
      │
      │ Agent Host Protocol
      ▼
Agent Host
inside Dev Container
      │
      ├── shell
      ├── compiler/interpreter
      ├── Python packages
      ├── Julia packages
      ├── Git
      └── workspace filesystem
```

So your PyDrive2 example is exactly the sort of problem Dev Container Agent Host sessions are intended to eliminate: the agent's commands execute using the dependencies inside the same containerized development environment. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agents/concepts/agent-host.md?utm_source=chatgpt.com)

This is therefore still a sound architecture:

```text
                         Host
 ┌─────────────────────────────────────────────┐
 │                                             │
 │ ~/projects/my-agents        Git controlled │
 │ ~/ai-skills                 Git controlled │
 │                                             │
 └──────────────────┬──────────────────────────┘
                    │ read-only bind mounts
                    ▼
            Dev Container for Project A
 ┌─────────────────────────────────────────────┐
 │ /home/jovyan/.copilot/agents                │
 │ /home/jovyan/.copilot/instructions          │
 │ /home/jovyan/.copilot/skills                │
 │ /home/jovyan/.agents/skills                 │
 │                                             │
 │ /home/jovyan/workspace  ← Project A         │
 │                                             │
 │        Copilot Agent Host runs here         │
 └─────────────────────────────────────────────┘

                    same sources
                         │
                         ▼
            Dev Container for Project B
```

That scales nicely to your tens of projects. You still have **one checkout, one update point, one Git history**, and every container receives the same version.

### One further change I'd make to your repository organization

I would separate **personal/global policy** from **project policy**.

Your shared `my-agents` repository should contain things genuinely applicable across projects:

```text
my-agents/
    copilot/
        agents/
        instructions/
        skills/
```

But anything that describes *ProjectTIPTree specifically* should live in that project's own repository:

```text
ProjectTIPTree/
├── .github/
│   ├── copilot-instructions.md
│   ├── agents/
│   ├── instructions/
│   └── skills/
└── ...
```

That maps cleanly onto Copilot's model: user-level customizations live under `~/.copilot`, while repository-level customizations live under `.github`. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/custom-agents.md?utm_source=chatgpt.com)

It also prevents an instruction intended for one project from unintentionally influencing another.

### And prompts really should become skills

For your current:

```text
my-agents/*/prompts/*.prompt.md
```

don't try to recreate a `~/.copilot/prompts` hierarchy.

Agent Host doesn't load prompt files. VS Code's current migration guidance explicitly says to convert them into skills. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/prompt-files.md?utm_source=chatgpt.com)

So conceptually:

```text
before

general/prompts/release.prompt.md
```

becomes something like:

```text
after

copilot/skills/release/
└── SKILL.md
```

and then arrives in the container as:

```text
/home/jovyan/.copilot/skills/release/SKILL.md
```

or under `~/.agents/skills`.

### If you intend to use multiple harnesses

This is the only area where I would avoid making your Git repository itself Copilot-specific.

The new framework separates **execution environment** from **harness**. The same Dev Container can run Copilot, Claude, Codex, etc., but each harness can have its own customization locations and semantics. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agents/run/agent-harnesses.md?utm_source=chatgpt.com)

If you anticipate that, I would call the source repo something generic such as:

```text
okatsn/agent-config
```

or keep:

```text
okatsn/my-agent
```

and organize it as:

```text
my-agent/
├── copilot/
│   ├── agents/
│   ├── instructions/
│   └── skills/
│
├── claude/
│   ├── agents/
│   └── rules/
│
└── shared/
    └── skills/
```

Then Compose determines how those canonical sources are projected into a particular harness's native filesystem.

For genuinely portable skills, `~/.agents/skills` is especially attractive because Copilot explicitly supports that convention. For repository instructions that need to work across multiple compatible agents, `AGENTS.md` is another increasingly portable format. [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills?utm_source=chatgpt.com)

### So my recommendation for your setup

I would **keep `okatsn/my-agent` as the Git source of truth**. There's no architectural reason to rename the repository `.copilot`.

Then change the deployment model from:

```text
mount repo somewhere
+
tell VS Code where it is
```

to:

```text
mount selected repo directories
directly into the harness's standard locations
```

In other words:

```text
OLD

~/projects/my-agents
       ↓
/home/jovyan/projects/my-agents
       ↓
chat.*FilesLocations
       ↓
Local harness
```

becomes:

```text
NEW

~/projects/my-agents
       ↓
read-only bind mount
       ↓
/home/jovyan/.copilot/{agents,instructions,skills}
       ↓
Copilot Agent Host
```

**That is the migration I would use for your environment.**

It preserves the best parts of your current setup—Git history, one checkout shared by tens of projects, read-only protection, and identical human/agent execution environments—while removing the deprecated VS Code-specific discovery layer.

## Instruction Architecture

No—**do not flatten your instruction files**. In VS Code 1.140, nested instruction directories are explicitly supported and are actually a good organizational pattern. VS Code searches both `.github/instructions/**/*.instructions.md` and `~/.copilot/instructions/**/*.instructions.md` recursively. [Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions?utm_source=chatgpt.com)

What changes is **how you select which instructions are active**. The old `chat.instructionsFilesLocations` gave VS Code a list of directories. With Agent Host, selection is better thought of as a combination of **scope + activation rules + what you expose to that container**.

### The structure I would use

Your central repository can stay hierarchical:

```text
my-agent/
├── copilot/
│   ├── agents/
│   ├── instructions/
│   │   ├── common/
│   │   │   ├── general.instructions.md
│   │   │   └── git.instructions.md
│   │   ├── python/
│   │   │   ├── python.instructions.md
│   │   │   └── pytest.instructions.md
│   │   ├── julia/
│   │   │   └── julia.instructions.md
│   │   ├── latex/
│   │   │   └── latex.instructions.md
│   │   ├── dvc/
│   │   │   └── dvc.instructions.md
│   │   └── project-specific/
│   │       └── ...
│   └── skills/
│
├── claude/
│   ├── agents/
│   └── rules/
│       ├── common/
│       ├── python/
│       ├── julia/
│       └── latex/
│
└── shared/
    └── skills/
```

There is no benefit to transforming that into:

```text
instructions/
├── common-general.instructions.md
├── common-git.instructions.md
├── python-python.instructions.md
├── python-pytest.instructions.md
├── julia-julia.instructions.md
...
```

The current documentation even gives nested `frontend/`, `backend/`, and `testing/` directories as an intended organization. [GitHub](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/custom-instructions.md?utm_source=chatgpt.com)

### Think in three instruction scopes

For Copilot, I'd use this model:

| Kind                           | Location inside container                                              | Purpose                                              |
| ------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------- |
| Truly universal personal rules | `~/.copilot/copilot-instructions.md`                                   | Always applicable everywhere                         |
| Reusable targeted rules        | `~/.copilot/instructions/**/*.instructions.md`                         | Language/tool/task rules shared across projects      |
| Project-owned rules            | `<repo>/.github/copilot-instructions.md` and `.github/instructions/**` | Architecture/conventions specific to that repository |

VS Code's current guidance is specifically to store instructions at the **narrowest appropriate scope**. [Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions?utm_source=chatgpt.com)

So, for example, I would **not** put this in your global repository:

```text
"ProjectTIPTree stores generated trees under src/output and
the main Julia module is TIPTree.jl."
```

That belongs in:

```text
ProjectTIPTree/.github/copilot-instructions.md
```

But something like:

```text
"When editing Julia, use JuliaFormatter conventions and
run Aqua.jl checks where available."
```

is a good candidate for:

```text
my-agent/copilot/instructions/julia/quality.instructions.md
```

---

### `applyTo` replaces a lot of the old manual selection

A reusable instruction can restrict itself:

```markdown
---
name: Julia conventions
description: Conventions for editing Julia source files.
applyTo: "**/*.jl"
---

# Julia conventions

- Follow ...
- Prefer ...
```

The important distinction is that **discovered does not necessarily mean automatically inserted into every request**.

For Copilot `.instructions.md` files:

- `applyTo` automatically activates the instruction when the agent works on matching files.
- `description` allows the agent to recognize that an instruction is relevant to a task.
- If both are absent, the file can be manually attached instead.

`applyTo` is relative to the workspace root. [Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions?utm_source=chatgpt.com)

So this:

```text
~/.copilot/instructions/
├── python/python.instructions.md       applyTo: **/*.py
├── julia/julia.instructions.md         applyTo: **/*.jl
└── latex/latex.instructions.md         applyTo: **/*.tex
```

is completely reasonable.

You can expose all three without automatically injecting Julia rules while editing Python.

---

### But `applyTo` does **not** replace your old project selector in every case

This is the important part for your setup.

Suppose you have:

```text
instructions/
├── python-scientific/
│   └── python.instructions.md
└── python-web/
    └── python.instructions.md
```

and both contain:

```yaml
applyTo: "**/*.py"
```

but their recommendations conflict.

If you expose both to Copilot, **both can become applicable**.

Current GitHub documentation explicitly says that multiple applicable instructions are combined and there is no general conflict-precedence mechanism you should depend on. It recommends avoiding conflicting instructions. [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions?utm_source=chatgpt.com)

So don't try to emulate:

```text
Project A → Python policy A
Project B → Python policy B
```

using `applyTo` alone.

That's where your Dev Container architecture becomes especially useful.

---

### I would use the container mounts as your new per-project selector

Previously you effectively had:

```text
settings.json
    ↓
chat.instructionsFilesLocations
    ↓
choose instruction sets
```

For your architecture, I would replace that with:

```text
docker-compose.yml
    ↓
bind mounts
    ↓
choose instruction sets exposed to this container
```

For example, ProjectTIPTree might contain:

```yaml
volumes:
  - ${HOME}/projects/my-agent/copilot/instructions/common:/home/jovyan/.copilot/instructions/common:ro

  - ${HOME}/projects/my-agent/copilot/instructions/julia:/home/jovyan/.copilot/instructions/julia:ro

  - ${HOME}/projects/my-agent/copilot/instructions/latex:/home/jovyan/.copilot/instructions/latex:ro
```

while a Python project might use:

```yaml
volumes:
  - ${HOME}/projects/my-agent/copilot/instructions/common:/home/jovyan/.copilot/instructions/common:ro

  - ${HOME}/projects/my-agent/copilot/instructions/python:/home/jovyan/.copilot/instructions/python:ro

  - ${HOME}/projects/my-agent/copilot/instructions/dvc:/home/jovyan/.copilot/instructions/dvc:ro
```

Now the effective environments are:

```text
ProjectTIPTree container

~/.copilot/instructions/
├── common/
├── julia/
└── latex/
```

versus:

```text
SomePythonProject container

~/.copilot/instructions/
├── common/
├── python/
└── dvc/
```

That is very close conceptually to what your old workspace setting did, except the selection is now made at the **Agent Host execution environment level**, rather than by the deprecated Local-harness VS Code setting.

Given that every one of your projects already has its own Dev Container, I think this is an especially clean solution.

---

### Use `applyTo` *inside* those selected sets too

I would actually use both mechanisms together.

For example, you mount the whole Julia set:

```text
my-agent/copilot/instructions/julia/
├── source.instructions.md
├── tests.instructions.md
└── docs.instructions.md
```

and then scope internally:

```yaml
# source.instructions.md
---
applyTo: "**/*.jl"
---
```

```yaml
# tests.instructions.md
---
applyTo: "**/test/**/*.jl"
---
```

```yaml
# docs.instructions.md
---
applyTo: "**/{docs,doc}/**"
---
```

So you get two levels of filtering:

```text
Level 1: container
        Which instruction families exist at all?
             ↓
       julia + latex + common

Level 2: applyTo
        Which instruction files apply to this particular work?
             ↓
       test/**/*.jl → Julia testing rules
```

That gives you much tighter context control than putting everything under one giant `~/.copilot/instructions`.

---

### I would be conservative with `description`

`description` is useful, but it is a **semantic/relevance mechanism**, whereas `applyTo` is a much more deterministic path mechanism.

For example:

```yaml
---
description: Use when working with DVC or data versioning.
---
```

allows the agent to decide that the instruction is relevant.

That's good for something task-oriented such as:

```text
dvc.instructions.md
release.instructions.md
benchmarking.instructions.md
```

But for genuinely conflicting conventions, I would not depend on descriptions such as:

```yaml
description: Python conventions for scientific projects
```

versus:

```yaml
description: Python conventions for web projects
```

and hope the model always chooses exactly one.

Your container-level selection is much safer for that case.

---

### Keep `~/.copilot/copilot-instructions.md` extremely small

Another thing I would change from many older configurations is avoiding a giant global instruction document.

This file:

```text
~/.copilot/copilot-instructions.md
```

is explicitly the Copilot user-level global instruction source. [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions?utm_source=chatgpt.com)

I would put only genuinely universal preferences there, perhaps things such as:

```text
- Never modify credentials or secrets.
- Prefer inspecting existing project conventions before introducing new ones.
- Run relevant tests after code changes when practical.
```

I would **not** put:

```text
Use pytest.
Use Documenter.jl.
Use DVC.
Use TeXLive.
Prefer NumPy.
```

there because those are stack-specific.

Those belong in targeted `.instructions.md` files.

---

### There is also an official environment-variable mechanism

Copilot currently supports:

```text
COPILOT_CUSTOM_INSTRUCTIONS_DIRS
```

as a comma-separated list of additional instruction directories. [GitHub](https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-command-reference.md?utm_source=chatgpt.com)

So technically you could keep:

```yaml
volumes:
  - ${HOME}/projects/my-agent:/home/jovyan/projects/my-agent:ro

environment:
  COPILOT_CUSTOM_INSTRUCTIONS_DIRS: >-
    /home/jovyan/projects/my-agent/copilot/instructions/common,
    /home/jovyan/projects/my-agent/copilot/instructions/julia,
    /home/jovyan/projects/my-agent/copilot/instructions/latex
```

That is arguably the closest literal replacement for:

```json
"chat.instructionsFilesLocations": ...
```

However, **I would still prefer the standard-path bind mounts for your setup**.

The standard:

```text
~/.copilot/instructions
```

location is the first-class user instruction location, while `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` is an additional-directory mechanism. The latter has also had some edge-case behavior around which instruction types and subagents inherit those extra directories. The standard location gives you fewer layers to reason about. [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions?utm_source=chatgpt.com)

So I'd keep the environment variable in mind as an escape hatch rather than build your whole configuration around it.

---

### Claude can follow essentially the same organization

Your:

```text
my-agent/
└── claude/
    └── rules/
```

can also remain nested:

```text
claude/rules/
├── common/
├── python/
├── julia/
└── latex/
```

The major syntax difference is that Claude rules use:

```yaml
---
paths:
  - "**/*.jl"
---
```

rather than Copilot's:

```yaml
---
applyTo: "**/*.jl"
---
```

VS Code 1.140 explicitly documents `.claude/rules` as Claude's targeted-instruction mechanism, with `paths` for path-specific activation. Without `paths`, the rule applies generally. [Visual Studio Code](https://code.visualstudio.com/docs/agents/guides/customize-copilot-guide?utm_source=chatgpt.com)

So the symmetry in your repo can be quite good:

```text
my-agent/
├── copilot/
│   └── instructions/
│       ├── common/
│       ├── julia/
│       └── latex/
│
└── claude/
    └── rules/
        ├── common/
        ├── julia/
        └── latex/
```

with project containers selectively mounting the corresponding families.

---

### Therefore I would slightly refine my previous recommendation

Previously I suggested mounting:

```text
my-agent/copilot/instructions
        ↓
~/.copilot/instructions
```

as a whole.

Given your clarification that you intentionally had **different instruction sets enabled for different projects**, I would **not** mount the whole directory.

Instead:

```text
                     okatsn/my-agent
                           │
          ┌────────────────┼────────────────┐
          │                │                │
        common           julia            latex
          │                │                │
          └────────────┬───┴────────────────┘
                       │
             selected by docker-compose
                       │
                       ▼
ProjectTIPTree container ~/.copilot/instructions/
                       │
                ┌──────┼──────┐
              common julia  latex
```

while another project might receive:

```text
              common + python + dvc
```

No flattening, no copying, no Git duplication, no deprecated VS Code location setting.

Then use `applyTo` inside each selected family for fine-grained activation.

That gives you a nice division of responsibility:

```text
Git repo directory structure
    → organizes reusable policy modules

docker-compose.yml
    → selects which policy modules this project is allowed to see

applyTo / paths
    → selects which policies apply to the current files/task

.github/copilot-instructions.md
    → describes this particular project's architecture/conventions
```

For your container-per-project workflow, **that is the instruction-management model I would recommend for the 1.140 Agent Host architecture**.

## CHECKPOINT: Permission Handling for `~/.copilot` in the container setup

https://gemini.google.com/app/a0f4d97ffe0d8292



## Docker-compose Architecture Refined and Explained

I recommend your second approach: one project-specific, persistent, writable Docker named volume for `~/.copilot`, with selected instruction directories bind-mounted read-only from your central Git repository.

This is a good fit for your one-project-one-Dev-Container architecture. There are, however, several important details to get right, particularly around Unix permissions, first-time initialization, and preventing silently missing or stale instructions.

The key distinction is that Docker mounting, filesystem permissions, and Copilot instruction discovery are three separate mechanisms. A successful container startup does not necessarily prove that all three are working.

### 1. Recommended architecture

Host machine — shared Git repository

\~/projects/my-agent/copilot/instructions/

common/

julia/

latex/

python/

Selective read-only bind mounts

ProjectTIPTree

/home/jovyan/.copilot/

Private named volume

sessions, config, logs — writable

instructions/

&#x20;common/

&#x20;julia/

&#x20;latex/

Python project

/home/jovyan/.copilot/

Different named volume

sessions, config, logs — writable

instructions/

&#x20;common/

&#x20;python/

The project-specific state volumes are independent. Only explicitly selected instruction directories are shared from the host.

#### How your two examples differ

| Property                      | First example: bind mounts only                     | Second example: named volume + bind mounts |
| ----------------------------- | --------------------------------------------------- | ------------------------------------------ |
| Instruction files             | Shared, read-only                                   | Shared, read-only                          |
| Copilot session data          | Container writable layer, unless separately mounted | Persistent named volume                    |
| Survives container recreation | Not reliably                                        | Yes                                        |
| Per-project isolation         | Container-dependent                                 | Explicit and persistent                    |
| Ownership handling            | Container filesystem                                | Named volume ownership must be considered  |
| Setup complexity              | Lower                                               | Slightly higher                            |

Docker documents that named volumes survive container removal and that a volume mounted over an existing directory obscures its underlying contents.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.docker.com\&sz=32)

Docker Docs

+1



Importantly, you are not combining conflicting mount types. You are creating nested mounts:

```
/home/jovyan/.copilot/
    ↳ named volume, writable

/home/jovyan/.copilot/instructions/common/
    ↳ host bind mount, read-only

/home/jovyan/.copilot/instructions/julia/
    ↳ host bind mount, read-only

/home/jovyan/.copilot/instructions/latex/
    ↳ host bind mount, read-only
```

The child bind mounts mask the corresponding directories inside the parent named volume. On a normally functioning Docker Engine, they do not duplicate the files.

One significant caveat: a named volume does not automatically delete or synchronize existing files elsewhere inside it. This matters when you change which instruction families are selected, and I'll address it in the verification strategy.

### 2. Recommended Docker Compose configuration

I would use the following, adapted from your second example.

.devcontainer/docker-compose.yml

```

name: projecttiptree

services:
  dev:
    # Keep your existing build/image configuration.
    # build: ...

    user: jovyan

    environment:
      HOME: /home/jovyan
      COPILOT_HOME: /home/jovyan/.copilot

    volumes:
      # Existing project workspace
      - ..:/home/jovyan/workspace

      # Private, persistent, writable Copilot state
      - type: volume
        source: copilot_state
        target: /home/jovyan/.copilot

      # Shared common instructions
      - type: bind
        source: ${HOME:?HOME is required}/projects/my-agent/copilot/instructions/common
        target: /home/jovyan/.copilot/instructions/common
        read_only: true
        bind:
          create_host_path: false

      # Shared Julia instructions
      - type: bind
        source: ${HOME:?HOME is required}/projects/my-agent/copilot/instructions/julia
        target: /home/jovyan/.copilot/instructions/julia
        read_only: true
        bind:
          create_host_path: false

      # Shared LaTeX instructions
      - type: bind
        source: ${HOME:?HOME is required}/projects/my-agent/copilot/instructions/latex
        target: /home/jovyan/.copilot/instructions/latex
        read_only: true
        bind:
          create_host_path: false

volumes:
  copilot_state:

```

#### Why these settings?

| Setting                   | Meaning                                                            |
| ------------------------- | ------------------------------------------------------------------ |
| `name: projecttiptree`    | Gives the Compose project a stable, project-specific identity      |
| `user: jovyan`            | Runs the container service as the `jovyan` user                    |
| `environment.HOME`        | Defines the home directory seen by processes in the container      |
| `COPILOT_HOME`            | Explicitly selects Copilot CLI's configuration and state directory |
| `type: volume`            | Uses Docker-managed persistent storage                             |
| `type: bind`              | Directly exposes a host directory                                  |
| `read_only: true`         | Prevents modification through the bind mount                       |
| `create_host_path: false` | Requests an error instead of creating a missing host path          |
| `volumes: copilot_state:` | Declares the Docker-managed volume                                 |

GitHub documents `COPILOT_HOME` as an override for the CLI's default `$HOME/.copilot` location. Setting it explicitly is optional, but useful for making the intended location unambiguous.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs

+1



I also recommend omitting the explicit volume `name: projecttiptree_copilot_state` from your original example.

With the top-level project name, Compose automatically names the volume:

```
projecttiptree_copilot_state
```

For another project:

```
name: mypythonproject

volumes:
  copilot_state:
```

Compose creates:

```
mypythonproject_copilot_state
```

This avoids accidentally sharing volumes because two projects explicitly configured the same volume name. Just ensure your Compose project names are unique; names can also be overridden using `docker compose -p` or `COMPOSE_PROJECT_NAME`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.docker.com\&sz=32)

Docker Docs

+1



### 3. What happens if `~/.copilot` doesn't exist?

There are two different situations.

#### Case A: `/home/jovyan/.copilot` doesn't exist in the image

Docker can create the necessary mount destination when setting up the container.

The named volume also gets created automatically if it does not already exist.

Therefore, you do not need `RUN mkdir /home/jovyan/.copilot` merely to make the mount work.

However, there is a separate concern: ownership.

#### Case B: The directory exists, but belongs to root

Suppose the original container filesystem has:

```
/home/jovyan/
└── .copilot/    root:root  755
```

The container runs with:

```
user: jovyan
```

The named volume may end up with ownership or permissions that prevent `jovyan` from writing to it.

That can break session storage, configuration updates, and other runtime operations.

Docker's default empty-volume initialization copies existing content from the image's target directory. Preparing that directory with appropriate ownership is therefore a useful first-run initialization technique.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.docker.com\&sz=32)

Docker Docs

+1



#### What I would put in the Dockerfile

Assuming the image already defines a `jovyan` user:

```

# Add to your existing Dockerfile, while building as root.
USER root

# Prepare the Copilot directory for the non-root user.
RUN install -d -m 0700 \
      -o jovyan -g "$(id -gn jovyan)" \
      /home/jovyan/.copilot \
    && install -d -m 0755 \
      -o jovyan -g "$(id -gn jovyan)" \
      /home/jovyan/.copilot/instructions

USER jovyan

```

This serves two purposes: it establishes the intended ownership for first-time volume initialization, and it makes the expected directory structure explicit in your image.

Do not set `volume.nocopy: true` if you are relying on Docker's initial population of the volume from this prepared directory.

Important: changing the Dockerfile later will not automatically change the ownership of an already-existing named volume. The volume persists independently of the image.

If an existing volume has the wrong ownership, inspect it and repair the volume root explicitly, without recursively changing your read-only bind mounts:

```
docker compose exec --user root dev sh -c '
  chown jovyan:$(id -gn jovyan) /home/jovyan/.copilot
  chmod 700 /home/jovyan/.copilot
'
```

### 4. Does the host username need to match `jovyan`?

No.

For example:

```
Host:
    /home/okatsn/projects/my-agent/

Container:
    /home/jovyan/.copilot/instructions/
```

This is perfectly valid.

Compose substitutes `${HOME}` on the machine running the Compose command, independently of the container's `HOME` variable. The resolved bind source must exist on the Docker daemon's host and be accessible to it. This distinction is especially relevant if you use a remote Docker daemon.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.docker.com\&sz=32)

Docker Docs

+1



The Linux filesystem is concerned with numeric UIDs, GIDs, and permission bits, not with matching usernames.

For example:

```
Host:
  UID 1001
  instruction directory 755
  instruction file      644

Container:
  jovyan UID 1000
```

The container user can normally read these files despite having a different UID.

However:

```
Host:
  instruction directory 700
  instruction file      600
```

may prevent the container user from reading anything.

The `read_only: true` option does not grant permission to read. It only restricts writing through that mount.

For your shared instruction repository, conventional permissions such as `755` for directories and `644` for Markdown files usually work well. Where files must remain private, use matching group permissions or ACLs rather than making them world-readable.

### 5. Understanding `create_host_path: false`

This is one of the most important options for your stated goal.

#### Without it

Your original short syntax:

```
- ${HOME}/projects/my-agent/copilot/instructions/julia:/home/jovyan/.copilot/instructions/julia:ro
```

can silently create the missing directory on the host.

Imagine accidentally renaming your Git repository:

```
Expected:
  ~/projects/my-agent/copilot/instructions/julia

Actual:
  ~/projects/my-agents/copilot/instructions/julia
```

Docker may create an empty directory at the expected location.

The container starts, but the Julia instruction directory appears empty. Copilot may then have no applicable Julia instructions.

#### With it

```
- type: bind
  source: ${HOME}/projects/my-agent/copilot/instructions/julia
  target: /home/jovyan/.copilot/instructions/julia
  read_only: true
  bind:
    create_host_path: false
```

The documented intention is that Docker Compose should fail rather than create the missing host directory.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.docker.com\&sz=32)

Docker Docs

+1



An important implementation caveat

As of October 2026, Docker Compose has an open issue, [#13602](https://github.com/docker/compose/issues/13602), reporting that `create_host_path: false` was ignored on Docker Desktop with WSL2, even though the configuration was accepted.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Therefore, keep the option, but do not rely on it as your only fail-fast protection.

It also cannot detect a directory that exists but is empty or contains old files.

For that, you need validation.

### 6. My recommended fail-fast verification

I would validate at three levels.

#### Level 1: Before starting Docker — verify the host sources

A small host-side script is the strongest safeguard against incorrect source paths.

For example:

```

#!/usr/bin/env bash
set -euo pipefail

AGENT_ROOT="${HOME}/projects/my-agent/copilot/instructions"

for family in common julia latex; do
    dir="${AGENT_ROOT}/${family}"

    if [[ ! -d "$dir" ]]; then
        echo "ERROR: Missing instruction directory: $dir" >&2
        exit 1
    fi

    if ! find "$dir" -type f -name '*.instructions.md' \
            -print -quit | grep -q .; then
        echo "ERROR: No instruction files found in: $dir" >&2
        exit 1
    fi
done

echo "All selected host instruction directories exist."
docker compose config --quiet

```

Run this before bringing up the project container, for example from your own Dev Container launch wrapper.

It ensures that `common`, `julia`, and `latex` exist and contain at least one instruction file each. You can strengthen it further by checking specific required filenames or Git repository status.

`docker compose config` validates the Compose model, but does not prove that the content of every bind mount is correct.

#### Level 2: Inside the container — verify the actual mounts

After starting your container, execute:

```
docker compose exec dev sh -c '
  id
  echo "HOME=$HOME"
  echo "COPILOT_HOME=$COPILOT_HOME"
  ls -la /home/jovyan/.copilot
  ls -la /home/jovyan/.copilot/instructions
'
```

You should see the correct users, expected directories, and persistent Copilot root.

Then inspect mount details:

```
docker compose exec dev findmnt \
  -M /home/jovyan/.copilot \
  -o TARGET,SOURCE,FSTYPE,OPTIONS
```

And:

```
docker compose exec dev findmnt \
  -M /home/jovyan/.copilot/instructions/julia \
  -o TARGET,SOURCE,FSTYPE,OPTIONS
```

`findmnt -M` checks for a mount at the exact path, rather than merely reporting its ancestor mount.

Expected properties:

- `/home/jovyan/.copilot` is the writable named-volume mount.
- `/home/jovyan/.copilot/instructions/julia` is a separate read-only bind mount.
- Its contents include the correct files.

If `findmnt` is unavailable in your image, install `util-linux` or inspect `/proc/self/mountinfo`.

For additional confirmation from the Docker host:

```
docker inspect "$(docker compose ps -q dev)" \
  --format '{{json .Mounts}}' | jq
```

This will show the source and destination paths configured for the container.

There have also been reports of nested-mount regressions on recent macOS Docker Desktop configurations, particularly involving a parent host bind mount and a child volume. Those reports do not demonstrate a failure of your exact arrangement, but they reinforce why checking the actual container filesystem is useful.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



#### Level 3: Confirm that changes are immediately visible

This directly addresses your concern about duplicated, never-updated instructions.

Take a real instruction file, for example:

```
~/projects/my-agent/copilot/instructions/common/general.instructions.md
```

Calculate the checksum on the host:

```
sha256sum \
  ~/projects/my-agent/copilot/instructions/common/general.instructions.md
```

Then inside the container:

```
sha256sum \
  /home/jovyan/.copilot/instructions/common/general.instructions.md
```

Both checksums should match.

Now edit the file on your host and repeat the check. The container should see the updated contents without rebuilding its image.

That verifies the actual file content, beyond simply proving that a path exists.

A running Copilot session may still need to reload its instruction context, so filesystem visibility and model activation are separate checks.

GitHub Copilot CLI provides the `/instructions` command to display discovered instructions and their enabled status. This is the final application-level check I would use.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs



### 7. The subtle stale-instructions problem with named volumes

There is one more risk worth highlighting.

Suppose your named volume initially contains:

```
~/.copilot/instructions/
├── common/
├── julia/
├── latex/
└── python/
```

You subsequently configure your Compose file to mount only:

```
common/
julia/
latex/
```

The `python/` directory already stored in the persistent named volume does not disappear automatically.

Therefore the effective filesystem could contain:

```
~/.copilot/instructions/
├── common/   ← live read-only bind
├── julia/    ← live read-only bind
├── latex/    ← live read-only bind
└── python/   ← leftover persistent directory
```

Copilot may discover that unwanted Python instruction folder too.

My recommendation: keep the writable volume's `instructions/` directory empty apart from the paths needed as mount targets. Do not copy instruction content into it, and audit for unexpected entries when switching instruction sets.

You can use a simple check:

```
docker compose exec dev \
  ls -la /home/jovyan/.copilot/instructions/
```

For stronger enforcement, add a startup validation that rejects any instruction family not on the project's allowlist.

I would not add a more complicated temporary filesystem arrangement unless stale entries become a practical problem. The named-volume-plus-bind-mount design is still a reasonable default.

### 8. When rebuilding or removing containers

One of the main benefits of your second design is that the lifecycle of the container is separated from the lifecycle of Copilot's state.

| Operation                            | Copilot session state | Shared instructions               |
| ------------------------------------ | --------------------- | --------------------------------- |
| Restart container                    | Preserved             | Bind-mounted again                |
| Recreate container                   | Preserved             | Bind-mounted again                |
| Rebuild image and recreate container | Preserved             | Bind-mounted again                |
| Edit an instruction file on host     | Preserved             | New file content normally visible |
| `docker compose down`                | Preserved             | Reattached on next startup        |
| `docker compose down -v`             | Deleted               | Host Git files unaffected         |

Avoid running `docker compose down -v` casually. It deletes the Compose-managed named volume, including Copilot state.

Likewise, don't use `docker volume prune` without considering volumes you want to retain.

One additional edge case: if your Git repository deployment process replaces entire instruction directories with new directories, rather than modifying files in place, an existing bind mount can continue referring to the old directory. Recreating the container and verifying the content is then appropriate.

### 9. Final architecture recommendation

For your many-project workflow, I would standardize these responsibilities:

| Component                        | Responsibility                                                 |
| -------------------------------- | -------------------------------------------------------------- |
| `okatsn/my-agent` Git repo       | Canonical source for reusable instructions, agents, and skills |
| Per-project `docker-compose.yml` | Selects the instruction families exposed to the project        |
| Named Docker volume              | Preserves that project's private Copilot state                 |
| Read-only bind mounts            | Expose current Git-controlled customizations                   |
| Dockerfile                       | Prepares non-root writable directory ownership                 |
| Host preflight script            | Rejects missing or empty Git-controlled sources                |
| Container mount verification     | Confirms the correct filesystem is mounted                     |
| Copilot `/instructions`          | Confirms the harness actually discovered the instruction files |

The resulting design has a useful separation:

```
Git repository
    |
    | Defines what instructions exist
    |
    v
Docker Compose
    |
    | Selects which instructions a project can see
    |
    v
Read-only bind mounts
    |
    | Expose canonical files without copying
    |
    v
Copilot Agent Host
    |
    | Reads applicable instructions
    | Writes private state
    |
    v
Project-specific named volume
```

My recommendation is to adopt your second Compose configuration, pre-create `.copilot` with the correct ownership in the Dockerfile, and retain `create_host_path: false` together with explicit preflight checks.

That achieves your main goals: independent session state for every project, selective instruction visibility, a single Git-controlled source of truth, and verification against silent failures.

The final principle I would adopt is:

Don't merely verify that Copilot can read an instruction file. Verify that it is reading the intended host-controlled file, through the intended read-only mount, and that no unselected instruction files are present.

## Docker-compose Architecture For Skill sets

As of October 2026, I recommend a hybrid approach: make your general-purpose skills available to every Dev Container, but selectively expose specialized skill sets based on each project's needs.

Unlike instructions, however, skills do not need aggressive filtering just to reduce context usage. This is the crucial difference from your earlier Instruction Architecture plan.

The choice is a genuine trade-off, not a situation where one solution overwhelmingly outperforms the other.

### 1. Why skills should be treated differently from instructions

The main reason is Copilot's progressive disclosure mechanism.

In current VS Code and Copilot CLI, skills are loaded in stages:

Stage 1 — Discovery

Every available skill

Copilot examines the skill's name and description to determine whether it is relevant.

Stage 2 — Activation

Relevant skill only

When selected, the skill's `SKILL.md` instructions are loaded into the agent's context.

Stage 3 — Resources

As needed

Supporting scripts, examples, and reference files are accessed when the workflow requires them.

Progressive disclosure as described by the current VS Code Agent Skills documentation.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://code.visualstudio.com\&sz=32)

code.visualstudio.com

Therefore, mounting 50 skills does not normally mean injecting the full contents of 50 `SKILL.md` files into every conversation. That is exactly what the skills architecture is designed to avoid.

But there is a qualification: discovering skills still has overhead. The names and descriptions of available skills must be made discoverable to the model. Copilot CLI has historically encountered metadata/token-budget problems with large skill collections, although improvements have been shipped.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+2



This means that mounting all skills is much less expensive than making all their instructions always-on, but it is not completely free.

### 2. Comparing the two approaches

| Factor                           | All skills in every project          | Selective skills           |
| -------------------------------- | ------------------------------------ | -------------------------- |
| Setup and maintenance            | Simpler                              | More configuration         |
| Discovering useful skills        | Broad availability                   | More focused               |
| Context usage                    | Low to moderate metadata overhead    | Usually lower              |
| Risk of inappropriate activation | Greater with overlapping skills      | Lower                      |
| Consistency across projects      | High                                 | Depends on selection       |
| Third-party skill exposure       | Broader                              | Narrower                   |
| Unexpected new workflows         | More likely to find a relevant skill | Skill might be unavailable |
| Scaling to a large skill library | Less predictable                     | More controlled            |

The biggest argument for including all skills is convenience. A general-purpose Markdown conversion skill could be useful even in a Julia project, and you might never anticipate when you need it.

The biggest argument for selective skills is controlling the agent's available capabilities. If a project never uses Kubernetes, browser automation, or AWS deployment, there may be no benefit to showing those skills to its agent.

So I would not create a separate Compose mount for every individual skill. But neither would I automatically expose a very large collection of unrelated capabilities to every container.

### 3. What I would implement in your `my-agent` repository

I would divide your library into three categories.

Universal skills — always available

Examples: Markdown manipulation, Git workflows, documentation generation, code review, general research, and repository exploration.

These have broad utility and little reason to restrict them by programming language.

Domain-specific skills — selectively available

Examples: Julia package maintenance, Python scientific computing, LaTeX publishing, DVC workflows, Playwright testing, and cloud deployment.

Mount these according to the project's technologies and likely workflows.

Project-specific skills — owned by the project

Examples: regenerating ProjectTIPTree datasets, running its custom verification pipeline, or packaging one application's release artifacts.

These belong in the project's `.github/skills/`, not your global repository.

This also follows VS Code's current recommendation to store customizations at the narrowest scope appropriate for their use.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://code.visualstudio.com\&sz=32)

code.visualstudio.com



#### Proposed source structure

```
my-agent/
└── copilot/
│   ├── agents/
    ├── instructions/
    │   ├── common/
    │   ├── ...
    │   └── typst/
    │
    └── skillsets/
        ├── common/
        │   ├── ...
        │   │   └── SKILL.md
        │   ├── ...
        │
        ├── typst/
        │   ├── ...
        │   │   └── SKILL.md
        │   └── ...
        │

```

Here, `skillsets/` and its categories are your own organizational conventions. The Copilot harness does not inherently understand them as skill categories.

#### Important difference from your instruction mounts

You should not assume that skill discovery works recursively like `.instructions.md` discovery.

The documented standard structure expects skills directly beneath a discovery root:

```
~/.copilot/skills/
├── git-review/
│   └── SKILL.md
└── markdown-convert/
    └── SKILL.md
```

Not a nested taxonomy such as:

```
~/.copilot/skills/
└── common/
    └── git-review/
        └── SKILL.md
```

The second structure adds an extra level that you should not rely on for default discovery.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs

+1



Consequently, if you want to mount complete skill sets rather than individual skill directories, mount each selected set as a skill discovery root.

### 4. Docker Compose implementation

Copilot CLI now officially supports the `COPILOT_SKILLS_DIRS` environment variable, a comma-separated list of additional skill discovery directories. This is not one of the deprecated VS Code `chat.*FilesLocations` settings.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs



For your ProjectTIPTree container, I would consider:

```

services:
  dev:
    environment:
      HOME: /home/jovyan
      COPILOT_SKILLS_DIRS: >-
        /home/jovyan/skillsets/julia,
        /home/jovyan/skillsets/latex

    volumes:
      # Project-exclusive writable Copilot state
      - type: volume
        source: copilot_state
        target: /home/jovyan/.copilot

      # Universal skills: native discovery location
      - type: bind
        source: ${HOME}/projects/my-agent/copilot/skillsets/common
        target: /home/jovyan/.copilot/skills
        read_only: true
        bind:
          create_host_path: false

      # Julia-specific skills
      - type: bind
        source: ${HOME}/projects/my-agent/copilot/skillsets/julia
        target: /home/jovyan/skillsets/julia
        read_only: true
        bind:
          create_host_path: false

      # LaTeX-specific skills
      - type: bind
        source: ${HOME}/projects/my-agent/copilot/skillsets/latex
        target: /home/jovyan/skillsets/latex
        read_only: true
        bind:
          create_host_path: false

volumes:
  copilot_state:
    name: projecttiptree_copilot_state

```

This is a skills-only excerpt; retain the workspace and instruction mounts from your existing Compose configuration. The folded YAML value is written without indentation between comma-separated directory names in the resolved value.

I like this arrangement because it provides universal skills at a native location while letting you add or remove specialized categories using the documented extra-directory mechanism.

If you prefer not to use an environment variable, another supported option is to mount `common` at `/home/jovyan/.copilot/skills` and a single selected specialist set at `/home/jovyan/.agents/skills`. However, this only gives you two convenient personal discovery roots, which becomes restrictive for projects combining Julia, LaTeX, DVC, and other specialties.

For Copilot CLI specifically, `COPILOT_SKILLS_DIRS` is a reasonable solution. If you later use Claude or Codex as a separate harness, verify their respective discovery mechanisms rather than assuming they recognize this Copilot-specific variable.

### 5. When exposing all skills is preferable

There are two circumstances in which I would deliberately depart from selective mounting.

First, when your library is relatively small. If you have a few dozen well-written, independently useful, nonconflicting skills, mounting everything could be simpler and equally effective. There is no official hard threshold at which selective loading suddenly becomes better.

Second, when workflows are difficult to predict. For example, a Julia project may unexpectedly need PDF processing, diagram generation, Markdown conversion, web research, or Python interoperability. Filtering those capabilities too strictly can become counterproductive.

For these reasons, I would define `common` fairly generously, not limit it to generic coding skills.

On the other hand, I would be more selective with skills that contain specialized operational instructions, significant scripts, broad tool permissions, or contradictory implementations of the same workflow.

Also remember that a read-only mount protects the skill's source files, not the rest of the workspace. A skill can instruct the agent to execute a script that modifies other writable paths. GitHub explicitly warns against casually pre-approving shell execution in untrusted skills.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs



### 6. Skill metadata matters more than aggressive filtering

Before splitting a library into ever-smaller groups, I would prioritize writing distinctive skill descriptions.

For example:

```

---
name: julia-package-audit
description: >
  Audit a Julia package using Julia-specific
  quality tools and package conventions.
  Use when checking Julia package correctness,
  compatibility, or release readiness.
---

```

This gives the agent a clear activation signal.

For workflows that should only run when explicitly requested, Copilot also supports:

```
disable-model-invocation: true
```

That keeps the skill available for explicit slash-command invocation while preventing the agent from automatically selecting it.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://code.visualstudio.com\&sz=32)

code.visualstudio.com

+1



Note that this is an activation preference, not a sandbox or tool-permission boundary.

Another consideration is name collisions. Copilot CLI resolves duplicate skill names according to discovery precedence, with project skills generally taking priority over personal skills. Choose distinctive skill names and verify which definition is actually loaded.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs



### 7. How I would validate the arrangement

After building your container, check both the available skill catalog and its actual contents:

```
# Run inside the container
copilot skill list

# For interactive Copilot CLI:
# /skills info julia-package-audit
# /skills info latex-build
# /skills reload
```

Current Copilot CLI documentation provides these commands for inspecting skill availability, locating a skill, and reloading skills after changes.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.github.com\&sz=32)

GitHub Docs



I would test that:

- The expected `common`, `julia`, and `latex` skills are discoverable.
- Python-only or DVC-only specialist skills from your shared repository are absent.
- The skill definitions resolve to the intended host bind-mount paths.
- A representative Julia task activates the appropriate Julia skill without incorrectly selecting another workflow.

Also inspect VS Code's Agent Customizations editor in an actual Agent Host session. The same filesystem and environment variables must be visible to the harness process, not only to a separate terminal you happen to open inside the container.

### Final recommendation for your architecture

I'd make instructions selective by default, but skills broadly available with selective specialization.

ProjectTIPTree — recommended effective customization set

| Instructions   | common + julia + latex            |
| -------------- | --------------------------------- |
| Skills         | common + julia + latex            |
| Project skills | `.github/skills/`                 |
| Runtime state  | Project-exclusive writable volume |

SomePythonProject — recommended effective customization set

| Instructions   | common + python + dvc    |
| -------------- | ------------------------ |
| Skills         | common + python + dvc    |
| Project skills | `.github/skills/`        |
| Runtime state  | Separate writable volume |

The apparent symmetry is convenient, but the rationale is different. For instructions, selective exposure primarily prevents irrelevant or conflicting rules from applying. For skills, selective exposure primarily improves capability discovery, reduces ambiguity, and limits unnecessary workflow exposure.

I would not invest heavily in fine-grained skill selection until your collection becomes large enough to cause measurable discoverability problems. Begin with a generous universal set and a handful of specialized sets, then refine based on actual agent behavior. That is a better balance of reliability and maintenance cost than either extreme.