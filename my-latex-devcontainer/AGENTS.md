# AGENTS.md

The latex manuscript structure:

```
.
├── AGENTS.md
├── chapters
│   ├── sec_abstract.tex
│   ├── sec_conclusion.tex
│   ├── sec_discussion.tex
│   ├── sec_introduction.tex
│   ├── sec_method.tex
│   └── sec_result.tex
├── contents
│   ├── ... # tex files to be included by `chapters/sec_*.tex` files
│   └── result_SilLowStress.tex
├── dvc.yaml
├── params.yaml
├── manuscript
│   ├── config.tex      # SSoT for authors' information
│   ├── main.tex        # (SSoT) The main (root) tex file.
│   ├── manuscript.tex  # (Replica) The expanded single manuscript files.
│   ├── README
├── manuscript_0.diff       # Comparison manuscript.tex between the workspace and branch `diff_ref.branch`.
├── tex_dependency_graph.md # The dependency graph derived from the root file `main.tex`.
└── README.md # This is for human. Don't peek inside.
```

## Rules

- Read `dvc.yaml`, `params.yaml` to understand the dependencies of `main.tex` and the pipeline of manuscript production.
- `manuscript.tex` is expanded from `main.tex`, it serves as a replica of the whole manuscript but in a single file. Only read it; NEVER edit it.
- `main.tex` and its dependencies (`chapters/*.tex`, `contents/*.tex`) are the SSoT.
- Read `tex_dependency_graph.md` to understand the dependencies of `main.tex` before dive into the SSoT.

Rationale:
1. `manuscript.tex` is tracked by DVC pipeline, so it should not be edited.
2. `main.tex` and its dependencies are tracked by Git, so you can make edits there.