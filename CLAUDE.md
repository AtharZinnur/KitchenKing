# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pic2Kitchen is a Flask-based web application that uses computer vision (YOLO) to detect food ingredients from uploaded photos and recommends recipes based on the detected ingredients using Doc2Vec similarity matching.

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Development mode
python -m app.app

# Production mode with gunicorn
gunicorn app.app:app --bind 127.0.0.1:8000
```

The application runs on http://127.0.0.1:8000 by default.

## Architecture Overview

### Machine Learning Pipeline
1. **Image Upload** → User uploads photo via web interface
2. **Object Detection** → YOLO model (`yolov3.cfg`, `yolov3_last.weights`) detects food ingredients
3. **Feature Extraction** → Detected ingredients are processed
4. **Recipe Matching** → Doc2Vec model (`d2v_v4.model`) finds similar recipes based on ingredients
5. **Results Display** → Top recipes shown with cooking instructions and videos

### Key Components

- **app/app.py**: Main Flask application with routes:
  - `/` - Homepage with upload form
  - `/send` - Handles image upload and processing
  - `/recipe` - Recipe list page
  
- **app/yolo.py**: YOLO object detection implementation
  - Loads YOLO configuration and weights
  - Detects objects in uploaded images
  - Saves predictions to `static/images/predict.jpg`

- **app/video_api.py**: Video API integration for recipe videos

### Data Dependencies

The application requires these data files (not included in repository):
- `./static/yolo/yolov3.cfg` - YOLO configuration
- `./static/yolo/yolov3_last.weights` - YOLO trained weights
- `./static/yolo/yolo.names` - Class names for detected objects
- Recipe JSON files referenced in the code

### Important Notes

1. **Path Handling**: The code uses Windows-style backslashes in some paths. When developing on Linux/Mac, these may need adjustment.

2. **Missing Files**: The YOLO model files and recipe data are not included in the repository and must be obtained separately.

3. **Authentication**: User authentication code is present but commented out. To enable it, uncomment the relevant sections in app.py and ensure database setup.

4. **File Upload**: Allowed file types are: txt, pdf, png, jpg, jpeg, gif. Upload directory is `static/images/upload/`.

5. **Model Loading**: The Doc2Vec model is loaded from `static/data/d2v_v4.model` at startup.