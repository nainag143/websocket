import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db import connection
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.room_group_name = f'chat_{self.agent_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_messages_for_agent(self.agent_id)
        for msg in messages:
            await self.send(text_data=json.dumps(msg))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        user_id = data['user_id']
        contact_id = data.get('contact_id')
        message = data['message']
        message_type = data['message_type']  # 'in' or 'out'
        attachment = data.get('attachment')

        await self.save_message(user_id, self.agent_id, contact_id, message, message_type, attachment)

        response = {
            'user_id': user_id,
            'agent_id': self.agent_id,
            'contact_id': contact_id,
            'message_type': message_type,
            'message': message,
            'attachment': attachment,
            'created_date': str(timezone.now())
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                **response
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_messages_for_agent(self, agent_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, agent_id, contact_id, message_type, message, attachment, created_date
                FROM chat_history
                WHERE agent_id = %s
                ORDER BY created_date ASC
            """, [agent_id])
            rows = cursor.fetchall()

        return [
            {
                'id': row[0],
                'user_id': row[1],
                'agent_id': row[2],
                'contact_id': row[3],
                'message_type': row[4],
                'message': row[5],
                'attachment': row[6],
                'created_date': str(row[7])
            } for row in rows
        ]

    @sync_to_async
    def save_message(self, user_id, agent_id, contact_id, message, message_type, attachment):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO chat_history (user_id, agent_id, contact_id, message_type, message, attachment, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [user_id, agent_id, contact_id, message_type, message, attachment, timezone.now()])
