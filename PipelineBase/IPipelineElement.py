from .ExecutionResult import ExecutionResult
from .Verdict import Verdict

from abc import ABCMeta, abstractmethod


class IPipelineElement:
    __metaclass__ = ABCMeta

    def __init__(self, name='IPipelineElement', verdict=Verdict.NR):
        self.executionResult = ExecutionResult(name, verdict)

    @abstractmethod
    def execute(self, ancestor_execution_result: ExecutionResult) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_result(self) -> ExecutionResult:
        return self.executionResult
