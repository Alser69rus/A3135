from datetime import datetime


class KU215:
    def __init__(self):
        self.handle = (
            '1 ступень (0.10-0.13)',
            '2 ступень (0.17-0.20)',
            '3 ступень (0.27-0.30)',
            '4 ступень (0.37-0.40)',
            '3 ступень',
            '2 ступень',
            '1 ступень',
            'отпуск',
        )
        self.range = (
            (0.10, 0.13),
            (0.17, 0.20),
            (0.27, 0.30),
            (0.37, 0.40),
            (0.27, 0.30),
            (0.17, 0.20),
            (0.10, 0.13),
            (0.0, 0.005),
        )


class Breaking:
    def __init__(self):
        self.tc = [[-1.0] * 8, [-1.0] * 8]
        self.pim = [-1.0] * 8
        self.ku_215: KU215 = KU215()

    def position_as_text(self, position: int):
        return self.ku_215.handle[position]

    def range_as_text(self, position: int) -> str:
        low, high = self.ku_215.range[position]
        return f'{low:.3f} - {high:.3f}'

    def pim_as_text(self, position: int) -> str:
        if self.pim[position] < -0.1:
            return '-'
        else:
            return f'{self.pim[position]:.3f}'

    def tc_as_text(self, tc: int, position: int) -> str:
        value: float = self.tc[tc][position]
        pim: float = self.pim[position]

        if value < -0.1 or pim < -0.1:
            return '-'
        elif self.check_tc(tc=tc, position=position):
            return f'{value:5.3f}'
        else:
            return f'{value:5.3f} (не норма)'

    def check_tc(self, tc: int, position: int) -> bool:
        value: float = self.tc[tc][position]
        pim: float = self.pim[position]
        if position < 4:
            low, high = self.ku_215.range[position]
        else:
            low, high = pim - 0.03, pim + 0.03
        if value < -0.1 or pim < -0.1:
            return False
        elif low <= value <= high:
            return True
        else:
            return False

    def success(self) -> bool:
        res = []
        for i in range(8):
            res.append(self.check_tc(0, i))
            res.append(self.check_tc(1, i))
        return all(res)


class FillTime:
    def __init__(self):
        self.tc = [0.0, 0.0]
        self.t = [datetime.now(), datetime.now()]
        self.running = [False, False]

    def start(self):
        self.tc = [0.0, 0.0]
        self.t = [datetime.now(), datetime.now()]
        self.running = [True, True]

    def stop(self, tc: int):
        if self.running[tc]:
            self.running[tc] = False
            self.tc[tc] = (datetime.now() - self.t[tc]).total_seconds()

    def success(self) -> bool:
        return all([0.05 < t <= 4 for t in self.tc])

    def time_as_text(self, tc: int) -> str:
        value = self.tc[tc]
        if value < 0.05:
            return '-'
        elif 0 < value <= 4:
            return f'{value:.1f}'
        else:
            return f'{value:.1f} (не норма)'


class EmptyTime:
    def __init__(self):
        self.tc = [0.0, 0.0]
        self.t = [datetime.now(), datetime.now()]
        self.running = [False, False]

    def start(self, tc: int):
        self.tc[tc] = 0.0
        self.t[tc] = datetime.now()
        self.running[tc] = True

    def stop(self, tc: int):
        if self.running[tc]:
            self.running[tc] = False
            self.tc[tc] = (datetime.now() - self.t[tc]).total_seconds()

    def success(self) -> bool:
        return all([0.05 < t <= 13 for t in self.tc])

    def time_as_text(self, tc: int) -> str:
        t: float = self.tc[tc]
        if t < 0.05:
            return '-'
        elif 0 < t <= 13:
            return f'{t:.1f}'
        else:
            return f'{t:.1f} (не норма)'


class BtpData:
    def __init__(self):
        self.ku_215: KU215 = KU215()
        self.auto_breaking: Breaking = Breaking()
        self.kvt_breaking: Breaking = Breaking()
        self.fill_time: FillTime = FillTime()
        self.empty_time: EmptyTime = EmptyTime()
        self.tightness: str = '-'
        self.substitution: FillTime = FillTime()
        self.speed_fill: FillTime = FillTime()
        self.speed_empty: EmptyTime = EmptyTime()
        self.sped_ok = ['-', '-']
