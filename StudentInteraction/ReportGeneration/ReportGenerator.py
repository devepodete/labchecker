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
    def __init__(self, gates: List[Gate]):
        self.gates = gates
        self.report = ''

    def generate_report(self, report_type: ReportType) -> None:
        if report_type == ReportType.Text:
            self.generate_text()
        elif report_type == ReportType.Html:
            self.generate_html()
        else:
            raise NotImplementedError

    def save_to(self, path: str) -> None:
        with open(path, 'w') as f:
            f.write(self.report)

    def generate_text(self) -> None:
        report = ''
        for gate in self.gates:
            report += f'\nGATE {gate.name}\n'

            for pipelineElem in gate.pipeline:
                result = pipelineElem.get_result()
                report += f'{result.name}: {result.verdict}{result.verdictInfo}\n'
                if len(result.message) != 0:
                    report += f'Message (first 1000 chars): `{result.message[:1000]}\''

        self.report = report

    def generate_html(self) -> None:
        report = "<table border=1 style='text-align:center; vertical-align:middle'>"
        report += "<caption>Verdict</caption>"

        report += f"<tr bgcolor={REPORT_BG_COLOR}>"
        for gate in self.gates:
            report += f"<td colspan={2 * len(gate.pipeline)}>Gate {gate.name}</td>"
        report += "</tr>"

        report += "<tr>"
        message = ''
        for gate in self.gates:
            for pipelineElem in gate.pipeline:
                res = pipelineElem.get_result()
                report += f"<td>{res.name}</td>"
                report += f"<td bgcolor={VERDICT_COLOR[res.verdict]}>{res.verdict}{res.verdictInfo}</td>"
                if len(res.message) != 0 and len(message) < 1000:
                    message += res.message[:1000]

        report += "</tr>"

        report += "</table>"
        if len(message) != 0:
            report += f'Message (first 1000 chars): {message}'

        self.report = report
