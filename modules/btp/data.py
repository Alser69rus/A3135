from dataclasses import dataclass, field
from typing import List
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
class Filling:
    t: float = -1.0
    t1: datetime = datetime.now()
    t2: datetime = datetime.now()
    tc1 = []
    tc2 = []
    t_arr = []

    def set_t1(self) -> None:
        self.t1 = datetime.now()
        self.tc1 = []
        self.tc2 = []
        self.t_arr = []

    def set_t2(self, tc1: float, tc2: float) -> None:
        self.t2 = datetime.now()
        t = (self.t2 - self.t1).total_seconds()
        self.t = round(t, 1)
        self.t_arr.append(t)
        self.tc1.append(tc1)
        self.tc2.append(tc2)

    def t_as_text(self) -> str:
        if self.t < 0:
            return '-'
        return f'{self.t:.1f}'

    def success(self) -> bool:
        return self.t <= 4.0


@dataclass()
class BtpData:
    auto_breaking: Breaking = field(default_factory=Breaking)
    kvt_breaking: Breaking = field(default_factory=Breaking)
    filing: Filling = field(default_factory=Filling)
