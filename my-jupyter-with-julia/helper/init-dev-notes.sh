#!/bin/sh

# init-dev-notes.sh
#
# Initialize a minimal Logseq developer-notes graph.
#
# Usage:
#   ./init-dev-notes.sh TARGET_DIR
#   ./init-dev-notes.sh --force TARGET_DIR
#   ./init-dev-notes.sh --help

(
    set -eu

    usage() {
        cat <<'EOF'
Usage:
  ./init-dev-notes.sh [--force] TARGET_DIR
  ./init-dev-notes.sh --help

Initialize a minimal Logseq developer-notes graph under TARGET_DIR.

Options:
  -f, --force   Overwrite existing generated pages.
  -h, --help    Show this help message.

Creates:
  TARGET_DIR/
  ├── journals/
  └── pages/
      ├── ARCH.md
      ├── INDEX.md
      ├── REPORT.md
      ├── REVIEW.md
      └── DECISION.md

By default, existing files are preserved.
EOF
    }

    force=0

    create_page() {
        # Create page file ($1) from template ($2)
        file=$1
        template=$2

        # When the file already exists (-e "$file" is true), the function chooses not to overwrite it.
        # cat >/dev/null is essential to  read and discard standard input (stdin) so the pipeline or calling script doesn't stall or leak unread data.
        if [ -e "$file" ] && [ "$force" -ne 1 ]; then
            printf 'keep       %s\n' "$file"
            return
        fi

        if [ -e "$file" ]; then
            action=overwrite
        else
            action=create
        fi

        cp "$template" "$file"
        printf '%-10s %s\n' "$action" "$file"
    }


    while [ "$#" -gt 0 ]; do
        case "$1" in
            -f|--force)
                force=1
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            --)
                shift
                break
                ;;
            -*)
                printf 'Unknown option: %s\n\n' "$1" >&2
                usage >&2
                exit 2
                ;;
            *)
                break
                ;;
        esac
    done

    if [ "$#" -ne 1 ]; then
        usage >&2
        exit 2
    fi
    # # Explain why this is path stable:
    # - CDPATH=: Temporarily clears the CDPATH environment variable for the cd command. If CDPATH is set in the user's environment, cd can navigate to an unexpected directory
    # - dirname "$0": Extracts the directory path component of $0 (the path used to invoke the script)
    # - cd ... && pwd: Navigates to the directory containing the script and outputs its absolute path. The && ensures pwd only runs if cd succeeds.
    # - The current working directory does not change because the expression is wrapped inside a command substitution $(...), the commands execute inside an isolated subshell.
    script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
    template_dir=$script_dir/logseq-dev-notes-templates

    target_dir=$1
    pages_dir=$target_dir/pages
    journals_dir=$target_dir/journals

    mkdir -p "$pages_dir" "$journals_dir"


    for name in ARCH REPORT DECISION REVIEW INDEX; do
        create_page \
            "$pages_dir/$name.md" \
            "$template_dir/$name.md"
    done

    for name in AGENTS; do
        create_page \
            "$target_dir/$name.md" \
            "$template_dir/$name.md"
    done

    printf 'Developer notes initialized at %s\n' "$target_dir"
)