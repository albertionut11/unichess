import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

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
        checkmate = data.get('checkmate', False)
        promotion = data.get('promotion', False)
        castling = data.get('castling', False)
        white_time_remaining = data['white_time_remaining']
        black_time_remaining = data['black_time_remaining']

        # Send move to game group
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_move',
                'from': from_pos,
                'to': to_pos,
                'turn': turn,
                'enPassant': enPassant,
                'checkmate': checkmate,
                'promotion': promotion,
                'castling': castling,
                'white_time_remaining': white_time_remaining,
                'black_time_remaining': black_time_remaining
            }
        )

    async def game_move(self, event):
        # Send move to WebSocket
        await self.send(text_data=json.dumps({
            'from': event['from'],
            'to': event['to'],
            'turn': event['turn'],
            'enPassant': event['enPassant'],
            'checkmate': event['checkmate'],
            'promotion': event['promotion'],
            'castling': event['castling'],
            'white_time_remaining': event['white_time_remaining'],
            'black_time_remaining': event['black_time_remaining']
        }))
