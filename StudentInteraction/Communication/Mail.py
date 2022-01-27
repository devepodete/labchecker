import os.path
import ssl

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from typing import List, Optional


class MailAttachedFile:
    def __init__(self, name: str, data):
        self.name = name
        self.data = data

    def save_to(self, path, mode='wb'):
        with open(os.path.join(path, self.name), mode) as f:
            f.write(self.data)


class MailMessage:
    def __init__(self, sender: str, receiver: str, subject: str, body=''):
        self.message = MIMEMultipart()

        self.From = sender
        self.To = receiver
        self.Subject = subject
        self.Body = body
        self.Attachments = []

    def pack(self):
        self.message['From'] = self.From
        self.message['To'] = self.To
        self.message['Subject'] = self.Subject
        # do I really need it?
        # self.message['Bcc'] = self.message['To']

        if self.Body and len(self.Body) != 0:
            self.message.attach(MIMEText(self.Body, 'plain'))

        for attachment in self.Attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment.name)}')

            self.message.attach(part)

    def __attach_base(self, file_name: str, file_data):
        self.Attachments.append(MailAttachedFile(file_name, file_data))

    def __attach_from_disk(self, filepath: str):
        with open(filepath, 'rb') as attachment:
            self.__attach_base(filepath, attachment.read())

    def __attach_from_mail_file(self, mail_file: MailAttachedFile):
        self.__attach_base(mail_file.name, mail_file.data)

    def attach_file(self, *args):
        if len(args) != 1:
            raise RuntimeError(f'Invalid number of arguments in attach_file(): {len(args)}')

        if type(args[0]) is str:
            return self.__attach_from_disk(args[0])
        if type(args[0]) is MailAttachedFile:
            return self.__attach_from_mail_file(args[0])

        raise RuntimeError(f'Unexpected argument type in attach_file(): {type(args[0])}')

    def __str__(self):
        s = f"""\
From: `{self.From}\', To: `{self.To}\', Subject: `{self.Subject}\'
Body: `{self.Body}\'
Attachments:"""

        for idx, attachment in enumerate(self.Attachments):
            s += f'{idx + 1}) `{attachment.name}\' with length {len(attachment.data)} bytes\n'

        s += f'(Total {len(self.Attachments)})\n'
        return s


class MailSender:
    def __init__(self, login: str, password: str, smtp_server='smtp.gmail.com', port=465):
        self.context = ssl.create_default_context()
        self.login = login
        self.password = password
        self.smtpServer = smtp_server
        self.port = port
        self.server = None

    def __enter__(self):
        self.server = SMTP(self.smtpServer, self.port, context=self.context)
        self.server.login(self.login, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.quit()

    def send_message(self, message: MailMessage):
        message.pack()
        self.server.sendmail(message.From, message.To, message.message.as_string())


def decode_if_needed(data, encoding=None) -> str:
    if type(data) is not str:
        encoding = 'utf-8' if encoding is None else encoding
        return data.decode(encoding)
    else:
        return data


import re
import poplib
import email
import email.header

MAIL_REGEX = r'^(?:.*?)([\w\.]+\@[\w]+\.[\w]+)(?:.*?)$'

SAVE_DIR = 'submits'


class MailReceiver:
    def __init__(self, login, password, pop_server='pop.gmail.com'):
        self.login = login
        self.password = password
        self.popServer = pop_server
        self.server = None

    def __enter__(self):
        self.server = poplib.POP3_SSL(self.popServer)
        self.server.user(self.login)
        self.server.pass_(self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.quit()

    @staticmethod
    def __parse_subject(msg):
        subject = msg['Subject']
        if subject is not None:
            subject = email.header.decode_header(subject)
            subject = decode_if_needed(subject[0][0], subject[0][1])
        return subject

    @staticmethod
    def __parse_sender(msg):
        from_who = email.header.decode_header(msg['From'])
        sender_email = None
        for infoIdx in range(len(from_who)):
            if len(from_who[infoIdx]) == 2:
                tmp = decode_if_needed(from_who[infoIdx][0], from_who[infoIdx][1])
                matched = re.match(MAIL_REGEX, tmp)
                if matched:
                    sender_email = matched.groups()[0]
                    break

        return sender_email

    @staticmethod
    def __parse_file_name(part) -> Optional[str]:
        filename = part.get_filename()
        filename = email.header.decode_header(filename)
        filename = decode_if_needed(filename[0][0])
        return filename

    def fetch(self) -> List[MailMessage]:
        result = []
        emails, total_bytes = self.server.stat()
        for i in range(emails):
            response = self.server.retr(i + 1)
            raw_message = response[1]
            str_message = email.message_from_bytes(b'\n'.join(raw_message))

            subject = self.__parse_subject(str_message)
            sender_email = self.__parse_sender(str_message)
            message = MailMessage(sender_email, self.login, subject)

            for part in str_message.walk():
                content_maintype = part.get_content_maintype()
                if content_maintype == 'multipart':
                    continue

                if content_maintype == 'text':
                    message.Body += part.get_payload()

                if part.get_content_disposition() is None:
                    continue

                message.attach_file(MailAttachedFile(self.__parse_file_name(part), part.get_payload()))

            result.append(message)

        return result
