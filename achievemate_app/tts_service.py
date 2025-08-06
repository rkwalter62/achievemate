"""
Text-to-Speech Service for AI Coach Responses
Supports multiple TTS providers with fallback options
"""
import os
import hashlib
import requests
import json
from django.conf import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.media_root = settings.MEDIA_ROOT
        self.audio_dir = Path(self.media_root) / 'coach_audio'
        self.audio_dir.mkdir(exist_ok=True)
        
    def generate_speech(self, text, voice_type='female', coach_expertise=None):
        """
        Generate speech audio from text using available TTS services
        
        Args:
            text (str): Text to convert to speech
            voice_type (str): 'male' or 'female' voice
            coach_expertise (str): Coach type for voice selection
            
        Returns:
            dict: {'status': 'success/failed', 'audio_url': url, 'error': error_msg}
        """
        try:
            # Create unique filename based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            filename = f"coach_speech_{text_hash}.mp3"
            audio_path = self.audio_dir / filename
            
            # Check if audio already exists (caching)
            if audio_path.exists():
                audio_url = f"/media/coach_audio/{filename}"
                return {
                    'status': 'success',
                    'audio_url': audio_url,
                    'cached': True
                }
            
            # Try different TTS services in order of preference (most realistic first)
            audio_data = None
            
            # Option 1: ElevenLabs (highest quality, most realistic)
            audio_data = self._try_elevenlabs_tts(text, voice_type)
            
            # Option 2: OpenAI TTS (high quality, natural)
            if not audio_data:
                audio_data = self._try_openai_tts(text, voice_type)
            
            # Option 3: Google Cloud TTS (good quality)
            if not audio_data:
                audio_data = self._try_google_tts(text, voice_type)
            
            # Option 4: Azure Cognitive Services (good quality)
            if not audio_data:
                audio_data = self._try_azure_tts(text, voice_type)
            
            # Option 5: Free TTS service
            if not audio_data:
                audio_data = self._try_free_tts(text, voice_type)
            
            # Option 6: Built-in browser TTS (fallback handled in frontend)
            if not audio_data:
                return {
                    'status': 'fallback_to_browser',
                    'text': text,
                    'voice_type': voice_type
                }
            
            # Save audio file
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            
            audio_url = f"/media/coach_audio/{filename}"
            return {
                'status': 'success',
                'audio_url': audio_url,
                'cached': False
            }
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'fallback_to_browser': True,
                'text': text,
                'voice_type': voice_type
            }
    
    def _try_elevenlabs_tts(self, text, voice_type):
        """Try ElevenLabs TTS API (most realistic voices)"""
        try:
            api_key = getattr(settings, 'ELEVENLABS_API_KEY', None)
            if not api_key:
                return None
            
            # ElevenLabs voice IDs for high-quality voices
            voice_ids = {
                'female': 'EXAVITQu4vr4xnSDxMaL',  # Bella - warm, friendly female
                'male': 'ErXwobaYiN019PkySvjV'     # Antoni - professional male
            }
            
            voice_id = voice_ids.get(voice_type, voice_ids['female'])
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': api_key
            }
            
            payload = {
                'text': text,
                'model_id': 'eleven_monolingual_v1',
                'voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.5
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info("ElevenLabs TTS generation successful")
                return response.content
            else:
                logger.warning(f"ElevenLabs TTS failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.warning(f"ElevenLabs TTS failed: {e}")
        
        return None
    
    def _try_openai_tts(self, text, voice_type):
        """Try OpenAI TTS API (high quality, natural voices)"""
        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                return None
            
            # OpenAI voice options
            voice_names = {
                'female': 'nova',  # Warm, engaging female voice
                'male': 'onyx'     # Deep, authoritative male voice
            }
            
            voice = voice_names.get(voice_type, voice_names['female'])
            
            url = "https://api.openai.com/v1/audio/speech"
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'tts-1',
                'input': text,
                'voice': voice,
                'response_format': 'mp3'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info("OpenAI TTS generation successful")
                return response.content
            else:
                logger.warning(f"OpenAI TTS failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.warning(f"OpenAI TTS failed: {e}")
        
        return None
    
    def _try_google_tts(self, text, voice_type):
        """Try Google Cloud Text-to-Speech API"""
        try:
            api_key = getattr(settings, 'GOOGLE_CLOUD_TTS_API_KEY', None)
            if not api_key:
                return None
            
            # Voice selection based on type
            voice_config = {
                'female': {'name': 'en-US-Standard-C', 'ssmlGender': 'FEMALE'},
                'male': {'name': 'en-US-Standard-B', 'ssmlGender': 'MALE'}
            }
            
            voice = voice_config.get(voice_type, voice_config['female'])
            
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
            
            payload = {
                'input': {'text': text},
                'voice': voice,
                'audioConfig': {'audioEncoding': 'MP3'}
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                import base64
                return base64.b64decode(result['audioContent'])
            
        except Exception as e:
            logger.warning(f"Google TTS failed: {e}")
        
        return None
    
    def _try_azure_tts(self, text, voice_type):
        """Try Azure Cognitive Services Text-to-Speech"""
        try:
            subscription_key = getattr(settings, 'AZURE_TTS_SUBSCRIPTION_KEY', None)
            region = getattr(settings, 'AZURE_TTS_REGION', 'eastus')
            
            if not subscription_key:
                return None
            
            # Voice selection
            voice_names = {
                'female': 'en-US-JennyNeural',
                'male': 'en-US-GuyNeural'
            }
            
            voice_name = voice_names.get(voice_type, voice_names['female'])
            
            url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
            
            headers = {
                'Ocp-Apim-Subscription-Key': subscription_key,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
            }
            
            ssml = f"""
            <speak version='1.0' xml:lang='en-US'>
                <voice name='{voice_name}'>
                    {text}
                </voice>
            </speak>
            """
            
            response = requests.post(url, headers=headers, data=ssml, timeout=30)
            
            if response.status_code == 200:
                return response.content
                
        except Exception as e:
            logger.warning(f"Azure TTS failed: {e}")
        
        return None
    
    def _try_free_tts(self, text, voice_type):
        """Try free TTS service"""
        try:
            # Use a free TTS API (VoiceRSS or similar)
            api_key = getattr(settings, 'VOICERSS_API_KEY', None)
            
            # If no API key, try a free service without authentication
            if not api_key:
                # Try Text-to-Speech API that doesn't require authentication
                # Note: These services often have rate limits
                
                # Option: Use gTTS alternative or similar free service
                # For now, return None to fallback to browser TTS
                return None
            
            # VoiceRSS implementation (if API key provided)
            url = "http://api.voicerss.org/"
            
            voice_codes = {
                'female': 'en-us-f',
                'male': 'en-us-m'
            }
            
            params = {
                'key': api_key,
                'src': text,
                'hl': voice_codes.get(voice_type, 'en-us-f'),
                'f': '44khz_16bit_mono',
                'c': 'mp3'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200 and 'audio' in response.headers.get('content-type', ''):
                return response.content
                
        except Exception as e:
            logger.warning(f"Free TTS failed: {e}")
        
        return None

# Coach voice mappings
COACH_VOICE_MAP = {
    'Life Coaching Experts': 'female',
    'Career Experts': 'male', 
    'Business Idea Experts': 'male',
    'Parenting Coach': 'female'
}

def get_coach_voice_type(coach_expertise):
    """Get appropriate voice type for coach"""
    return COACH_VOICE_MAP.get(coach_expertise, 'female')