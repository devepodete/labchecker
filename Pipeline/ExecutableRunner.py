from PipelineBase import IPipelineElement, ExecutionResult, Verdict


class ExecutableRunner(IPipelineElement):
    def __init__(self):
        super().__init__('Run')

    def execute(self, ancestor_execution_result: ExecutionResult) -> None:
        if ancestor_execution_result.verdict != Verdict.OK:
            return

    def get_result(self) -> ExecutionResult:
        pass
