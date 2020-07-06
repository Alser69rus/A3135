from dataclasses import dataclass, field
from datetime import datetime


@dataclass()
class Fill:
    t1 = datetime.now()
    t2 = datetime.now()

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()

    def update(self):
        self.t2 = datetime.now()

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return self.time() <= 4


@dataclass()
class Sensitivity:
    ptc = []
    t1 = datetime.now()
    t2 = datetime.now()

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.ptc = []

    def update(self, value: float):
        self.t2 = datetime.now()
        self.ptc.append(value)

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def delta_p(self) -> float:
        return max(self.ptc) - min(self.ptc)

    def result(self) -> bool:
        return self.delta_p() <= 0.015

    def text(self) -> str:
        if self.result():
            return f'{self.delta_p():.3f}'
        return f'{self.delta_p():.3f} (не норма)'


@dataclass()
class Empty:
    t1 = datetime.now()
    t2 = datetime.now()

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()

    def update(self):
        self.t2 = datetime.now()

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return self.time() <= 10


@dataclass()
class RdData:
    fill = Fill()
    sensitivity = Sensitivity()
    empty = Empty()
    valve = '-'
    junctions = '-'
