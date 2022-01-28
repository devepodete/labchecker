from PipelineBase import IPipelineElement


class ExecutableBuilder(IPipelineElement):
    def __init__(self):
        super().__init__('Build')

    def execute(self) -> None:
        pass
