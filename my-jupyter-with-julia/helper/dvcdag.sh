#!/usr/bin/env bash
set -e

# Usage examples:
#   ./dvcDag.sh                    # Generate dvc-dag-temp.png with Top-Bottom layout
#   ./dvcDag.sh -o mydag.png       # Generate mydag.png with Top-Bottom layout
#   ./dvcDag.sh -LR                # Generate dvc-dag-temp.png with Left-Right layout
#   ./dvcDag.sh -LR -o mydag.png   # Generate mydag.png with Left-Right layout
#   ./dvcDag.sh -TB -o mydag.png   # Generate mydag.png with Top-Bottom layout

# Pause before exit when the script fails so the caller can see the error.
# - Uses an EXIT trap to catch any non-zero exit (including explicit `exit 1`).
# - If running interactively it prompts the user to press Enter. In CI or
#   non-interactive environments it sleeps for 5 seconds instead.
trap 'rc=$?; if [ "$rc" -ne 0 ]; then
  echo "\nERROR: script exited with code $rc at $(date)" >&2
  if [ -n "$CI" ] || [ ! -t 1 ]; then
    echo "Non-interactive or CI environment detected; sleeping 5s before exit..." >&2
    sleep 5
  else
    read -rp "Press Enter to exit..."
  fi
fi' EXIT

# Show usage if help is requested
show_usage() {
  echo "Usage: $0 [-LR|-TB] [-o OUTPUT_FILE]"
  echo ""
  echo "Options:"
  echo "  -LR          - Use Left-Right graph direction"
  echo "  -TB          - Use Top-Bottom graph direction (default)"
  echo "  -o FILE      - Output PNG file (default: dvc-dag-temp.png)"
  echo "  -h, --help   - Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0                    # Generate dvc-dag-temp.png with Top-Bottom layout"
  echo "  $0 -o mydag.png       # Generate mydag.png with Top-Bottom layout"
  echo "  $0 -LR                # Generate dvc-dag-temp.png with Left-Right layout"
  echo "  $0 -LR -o mydag.png   # Generate mydag.png with Left-Right layout"
  echo "  $0 -TB -o mydag.png   # Generate mydag.png with Top-Bottom layout"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  show_usage
  exit 0
fi

# Parse arguments
OUTPUT_FILE="dvc-dag-temp.png"
DIRECTION="TB"  # Default to Top-Bottom

while [[ $# -gt 0 ]]; do
  case "$1" in
    -LR)
      DIRECTION="LR"
      shift
      ;;
    -TB)
      DIRECTION="TB"
      shift
      ;;
    -o)
      if [[ -z "$2" ]]; then
        echo "ERROR: -o requires an output filename" >&2
        show_usage
        exit 1
      fi
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      echo "ERROR: Unknown option '$1'" >&2
      show_usage
      exit 1
      ;;
  esac
done

echo "Generating DVC DAG visualization (direction: $DIRECTION)..."
dvc dag --dot | sed "s/digraph {/digraph {\n  rankdir=$DIRECTION;/" | dot -Tpng -o "$OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
  echo "✓ DAG visualization saved to: $OUTPUT_FILE"
else
  echo "ERROR: Failed to generate $OUTPUT_FILE" >&2
  exit 1
fi