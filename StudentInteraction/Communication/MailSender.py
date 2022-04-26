from .MailMessage import MailMessage

import ssl
from smtplib import SMTP_SSL as SMTP


class MailSender:
    def __init__(self, login: str, password: str, smtp_server='smtp.mail.ru', port=465):
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
