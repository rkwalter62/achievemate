# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import sync_to_async
import re
import requests
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(f"[WebSocket] Connecting to room: {self.room_name}")
        self.uid, self.cid =await self.extract_uid_cid(self.room_name)
        print(f"[WebSocket] Extracted UID: {self.uid}, CID: {self.cid}")
        self.room_group_name = 'chat_%s' % self.room_name
      
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(f"[WebSocket] Added to group: {self.room_group_name}")

        await self.accept()
        print(f"[WebSocket] Connection accepted for {self.room_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"[WebSocket] Received message: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            print(f"[WebSocket] Parsed message: {message}")
            print(f"[WebSocket] UID: {self.uid}, CID: {self.cid}")
            
            # Send immediate acknowledgment
            await self.send(text_data=json.dumps({
                'status': 'thinking',
                'message': 'Coach is thinking...'
            }))
            print(f"[WebSocket] Sent thinking status")
            
            # Save user message first
            await self.save_user_message(message)
            print(f"[WebSocket] Saved user message")
            
            # Call AI expert server and get response
            print(f"[WebSocket] Calling AI API...")
            ai_response = await self.getting_repsonse_by_api(self.cid,message)
            print(f"[WebSocket] Got AI response: {ai_response[:100]}...")
            
            # Generate speech audio (TTS) for coach response
            audio_result = await self.generate_speech_audio(ai_response, self.cid)
            print(f"[WebSocket] TTS Result: {audio_result}")
            
            # Send AI response to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_response,
                    'audio_url': audio_result.get('audio_url'),
                    'use_browser_tts': audio_result.get('status') == 'fallback_to_browser',
                    'tts_text': audio_result.get('text'),
                    'voice_type': audio_result.get('voice_type')
                }
            )
            print(f"[WebSocket] Sent AI response to group")
            
        except Exception as e:
            print(f"[WebSocket ERROR] Error in receive: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error response
            await self.send(text_data=json.dumps({
                'message': 'Sorry, I encountered an error. Please try again.'
            }))

    async def chat_message(self, event):
        message = event['message']
        audio_url = event.get('audio_url')
        use_browser_tts = event.get('use_browser_tts', False)
        tts_text = event.get('tts_text')
        voice_type = event.get('voice_type')
        
        print(f"[WebSocket] Inside chat_message method")
        print(f"[WebSocket] Message to send: {message[:100]}...")
        print(f"[WebSocket] Audio URL: {audio_url}")
        print(f"[WebSocket] Use browser TTS: {use_browser_tts}")
        print(f"[WebSocket] Voice type: {voice_type}")
        if audio_url:
            print(f"[WebSocket] Sending audio URL: {audio_url}")
        elif use_browser_tts:
            print(f"[WebSocket] Falling back to browser TTS with voice: {voice_type}")
        
        try:
            # Send message to WebSocket
            await self.save_chat_message(message)
            print(f"[WebSocket] Saved chat message to DB")
            
            response_data = {'message': message}
            
            # Add audio/TTS data
            if audio_url:
                response_data['audio_url'] = audio_url
            
            if use_browser_tts:
                response_data['use_browser_tts'] = True
                response_data['tts_text'] = tts_text or message
                response_data['voice_type'] = voice_type or 'female'
            
            await self.send(text_data=json.dumps(response_data))
            print(f"[WebSocket] Sent message to client")
            
        except Exception as e:
            print(f"[WebSocket ERROR] Error in chat_message: {e}")
            import traceback
            traceback.print_exc()
    
    async def extract_uid_cid(self, s):
        # Using regular expression to extract numbers asynchronously
        pattern = re.compile(r'room_(\d+)_(\d+)')
        match = pattern.match(s)
        if match:
            uid = int(match.group(1))
            cid = int(match.group(2))
            return uid, cid
        else:
            return None, None

    @sync_to_async
    def save_chat_message(self, message):
        from achievemate_app.models import Chat
        # Save the chat message to the database
        Chat.objects.create(
            chat_text=repr(message)[1:-1],
            user_type='coach',
            user_id=self.uid,
            coach_id=self.cid
        )
    
    @sync_to_async
    def save_user_message(self, message):
        from achievemate_app.models import Chat
        # Save the user message to the database
        Chat.objects.create(
            chat_text=message,
            user_type='user',
            user_id=self.uid,
            coach_id=self.cid
        )
    @sync_to_async
    def getting_repsonse_by_api(self,coach_id,query):
        from achievemate_app.models import AiCoach
        import random
        
        # Save the chat message to the database
        print("Inside API CALLING",coach_id,query)
        current_coach=AiCoach.objects.get(id=coach_id)
        expertise=current_coach.coach_expertise
        print(expertise)
        
        # Fallback responses for local testing
        fallback_responses = {
            'Life Coaching Experts': [
                f"Thanks for your question about '{query}'. As a life coach, I'd suggest breaking this down into smaller, manageable steps. What specific aspect would you like to focus on first?",
                f"That's a great question! Let's explore '{query}' together. Can you tell me what outcome you're hoping to achieve?",
                f"I appreciate you reaching out about '{query}'. Let's work on creating a personalized action plan. What's your current situation?"
            ],
            'Career Experts': [
                f"Excellent career question about '{query}'! Let's discuss your professional goals and how to achieve them. What's your timeline?",
                f"Thanks for asking about '{query}'. Career development is a journey. What skills or areas do you want to focus on?",
                f"Great to help with '{query}'! Let's create a career roadmap. What's your ultimate professional goal?"
            ],
            'Business Idea Experts': [
                f"Interesting business question about '{query}'! Let's analyze the market potential and strategy. What's your business model?",
                f"Thanks for the business inquiry about '{query}'. Let's explore the opportunities and challenges. What's your target market?",
                f"Great business question about '{query}'! Let's develop a strategic approach. What resources do you have available?"
            ]
        }
        # Try to call production API first, with fallback to local responses
        try:
            print(f"Calling API for expertise: {expertise}")
            
            # Map expertise to API endpoints
            api_endpoints = {
                "Life Coaching Experts": "https://api.achievemate.ai/Achievemate/life_coaching_expert",
                "Career Experts": "https://api.achievemate.ai/Achievemate/Career_expert", 
                "Business Idea Experts": "https://api.achievemate.ai/Achievemate/business_expert",
                "Parenting Coach": "https://api.achievemate.ai/Achievemate/parenting_coach"
            }
            
            url = api_endpoints.get(expertise, api_endpoints["Life Coaching Experts"])
            payload = {'question': query}
            headers = {}
            
            print("Calling production API...")
            response = requests.request("POST", url, headers=headers, data=payload, timeout=20)
            data = response.json()
            answer = data.get('answer')
            
            if answer:
                print("Got response from production API")
                return answer
            else:
                raise Exception("No answer in API response")
                
        except Exception as e:
            print(f"Production API call failed: {e}")
            print(f"Exception type: {type(e).__name__}")
            print("Using fallback response for local testing")
            return f"Hi! I'm your {expertise.replace('Experts', 'Expert').replace('Life Coaching Expert', 'Life Coach')}. " + random.choice(fallback_responses.get(expertise, fallback_responses['Life Coaching Experts']))
        
        # Fallback for unknown expertise types
        print(f"Unknown expertise type: {expertise}, using Life Coaching fallback")
        return random.choice(fallback_responses['Life Coaching Experts'])
    
    @sync_to_async
    def generate_speech_audio(self, text, coach_id):
        """Generate speech audio for coach response"""
        try:
            from achievemate_app.tts_service import TTSService, get_coach_voice_type
            from achievemate_app.models import AiCoach
            
            # Get coach info
            coach = AiCoach.objects.get(id=coach_id)
            expertise = coach.coach_expertise
            
            # Get appropriate voice type for this coach
            voice_type = get_coach_voice_type(expertise)
            
            print(f"[TTS] Generating speech audio for {expertise} with {voice_type} voice")
            
            # Initialize TTS service
            tts_service = TTSService()
            
            # Generate speech audio
            result = tts_service.generate_speech(
                text=text,
                voice_type=voice_type,
                coach_expertise=expertise
            )
            
            if result.get('status') == 'success':
                print(f"[TTS] Speech audio generated: {result.get('audio_url')}")
            elif result.get('status') == 'fallback_to_browser':
                print(f"[TTS] Falling back to browser TTS")
            else:
                print(f"[TTS] Speech generation failed: {result}")
            
            return result
                
        except Exception as e:
            print(f"[TTS ERROR] Error generating speech audio: {e}")
            # Return fallback result
            return {
                'status': 'fallback_to_browser',
                'text': text,
                'voice_type': 'female'
            }

