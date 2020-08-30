class KpData:
    def __init__(self):
        self.p: float = 0.0
        self.t1: float = 0.0
        self.t2: float = 0.0

    def reset(self):
        self.p = 0.0
        self.t1 = 0.0
        self.t2 = self.t1

    def text_p(self) -> str:
        if not self.p:
            return '-'
        elif 0.2 < self.p <= 0.25:
            return f'{self.p:.3f}'
        else:
            return f'{self.p:.3f} (не норма)'

    def text_t(self) -> str:
        t = self.t2 - self.t1
        if t < 0.1:
            return '-'
        elif 0.1 <= t <= 4:
            return f'{t:.1f}'
        else:
            return f'{t:.1f} (не норма)'

    def result(self) -> bool:
        t = self.t2 - self.t1
        return 0.2 <= self.p <= 0.25 and 0.1 <= t <= 4
