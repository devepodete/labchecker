from PipelineBase import IPipelineElement, ExecutionResult


class Antiplagiarism(IPipelineElement):
    def __init__(self):
        super().__init__('Antiplagiarism')

    def execute(self, ancestor_execution_result: ExecutionResult) -> None:
        pass

    def get_result(self) -> ExecutionResult:
        pass
