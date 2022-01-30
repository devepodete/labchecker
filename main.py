from PipelineBase import Gate, GateHolder, IPipelineElement, ExecutionPolicy, Verdict
from StudentInteraction.Communication import MailMessage, MailAttachment, AttachmentKind, MailSender, MailReceiver, \
    authentication
from StudentInteraction.ReportGeneration import ReportGenerator, ReportType

from Pipeline import ExecutableBuilder, FileSizeLimiter, FileCleaner


class A(IPipelineElement):
    def __init__(self):
        super().__init__('A')

    def execute(self) -> None:
        self.executionResult.verdict = Verdict.OK


class B(IPipelineElement):
    def __init__(self):
        super().__init__('B')

    def execute(self) -> None:
        self.executionResult.verdict = Verdict.WA
        self.executionResult.message = '7'


class C(IPipelineElement):
    def __init__(self, name='C'):
        super().__init__(name)

    def execute(self) -> None:
        self.executionResult.verdict = Verdict.OK


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
                    msg.Attachments[0].save_to('TestingArea/main.c')
                    gate0 = Gate('PreparationChecks',
                                 [FileSizeLimiter('TestingArea/main.c', 10000)], ExecutionPolicy.RUN_ALWAYS)
                    gate1 = Gate('Build',
                                 [ExecutableBuilder('gcc', ['-Wall', '-Werror'], 'TestingArea/main.c',
                                                    'TestingArea/main.out')],
                                 ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)
                    gate2 = Gate('Clean',
                                 [FileCleaner(['TestingArea/main.out'])], ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)

                    gh = GateHolder([gate0, gate1, gate2])
                    gh.execute()

                    rg = ReportGenerator(gh.gates)

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

    return

    gate1 = Gate('1', [A(), B()], ExecutionPolicy.RUN_ALWAYS)
    gate2 = Gate('2 (testing)', [C('C')], ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)
    gate3 = Gate('3', [C('C1')], ExecutionPolicy.RUN_ALWAYS)
    gate4 = Gate('4', [C('C2')], ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED)

    gh = GateHolder([gate1, gate2, gate3, gate4])
    gh.execute()

    rg = ReportGenerator(gh.gates, 'result.html', ReportType.Html)
    rg.generate_report()


if __name__ == '__main__':
    main()
