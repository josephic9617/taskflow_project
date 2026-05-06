import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TaskConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time board updates.
    Clients connect to ws://host/ws/board/<board_id>/
    """

    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.group_name = f'board_{self.board_id}'

        # Join board group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': f'Connected to board {self.board_id}',
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages sent from the client over WebSocket."""
        try:
            data = json.loads(text_data)
            msg_type = data.get('type')

            if msg_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))

    # --- Group message handlers ---

    async def task_moved(self, event):
        """Broadcast task move to all clients in the board group."""
        await self.send(text_data=json.dumps({
            'type': 'task_moved',
            'task_id': event['task_id'],
            'column_id': event['column_id'],
            'order': event['order'],
        }))

    async def task_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_created',
            'task': event['task'],
        }))

    async def task_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_deleted',
            'task_id': event['task_id'],
        }))

    async def task_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'task': event['task'],
        }))
