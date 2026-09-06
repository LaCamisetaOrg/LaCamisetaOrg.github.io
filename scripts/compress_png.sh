#!/bin/bash

# Usage: ./compress_png.sh output_dir input1.png [input2.png ...]
# Compresses PNG(s) to 300KB or less using ImageMagick

set -e

TARGET_KB=300
TARGET_BYTES=$((TARGET_KB * 1024))

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 output_dir input1.png [input2.png ...]"
  exit 1
fi

OUTPUT_DIR="$1"
shift

mkdir -p "$OUTPUT_DIR"

under_target() { [[ $(stat -c%s "$1") -le "$TARGET_BYTES" ]]; }
size_kb()      { echo $(( $(stat -c%s "$1") / 1024 )); }

compress_one() {
  local INPUT="$1"
  local OUTPUT="$OUTPUT_DIR/$(basename "$INPUT")"

  if [[ ! -f "$INPUT" ]]; then
    echo "Error: file not found: $INPUT"
    return 1
  fi

  echo "$INPUT: $(size_kb "$INPUT")KB — compressing..."

  # Step 1: strip + quantize 128 colors + max compression
  convert "$INPUT" -strip -quantize transparent -colors 128 -define png:compression-level=9 "$OUTPUT"
  echo "  after quantize+compress: $(size_kb "$OUTPUT")KB"
  under_target "$OUTPUT" && { echo "  done."; return 0; }

  # Step 2: binary search on resize scale
  local MIN_SCALE=10 MAX_SCALE=95 BEST_SCALE=10 MID
  while [[ "$MIN_SCALE" -le "$MAX_SCALE" ]]; do
    MID=$(( (MIN_SCALE + MAX_SCALE) / 2 ))
    convert "$INPUT" -strip -resize "${MID}%" -quantize transparent -colors 128 \
      -define png:compression-level=9 "$OUTPUT"
    if under_target "$OUTPUT"; then
      BEST_SCALE="$MID"
      MIN_SCALE=$(( MID + 1 ))
    else
      MAX_SCALE=$(( MID - 1 ))
    fi
  done

  convert "$INPUT" -strip -resize "${BEST_SCALE}%" -quantize transparent -colors 128 \
    -define png:compression-level=9 "$OUTPUT"

  if under_target "$OUTPUT"; then
    echo "  after resize ${BEST_SCALE}%: $(size_kb "$OUTPUT")KB — done."
  else
    echo "  Skipping $INPUT: could not reach ${TARGET_KB}KB (got $(size_kb "$OUTPUT")KB)."
    rm -f "$OUTPUT"
    return 1
  fi
}

for INPUT in "$@"; do
  compress_one "$INPUT" || true
done
