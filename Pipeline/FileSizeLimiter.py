from PipelineBase import IPipelineElement, Verdict
from Utils import get_file_size

from pathlib import Path


class FileSizeLimiter(IPipelineElement):
    def __init__(self, file: Path, max_size_bytes: int):
        super().__init__('FileSize')
        self.file = file
        self.maxSizeBytes = max_size_bytes

    def execute(self) -> None:
        size = get_file_size(self.file)
        if size > self.maxSizeBytes:
            self.executionResult.verdict = Verdict.FAIL
            self.executionResult.message = f'File `{self.file}\' size is {size}. Maximum is {self.maxSizeBytes}'
        else:
            self.executionResult.verdict = Verdict.OK
