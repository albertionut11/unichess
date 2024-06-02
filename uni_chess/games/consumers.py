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
        print('Received: ', data)
        from_pos = data['from']
        to_pos = data['to']
        turn = data['turn']
        enPassant = data.get('enPassant', False)
        checkmate = data['checkmate']
        promotion = data.get('promotion', False)
        castling = data.get('castling', False)
        white_time_remaining = data.get('white_time_remaining', False)
        black_time_remaining = data.get('black_time_remaining', False)

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_move',
                'from': from_pos,
                'to': to_pos,
                'turn': turn,
                'EnPassant': enPassant,
                'checkmate': checkmate,
                'promotion': promotion,
                'castling': castling,
                'white_time_remaining': white_time_remaining,
                'black_time_remaining': black_time_remaining
            }
        )

    async def game_move(self, event):
        print('Send: ', event)
        from_pos = event['from']
        to_pos = event['to']
        turn = event['turn']
        enPassant = event.get('enPassant', False)
        checkmate = event.get('checkmate', False)
        promotion = event.get('promotion', False)
        castling = event.get('castling', False)
        white_time_remaining = event.get('white_time_remaining', False)
        black_time_remaining = event.get('black_time_remaining', False)

        await self.send(text_data=json.dumps({
            'from': from_pos,
            'to': to_pos,
            'turn': turn,
            'enPassant': enPassant,
            'checkmate': checkmate,
            'promotion': promotion,
            'castling': castling,
            'white_time_remaining': white_time_remaining,
            'black_time_remaining': black_time_remaining
        }))
