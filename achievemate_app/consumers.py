# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import sync_to_async
import re
import requests
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        self.uid, self.cid =await self.extract_uid_cid(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
      
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(text_data_json)
        print(message)
        # Call AI expert server and get response
        ai_response = await self.getting_repsonse_by_api(self.cid,message)
        # Send AI response to the group
        # user_message = Chat.objects.create(chat_text=message, user_type='user', user_id=uid, coach_id=cid)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message':ai_response
            }
        )

    async def chat_message(self, event):
        message = event['message']
        print("Inside chat message")
        # Send message to WebSocket
        await self.save_chat_message(message)
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
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
            chat_text=message,
            user_type='coach',
            user_id=self.uid,
            coach_id=self.cid
        )
    @sync_to_async
    def getting_repsonse_by_api(self,coach_id,query):
        from achievemate_app.models import AiCoach
        # Save the chat message to the database
        print("Inside API CALLING",coach_id,query)
        current_coach=AiCoach.objects.get(id=coach_id)
        expertise=current_coach.coach_expertise
        print(expertise)
        if expertise=="Life Coaching Experts":
            print("inside expertise")
            # url = "http://127.0.0.1:5000/life_coaching_expert"
            url = "http://3.220.247.187:9001/life_coaching_expert"

            payload = {'question': query}
            files=[
                
            ]
            headers = {}
            print("Aclling response")
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            data = response.json()
            print("Getting data")
    # Get the value of the "answer" key
            answer = data.get('answer')
            print("Answer is -------->",answer)
            return answer
        elif expertise=="Health Experts":
            print("inside expertise")
            # url = "http://127.0.0.1:5000/health_expert"
            url = "http://3.220.247.187:9001/health_expert"

            payload = {'question': query}
            files=[

            ]
            headers = {}
            print("Aclling response")
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            data = response.json()
            print("Getting data")
    # Get the value of the "answer" key
            answer = data.get('answer')
            print("Answer is -------->",answer)
            return answer
        elif expertise=="Business Idea Experts":
            print("inside expertise")
            # url = "http://127.0.0.1:5000/Business_expert"
            url = "http://3.220.247.187:9001/Business_expert"

            payload = {'question': query}
            files=[

            ]
            headers = {}
            print("Aclling response")
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            data = response.json()
            print("Getting data")
    # Get the value of the "answer" key
            answer = data.get('answer')
            print("Answer is -------->",answer)
            return answer
        elif expertise=="Career Experts":
            print("inside expertise")
            # url = "http://127.0.0.1:5000/Career_expert"
            url = "http://3.220.247.187:9001/Career_expert"

            payload = {'question': query}
            files=[

            ]
            headers = {}
            print("Aclling response")
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            data = response.json()
            print("Getting data")
    # Get the value of the "answer" key
            answer = data.get('answer')
            print("Answer is -------->",answer)
            return answer

