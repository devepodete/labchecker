from .Verdict import Verdict


class ExecutionResult:
    def __init__(self, name: str, verdict: Verdict, message=''):
        self.name = name
        self.verdict = verdict
        self.message = message
