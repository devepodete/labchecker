import re
import sys
import subprocess

from CheckerInteraction import Message, ListenerBase

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
PID = None

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
            return Message(False, '', res.groups())

    return Message(True, 'unknown command')


def cmd_kill(pid) -> Message:
    if type(pid) is not int:
        return Message(True, f'Invalid {pid=}')

    proc = subprocess.run(['kill', '-9', str(pid)], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)

    if proc.returncode != 0:
        return Message(True, str(proc.stderr))

    return Message(False, '')


def cmd_start() -> Message:
    global STARTED, PID

    if STARTED:
        return Message(True, 'Checker already started')
    proc = subprocess.Popen([PYTHON_EXE, 'checker.py', CONFIG_FILE_PATH, str(PORT)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    checker_code = None
    try:
        checker_code = proc.wait(1)
    except subprocess.TimeoutExpired:
        pass

    if checker_code:
        return Message(True, f'Failed to start checker. Exit code {checker_code}',
                       [line.decode('utf-8').replace('\n', '') for line in proc.stderr])
    PID = proc.pid
    LISTENER.accept_connection()
    return Message(False, '')


def send_message_to_checker(message: Message, wait_reply: bool, timeout=1.0) -> Message:
    LISTENER.send_message(message)
    if not wait_reply:
        return Message(False, '')

    return LISTENER.receive_message(timeout)


def do_command_action(command: Tuple[str]) -> Message:
    global STARTED, PID

    if not command or len(command) == 0:
        return Message(True, 'No command provided')

    if command[0] == 'help':
        print_help()
    elif command[0] == 'pid':
        print(f'{PID=}')
    elif command[0] == 'kill':
        return cmd_kill(PID)
    elif command == ('restart', 'now'):
        cmd_kill(PID)
        return cmd_start()
    elif command[0] == 'start':
        return cmd_start()
    elif command[0] == 'stat':
        stat = send_message_to_checker(Message(False, 'stat', command), wait_reply=True)
        print(stat.message)
    elif command[0] == 'exit':
        stat = send_message_to_checker(Message(False, 'exit'), wait_reply=True)
        print(stat.message)
    elif command[0] == 'skip':
        stat = send_message_to_checker(Message(False, 'skip'), wait_reply=True)
        print(stat.message)
    else:
        print('unsupported command')

    return Message(False, '')


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
