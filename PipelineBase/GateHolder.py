from .Gate import Gate
from .ExecutionResult import ExecutionResult

from typing import List


class GateHolder:
    def __init__(self, gates: List[Gate]):
        self.gates = gates

    def execute(self):
        for gate in self.gates:
            result = None
            for pipelineElem in gate.pipeline:
                pipelineElem.execute(result)
                result = pipelineElem.get_result()
