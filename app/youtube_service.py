"""
YouTube API Service for recipe videos
"""
import os
import json
import requests
from typing import List, Dict, Optional
from urllib.parse import urlencode
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeService:
    """Service for fetching recipe videos from YouTube"""
    
    def __init__(self, api_key: str = None):
        """Initialize YouTube service"""
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY', 'AIzaSyAASxTSqfFFIHF0hzyGMEDWsVSskLyyMgo')
        self.youtube = None
        self._init_service()
    
    def _init_service(self):
        """Initialize YouTube API service"""
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        except Exception as e:
            print(f"Failed to initialize YouTube service: {e}")
    
    def search_recipe_videos(self, recipe_name: str, max_results: int = 3) -> List[Dict]:
        """
        Search for recipe videos on YouTube
        
        Returns list of video dictionaries with:
        - video_id
        - title
        - description
        - thumbnail_url
        - channel_title
        - duration (if available)
        """
        if not self.youtube:
            return self._fallback_search(recipe_name)
        
        try:
            # Search for videos
            search_query = f"how to cook {recipe_name} recipe"
            search_response = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoDuration='short',  # Prefer shorter videos
                relevanceLanguage='en',
                safeSearch='strict'
            ).execute()
            
            videos = []
            video_ids = []
            
            # Process search results
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    video_ids.append(video_id)
                    
                    video = {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:200] + '...',
                        'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                        'channel_title': item['snippet']['channelTitle'],
                        'embed_url': f'https://www.youtube.com/embed/{video_id}'
                    }
                    videos.append(video)
            
            # Get additional details like duration
            if video_ids:
                try:
                    videos_response = self.youtube.videos().list(
                        part='contentDetails',
                        id=','.join(video_ids)
                    ).execute()
                    
                    for i, item in enumerate(videos_response.get('items', [])):
                        if i < len(videos):
                            duration = item['contentDetails']['duration']
                            videos[i]['duration'] = self._parse_duration(duration)
                except:
                    pass
            
            return videos
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return self._fallback_search(recipe_name)
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return self._fallback_search(recipe_name)
    
    def _parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to human readable format"""
        # Duration format: PT#M#S
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours, minutes, seconds = match.groups()
            parts = []
            if hours:
                parts.append(f"{hours}h")
            if minutes:
                parts.append(f"{minutes}m")
            if seconds:
                parts.append(f"{seconds}s")
            return ' '.join(parts) if parts else 'Unknown'
        return duration
    
    def _fallback_search(self, recipe_name: str) -> List[Dict]:
        """Fallback search when YouTube API is not available"""
        # Return mock data with actual YouTube search URLs
        base_url = "https://www.youtube.com/results?"
        search_params = urlencode({'search_query': f'how to cook {recipe_name} recipe'})
        search_url = base_url + search_params
        
        # Generate unique video IDs to avoid duplicates
        import hashlib
        base_id = hashlib.md5(recipe_name.encode()).hexdigest()[:8]
        
        videos = []
        for i in range(3):
            videos.append({
                'video_id': f'{base_id}_v{i}',
                'title': f'How to Make {recipe_name} - Recipe {i+1}',
                'description': f'Learn how to make delicious {recipe_name} with this easy step-by-step recipe tutorial...',
                'thumbnail_url': '/static/images/video_placeholder.svg',
                'channel_title': 'Cooking Channel',
                'embed_url': search_url if i == 0 else f'{search_url}&variation={i}',
                'duration': '5m 30s',
                'is_fallback': True
            })
        
        return videos
    
    def get_recipe_video_url(self, recipe_name: str) -> Optional[str]:
        """Get the best video URL for a recipe"""
        videos = self.search_recipe_videos(recipe_name, max_results=1)
        if videos:
            return videos[0]['embed_url']
        return None
    
    def get_step_by_step_videos(self, recipe_name: str, steps: List[str]) -> Dict[str, str]:
        """
        Get videos for specific recipe steps
        Returns dict mapping step number to video URL
        """
        step_videos = {}
        
        # For key steps, try to find specific technique videos
        technique_keywords = ['chop', 'dice', 'sauté', 'boil', 'fry', 'bake', 'grill', 
                            'steam', 'roast', 'simmer', 'whisk', 'fold', 'knead']
        
        for i, step in enumerate(steps[:3]):  # Limit to first 3 steps to avoid API quota
            # Check if step contains a technique
            for technique in technique_keywords:
                if technique in step.lower():
                    videos = self.search_recipe_videos(
                        f"{technique} technique cooking", 
                        max_results=1
                    )
                    if videos:
                        step_videos[str(i)] = videos[0]['embed_url']
                    break
        
        return step_videos

# Global instance
youtube_service = None

def get_youtube_service():
    """Get or create YouTube service instance"""
    global youtube_service
    if youtube_service is None:
        youtube_service = YouTubeService()
    return youtube_service