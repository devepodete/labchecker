from .Gate import Gate
from .GateExecutionPolicy import ExecutionPolicy
from .Verdict import Verdict

from typing import List


class GateHolder:
    def __init__(self, gates: List[Gate]):
        self.gates = gates

    def execute(self):
        prev_gate_result = Verdict.OK
        for gate in self.gates:
            if prev_gate_result != Verdict.OK and gate.executionPolicy == ExecutionPolicy.RUN_IF_PREVIOUS_SUCCEED:
                continue
            gate.execute()
            prev_gate_result = gate.get_result().verdict
