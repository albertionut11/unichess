import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'

        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        from_pos = data['from']
        to_pos = data['to']
        turn = data['turn']
        enPassant = data.get('enPassant', False)

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_move',
                'from': from_pos,
                'to': to_pos,
                'turn': turn,
                'EnPassant': enPassant
            }
        )

    async def game_move(self, event):
        from_pos = event['from']
        to_pos = event['to']
        turn = event['turn']
        enPassant = event.get('enPassant', False)

        await self.send(text_data=json.dumps({
            'from': from_pos,
            'to': to_pos,
            'turn': turn,
            'enPassant': enPassant
        }))
