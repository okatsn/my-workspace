
## Human--AI-Agent Collaboration Rules

Ownership:

- Only human developers write `journals/*.md`, review and update status of `DECISION`.
- AI agents write and update `REPORT`, `REVIEW` and `DECISION` pages for their implementation, experimental testing or design works.
- Both human and AI writes and maintains `KNOWLEDGE` pages and architecture pages (`[[ARCH/*]]`).
- `chat` pages: Archived external conversations (Q&A sessions) and third opinions for traceability. Never regard a description in `chat` as proofed or confirmed.

## Logseq dev-notes structure

Under `GRAPH/pages`:

| Type        | Logical page name        | Physical filename             |
| ----------- | ------------------------ | ----------------------------- |
| `ARCH`      | `ARCH/<description>`     | `ARCH___<description>.md`     |
| `KNOWLEDGE` | natural page name        | `<page name>.md`              |
| `DECISION`  | `DECISION/<description>` | `DECISION___<description>.md` |
| `REPORT`    | `REPORT/<description>`   | `REPORT___<description>.md`   |
| `REVIEW`    | `REVIEW/<description>`   | `REVIEW___<description>.md`   |
| `chat`      | `chat/<description>`     | `chat___<description>.md`     |

> **IMPORTANT**:
>
> 1. Contents in the pages of type `chat` should ALWAYS be considered as **UNVERIFIED**: never regard `chat` as consolidated knowledge, adopted plans or determined decisions.
>    Always assume a `chat` page to be not well-formatted and unnecessarily detailed.
> 2. When writing, avoid strong words or overstatements unless it truly fits. Make statements that "no more or less" to the fact and evidence.
> 3. `ARCH` pages should not be stuffed with details of specs. Be concise but readable, focusing on explain the architecture and the rationale behind. Cross referencing details using `files:: ` or `stages:: ` at block level instead.
> 4. `DECISION` pages should focus on explaining the rationale, complementary to REVIEW or REPORT pages with overlapping (duplicated details) minimized.

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

Noted that `files::` remain a deliberately lexical field; simply use `rg -l 'src/ingest\.jl' path/to/GRAPH/` (both prose and metadata) or `rg -l '^files:: .*src/ingest\.jl'` (targeting metadata `files` only) to get the files with such file.
We don't use `files:: [[src/ingest.jl]], [[scripts/ingest.jl]]` because we don't want the logseq graph to be cluttered with file/path entities.


## Progressive Disclosure in Understanding the Context

Journal pages are expected to be short, and it cost little to read all RAW journal pages (i.e., `journals/*.md`) without pulling relational context. Journals will mention some critical events. So the recommended workflow would be:

1. Read all journal pages in raw, and select a few pages that is relevant to the current task.
2. Use `python helper/logseq_refs.py path/to/GRAPH/ journals <page1> <page2>` to pull these relevant pages with relational context.
3. Read page `[[ARCH/CURRENT-STATUS]]`, `dvc.yaml`, `params.yaml` if provided.

> Note: the date on a journal do not have too much meaning, at most hinting at the sequential order for when an idea/issue firstly proposed. It is expected that a journal date might be misaligned against the date in the committed history.

## Page Layout Instructions

Read the corresponding instruction(s) first when editing a page in the Target list.

| Instructions                                            | Target                           |
| ------------------------------------------------------- | -------------------------------- |
| `logseq-current-status-format.instructions.md`          | `ARCH___CURRENT-STATUS.md`       |
| `logseq-decision-page-format.instructions.md`           | `DECISION___*.md`                |
| `logseq-review-implement-report-format.instructions.md` | `REPORT___*.md`; `REVIEW___*.md` |
