#!/usr/bin/env bash

# Create a structured LaTeX manuscript template in the current directory.
# The current directory is assumed to be the intended NameOfMainFolder.
# No arguments are accepted. Existing files are NOT overwritten.

set -euo pipefail

sleep_and_exit() {
	# Sleep 5 seconds so user can read the error per project shell guide.
	echo "Error: $1" >&2
	sleep 5
	exit 1
}

ensure_no_args() {
	if [ "$#" -ne 0 ]; then
		sleep_and_exit "This script takes no arguments. Run it inside the target folder."
	fi
}

make_dir() {
	# Create directory if it does not exist.
	local dir="$1"
	if [ ! -d "$dir" ]; then
		mkdir -p "$dir"
		echo "Created directory: $dir"
	else
		echo "Directory exists (skip): $dir"
	fi
}

create_file_if_missing_from_stdin() {
	# Create a file from stdin (heredoc) if it does not already exist.
	local file_path="$1"
	if [ -f "$file_path" ]; then
		echo "File exists (skip): $file_path"
	else
		cat > "$file_path"
		echo "Created file: $file_path"
	fi
}

create_readme() {
	create_file_if_missing_from_stdin "README.md" <<'EOF'
Following the practice below to safely share the entire script:

- write your manuscript in *chapter* files
- include tex files of *chapter* in `main.tex`
- (optional) include *contents* files in a *chapter* file to better organize your idea.
- To create the `manuscript.tex`: `latexpand -o manuscript.tex main.tex`
- share `manuscript.tex` rather than `main.tex`
- Render the `manuscript.tex`.
- Put figures in *manuscript*: `latexpand` simply expand latex code, which means when you include a figure in *chapter* files, use `Fig.eps` (to be read by `manuscript.tex`), not `../manuscript/Fig.eps`.

EOF
}

create_main_tex() {
	create_file_if_missing_from_stdin "manuscript/main.tex" <<'EOF'
% This is main.tex, the simplest LaTeX document
\documentclass{article}
% Bring in configuration macros
\input{./config.tex}

\begin{document}

\title{Title Placeholder}
\author{Author Name}
\date{\today}

\maketitle


% Include chapter sections
\input{../chapters/sec_1.tex}

This document includes a reference \cite{placeholder2025}.
% ... add more chapter inputs here ...

\bibliographystyle{plain}
\bibliography{bibtex} % refers to bibtex.bib

\end{document}
EOF
}

create_config_tex() {
	create_file_if_missing_from_stdin "manuscript/config.tex" <<'EOF'
% Example macro configuration file
\def\variableFoobar {Foobar2000}
EOF
}

create_bib() {
	create_file_if_missing_from_stdin "manuscript/bibtex.bib" <<'EOF'
@article{placeholder2025,
  title   = {Placeholder Article},
  author  = {Placeholder Author},
  journal = {Placeholder Journal},
  year    = {2025},
  volume  = {1},
  number  = {1},
  pages   = {1--10}
}
EOF
}

create_chapter_section() {
	create_file_if_missing_from_stdin "chapters/sec_1.tex" <<'EOF'
% sec_1.tex includes content files
\input{../contents/content_1.tex}
EOF
}

create_content_example() {
	create_file_if_missing_from_stdin "contents/content_1.tex" <<'EOF'
% Example content file referenced in sec_1.tex
% Write in pure text as possible.
\section{Introduction}
Sample content referencing \variableFoobar.
EOF
}

create_compile_script() {
	create_file_if_missing_from_stdin "manuscript/compile.sh" <<'EOF'
#!/usr/bin/env bash

# Compile LaTeX document with bibliography support
# Usage: ./compile.sh <document.tex>

set -euo pipefail

DOCFILE="$1"

xelatex -synctex=1 -interaction=nonstopmode -file-line-error "$DOCFILE"
DOCFILE_BASE="${DOCFILE%.*}" # Remove extension to get base filename for bibtex
bibtex "$DOCFILE_BASE"
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "$DOCFILE"
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "$DOCFILE"
EOF
}

main() {
	ensure_no_args "$@"

	echo "Initializing LaTeX manuscript template in: $(pwd)"

	make_dir chapters
	make_dir manuscript
	make_dir contents

	create_readme
	create_main_tex
	create_config_tex
	create_bib
	create_chapter_section
	create_content_example
	create_compile_script

	# Add DVC stage for expanding LaTeX files
	dvc stage add -n expand_to_output \
	              -d contents \
	              -d chapters \
	              -d manuscript/main.tex \
	              -o manuscript/manuscript.tex \
	              '. expand_output.sh manuscript'
    dvc stage add -n compile \
                  -d manuscript/main.tex \
                  -d manuscript/manuscript.tex \
                  -o manuscript/main.pdf \
                  -o manuscript/manuscript.pdf \
                  -o manuscript/main.aux \
                  -o manuscript/manuscript.aux \
                  -o manuscript/main.bbl \
                  -o manuscript/manuscript.bbl \
                  -o manuscript/main.blg \
                  -o manuscript/manuscript.blg \
                  -o manuscript/main.synctex.gz \
                  -o manuscript/manuscript.synctex.gz \
                  'cd manuscript/ && . compile.sh main.tex && . compile.sh manuscript.tex'
	dvc stage add -n clean_n_zip manuscript \
	              -d manuscript/manuscript.pdf \
				  -o latex-manuscript.zip \
				  '. clean_n_zip.sh'

	echo "Done. Review the generated files and start writing!"
}

main "$@"

