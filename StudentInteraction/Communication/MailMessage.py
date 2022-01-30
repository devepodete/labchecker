from base64 import b64decode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


class AttachmentKind:
    Binary = 0
    Html = 1
    Text = 2


class MailAttachment:
    def __init__(self, name: str, data, kind=AttachmentKind.Binary):
        self.name = name
        self.data = data
        self.kind = kind

    def save_to(self, path):
        mode = 'w'
        mode += 'b' if self.kind == AttachmentKind.Binary else ''
        with open(path, mode) as f:
            data = self.data
            if self.kind == AttachmentKind.Binary:
                data = b64decode(self.data)
            f.write(data)


class MailMessage:
    def __init__(self, sender: str, receiver: str, subject: str, body='', date=''):
        self.message = MIMEMultipart()

        self.From = sender
        self.To = receiver
        self.Subject = subject
        self.Body = body
        self.Date = date

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
            if attachment.kind == AttachmentKind.Binary:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment.name)}')
            elif attachment.kind == AttachmentKind.Html:
                part = MIMEText(attachment.data, 'html')
            else:
                part = MIMEText(attachment.data, 'plain')

            self.message.attach(part)

    def __attach_from_mail_file(self, mail_file: MailAttachment):
        self.Attachments.append(mail_file)

    def __attach_from_disk(self, filepath: str):
        with open(filepath, 'rb') as attachment:
            self.__attach_from_mail_file(MailAttachment(filepath, attachment.read()))

    def attach_file(self, *args):
        if len(args) != 1:
            raise RuntimeError(f'Invalid number of arguments in attach_file(): {len(args)}')

        if type(args[0]) is str:
            return self.__attach_from_disk(args[0])
        if type(args[0]) is MailAttachment:
            return self.__attach_from_mail_file(args[0])

        raise RuntimeError(f'Unexpected argument type in attach_file(): {type(args[0])}')

    def __str__(self):
        s = f"""\
From: `{self.From}\', To: `{self.To}\', Subject: `{self.Subject}\'
Body: `{self.Body}\', Date: `{self.Date}\'
Attachments:
"""

        for idx, attachment in enumerate(self.Attachments):
            s += f'{idx + 1}) `{attachment.name}\' with length {len(attachment.data)} bytes\n'

        s += f'(Total {len(self.Attachments)})\n'
        return s
