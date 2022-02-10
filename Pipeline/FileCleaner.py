from PipelineBase import IPipelineElement, Verdict

from pathlib import Path
from typing import List


class FileCleaner(IPipelineElement):
    def __init__(self, files: List[Path]):
        super().__init__('FileCleaner')
        self.files = files

    def execute(self) -> None:
        self.executionResult.verdict = Verdict.OK
        for file in self.files:
            file.unlink(missing_ok=True)
