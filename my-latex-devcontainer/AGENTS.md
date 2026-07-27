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

- Read `dvc.yaml`, `params.yaml` to understand the dependencies of `main.tex` and peripheral files in the manuscript production pipeline.
- `manuscript.tex` is expanded from `main.tex`, it serves as a replica of the whole manuscript but in a single file. Only read it; NEVER edit it. The final product is `manuscript.tex` (to be shared); it is tracked by DVC.
- `main.tex` and its dependencies (`chapters/*.tex`, `contents/*.tex`) are the SSoT; they are tracked by GIT.
- Read `tex_dependency_graph.md` to understand the dependencies of `main.tex` before dive into the SSoT.
- Write manuscript in `chapters/*.tex` and `contents/*.tex`. Keep `main.tex` as a pure skeleton.
- Put figures in `manuscript/`: `latexpand` simply expand latex code, which means when you include a figure in `chapters/*.tex` or `contents/*.tex` files, you have to use path `Fig.eps` (to be read by `manuscript.tex`), rather than `../manuscript/Fig.eps` (errored/cannot find the file in compiling `manuscript.tex`).

Rationale:
1. `manuscript.tex` is tracked by DVC pipeline, so it should not be edited.
2. `main.tex` and its dependencies are tracked by Git, so you can make edits there.