from PipelineBase import IPipelineElement, ExecutionResult


class ExecutableBuilder(IPipelineElement):
    def __init__(self):
        super().__init__('Build')

    def execute(self, ancestor_execution_result: ExecutionResult) -> None:
        pass

    def get_result(self) -> ExecutionResult:
        pass
