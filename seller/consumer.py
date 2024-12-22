import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SellerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.seller_id = self.scope['url_route']['kwargs']['seller_id']
        self.group_name = f'seller_{self.seller_id}'

        # 그룹에 추가
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        # 그룹에 메시지 보내기
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'order_update',
                'message': message
            }
        )

    async def order_update(self, event):
        message = event['message']

        # WebSocket에 메시지 전송
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'message': message
        }))
