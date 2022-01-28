from PipelineBase import Gate, Verdict

from typing import List

REPORT_BG_COLOR = '#c9a0dc'

VERDICT_COLOR = {
    Verdict.OK: '#8dfc71',
    Verdict.WA: '#ff896a',
    Verdict.CE: '#ff896a',
    Verdict.TL: '#ff896a',
    Verdict.ML: '#ff896a',
    Verdict.RE: '#ff896a',
    Verdict.FAIL: '#c70039',
    Verdict.NR: '#fffd71',
}


class ReportType:
    Text = 0,
    Html = 1


class ReportGenerator:
    def __init__(self, gates: List[Gate], output: str, report_type: ReportType):
        self.gates = gates
        self.output = output
        self.reportType = report_type

    def generate_report(self) -> None:
        if self.reportType == ReportType.Text:
            report = self.generate_text()
        elif self.reportType == ReportType.Html:
            report = self.generate_html()
        else:
            raise NotImplementedError

        if self.output is not None and len(self.output) != 0:
            with open(self.output, 'w') as f:
                f.write(report)

    def generate_text(self) -> str:
        report = ''
        for gate in self.gates:
            report += f'\nGATE {gate.name}\n'

            for pipelineElem in gate.pipeline:
                result = pipelineElem.get_result()
                report += f'{result.name}: {result.verdict}{result.message}\n'

        return report

    def generate_html(self) -> str:
        report = "<table border=1 style='text-align:center; vertical-align:middle'>"
        report += "<caption>Verdict</caption>"

        report += f"<tr bgcolor={REPORT_BG_COLOR}>"
        for gate in self.gates:
            report += f"<td colspan={2 * len(gate.pipeline)}>Gate {gate.name}</td>"
        report += "</tr>"

        report += "<tr>"
        for gate in self.gates:
            for pipelineElem in gate.pipeline:
                res = pipelineElem.get_result()
                report += f"<td>{res.name}</td>"
                report += f"<td bgcolor={VERDICT_COLOR[res.verdict]}>{res.verdict}{res.message}</td>"
        report += "</tr>"

        report += "</table>"

        return report
