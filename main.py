import re
import sys
import subprocess

from CheckerInteraction import Message, ListenerBase
from Utils import process_exist

from typing import Tuple

CONFIG_FILE_PATH = 'config.json'
PYTHON_EXE = sys.executable

# checker info
VERSION = '0.0.1'
AUTHOR = '@devepodete (Maksim Cheremisinov)'
RELEASE_DATE = '09 Feb 2022'
LICENSE = 'MIT'

# checker state
STARTED = False
PID: int = -1

# checker communication
PORT = 6000
LISTENER = ListenerBase()

COMMANDS = (
    'fetch', 'check', 'skip', 'start', 'restart', 'exit', 'kill', 'set', 'mail', 'stat', 'help'
)

EMPTY_COMMAND_RE = re.compile(R'^\s*$')

COMMANDS_RE = (
    re.compile(R'^\s*(fetch)\s+(start|stop)?\s*$'),
    re.compile(R'^\s*(check)\s+([\w\\/]+)\s+(--report)?\s*$'),
    re.compile(R'^\s*(skip)\s*$'),

    re.compile(R'^\s*(start)\s*$'),
    re.compile(R'^\s*(restart)\s*$'),
    re.compile(R'^\s*(restart)\s+(now)\s*$'),
    re.compile(R'^\s*(exit)\s*$'),
    re.compile(R'^\s*(kill)\s*$'),

    re.compile(R'^\s*(get)\s+(news)\s*$'),
    re.compile(R'^\s*(set)\s+(config)\s+([\w\\/]+)\s*$'),
    re.compile(R'^\s*(set)\s+(fetch)\s+(delay)\s+([0-9]+)\s*$'),

    re.compile(R'^\s*(mail)\s+(all)\s+\"(.*)\"\s*$'),
    re.compile(R'^\s*(mail)\s+(.*@.*)\s+\"(.*)\"\s*$'),

    re.compile(R'^\s*(pid)\s*$'),
    re.compile(R'^\s*(stat)\s*$'),
    re.compile(R'^\s*(help)\s*$'),
)


def print_welcome():
    print(f'=== LAB CHECKER ===')
    print(f'Made by {AUTHOR}')
    print(f'Version {VERSION} from {RELEASE_DATE}')
    print(f'License: {LICENSE}')
    print(f'===================')


def print_help():
    print('Available checker commands:\n')
    print('fetch - fetch new submits (by default checker wait some time between fetches)')
    print('fetch start - start fetching new submits')
    print('fetch stop - stop fetching new submits')
    print('check path/to/submit - check target path/to/submit')
    print('check path/to/submit --report - same as check, but send report also')
    print('skip - skip all pending submits')
    print()
    print('start - start checker process')
    print('restart - equivalent to exit + start')
    print('restart now - equivalent to kill + start')
    print('exit - wait until checker done and close checker process')
    print('kill - force kill checker process')
    print()
    print('get news - get messages from checker')
    print('set config path/to/config - update checker configuration from path/to/config')
    print('set fetch delay SECONDS - set new delay between fetching submits')
    print()
    print('mail all \"Message\" - send \"Message\" to all users')
    print('mail user@gmail.com \"Message\" - send \"Message\" to user@gmail.com')
    print()
    print('pid - print checker PID')
    print('stat - print checker statistics')
    print('help - print available commands')


def command_ok(command: str) -> Message:
    for command_re in COMMANDS_RE:
        res = command_re.match(command)
        if res:
            return Message('', False, res.groups())

    return Message('unknown command', True)


def cmd_kill(pid) -> Message:
    global STARTED
    if type(pid) is not int:
        return Message(f'Invalid {pid=}', True)

    STARTED = False
    proc = subprocess.run(['kill', '-9', str(pid)], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)

    if proc.returncode != 0:
        return Message(str(proc.stderr), True)

    return Message('')


def cmd_start() -> Message:
    global STARTED, PID

    if process_exist(PID) or STARTED:
        return Message('Checker already started', True)
    proc = subprocess.Popen([PYTHON_EXE, 'checker.py', CONFIG_FILE_PATH, str(PORT)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    checker_code = None
    try:
        checker_code = proc.wait(1)
    except subprocess.TimeoutExpired:
        pass

    if checker_code:
        return Message(f'Failed to start checker. Exit code {checker_code}', True,
                       [line.decode('utf-8').replace('\n', '') for line in proc.stderr])
    PID = proc.pid
    LISTENER.accept_connection()
    STARTED = True
    return Message('')


def cmd_exit() -> Message:
    global STARTED, PID
    if not STARTED or not process_exist(PID):
        return Message('')

    send_message_to_checker(Message('exit'))
    msg = receive_message_from_checker(timeout=5.0)
    if not msg.error_occurred:
        STARTED = False
    return msg


def send_message_to_checker(message: Message) -> None:
    LISTENER.send_message(message)


def receive_message_from_checker(timeout=-1.0) -> Message:
    msg = LISTENER.receive_message(timeout)
    if msg.error_occurred:
        msg.message = 'no news'
    return msg


def do_command_action(command: Tuple[str]) -> Message:
    global STARTED, PID

    if not command or len(command) == 0:
        return Message('No command provided', True)

    if command[0] == 'help':
        print_help()
    elif command[0] == 'pid':
        print(f'{PID=}')
    elif command[0] == 'kill':
        return cmd_kill(PID)
    elif command[0] == 'exit':
        return cmd_exit()
    elif command == 'restart':
        msg = cmd_exit()
        if msg.error_occurred:
            return msg
        return cmd_start()
    elif command == ('restart', 'now'):
        cmd_kill(PID)
        return cmd_start()
    elif command[0] == 'start':
        msg = cmd_start()
        if not msg.error_occurred:
            print(f'{PID=}')
        return msg
    elif command == ('get', 'news'):
        msg = receive_message_from_checker(0.0)
        if not msg.error_occurred:
            print(msg.message)
            if msg.args:
                for arg in msg.args:
                    print(arg)
        return msg
    else:
        print('command is:', command)
        if not STARTED:
            return Message('start checker first', True)
        send_message_to_checker(Message(command[0], False, command))

    return Message('')


def init_listener():
    global LISTENER

    LISTENER.bind_socket(('localhost', PORT))


def process_input():
    while True:
        try:
            command = input('> ')
            if EMPTY_COMMAND_RE.match(command):
                continue

            command = command_ok(command)
            if command.error_occurred:
                print(f'Error: {command.message}')
                continue

            print(f'Parsed command: {command.args}')

            result = do_command_action(command.args)
            if result.error_occurred:
                print(f'Error: {result.message}')
                if result.args:
                    for arg in result.args:
                        print(arg)

        except EOFError:
            print()


def main():
    print_welcome()
    print_help()
    init_listener()
    process_input()


if __name__ == '__main__':
    main()
