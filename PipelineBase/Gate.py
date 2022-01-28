from .GateExecutionPolicy import ExecutionPolicy
from .IPipelineElement import IPipelineElement
from .Verdict import Verdict

from typing import List


class Gate(IPipelineElement):
    def __init__(self, name: str, pipeline: List[IPipelineElement], execution_policy: ExecutionPolicy):
        super().__init__(name)
        self.name = name
        self.pipeline = pipeline
        self.executionPolicy = execution_policy

    def execute(self):
        for pipelineElem in self.pipeline:
            pipelineElem.execute()
            res = pipelineElem.get_result()
            if res.verdict != Verdict.OK:
                self.executionResult.verdict = Verdict.FAIL
                return

        self.executionResult.verdict = Verdict.OK
