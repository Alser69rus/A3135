from PyQt5 import QtWidgets, QtCore
from dataclasses import dataclass, field
from PyQt5.QtCore import QPointF, QRectF, QLineF, pyqtSlot
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont
from opc.opc import AnalogItemType

WIDGET_WIDTH = 190
WIDGET_HEIGHT = 220


class Caption(QtWidgets.QLabel):
    def __init__(self, text: str = 'Манометр', parent=None):
        super().__init__(parent=parent)
        self.setText(text)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(QFont('Segoi UI', 14))


class Value(QtWidgets.QLabel):
    def __init__(self, value: float = 0, parent=None):
        super().__init__(parent=parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(QFont('Segoi UI', 14))
        self.format: str = '{:5.3f} МПа'
        self.setText(self.format.format(value))


class Manometer(QtWidgets.QWidget):
    def __init__(self, manometer: AnalogItemType, parent=None):
        super().__init__(parent=parent)
        self.setMinimumSize(150, 150)
        self.setFixedSize(WIDGET_WIDTH, WIDGET_HEIGHT)

        self.caption = Caption(manometer.name)
        self.value = Value()
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.addWidget(self.caption)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.value)

        self.scale = Scale()
        self.arrow = Arrow()

        self.scale.label.max = manometer.eu_range.high
        self.scale.primary.count = round(10 * manometer.eu_range.high)
        self.scale.secondary.count = 2
        self.scale.tertiary.count = 2

        manometer.value_changed.connect(self.set_value)

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.bevel_draw(painter)
        self.scale.draw(painter)
        self.arrow.draw(painter)

    def bevel_draw(self, painter: QPainter):
        painter.drawRoundedRect(0, 0, self.width() - 2, self.height() - 2, 8, 8)

    @pyqtSlot(float)
    def set_value(self, value: float):
        self.value.setText(self.value.format.format(value))
        angle_range = self.scale.angle.max - self.scale.angle.min
        value_range = self.scale.label.max - self.scale.label.min
        angle = value * angle_range / value_range
        self.arrow.angle = self.scale.angle.min + angle
        self.update()


@dataclass
class ScaleMark:
    count: int
    line: QLineF = field(default_factory=QLineF)


@dataclass
class ScalePen:
    primary: QPen = field(default=QPen(QBrush(QColor(QtCore.Qt.black)), 3))
    secondary: QPen = field(default=QPen(QBrush(QColor(QtCore.Qt.black)), 1))


@dataclass
class ScaleAngle:
    min: float = 210
    max: float = -30


@dataclass
class ScaleLabel:
    min: float = 0
    max: float = 1.6
    radius: QPointF = field(default=QPointF(80, 0))
    rect: QRectF = field(default=QRectF(-10, -10, 20, 20))
    format: str = '{:3.1f}'


class Scale:
    def __init__(self):
        self.center: QPointF = QPointF(95, 130)
        self.angle = ScaleAngle()
        self.label = ScaleLabel()
        self.primary = ScaleMark(8, QLineF(58, 0, 62, 0))
        self.secondary = ScaleMark(2, QLineF(50, 0, 58, 0))
        self.tertiary = ScaleMark(2, QLineF(50, 0, 54, 0))
        self.pen = ScalePen()

    def draw(self, painter: QPainter):
        count = self.primary.count * self.secondary.count * self.tertiary.count
        da = (self.angle.max - self.angle.min) / count
        dv = (self.label.max - self.label.min) / count

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.center)
        painter.rotate(-self.angle.min)

        for i in range(count + 1):
            if self.is_primary(i):
                self.draw_primary(painter)
                v = self.label.min + i * dv
                a = self.angle.min + da * i
                self.draw_label(painter, v, a)
            elif self.is_secondary(i):
                self.draw_secondary(painter)
            else:
                self.draw_tertiary(painter)
            painter.rotate(-da)
        painter.restore()

    def draw_primary(self, painter: QPainter) -> None:
        painter.setPen(self.pen.primary)
        painter.drawLine(self.primary.line)
        self.draw_secondary(painter)

    def draw_secondary(self, painter: QPainter) -> None:
        painter.setPen(self.pen.secondary)
        painter.drawLine(self.secondary.line)

    def draw_tertiary(self, painter: QPainter) -> None:
        painter.setPen(self.pen.secondary)
        painter.drawLine(self.tertiary.line)

    def draw_label(self, painter: QPainter, value: float, angle: float) -> None:
        painter.save()
        painter.translate(self.label.radius)
        painter.rotate(angle)
        painter.drawText(self.label.rect, QtCore.Qt.AlignCenter, self.label.format.format(value))
        painter.restore()

    def is_primary(self, idx: int) -> bool:
        return not idx % (self.secondary.count * self.tertiary.count)

    def is_secondary(self, idx: int) -> bool:
        return not idx % self.tertiary.count


class Arrow:
    def __init__(self):
        self.center = QPointF(95, 130)
        self.angle: float = 210
        self.pen = QPen(QtCore.Qt.red)
        self.brush = QBrush(QtCore.Qt.red)

    def draw(self, painter: QPainter):
        painter.save()
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.center)
        painter.rotate(-self.angle)

        self.draw_head(painter)
        self.draw_tail(painter)
        painter.restore()

    @staticmethod
    def draw_head(painter: QPainter):
        p1 = QPointF(0, 4)
        p2 = QPointF(48, 0)
        p3 = QPointF(0, -4)
        painter.drawPolygon(p1, p2, p3)

    @staticmethod
    def draw_tail(painter: QPainter):
        rect = QRectF(-4, -4, 8, 8)
        painter.drawEllipse(rect)
