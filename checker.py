import logging

import Utils
from PipelineBase import Gate, GateHolder, ExecutionPolicy
from Pipeline import ExecutableBuilder, FileSizeLimiter, FileCleaner, ExecutableRunner

from StudentInteraction.Communication import *
from StudentInteraction.ReportGeneration import ReportGenerator, ReportType
from CheckerInteraction import Message, ClientBase

from Utils import AnswerComparator, Logger

import dateutil.parser
import json
import sys

from pathlib import Path
from time import sleep
from typing import List

# checker communication
PORT = -1
LOGGER = Logger()
CLIENT = ClientBase()

# mail communication
LOGIN = ''
PASSWORD = ''

# time delays
FETCH_DELAY_SECONDS = 10

# checker folders
PUBLIC_KEYS_FOLDER = Path()
ADMIN_CREDS_FILE = Path()
LOG_FILE = Path()
SUBMITS_FOLDER = Path()
LABS_FOLDER = Path()

# checker flags
REMOVE_EXECUTABLE_AFTER_RUN = None
REMOVE_SUBMIT_AFTER_RUN = None
RETURN_STDERR_TO_STUDENT = None
RETURN_STDERR_TO_STUDENT_SIZE = None

# correct submit subjects
GOOD_SUBJECTS = (
    'os:key',
    'os:1', 'os:2', 'os:3',
    'os:test'
)

# statistics
TOTAL_STUDENTS = 0
TOTAL_SUBMITS = 0
BAD_SUBMITS = 0
VERDICTS_OK = 0
VERDICTS_RE = 0
VERDICTS_TL = 0
VERDICTS_ML = 0


class Action:
    CHECK = 'CHECK'
    SKIP = 'SKIP'
    STAT = 'STAT'
    SET = 'SET'
    MAIL = 'MAIL'
    EXIT = 'EXIT'
    NONE = 'NONE'


def get_action_from_host() -> (int, Message):
    if not CLIENT.has_new_message():
        return Action.NONE, None

    message = CLIENT.receive_message()
    if message.message == 'check':
        return Action.CHECK, message
    elif message.message == 'exit':
        return Action.EXIT, message

    return Action.NONE, None


def work():
    global TOTAL_STUDENTS, TOTAL_SUBMITS

    LOGGER.log('begin work')
    done = False

    while not done:
        action, message = get_action_from_host()

        if action != Action.NONE:
            LOGGER.log(f'received action `{action}\' from host')

        if action == Action.EXIT:
            break
        elif action == Action.MAIL:
            pass
        elif action == Action.STAT:
            pass
        elif action == Action.SKIP:
            pass

        messages_to_send = []
        sleep(FETCH_DELAY_SECONDS)

        with MailReceiver(LOGIN, PASSWORD) as receiveServer:
            new_messages = receiveServer.fetch()

            if len(new_messages) != 0:
                LOGGER.log(f'got {len(new_messages)} new submits')

            for msg in new_messages:
                TOTAL_SUBMITS += 1
                LOGGER.log(f'start submit check from `{msg.From}\'')

                if len(msg.Attachments) == 0:
                    LOGGER.log('no attachments')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Empty attachments'))
                    continue

                if msg.Subject not in GOOD_SUBJECTS:
                    LOGGER.log(f'bad subject: {msg.Subject}')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Bad subject'))
                    continue

                key_file = PUBLIC_KEYS_FOLDER / (msg.From + '.asc')
                if msg.Subject == 'os:key':
                    LOGGER.log('user want to add GPG key')
                    if len(msg.Attachments) != 1:
                        LOGGER.log('bad GPG attachments length')
                        messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Bad attachments'))
                        continue
                    msg.Attachments[0].save_to(key_file)
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Result', 'Your key is saved'))
                    LOGGER.log(f'GPG key saved to `{key_file}\'')
                    continue

                if not key_file.exists():
                    LOGGER.log(f'no gpg key `{key_file}\'')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Please send your public GPG key'))
                    continue

                if len(msg.Attachments) != 2:
                    LOGGER.log(f'bad attachments with length {len(msg.Attachments)}')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Bad attachments'))
                    continue

                if not msg.Attachments[1].name.endswith('.asc'):
                    LOGGER.log(f'bad signature extension: `{msg.Attachments[1].name}\'')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Bad signature extension'))
                    continue

                user_folder = SUBMITS_FOLDER / msg.From
                user_folder.mkdir(exist_ok=True)

                lab_folder = user_folder / msg.Subject
                lab_folder.mkdir(exist_ok=True)

                date = dateutil.parser.parse(msg.Date)
                submit_folder = lab_folder / f'{date.date()}+{date.time()}'
                LOGGER.log(f'submit folder `{submit_folder}\'')
                try:
                    submit_folder.mkdir(exist_ok=False)
                except FileExistsError:
                    LOGGER.log('too fast submit')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error',
                                                        'Your submit already exist. How can you send 2 messages at '
                                                        'the same moment?'))
                    continue

                src_path = submit_folder / 'main.cpp'
                sign_path = submit_folder / 'main.cpp.asc'
                exec_path = submit_folder / 'main.out'

                msg.Attachments[0].save_to(src_path)
                msg.Attachments[1].save_to(sign_path)
                LOGGER.log(f'attachments saved to {src_path}')

                if not Utils.signature_ok(src_path, sign_path, key_file):
                    LOGGER.log('bad signature')
                    messages_to_send.append(MailMessage(LOGIN, msg.From, 'Error', 'Bad signature'))
                    continue

                LOGGER.log('signature ok')

                # generate tests folder path
                lab_number = msg.Subject.split(':')[-1]
                student_var = 'var12'  # TODO

                lab_variant_path = LABS_FOLDER / lab_number / student_var

                gate0 = Gate('PreparationChecks',
                             [FileSizeLimiter(src_path, 10000)], ExecutionPolicy.RUN_ALWAYS)
                gate1 = Gate('Build',
                             [ExecutableBuilder('g++', ['-Wall', '-Werror'], src_path, exec_path)],
                             ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)
                gate2 = Gate('Test',
                             [ExecutableRunner(exec_path,
                                               lab_variant_path,
                                               AnswerComparator('./TestingArea/AnswerComparators/ncmp.out',  # TODO
                                                                '1 {0} {1}'),
                                               Path('./TestingArea/.temp.txt'))],
                             ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)
                gate3 = Gate('Clean',
                             [FileCleaner([exec_path])], ExecutionPolicy.RUN_ALWAYS)

                gh = GateHolder([gate0, gate1, gate2, gate3])
                LOGGER.log('executing pipeline')
                gh.execute()
                LOGGER.log('pipeline executed')

                rg = ReportGenerator([gate1, gate2])
                rg.generate_report(ReportType.Html)

                m = MailMessage(LOGIN, msg.From, 'Result')
                m.attach_file(MailAttachment('report', rg.report, AttachmentKind.Html))
                messages_to_send.append(m)

        with MailSender(LOGIN, PASSWORD) as sendServer:
            for msg in messages_to_send:
                if msg.To == LOGIN:
                    continue
                sendServer.send_message(msg)

    LOGGER.log('end work')


def read_config(file: str):
    global PUBLIC_KEYS_FOLDER, ADMIN_CREDS_FILE, SUBMITS_FOLDER, LABS_FOLDER
    global LOG_FILE
    global REMOVE_EXECUTABLE_AFTER_RUN, REMOVE_SUBMIT_AFTER_RUN
    global RETURN_STDERR_TO_STUDENT, RETURN_STDERR_TO_STUDENT_SIZE

    with open(file, 'r') as f:
        cfg = json.load(f)

        PUBLIC_KEYS_FOLDER = Path(cfg['public_keys'])
        ADMIN_CREDS_FILE = Path(cfg['admin_credentials'])
        SUBMITS_FOLDER = Path(cfg['submits'])
        LABS_FOLDER = Path(cfg['labs'])
        LOG_FILE = Path(cfg['checker_logs'])

        REMOVE_EXECUTABLE_AFTER_RUN = cfg['remove_executable_after_run']
        REMOVE_SUBMIT_AFTER_RUN = cfg['remove_submit_after_run']
        RETURN_STDERR_TO_STUDENT = cfg['return_stderr_to_student']
        RETURN_STDERR_TO_STUDENT_SIZE = cfg['return_stderr_to_student_size_bytes']


def cmd_update_config(new_config_path: str) -> Message:
    result = Message(False, '')
    try:
        read_config(new_config_path)
    except OSError as e:
        result.error_occurred = True
        result.message = str(e)
    return result


def connect_to_host():
    LOGGER.log('connecting to host')
    CLIENT.connect_to_socket(('localhost', PORT))
    LOGGER.log(f'successfully connected to host. Working on port {PORT}')


def disconnect_from_host():
    LOGGER.log('disconnecting from host')
    CLIENT.close_connection()
    LOGGER.log('disconnected from host')


def init_logger():
    global LOGGER
    LOGGER = Logger(LOG_FILE)
    LOGGER.log('logger initialized')


def init_mail_credentials():
    global LOGIN, PASSWORD
    LOGGER.log('retrieving admin credentials')
    LOGIN, PASSWORD = authentication.get_credentials(ADMIN_CREDS_FILE)
    LOGGER.log(f'got credentials from {ADMIN_CREDS_FILE}')


def init_checker(argv: List[str]) -> Message:
    global PORT

    if len(argv) not in (3, 4):
        return Message(True, f'Wrong arguments. Usage: python {argv[0]} CONFIG_FILE PORT')

    PORT = int(argv[2])

    upd_config_res = cmd_update_config(argv[1])
    if upd_config_res.error_occurred:
        return upd_config_res

    init_logger()
    init_mail_credentials()

    return Message(False, '')


def main():
    init_result = init_checker(sys.argv)
    if init_result.error_occurred:
        return

    LOGGER.log('checker initialization DONE')

    sleep(2)

    try:
        connect_to_host()
        work()
        disconnect_from_host()
    except Exception as e:
        LOGGER.log(f'unexpected exception with message `{str(e)}\'. Exit.', logging.FATAL)

    LOGGER.log('CHECKER EXITED')


if __name__ == '__main__':
    main()