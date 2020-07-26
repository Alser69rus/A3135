from datetime import datetime


class Fill:
    def __init__(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty = True

    def reset(self):
        self.empty = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty = False

    def stop(self):
        self.t2 = datetime.now()

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.empty:
            return '-'
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return 0 < self.time() <= 4


class Empty:
    def __init__(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty = True

    def reset(self):
        self.empty = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty = False

    def stop(self):
        self.t2 = datetime.now()

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.empty:
            return '-'
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return 0 < self.time() <= 4


class Junctions:
    def __init__(self):
        self.empty = True
        self.condition = False

    def reset(self):
        self.empty = True

    def success(self):
        self.empty = False
        self.condition = True

    def fail(self):
        self.empty = False
        self.condition = False

    def result(self) -> bool:
        return not self.empty and self.condition

    def text(self) -> str:
        if self.empty:
            return '-'
        if self.condition:
            return f'норма'
        else:
            return f'не норма'


class KebData:
    def __init__(self):
        self.fill = Fill()
        self.empty = Empty()
        self.junctions = Junctions()
