"""
HeyGen API Service for Avatar Video Generation
"""
import requests
import json
import time
from django.conf import settings

class HeyGenService:
    def __init__(self):
        self.api_key = settings.HEYGEN_API_KEY
        self.base_url = settings.HEYGEN_BASE_URL
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_available_avatars(self):
        """Get list of available avatars (may require paid subscription)"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/avatar.list?is_public=true",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Avatar list access denied (code {response.status_code}). Using default public avatars.")
                return None
        except Exception as e:
            print(f"Error getting avatars: {e}")
            return None
    
    def get_available_voices(self):
        """Get list of available voices"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/voice.list",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting voices: {e}")
            return None
    
    def generate_avatar_video(self, text, avatar_id=None, voice_id=None):
        """Generate avatar video from text"""
        
        # Default avatar and voice (using public avatars)
        if not avatar_id:
            avatar_id = "Lina_Dress_Sitting_Side_public"  # Public female avatar
        if not voice_id:
            voice_id = "119caed25533477ba63822d5d1552d25"  # Public voice ID
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": text,
                    "voice_id": voice_id
                },
                "background": {
                    "type": "color",
                    "value": "#FFFFFF"
                }
            }],
            "dimension": {
                "width": 1280,
                "height": 720
            },
            "aspect_ratio": "16:9"
        }
        
        try:
            # Submit video generation request
            response = requests.post(
                f"{self.base_url}/v2/video/generate",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                video_id = result.get('data', {}).get('video_id')
                
                if video_id:
                    # Poll for completion
                    return self.wait_for_video_completion(video_id)
            
            print(f"Error generating video: {response.text}")
            return None
            
        except Exception as e:
            print(f"Error in generate_avatar_video: {e}")
            return None
    
    def wait_for_video_completion(self, video_id, max_wait_time=60):
        """Wait for video generation to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/v1/video_status.get?video_id={video_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('data', {}).get('status')
                    
                    if status == 'completed':
                        video_url = result.get('data', {}).get('video_url')
                        return {
                            'status': 'completed',
                            'video_url': video_url,
                            'video_id': video_id
                        }
                    elif status == 'failed':
                        return {
                            'status': 'failed',
                            'error': result.get('data', {}).get('error', 'Unknown error')
                        }
                    
                    # Still processing, wait a bit
                    time.sleep(2)
                else:
                    print(f"Error checking status: {response.text}")
                    break
                    
            except Exception as e:
                print(f"Error waiting for completion: {e}")
                break
        
        return {
            'status': 'timeout',
            'error': 'Video generation timed out'
        }

# Default coach avatar mappings (using public avatars)
COACH_AVATAR_MAP = {
    'Life Coaching Experts': {
        'avatar_id': 'Lina_Dress_Sitting_Side_public',  # Female coach for life coaching
        'voice_id': '119caed25533477ba63822d5d1552d25'
    },
    'Career Experts': {
        'avatar_id': 'Wayne_20240711_public',  # Professional male avatar
        'voice_id': '119caed25533477ba63822d5d1552d25'
    },
    'Business Idea Experts': {
        'avatar_id': 'Wayne_20240711_public',  # Business professional
        'voice_id': '119caed25533477ba63822d5d1552d25'
    }
}