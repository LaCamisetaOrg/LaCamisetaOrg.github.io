#!/bin/bash
set -euo pipefail

usage() {
  echo "Usage:"
  echo "  $0 <background.png> <layer.png>       # single combination"
  echo "  $0                                     # all combinations from backgrounds/ and layers/"
  exit 1
}

scale_layer() {
  local layer="$1"
  local w h scaled
  w=$(identify -format "%w" "$layer")
  h=$(identify -format "%h" "$layer")
  scaled_w=$(( w * 140 / 100 ))
  scaled_h=$(( h * 140 / 100 ))
  scaled=$(mktemp /tmp/layer_scaled_XXXXXX.png)
  convert "$layer" -resize "${scaled_w}x${scaled_h}!" "$scaled"
  echo "$scaled"
}

single() {
  local background="$1" layer="$2"
  local bg_base layer_base output scaled
  bg_base="$(basename "${background%.*}")"
  layer_base="$(basename "${layer%.*}")"
  output="${bg_base}_${layer_base}.png"
  scaled=$(scale_layer "$layer")
  composite -gravity Center "$scaled" "$background" "$output"
  rm "$scaled"
  echo "$output"
}

batch() {
  local backgrounds_dir="backgrounds"
  local layers_dir="layers"
  local output_dir="outputs"

  [ -d "$backgrounds_dir" ] || { echo "Error: '$backgrounds_dir' directory not found"; exit 1; }
  [ -d "$layers_dir" ]     || { echo "Error: '$layers_dir' directory not found"; exit 1; }

  mkdir -p "$output_dir"

  local count=0
  for background in "$backgrounds_dir"/*.png; do
    [ -f "$background" ] || { echo "No PNGs found in $backgrounds_dir"; exit 1; }
    for layer in "$layers_dir"/*.png; do
      [ -f "$layer" ] || { echo "No PNGs found in $layers_dir"; exit 1; }
      local bg_base layer_base output
      bg_base="$(basename "${background%.*}")"
      layer_base="$(basename "${layer%.*}")"
      output="$output_dir/${bg_base}_${layer_base}.png"
      scaled=$(scale_layer "$layer")
      composite -gravity Center "$scaled" "$background" "$output"
      rm "$scaled"
      echo "$output"
      (( count++ )) || true
    done
  done

  echo "Done: $count image(s) generated in '$output_dir/'"
}

if [ $# -eq 2 ]; then
  single "$1" "$2"
elif [ $# -eq 0 ]; then
  batch
else
  usage
fi
