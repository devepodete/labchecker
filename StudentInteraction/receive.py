from Communication.authentication import get_credentials
from Communication.Mail import MailReceiver

CREDENTIALS_FILE = '.admin_credentials'


def main():
    login, password = get_credentials(CREDENTIALS_FILE)

    print('Logging in...')
    with MailReceiver(login, password) as server:
        print('Fetching...')
        mails = server.fetch()

        print(f'Fetched {len(mails)} mails')
        for mail in mails:
            print('\nNEW MAIL:')
            print(f'FROM: {mail.From}, TO: {mail.To}')
            print(f'SUBJECT: `{mail.Subject}\'')
            print(f'BODY: `{mail.Body}\'')
            print('ATTACHMENTS:')

            for idx, attachment in enumerate(mail.Attachments):
                print(f'{idx}: {attachment.name}, size: {len(attachment.data)}')


if __name__ == '__main__':
    main()
