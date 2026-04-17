import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.customer_id = self.scope['url_route']['kwargs'].get('customer_id')
        if self.customer_id:
            self.room_group_name = f'chat_support_{self.customer_id}'
        else:
            self.room_group_name = 'chat_staff_admin'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        data_type = data.get('type', 'chat_message')

        if data_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'sender_id': self.user.id,
                    'is_typing': data.get('is_typing')
                }
            )
        elif data_type == 'message_read':
            # တစ်ဖက်လူ စာဖတ်လိုက်ကြောင်း Signal ပေးပို့ခြင်း
            await self.mark_messages_as_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_read_update',
                    'reader_id': self.user.id
                }
            )
        elif data_type == 'chat_message':
            message_text = data['message']
            msg_obj = await self.save_message(message_text)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': msg_obj.id,
                    'message': message_text,
                    'sender_id': self.user.id,
                    'sender_name': self.user.username,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_read_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, text):
        customer = None
        if self.customer_id:
            customer = User.objects.get(id=self.customer_id)
            
        return Message.objects.create(
            user=self.user,
            customer=customer,
            text=text,
            channel='support' if self.customer_id else 'staff_admin',
            is_staff_response=self.user.is_staff or self.user.is_superuser
        )

    @database_sync_to_async
    def mark_messages_as_read(self):
        if self.customer_id:
            is_staff = self.user.is_staff or self.user.is_superuser
            # တစ်ဖက်လူပို့ထားသော message များကိုသာ ဖတ်ပြီးသားအဖြစ် သတ်မှတ်ရန်
            Message.objects.filter(
                channel='support',
                customer_id=self.customer_id,
                is_staff_response=not is_staff,
                is_read=False
            ).update(is_read=True)