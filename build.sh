#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p app/static/yolo
mkdir -p app/static/data
mkdir -p app/static/images/upload

echo "Setting up placeholder files..."
# Create placeholder files for models
touch app/static/yolo/yolov3.cfg
touch app/static/yolo/yolo.names
touch app/static/data/d2v_v4.model

echo "Build complete!"
echo "NOTE: You need to manually upload the following files after deployment:"
echo "  - app/static/yolo/yolov3.cfg"
echo "  - app/static/yolo/yolov3_last.weights"
echo "  - app/static/yolo/yolo.names"
echo "  - app/static/data/d2v_v4.model"