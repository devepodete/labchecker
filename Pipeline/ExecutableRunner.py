from PipelineBase import IPipelineElement


class ExecutableRunner(IPipelineElement):
    def __init__(self):
        super().__init__('Run')

    def execute(self) -> None:
        pass
