from PipelineBase import IPipelineElement, Verdict
from Utils import AnswerComparator

from pathlib import Path
import subprocess

from subprocess import SubprocessError


class ExecutableRunner(IPipelineElement):
    def __init__(self, executable_path: Path, lab_variant_path: Path, comparator: AnswerComparator, temp_file: Path):
        super().__init__('Tests')
        self.executablePath = executable_path
        self.labVariantPath = lab_variant_path
        self.testsPath = lab_variant_path / 'tests'
        self.limitsFile = lab_variant_path / 'limits.txt'
        self.comparator = comparator
        self.tempFile = temp_file

    def execute(self) -> None:
        if not self.testsPath.exists() or not self.limitsFile.exists():
            self.executionResult.verdict = Verdict.FAIL
            self.executionResult.message = f'Unable to find tests info in {self.labVariantPath}'
            return

        test_idx = 1
        self.executionResult.verdict = Verdict.OK

        with open(self.limitsFile, 'r') as f:
            lines = f.readlines()

        if len(lines) != 2 or not lines[0].startswith('ML=') or not lines[1].startswith('TL='):
            self.executionResult.verdict = Verdict.FAIL
            self.executionResult.message = f'Bad limits file file {self.limitsFile}'
            return

        # memory_limit = int(lines[0].split('=')[-1]) TODO
        time_limit = int(lines[1].split('=')[-1])

        while True:
            test_input = self.testsPath / f'in{str(test_idx)}.txt'
            test_output = self.testsPath / f'out{str(test_idx)}.txt'

            if not (test_input.exists() and test_output.exists()):
                break

            try:
                p1 = subprocess.Popen(('cat', test_input), stdout=subprocess.PIPE)
                output = subprocess.check_output(self.executablePath,
                                                 stdin=p1.stdout,
                                                 stderr=subprocess.DEVNULL,
                                                 timeout=time_limit)
                p1.wait()
            except SubprocessError:
                self.executionResult.verdict = Verdict.RE
                self.executionResult.verdictInfo = str(test_idx)
                break

            with open(self.tempFile, 'wb') as f:
                f.write(output)

            if not self.comparator.are_equal(self.tempFile, test_output):
                self.executionResult.verdict = Verdict.WA
                self.executionResult.verdictInfo = str(test_idx)
                break

            test_idx += 1
