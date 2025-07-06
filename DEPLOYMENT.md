# Deployment Instructions for KitchenKing on Render

## Prerequisites
- GitHub repository connected to Render
- Render account with API key
- Large model files ready to upload

## Deployment Steps

### 1. Initial Deployment
The app is configured to deploy automatically from your GitHub repository.

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Click "Create Web Service"

### 2. Environment Variables
The following environment variables are automatically configured:
- `FLASK_ENV`: production
- `SECRET_KEY`: Auto-generated secure key
- `YOUTUBE_API_KEY`: Pre-configured (replace with your own if needed)
- `DATABASE_URL`: Automatically set by Render when database is created

### 3. Upload Model Files
After deployment, you need to manually upload the large model files:

1. Use Render's Shell feature or connect via SSH
2. Upload these files to their respective directories:
   - `app/static/yolo/yolov3.cfg`
   - `app/static/yolo/yolov3_last.weights` (236MB)
   - `app/static/yolo/yolo.names`
   - `app/static/data/d2v_v4.model`

### 4. Alternative: Using Cloud Storage
For large files, consider using cloud storage:
1. Upload model files to a service like Google Cloud Storage or AWS S3
2. Modify `build.sh` to download files during build
3. Add storage credentials as environment variables

## Monitoring
- Check deployment logs in Render dashboard
- Monitor the health endpoint at `/`
- Database connection is automatically managed by Render

## Troubleshooting
- If deployment fails, check the build logs
- Ensure all Python dependencies are in `requirements.txt`
- Verify model files are accessible
- Check database connection string format

## Updating
Push changes to your GitHub repository and Render will automatically redeploy.