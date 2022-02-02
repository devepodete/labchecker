from PipelineBase import Gate, GateHolder, ExecutionPolicy
from StudentInteraction.Communication import MailMessage, MailAttachment, AttachmentKind, MailSender, MailReceiver, \
    authentication
from StudentInteraction.ReportGeneration import ReportGenerator, ReportType

from Pipeline import ExecutableBuilder, FileSizeLimiter, FileCleaner, ExecutableRunner

from Utils import AnswerComparator

import os.path
import dateutil.parser

TEST_FOLDER = 'TestingArea'
SUBMITS_FOLDER = os.path.join(TEST_FOLDER, 'Submits')
LABS_FOLDER = os.path.join(TEST_FOLDER, 'Labs')


def good_subject(subject: str):
    return len(subject) == 4 and subject.startswith('os:') and subject[-1] in ('1', '2', '3', '4', '5')


def main():
    from time import sleep
    login, password = authentication.get_credentials('StudentInteraction/.admin_credentials')
    done = False

    while not done:
        messages_to_send = []
        print('Sleeping 5 sec')
        sleep(5)
        with MailReceiver(login, password) as receiveServer:
            new_messages = receiveServer.fetch()
            print(f'got {len(new_messages)} new messages')

            for idx, msg in enumerate(new_messages):
                done = True
                print(f'{idx}. {str(msg)}')
                if len(msg.Attachments) != 0:

                    user_folder = os.path.join(SUBMITS_FOLDER, msg.From)
                    if not os.path.exists(user_folder):
                        os.mkdir(user_folder)

                    if not good_subject(msg.Subject):
                        messages_to_send.append(MailMessage(login, msg.From, 'Result', 'Bad subject'))
                        continue

                    lab_folder = os.path.join(user_folder, msg.Subject)
                    if not os.path.exists(lab_folder):
                        os.mkdir(lab_folder)

                    date = dateutil.parser.parse(msg.Date)
                    submit_folder = os.path.join(lab_folder, f'{date.date()}+{date.time()}')
                    if not os.path.exists(lab_folder):
                        messages_to_send.append(MailMessage(login, msg.From, 'Result', 'Don not send too quickly!'))
                        continue

                    os.mkdir(submit_folder)

                    src_path = os.path.join(submit_folder, 'main.cpp')
                    exec_path = os.path.join(submit_folder, 'main.out')

                    msg.Attachments[0].save_to(src_path)

                    # generate tests folder path
                    lab_number = msg.Subject.split(':')[-1]
                    student_var = 'var12'  # TODO

                    lab_variant_path = os.path.join(LABS_FOLDER, lab_number)
                    lab_variant_path = os.path.join(lab_variant_path, student_var)

                    gate0 = Gate('PreparationChecks',
                                 [FileSizeLimiter(src_path, 10000)], ExecutionPolicy.RUN_ALWAYS)
                    gate1 = Gate('Build',
                                 [ExecutableBuilder('g++', ['-Wall', '-Werror'], src_path, exec_path)],
                                 ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)
                    gate2 = Gate('Test',
                                 [ExecutableRunner(exec_path,
                                                   lab_variant_path,
                                                   AnswerComparator('./TestingArea/AnswerComparators/ncmp.out',  # TODOs
                                                                    '1 {0} {1}'),
                                                   './TestingArea/.temp.txt')],
                                 ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)
                    gate3 = Gate('Clean',
                                 [FileCleaner([exec_path])], ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)

                    gh = GateHolder([gate0, gate1, gate2])
                    gh.execute()

                    rg = ReportGenerator([gate1, gate2])

                    rg.generate_report(ReportType.Html)
                    m = MailMessage(login, msg.From, 'Result')
                    m.attach_file(MailAttachment('report', rg.report, AttachmentKind.Html))
                    messages_to_send.append(m)
                else:
                    print('No attachments')

        with MailSender(login, password) as sendServer:
            print('Sending replies... ', end='')
            for idx, msg in enumerate(messages_to_send):
                print(f'{idx}. {str(msg)}')
                assert msg.From != msg.To
                sendServer.send_message(msg)
            print('Done')


if __name__ == '__main__':
    main()
