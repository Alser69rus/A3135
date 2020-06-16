from dataclasses import dataclass, field
from datetime import datetime


@dataclass()
class Breaking:
    stage = (
        '1 ступень',
        '2 ступень',
        '3 ступень',
        '4 ступень',
        '3 ступень',
        '2 ступень',
        '1 ступень',
        'отпускное',
    )
    range = (
        (0.10, 0.13),
        (0.17, 0.20),
        (0.27, 0.30),
        (0.37, 0.40),
        (0.27, 0.30),
        (0.17, 0.20),
        (0.10, 0.13),
        (0.00, 0.01),
    )
    tc1 = [-1.0] * 8
    tc2 = [-1.0] * 8

    def range_as_text(self, stage: int) -> str:
        low, high = self.range[stage]
        return f'{low:.3f} - {high:.3f}'

    def tc1_as_text(self, stage: int) -> str:
        value: float = self.tc1[stage]
        low, high = self.range[stage]
        res = '' if low <= value <= high else '(не норма)'
        if value < -0.1: return '-'
        return f'{value:5.3f} {res}'

    def tc2_as_text(self, stage: int) -> str:
        value: float = self.tc2[stage]
        low, high = self.range[stage]
        res = '' if low <= value <= high else '(не норма)'
        if value < -0.1: return '-'
        return f'{value:5.3f} {res}'

    def success(self) -> bool:
        res1 = [self.range[i][0] <= self.tc1[i] <= self.range[i][1] for i in range(8)]
        res2 = [self.range[i][0] <= self.tc2[i] <= self.range[i][1] for i in range(8)]
        return all(res1 + res2)


@dataclass()
class FillTime:
    tc1: float = 0
    tc2: float = 0

    def success(self) -> bool:
        return 0 < self.tc1 <= 4 and 0 < self.tc2 <= 4

    @staticmethod
    def time_as_text(value: float) -> str:
        if value == 0:
            return '-'
        elif 0 < value <= 4:
            return f'{value:.1f}'
        else:
            return f'{value:.1f} (не норма)'


@dataclass()
class EmptyTime:
    tc = [0.0, 0.0]
    t = [datetime.now(), datetime.now()]
    running = [False, False]

    def start(self, tc: int):
        self.tc[tc] = 0.0
        self.t[tc] = datetime.now()
        self.running[tc] = True

    def stop(self, tc: int):
        if self.running[tc]:
            self.running[tc] = False
            self.tc[tc] = (datetime.now() - self.t[tc]).total_seconds()

    def success(self) -> bool:
        return all([0 < t <= 13 for t in self.tc])

    def time_as_text(self, tc: int) -> str:
        t: float = self.tc[tc]
        if t == 0:
            return '-'
        elif 0 < t <= 13:
            return f'{t:.1f}'
        else:
            return f'{t:.1f} (не норма)'


@dataclass()
class BtpData:
    auto_breaking: Breaking = field(default_factory=Breaking)
    kvt_breaking: Breaking = field(default_factory=Breaking)
    fill_time: FillTime = field(default_factory=FillTime)
    empty_time: EmptyTime = field(default_factory=EmptyTime)
    tightness: str = '-'
