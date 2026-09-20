import math

from PySide6.QtCore import (
    Property, QEasingCurve, QPropertyAnimation, QRectF, QTimer, Qt, Signal,
)
from PySide6.QtGui import (
    QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient,
)
from PySide6.QtWidgets import QPushButton

from . import theme


def _lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return QColor(
        int(a.red() + (b.red() - a.red()) * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue() + (b.blue() - a.blue()) * t),
    )


class ToggleSwitch(QPushButton):
    switched = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(56, 30)
        self._t = 0.0
        self._glow = 0.0
        self._halo = 0.0
        self._hovered = False
        self._anim = QPropertyAnimation(self, b"posT")
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.OutBack)
        self._glow_anim = QPropertyAnimation(self, b"glowT")
        self._glow_anim.setDuration(520)
        self._glow_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._halo_anim = QPropertyAnimation(self, b"haloT")
        self._halo_anim.setDuration(240)
        self._halo_anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self._hovered = True
        self._start_halo(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._start_halo(0.0)
        super().leaveEvent(event)

    def _start_halo(self, end):
        self._halo_anim.stop()
        self._halo_anim.setStartValue(self._halo)
        self._halo_anim.setEndValue(end)
        self._halo_anim.start()

    def mouseReleaseEvent(self, event):
        before = self.isChecked()
        super().mouseReleaseEvent(event)
        if before != self.isChecked():
            self._animate()

    def _animate(self):
        self._anim.stop()
        self._anim.setStartValue(self._t)
        self._anim.setEndValue(1.0 if self.isChecked() else 0.0)
        self._anim.start()
        self._glow_anim.stop()
        self._glow_anim.setStartValue(1.0)
        self._glow_anim.setEndValue(0.88 if self.isChecked() else 0.62)
        self._glow_anim.start()
        self.switched.emit(self.isChecked())

    def setCheckedState(self, on, animate=True):
        if self.isChecked() == on:
            return
        self.setChecked(on)
        if animate:
            self._animate()
        else:
            self._t = 1.0 if on else 0.0
            self._glow = 0.88 if on else 0.62
            self.update()

    def getPosT(self):
        return self._t

    def setPosT(self, v):
        self._t = v
        self.update()

    posT = Property(float, getPosT, setPosT)

    def getGlowT(self):
        return self._glow

    def setGlowT(self, v):
        self._glow = v
        self.update()

    glowT = Property(float, getGlowT, setGlowT)

    def getHaloT(self):
        return self._halo

    def setHaloT(self, v):
        self._halo = v
        self.update()

    haloT = Property(float, getHaloT, setHaloT)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(0, 0, self.width(), self.height())
        on = self._t >= 0.5
        on_color = QColor(theme.ACCENT)
        off_color = QColor(theme.TRACK_OFF)
        track = _lerp_color(off_color, on_color, self._t) if self._t > 0 else QColor(off_color)
        if self._hovered:
            track = track.lighter(106)
        glow_rgb = theme.GLOW_ACCENT if on else theme.GLOW_OFF
        glow_color = QColor(*glow_rgb)
        strength = max(0.5, self._glow) * (1.0 if on else 0.85 + 0.15 * self._halo)
        glow_alpha = int((66 if on else 54) * strength)
        if glow_alpha > 1:
            glow = QRadialGradient(r.center(), self.width() * 1.15)
            gc = QColor(glow_color)
            gc.setAlpha(glow_alpha)
            glow.setColorAt(0.0, gc)
            gc2 = QColor(glow_color)
            gc2.setAlpha(0)
            glow.setColorAt(1.0, gc2)
            p.setBrush(glow)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(-10, -10, self.width() + 20, self.height() + 20))
        rim = QColor(glow_color)
        rim.setAlpha(int(190 * max(0.45, self._glow)))
        p.setPen(QPen(rim, 1.6))
        p.setBrush(track)
        p.drawRect(r.adjusted(1, 1, -1, -1))
        knob_r = 11
        margin = 4
        x = margin + (self.width() - knob_r * 2 - margin * 2) * self._t
        y = (self.height() - knob_r * 2) / 2.0
        knob_rect = QRectF(x, y, knob_r * 2, knob_r * 2)
        knob_grad = QLinearGradient(knob_rect.topLeft(), knob_rect.bottomLeft())
        knob_grad.setColorAt(0.0, QColor(theme.KNOB_TOP))
        knob_grad.setColorAt(1.0, QColor(theme.KNOB_TOP) if on else QColor(theme.KNOB_BOTTOM))
        knob_glow = QColor(glow_color)
        knob_glow.setAlpha(int(150 * max(0.5, self._glow)))
        p.setPen(Qt.NoPen)
        p.setBrush(knob_glow)
        p.drawRect(knob_rect.adjusted(-3, -3, 3, 3))
        p.setBrush(QBrush(knob_grad))
        p.drawRect(knob_rect)


class GlowButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(54)
        self._pulse = 0.0
        self._phase = 0.0
        self._pulsing = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(33)

    def setPulsing(self, on):
        self._pulsing = on
        if on:
            self._timer.start()
        else:
            self._timer.stop()
            self._pulse = 0.0
            self.update()

    def _tick(self):
        self._phase += 0.11
        self._pulse = (math.sin(self._phase) + 1.0) / 2.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRect(r)
        enabled = self.isEnabled()
        grad = QLinearGradient(0, 0, self.width(), 0)
        if enabled:
            grad.setColorAt(0.0, QColor(theme.ACCENT))
            grad.setColorAt(1.0, QColor(theme.ACCENT_2))
        else:
            grad.setColorAt(0.0, QColor(theme.BTN_DISABLED))
            grad.setColorAt(1.0, QColor(theme.BTN_DISABLED))
        hover = self.underMouse() and enabled
        glow_alpha = int(90 * (self._pulse if self._pulsing else (0.75 if hover else 0.35 if enabled else 0.0)))
        if glow_alpha > 0:
            g = QRadialGradient(r.center(), self.width() * 0.8)
            gc = QColor(theme.ACCENT_2 if not hover else theme.ACCENT)
            gc.setAlpha(glow_alpha)
            g.setColorAt(0.0, gc)
            gc2 = gc
            gc2.setAlpha(0)
            g.setColorAt(1.0, gc2)
            p.setBrush(g)
            p.setPen(Qt.NoPen)
            p.drawRect(r.adjusted(-10, -10, 10, 10))
        p.setPen(QPen(QColor(theme.BTN_BORDER) if not enabled else QColor(theme.ACCENT).darker(118), 1))
        p.setBrush(grad)
        p.drawPath(path)
        p.setFont(self._font())
        p.setPen(QColor("#ffffff") if enabled else QColor(theme.TEXT_FAINT))
        p.drawText(r, Qt.AlignCenter, self.text())

    def _font(self):
        f = QFont(theme.FONT_FALLBACK)
        f.setWeight(QFont.Bold)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 4.0)
        f.setPointSize(12)
        return f


class PillButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self._hover = 0.0
        self._anim = QPropertyAnimation(self, b"hoverT")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self._start(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._start(0.0)
        super().leaveEvent(event)

    def _start(self, end):
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(end)
        self._anim.start()

    def getHoverT(self):
        return self._hover

    def setHoverT(self, v):
        self._hover = v
        self.update()

    hoverT = Property(float, getHoverT, setHoverT)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRect(r)
        base = QColor(theme.INPUT)
        border = _lerp_color(QColor(theme.BORDER), QColor(theme.ACCENT), self._hover)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, base.lighter(104))
        grad.setColorAt(1.0, _lerp_color(base, QColor(theme.CARD_HOVER), self._hover))
        p.setPen(QPen(border, 1.2))
        p.setBrush(grad)
        p.drawPath(path)
        p.setFont(self._font())
        p.setPen(_lerp_color(QColor(theme.TEXT), QColor(theme.ACCENT), self._hover))
        p.drawText(r, Qt.AlignCenter, self.text())

    def _font(self):
        f = QFont(theme.FONT_FALLBACK)
        f.setWeight(QFont.DemiBold)
        f.setPointSize(10)
        return f


class Segmented(QPushButton):
    changed = Signal(str)

    def __init__(self, options, parent=None, height=42):
        super().__init__(parent)
        self._options = options
        self._index = 0
        self._slide = 0.0
        self.setCheckable(True)
        self.setChecked(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(height)
        self._anim = QPropertyAnimation(self, b"slideT")
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.OutBack)

    def value(self):
        return self._options[self._index]

    def setIndex(self, i, animate=True):
        old = self._index
        self._index = i
        if animate:
            self._anim.stop()
            self._anim.setStartValue(float(old))
            self._anim.setEndValue(float(i))
            self._anim.start()
        else:
            self._slide = float(i)
        self.update()

    def getSlideT(self):
        return self._slide

    def setSlideT(self, v):
        self._slide = v
        self.update()

    slideT = Property(float, getSlideT, setSlideT)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        w = self.width() / max(1, len(self._options))
        idx = min(len(self._options) - 1, max(0, int(event.position().x() // w)))
        if idx != self._index:
            self.setIndex(idx)
            self.changed.emit(self.value())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(0, 0, self.width(), self.height())
        p.setPen(QPen(QColor(theme.BORDER), 1))
        p.setBrush(QColor(theme.INPUT))
        p.drawRect(r)
        seg_w = self.width() / len(self._options)
        sel_x = self._slide * seg_w
        sel = QRectF(sel_x + 3, 3, seg_w - 6, self.height() - 6)
        glow = QRadialGradient(sel.center(), seg_w * 0.9)
        gc = QColor(theme.ACCENT)
        gc.setAlpha(80)
        glow.setColorAt(0.0, gc)
        gc2 = QColor(theme.ACCENT)
        gc2.setAlpha(0)
        glow.setColorAt(1.0, gc2)
        p.setPen(Qt.NoPen)
        p.setBrush(glow)
        p.drawRect(sel.adjusted(-6, -6, 6, 6))
        grad = QLinearGradient(sel.topLeft(), sel.bottomRight())
        grad.setColorAt(0.0, QColor(theme.ACCENT))
        grad.setColorAt(1.0, QColor(theme.ACCENT_2))
        p.setBrush(grad)
        p.drawRect(sel)
        f = QFont(theme.FONT_FALLBACK)
        f.setPointSize(11)
        f.setBold(True)
        p.setFont(f)
        for i, opt in enumerate(self._options):
            rect = QRectF(i * seg_w, 0, seg_w, self.height())
            p.setPen(QColor("#ffffff") if i == self._index else QColor(theme.TEXT_MUTED))
            p.drawText(rect, Qt.AlignCenter, opt)


def lerp_color(a, b, t):
    return _lerp_color(a, b, t)
