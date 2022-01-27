from .MailMessage import MailMessage, MailAttachedFile

import re
import poplib
import email
import email.header
from typing import List, Optional

MAIL_REGEX = r'^(?:.*?)([\w\.]+\@[\w]+\.[\w]+)(?:.*?)$'
SAVE_DIR = 'submits'


def decode_if_needed(data, encoding=None) -> str:
    if type(data) is not str:
        encoding = 'utf-8' if encoding is None else encoding
        return data.decode(encoding)
    else:
        return data


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
