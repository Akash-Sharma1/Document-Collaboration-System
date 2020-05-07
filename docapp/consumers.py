# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.branch_name = self.scope['url_route']['kwargs']['branch_name']
        self.room_group_name = 'chat_%s' % self.room_name+self.branch_name

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

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        #print("text")
        #print(text_data)
        #print("dictionary")
        #print(text_data_json)
        op = text_data_json['op']
        if op=="":
            return
        position = text_data_json['pos']
        time = text_data_json['time']
        name = text_data_json['name']
        word = text_data_json['word']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'op': op,
                'pos' :position,
                'time': time,
                'word': word,
                'name' : name
            }
        )
            
    # Receive message from room group
    async def chat_message(self, event):
        op = event['op']
        pos = event['pos']
        time = event['time']
        word = event['word']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
                'op': op,
                'pos' : pos,
                'time': time,
                'word': word,
                'name' : event['name']
        }))