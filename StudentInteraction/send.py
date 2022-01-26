import sys

from Communication.authentication import get_credentials
from Communication.Mail import MailMessage, MailSender

CREDENTIALS_FILE = '.admin_credentials'


def main():
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <mail_address> [ATTACHMENT1 [ATTACHMENT2 ...]]')
        exit(1)

    destination = sys.argv[1]
    attachments = sys.argv[2:] if len(sys.argv) > 2 else []

    subject = 'Test subject'
    body = 'This is an automatic reply. Thank you for participating!'

    login, password = get_credentials(CREDENTIALS_FILE)
    print(f'{login=}')
    message = MailMessage(login, destination, subject, body)

    for attachment in attachments:
        message.attach_file(attachment)

    print('Logging in...')
    with MailSender(login, password) as server:
        print('Sending message...')
        server.send_message(message)


if __name__ == '__main__':
    main()
