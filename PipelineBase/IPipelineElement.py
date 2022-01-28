from .ExecutionResult import ExecutionResult
from .Verdict import Verdict

from abc import ABCMeta, abstractmethod


class IPipelineElement:
    __metaclass__ = ABCMeta

    def __init__(self, name: str):
        self.executionResult = ExecutionResult(name, Verdict.NR)

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError

    def get_result(self) -> ExecutionResult:
        return self.executionResult
