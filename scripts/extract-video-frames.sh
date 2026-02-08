#!/bin/bash
# Extract thumbnail frames from MP4 files for visual analysis
# Usage: ./extract-video-frames.sh /path/to/whatsapp/export

set -e

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${INPUT_DIR}/extracted-frames"

mkdir -p "$OUTPUT_DIR"

echo "Extracting frames from MP4 files in: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

count=0
for f in "$INPUT_DIR"/*.mp4; do
    [ -e "$f" ] || continue

    basename=$(basename "$f" .mp4)
    output="$OUTPUT_DIR/${basename}-frame.jpg"

    if [ ! -f "$output" ]; then
        ffmpeg -i "$f" -vframes 1 -q:v 2 "$output" -y -loglevel error
        echo "✓ $basename"
        ((count++))
    fi
done

echo ""
echo "Extracted $count frames to $OUTPUT_DIR"
echo ""
echo "Now you can analyze these with Claude Code:"
echo "  - Read individual frames with the Read tool"
echo "  - Or ask Claude to 'analyze the extracted video frames'"
