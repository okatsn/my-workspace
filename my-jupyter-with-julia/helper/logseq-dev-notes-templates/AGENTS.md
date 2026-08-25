## Logseq basics

Logseq use double square brackets syntax `[[page]]` to connect a dedicate page.
For example, `[[Algorithm Whatever]]` in the body text or the metadata value connects to `pages/Algorithm Whatever.md`; similarly,
`[[REPORT/implement-stage-1]]` or `#REPORT/implement-stage-1` connects to `REPORT___implement-stage-1.md` (`___` in file ↔️ `/` in wikilink text).

Logseq metadata are key-value pairs (syntax: `keys:: value`) for searchable attributes, tags, alias to an entire document pages.

## Human--AI-Agent Collaboration Rules

Ownership:

- Only human developers write `journals/*.md`, review and update status of `DECISION`.
- AI agents write and update `REPORT`, `REVIEW` and `DECISION` pages for their implementation, experimental testing or design works.
- Both human and AI writes and maintains `KNOWLEDGE` (see below) pages and architecture pages (`[[ARCH/*]]`).

## Logseq dev-notes structure

Under `logseq-dev-notes/pages`:

| Type        | Logical page name        | Physical filename             |
| ----------- | ------------------------ | ----------------------------- |
| `KNOWLEDGE` | natural page name        | `<page name>.md`              |
| `DECISION`  | `DECISION/<description>` | `DECISION___<description>.md` |
| `REPORT`    | `REPORT/<description>`   | `REPORT___<description>.md`   |
| `REVIEW`    | `REVIEW/<description>`   | `REVIEW___<description>.md`   |

Examples of pairing Metadata structure and page name:

- `type:: [[KNOWLEDGE]]` w/ natural page name (e.g., `[[Algorithm Whatever]]`)
- `type:: [[DECISION]]` w/ hierarchical page name (e.g., `[[DECISION/choose-A-B]]`)
- `type:: [[REPORT]]` w/ hierarchical page name (e.g., `[[REPORT/implement-stage-1]]`)
- `type:: [[REVIEW]]` w/ hierarchical page name (e.g., `[[REVIEW/math-num-honesty]]`)

> For pages of types `DECISION`, `REPORT` and `REVIEW`, the hierarchy value is intentionally duplicated from the property value to avoid name collision (thus `REVIEW___stage-1.md` and `REPORT___stage-1.md` won't collide, for example).



## Page Metadata

- `type`: File/Page level metadata. Mandatory for ALL non-journal pages.
- `status`: File/Page level metadata. Exclusively mandatory for type `DECISION`
- `files`: Block level metadata. Refer associated files. Optional for `DECISION`; mandatory for `REPORT` and `REVIEW`.
- `evidences`: Block level metadata. Refer associated evidence files (test files and test output log). Mandatory for `REVIEW`; optional for `REPORT` when applicable.
- `stages`: File/Page level metadata. Refer associated DVC stages.


File/Page level metadata example:

```
type:: [[DECISION]]
status:: [[ACTIVE]]
```

Block level metadata example:

```
- This is a logseq block in a report of an implementation, modifying `src/ingest.jl`.
  files:: src/ingest.jl
```

Optional Metadata:

- `prerequisites`: Use this to establish dependencies between pages of type `DECISION`, `REPORT` and `REVIEW`, following the rules:
  - `KNOWLEDGE` mostly depends on another `KNOWLEDGE`. For example, a `[[Coding]]` KNOWLEDGE page can declare:
    ```markdown
    type:: [[KNOWLEDGE]]
    prerequisites:: [[Keeping a Notepad]], [[Core Docs]]
    ```
  - `REPORT` can depends on another DECISION, REPORT, REVIEW or a KNOWLEDGE page.
    For example, for an implementation report:
    ```md
    type:: [[REPORT]]
    prerequisites:: [[REPORT/pre-implementation.md]], [[REVIEW/test-feasibility.md]], [[DECISION/choosing-A-B]], [[Designing for Validation]]
    ```
  - `REVIEW` mostly depend on another `REVIEW` or a `KNOWLEDGE` page.
  - `DECISION` basically depends on `REVIEW` or `KNOWLEDGE` pages.
  - Add to `prerequisites` only when a page is directly essential for the context in the current page.




## File and Path Annotation Rules

For file/path, keep backticks in prose (e.g., "... `src/ingest.jl` and `scripts/ingest.jl`  ...") but plain-text in metadata, for example:

```md
files:: src/ingest.jl, scripts/ingest.jl
evidences:: test/ingest.jl
- `src/ingest.jl` in Stage 1 ...
```

Noted that `files::` remain a deliberately lexical field; simply use `rg -l 'src/ingest\.jl' logseq-dev-notes/` (both prose and metadata) or `rg -l '^files:: .*src/ingest\.jl'` (targeting metadata `files` only) to get the files with such file.
We don't use `files:: [[src/ingest.jl]], [[scripts/ingest.jl]]` because we don't want the logseq graph to be cluttered with file/path entities.


