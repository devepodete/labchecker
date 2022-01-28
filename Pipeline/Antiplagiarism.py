from PipelineBase import IPipelineElement


class Antiplagiarism(IPipelineElement):
    def __init__(self):
        super().__init__('Antiplagiarism')

    def execute(self) -> None:
        pass
