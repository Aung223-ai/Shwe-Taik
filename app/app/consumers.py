import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import Message
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user', AnonymousUser())
        if not user or not user.is_authenticated:
            await self.close()
            return

        path = self.scope['path']
        self.channel_name_group = None
        self.channel_kind = None
        self.customer_id = None

        if 'staff_admin' in path:
            self.channel_kind = 'staff_admin'
            self.channel_name_group = 'chat_staff_admin'
        elif 'support_all' in path:
            if not user.is_staff and not user.is_superuser:
                await self.close()
                return
            self.channel_kind = 'support_all'
            self.channel_name_group = 'chat_support_staff'
        elif 'support' in path:
            self.channel_kind = 'support'
            customer_id = self.scope['url_route']['kwargs'].get('customer_id')
            self.customer_id = int(customer_id)
            # Customers can only join their own room
            if (not user.is_staff and not user.is_superuser) and user.id != self.customer_id:
                await self.close()
                return
            self.channel_name_group = f'chat_support_{self.customer_id}'

        if not self.channel_name_group:
            await self.close()
            return

        await self.channel_layer.group_add(self.channel_name_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.channel_name_group:
            await self.channel_layer.group_discard(self.channel_name_group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope['user']
        data = json.loads(text_data or '{}')
        message = (data.get('message') or '').strip()
        if not message:
            return

        target_customer_id = data.get('customer_id')
        msg = await self._save_message(user, message, target_customer_id)

        await self.channel_layer.group_send(
            self.channel_name_group,
            {
                'type': 'chat_message',
                'message': msg['text'],
                'sender_id': msg['user_id'],
                'sender_name': msg['username'],
                'created_at': msg['created_at'],
                'customer_id': msg['customer_id'],
            }
        )
        if self.channel_kind == 'support' and self.channel_name_group != 'chat_support_staff':
            await self.channel_layer.group_send(
                'chat_support_staff',
                {
                    'type': 'chat_message',
                    'message': msg['text'],
                    'sender_id': msg['user_id'],
                    'sender_name': msg['username'],
                    'created_at': msg['created_at'],
                    'customer_id': msg['customer_id'],
                }
            )
        if self.channel_kind == 'support_all' and msg['customer_id']:
            await self.channel_layer.group_send(
                f"chat_support_{msg['customer_id']}",
                {
                    'type': 'chat_message',
                    'message': msg['text'],
                    'sender_id': msg['user_id'],
                    'sender_name': msg['username'],
                    'created_at': msg['created_at'],
                    'customer_id': msg['customer_id'],
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def _save_message(self, user, text, target_customer_id=None):
        customer = None
        if self.channel_kind == 'support':
            customer = User.objects.get(id=self.customer_id)
        elif self.channel_kind == 'support_all' and target_customer_id:
            try:
                customer = User.objects.get(id=int(target_customer_id))
            except (User.DoesNotExist, ValueError, TypeError):
                customer = None
        channel = 'support'
        if self.channel_kind == 'staff_admin':
            channel = 'staff_admin'
        msg = Message.objects.create(
            user=user,
            customer=customer,
            channel=channel,
            text=text,
            is_staff_response=user.is_staff or user.is_superuser,
        )
        return {
            'text': msg.text,
            'user_id': msg.user_id,
            'username': msg.user.username,
            'created_at': msg.created_at.isoformat(),
            'customer_id': msg.customer_id,
        }
