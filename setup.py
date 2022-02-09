import json
from pathlib import Path
from getpass import getpass

CONFIG_FILE_PATH = 'config.json'
CREDENTIALS_FILE = ''


def safe_mkdir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def create_checker_folders():
    global CREDENTIALS_FILE
    print('Creating checker folders...', end=' ')

    with open(CONFIG_FILE_PATH, 'r') as f:
        cfg = json.load(f)
        safe_mkdir(cfg['public_keys'])
        safe_mkdir(cfg['submits'])
        safe_mkdir(cfg['labs'])
        CREDENTIALS_FILE = cfg['admin_credentials']

    print('OK')


def create_credentials_file():
    print('Creating credentials file...')
    Path(CREDENTIALS_FILE).touch(exist_ok=True)

    ans = input('Would you like to enter your gmail credentials now? (y/n):')
    if ans == 'y':
        address = input('Gmail address: ')
        password = getpass()
        with open(CREDENTIALS_FILE, 'w') as f:
            f.write(address + ' ' + password)
        print(f'Login and password are saved to {CREDENTIALS_FILE}')
    else:
        print(f'Do not forget to update {CREDENTIALS_FILE} with your credentials')


def main():
    create_checker_folders()
    create_credentials_file()
    print('Setup complete')


if __name__ == '__main__':
    main()
