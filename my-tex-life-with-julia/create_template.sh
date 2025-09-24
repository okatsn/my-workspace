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

create_file_if_missing() {
	# Create a file with provided content only if it does not already exist.
	local file_path="$1"
	local content="$2"
	if [ -f "$file_path" ]; then
		echo "File exists (skip): $file_path"
	else
		printf "%s" "$content" > "$file_path"
		echo "Created file: $file_path"
	fi
}

create_readme() {
	local file="README.md"
	local content="Following the practice below to safely share the entire script:\n\n- write your manuscript in *chapter* files\n- include tex files of *chapter* in \`main.tex\`\n- (optional) include *contents* files in a *chapter* file to better organize your idea.\n- To create the \`output.tex\`: \`latexpand -o output.tex main.tex\`\n- share \`output.tex\` rather than \`main.tex\`\n\n"
	create_file_if_missing "$file" "$content"
}

create_main_tex() {
	local file="manuscript/main.tex"
	# Keep minimal viable example; includes config + one chapter file.
	local content
	content="% This is main.tex, the simplest LaTeX document\n"
	content+="\\documentclass{article}\n"
	content+="% Bring in configuration macros\n"
	content+="\\input{./config.tex}\n\n"
	content+="\\begin{document}\n\n"
	content+="\\title{Title Placeholder}\n\\author{Author Name}\n\\date{\\today}\n\n"
	content+="\\maketitle\n\n"
	content+="\\tableofcontents\n\n"
	content+="% Include chapter sections\n"
	content+="\\input{../chapters/sec_1.tex}\n\n"
	content+="% ... add more chapter inputs here ...\n\n"
	content+="\\end{document}\n"
	create_file_if_missing "$file" "$content"
}

create_config_tex() {
	local file="manuscript/config.tex"
	local content="% Example macro configuration file\n\\def\\variableFoobar {Foobar2000}\n"
	create_file_if_missing "$file" "$content"
}

create_bib() {
	local file="manuscript/main.bib"
	local content="% main.bib -- add your bibliography entries here\n"
	create_file_if_missing "$file" "$content"
}

create_chapter_section() {
	local file="chapters/sec_1.tex"
	local content="% sec_1.tex includes a single content file as an example\n\\input{../contents/content_1.tex}\n"
	create_file_if_missing "$file" "$content"
}

create_content_example() {
	local file="contents/content_1.tex"
	local content="% Example content file referenced in sec_1.tex\n\\section{Introduction}\nSample content referencing \\variableFoobar.\n"
	create_file_if_missing "$file" "$content"
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

	echo "Done. Review the generated files and start writing!"
}

main "$@"

