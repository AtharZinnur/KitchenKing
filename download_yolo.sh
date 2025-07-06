#!/bin/bash

# Create directories
mkdir -p app/static/yolo

# Download YOLOv3 configuration
echo "Downloading YOLOv3 configuration..."
wget -O app/static/yolo/yolov3.cfg https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg

# Download YOLOv3 weights (this is large ~240MB)
echo "Downloading YOLOv3 weights..."
wget -O app/static/yolo/yolov3.weights https://pjreddie.com/media/files/yolov3.weights

# Download COCO class names
echo "Downloading COCO class names..."
wget -O app/static/yolo/coco.names https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

echo "Download complete!"