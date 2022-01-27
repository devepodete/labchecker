import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


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