#!/bin/bash

# Directory containing the videos
VIDEO_DIR="frontend/public/examples"
# Directory for thumbnails (same as videos)
THUMB_DIR="frontend/public/examples"

# Create thumbnails directory if it doesn't exist
mkdir -p "$THUMB_DIR"

# Process each MP4 file
for video in "$VIDEO_DIR"/*.mp4; do
    if [ -f "$video" ]; then
        # Get the filename without extension
        filename=$(basename "$video" .mp4)
        
        # Use different seek positions for specific videos
        if [[ "$filename" == "sin-graph" || "$filename" == "text-reveal" ]]; then
            # Get duration in seconds
            duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video")
            # Calculate 80% of duration
            seek_time=$(awk "BEGIN {printf \"%.2f\", $duration * 0.8}")
            # Extract frame at 80% of duration
            ffmpeg -ss $seek_time -i "$video" -frames:v 1 "$THUMB_DIR/${filename}-thumbnail.jpg"
        else
            # Use last frame for other videos
            ffmpeg -sseof -3 -i "$video" -update 1 -frames:v 1 "$THUMB_DIR/${filename}-thumbnail.jpg"
        fi
        
        echo "Generated thumbnail for $filename"
    fi
done

echo "All thumbnails generated successfully!" 