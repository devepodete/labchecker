from PipelineBase import IPipelineElement, Verdict

import subprocess
from pathlib import Path
from typing import List


class ExecutableBuilder(IPipelineElement):
    def __init__(self, compiler: str, compiler_flags: List[str], source_file: Path, output_file: Path):
        super().__init__('Build')
        self.compiler = compiler
        self.compilerFlags = compiler_flags
        self.sourceFile = source_file
        self.outputFile = output_file

    def execute(self) -> None:
        res = subprocess.run([self.compiler, *self.compilerFlags, str(self.sourceFile), '-o', str(self.outputFile)],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)

        if res.returncode != 0:
            if res.stderr:
                try:
                    self.executionResult.message = res.stderr.decode('utf-8')
                except UnicodeDecodeError:
                    pass
            self.executionResult.verdict = Verdict.FAIL
        else:
            self.executionResult.verdict = Verdict.OK
