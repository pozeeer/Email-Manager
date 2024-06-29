
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EmailConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.group_name = 'email_progress'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_progress(self, event):
        progress = event['progres']
        await self.send(text_data=json.dumps(
            {'progress': progress}
        )
        )

    async def send_email(self, event):
        email_data = event['email_data']
        await self.send(text_data=json.dumps(
            {'email_data': email_data, }
        )
        )