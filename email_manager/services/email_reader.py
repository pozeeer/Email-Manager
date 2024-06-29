import email
import os
from email.header import decode_header

import aiofiles
from bs4 import BeautifulSoup
from imapclient import IMAPClient


class AsyncEmailReader:
    def __init__(self, imap_server, email, password):
        self.imap_server = imap_server
        self.email = email
        self.password = password
        self.connection = None

    async def connect(self):
        """Подключение к почтовому серверу и вход в систему."""
        self.connection = IMAPClient(self.imap_server, ssl=True)
        self.connection.login(self.email, self.password)

    async def close(self):
        """Закрытие соединения с почтовым сервером."""
        self.connection.logout()

    async def fetch_emails(self, mailbox="INBOX"):
        """Извлечение писем из указанного почтового ящика."""
        self.connection.select_folder(mailbox)
        messages = self.connection.search(['ALL'])[::-1]
        emails = [await self._fetch_email(mail_id) for mail_id in messages]
        return emails

    async def _fetch_email(self, mail_id):
        """Извлечение и парсинг одного письма."""
        response = self.connection.fetch(mail_id, ['RFC822'])
        msg = email.message_from_bytes(response[mail_id][b'RFC822'])
        email_data = await self._parse_email(msg)
        return email_data

    async def _parse_email(self, msg):
        """Парсинг одного письма и извлечение его частей."""
        subject = self._decode_header(msg["Subject"])
        from_ = self._decode_header(msg.get("From"))
        date = self._parse_date(msg.get("Date"))
        body, attachments = await self._extract_body_and_attachments(msg)
        formatted_body = self._format_body(body)
        return {
            "subject": subject,
            "from": from_,
            "date": date,
            "body": formatted_body,
            "attachments": attachments,
        }

    def _decode_header(self, header):
        """Декодирование заголовка письма."""
        decoded_header, encoding = decode_header(header)[0]
        if isinstance(decoded_header, bytes):
            decoded_header = decoded_header.decode(encoding if encoding else "utf-8")
        return decoded_header

    def _parse_date(self, date_str):
        """Парсинг даты отправки письма."""
        try:
            email_date = email.utils.parsedate_to_datetime(date_str)
            return email_date.strftime('%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError):
            return None

    async def _extract_body_and_attachments(self, msg):
        """Извлечение тела письма и вложений."""
        body = ""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    html_body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                    body += self._html_to_text(html_body)
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
                        await self._save_attachment(part, filename)
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
            elif content_type == "text/html":
                html_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
                body = self._html_to_text(html_body)
        return body, attachments

    async def _save_attachment(self, part, filename):
        """Сохранение вложения на диск."""
        filepath = os.path.join("downloads", filename)
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(part.get_payload(decode=True))

    def _format_body(self, body):
        """Форматирование тела письма для удаления лишних пустых строк."""
        lines = body.split('\n')
        formatted_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(formatted_lines)

    def _html_to_text(self, html):
        """Конвертация HTML-контента в текст."""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

