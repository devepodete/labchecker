from PipelineBase import IPipelineElement, Verdict
from Utils import remove_file

from typing import List


class FileCleaner(IPipelineElement):
    def __init__(self, files: List[str]):
        super().__init__('FileCleaner')
        self.files = files

    def execute(self) -> None:
        self.executionResult.verdict = Verdict.OK
        for file in self.files:
            try:
                remove_file(file)
            except OSError:
                self.executionResult.verdict = Verdict.FAIL
                self.executionResult.verdictInfo += f'{file} '
