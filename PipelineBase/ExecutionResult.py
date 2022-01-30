from .Verdict import Verdict


class ExecutionResult:
    def __init__(self, name: str, verdict: Verdict, verdict_info='', message=''):
        self.name = name
        self.verdict = verdict
        self.verdictInfo = verdict_info
        self.message = message
