import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import LettersInfo, EmailAccount, MailServices
from asgiref.sync import sync_to_async
from .services.email_reader import AsyncEmailReader


class ProgressBarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        asyncio.create_task(self.produce_data())

    async def produce_data(self):
        account = await self.get_account_data()
        imap_server = await self.get_service_object(account.imap_id)

        email_login = account.login
        password = account.email_password
        reader = AsyncEmailReader(imap_server=imap_server, email=email_login, password=password)
        await reader.connect()
        data = await reader.fetch_emails()
        await reader.close()

        total = len(data)
        for i, item in enumerate(data, start=1):
            await self.save_to_db(item)
            progress = int((i / total) * 100)
            await self.send(json.dumps({'progress': progress}))
            await asyncio.sleep(1)  # Имитация задержки для демонстрации прогресса

        await self.dynamic_countdown_and_display_data(total)

    async def dynamic_countdown_and_display_data(self, total):
        for i in range(total, -1, -1):
            await self.send(json.dumps({'progress': int((i / total) * 100)}))
            letter = await self.get_letter_by_index(total - i)
            if letter:
                await self.send_letter_data(letter)
                await asyncio.sleep(0.5)

    @sync_to_async
    def get_service_object(self, service_id: int):
        return MailServices.objects.get(id=service_id).imap

    @sync_to_async
    def get_account_data(self):
        return EmailAccount.objects.latest('id')

    @sync_to_async
    def save_to_db(self, item):
        """Синхронное сохранение данных в базу, обернутое в асинхронный вызов."""
        LettersInfo.objects.create(
            title=item['subject'], author=item['from'], receipt_date=item['date'],
            content=item['body'], files_list=item['attachments']
        )

    @sync_to_async
    def get_letter_by_index(self, index):
        return LettersInfo.objects.all()[index]

    async def send_letter_data(self, letter):
        if letter.files_list == []:
            attachments = 'нету приложенных файлов'
        else:
            attachments = letter.files_list
            # date = letter.strftime("%d.%m.%Y %H:%M ")
        data = {
            'title': letter.title,
            'author': letter.author,
            'date': letter.receipt_date.strftime("%d.%m.%Y %H:%M "),
            'content': letter.content,
            'files_list': attachments
        }
        await self.send(json.dumps({'letter': data}))
