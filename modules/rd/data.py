from datetime import datetime


class Fill:
    def __init__(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = True

    def reset(self):
        self.empty_value = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = False

    def update(self):
        self.t2 = datetime.now()

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.empty_value:
            return '-'
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return 0 < self.time() <= 4


class Sensitivity:
    def __init__(self):
        self.ptc = []
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = True

    def reset(self):
        self.empty_value = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.ptc = []
        self.empty_value = False

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
        if self.empty_value:
            return '-'
        if self.result():
            return f'{self.delta_p():.3f}'
        return f'{self.delta_p():.3f} (не норма)'


class Empty:
    def __init__(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = True

    def reset(self):
        self.empty_value = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = False

    def update(self):
        self.t2 = datetime.now()

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.empty_value:
            return '-'
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return 0 < self.time() <= 10


class RdData:
    def __init__(self):
        self.fill = Fill()
        self.sensitivity = Sensitivity()
        self.empty = Empty()
        self.valve = '-'
        self.junctions = '-'
