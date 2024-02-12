# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
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
        #ai_response = await get_ai_response(message)
        # Send AI response to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message':"hello ,MEssage recieved we reply you soon"
            }
        )

    async def chat_message(self, event):
        message = event['message']
        print("Inside chat message")
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


# # consumers.py
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from achievemate_app.models import *
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         user_type = text_data_json['user_type']
#         user_id = text_data_json['user_id']
#         coach_id = text_data_json['coach_id']
        
#         # Save the message to the database
#         await self.save_message(message, user_type, user_id, coach_id)

#         # Broadcast the message to all connected clients
#         await self.channel_layer.group_send(
#             'chat_group',
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'user_type': user_type,
#                 'user_id': user_id,
#                 'coach_id': coach_id
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         user_type = event['user_type']
#         user_id = event['user_id']
#         coach_id = event['coach_id']

#         await self.send(text_data=json.dumps({
#             'message': message,
#             'user_type': user_type,
#             'user_id': user_id,
#             'coach_id': coach_id
#         }))

#     async def save_message(self, message, user_type, user_id, coach_id):
#         # Save the message to the database based on user type
#         if user_type == 'user':
#             user = Users.objects.get(id=user_id)
#             Chat.objects.create(chat_text=message, user_type=user_type, user=user)
#         elif user_type == 'coach':
#             coach = AiCoach.objects.get(id=coach_id)
#             Chat.objects.create(chat_text=message, user_type=user_type, coach=coach)
