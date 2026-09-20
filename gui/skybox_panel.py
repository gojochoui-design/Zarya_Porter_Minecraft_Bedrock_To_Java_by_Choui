import math
import os

from PIL import Image
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QToolButton, QVBoxLayout, QWidget

from . import i18n
from . import theme

PREVIEW_W = 122
PREVIEW_H = 66
CARD_W = 140
CARD_H = 134
MAX_CARDS = 14

PHASE_KEYS = {
    "dawn": "sky_phase_dawn",
    "day": "sky_phase_day",
    "dusk": "sky_phase_dusk",
    "night": "sky_phase_night",
    "all": "sky_phase_all",
}


def _rectilinear(img, w, h, fov_x=118.0, fov_y=64.0):
    half = 2
    rw, rh = w // half, h // half
    if img.width > 2048:
        img = img.resize((2048, 1024), Image.BILINEAR)
    px = img.load()
    sw, sh = img.size
    out = Image.new("RGBA", (rw, rh), (8, 9, 11, 255))
    dst = out.load()
    tx = math.tan(math.radians(fov_x) / 2.0)
    ty = math.tan(math.radians(fov_y) / 2.0)
    for y in range(rh):
        ny = (1.0 - 2.0 * y / (rh - 1)) * ty
        for x in range(rw):
            nx = (2.0 * x / (rw - 1) - 1.0) * tx
            inv = 1.0 / math.sqrt(nx * nx + ny * ny + 1.0)
            dx, dyv, dz = nx * inv, ny * inv, inv
            yaw = math.atan2(dx, dz)
            pitch = math.asin(max(-1.0, min(1.0, dyv)))
            u = (yaw / (2.0 * math.pi) + 0.5) % 1.0
            v = 0.5 - pitch / math.pi
            sx = sw - 1 if u >= 1.0 else int(u * sw)
            sy = sh - 1 if v >= 1.0 else int(v * sh)
            dst[x, y] = px[sx, sy]
    return out.resize((w, h), Image.NEAREST)


def _letterbox(img, w, h):
    scale = min(w / img.width, h / img.height)
    tw = max(1, int(img.width * scale))
    th = max(1, int(img.height * scale))
    mode = Image.NEAREST if scale >= 3 else Image.BILINEAR
    resized = img.resize((tw, th), mode)
    out = Image.new("RGBA", (w, h), (8, 9, 11, 255))
    out.alpha_composite(resized, ((w - tw) // 2, (h - th) // 2))
    return out


def render_preview(path, w=PREVIEW_W, h=PREVIEW_H):
    try:
        img = Image.open(path).convert("RGBA")
    except Exception:
        return None
    if img.width == 0 or img.height == 0:
        return None
    if img.width == img.height * 2 and img.width >= 96:
        out = _rectilinear(img, w, h)
    else:
        out = _letterbox(img, w, h)
    buf = out.tobytes("raw", "RGBA")
    image = QImage(buf, out.width, out.height, out.width * 4, QImage.Format_RGBA8888)
    if image.isNull():
        return None
    return QPixmap.fromImage(image.copy())


def _missing_pixmap():
    pix = QPixmap(PREVIEW_W, PREVIEW_H)
    pix.fill(QColor(theme.BG))
    painter = QPainter(pix)
    painter.setPen(QColor(theme.WARN))
    painter.drawRect(0, 0, PREVIEW_W - 1, PREVIEW_H - 1)
    painter.setPen(QColor(theme.TEXT_FAINT))
    f = QFont(theme.FONT_FALLBACK)
    f.setPointSize(8)
    painter.setFont(f)
    painter.drawText(pix.rect(), Qt.AlignCenter, i18n.tr("sky_missing_img"))
    painter.end()
    return pix


def _chip_style(color):
    return ("QLabel { background-color: %s; border: 1px solid %s; border-radius: 0px;"
            " padding: 3px 9px; font-size: 10px; font-weight: 800; color: %s; }"
            % (theme.INPUT, color, color))


def _chip(text, color):
    chip = QLabel(text)
    chip.setStyleSheet(_chip_style(color))
    return chip


class SkyCard(QFrame):
    picked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.key = None
        self.selectable = False
        self.selected = False
        self.accent = theme.ACCENT
        self.setFixedSize(CARD_W, CARD_H)
        self.setToolTipDuration(8000)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(4)
        self.preview = QLabel()
        self.preview.setFixedSize(PREVIEW_W, PREVIEW_H)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("QLabel { border: none; background-color: %s; }" % theme.BG)
        lay.addWidget(self.preview)
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 11px; font-weight: 800; border: none;")
        lay.addWidget(self.title)
        self.caption = QLabel()
        self.caption.setStyleSheet("font-size: 9px; font-weight: 700; border: none;")
        lay.addWidget(self.caption)
        self.sub = QLabel()
        self.sub.setStyleSheet("font-size: 9px; border: none;")
        lay.addWidget(self.sub, 1)
        self.setStyleSheet("QFrame { background-color: %s; border: 1px solid %s; }" % (theme.INPUT, theme.BORDER))
        self.badge = QLabel("\u2713", self)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setFixedSize(20, 20)
        self.badge.setStyleSheet(
            "QLabel { background-color: %s; color: #0d0e12; font-size: 13px; font-weight: 900;"
            " border: 1px solid #0d0e12; }" % theme.ACCENT)
        self.badge.move(self.preview.x() + self.preview.width() - 20, self.preview.y() + 2)
        self.badge.hide()

    def set_texts(self, title, accent, caption, cap_color, sub, tooltip):
        self.title.setText(title)
        self.title.setStyleSheet("font-size: 11px; font-weight: 800; color: %s; border: none;" % accent)
        self.caption.setText(caption)
        self.caption.setStyleSheet("font-size: 9px; font-weight: 700; color: %s; border: none;" % cap_color)
        self.sub.setText(sub)
        self.sub.setStyleSheet("font-size: 9px; color: %s; border: none;" % theme.TEXT_FAINT)
        self.setToolTip(tooltip)

    def set_identity(self, key, selectable, accent):
        self.key = key
        self.selectable = selectable
        self.accent = accent
        if selectable:
            self.setCursor(Qt.PointingHandCursor)

    def set_selected(self, on):
        self.selected = bool(on)
        self.badge.setVisible(self.selected)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.selected:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(self.accent), 2)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRect(self.rect().adjusted(1, 1, -2, -2))
        p.end()

    def mouseReleaseEvent(self, event):
        if self.selectable and event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.picked.emit(self.key)
        super().mouseReleaseEvent(event)


def _schedule_text(layer):
    start = layer.get("start") or "00:00"
    fade_out = layer.get("fade_out") or start
    if start == fade_out:
        return i18n.tr("sky_always")
    return "%s - %s" % (start, fade_out)


def _layer_tooltip(layer, group):
    lines = [group["folder"], i18n.tr("sky_props", layer.get("file") or layer.get("name", ""))]
    lines.append(i18n.tr("sky_rotate") if layer.get("rotate", True) else i18n.tr("sky_static"))
    lines.append(i18n.tr("sky_fades", "%s - %s" % (layer.get("start"), layer.get("fade_out"))))
    fade_in = layer.get("fade_in")
    fade_out_start = layer.get("fade_out_start")
    if fade_in and fade_out_start and fade_in != fade_out_start:
        lines.append("%s > %s" % (fade_in, fade_out_start))
    extras = []
    for key in ("blend", "speed", "axis", "weather", "days"):
        value = layer.get(key)
        if value:
            extras.append("%s: %s" % (key, value))
    lines.extend(extras)
    for src in layer.get("missing_sources") or []:
        lines.append(i18n.tr("sky_missing_note", src))
    if layer.get("missing"):
        lines.append(i18n.tr("sky_missing_tip"))
    else:
        lines.append(i18n.tr("sky_pick_tip"))
    return "\n".join(lines)


def _fill_sky_card(card, layer, group):
    source = (layer.get("sources") or [None])[0]
    pix = render_preview(source) if source and os.path.isfile(source) else None
    if pix is None:
        card.preview.setPixmap(_missing_pixmap())
    else:
        painter = QPainter(pix)
        painter.setPen(QColor(theme.BORDER_STRONG))
        painter.drawRect(0, 0, pix.width() - 1, pix.height() - 1)
        painter.end()
        card.preview.setPixmap(pix)
    missing = bool(layer.get("missing"))
    accent = theme.WARN if missing else (theme.ACCENT if group["provider"] == "optifine" else theme.ACCENT_2)
    phase_key = PHASE_KEYS.get(layer.get("phase") or "all", "sky_phase_all")
    if missing:
        declared = (layer.get("missing_sources") or [None])[0] or layer.get("name", "")
        title = os.path.basename(declared.replace("\\", "/"))
    else:
        title = os.path.basename(source or layer.get("name", ""))
    caption = "%s \u00b7 %s" % (group["world_label"], i18n.tr(phase_key))
    card.set_texts(title, accent, caption, accent, _schedule_text(layer),
                   _layer_tooltip(layer, group))
    card.set_identity(layer.get("key"), not missing, accent)
    return title


def _fill_env_card(card, env):
    pix = render_preview(env["path"]) if os.path.isfile(env["path"]) else None
    if pix is None:
        card.preview.setPixmap(_missing_pixmap())
    else:
        painter = QPainter(pix)
        painter.setPen(QColor(theme.BORDER_STRONG))
        painter.drawRect(0, 0, pix.width() - 1, pix.height() - 1)
        painter.end()
        card.preview.setPixmap(pix)
    card.set_texts(env["file"], theme.SUCCESS, i18n.tr("sky_env"), theme.SUCCESS,
                   i18n.tr("sky_env_note"), env["path"])
    card.set_identity(None, False, theme.SUCCESS)
    return env["file"]


class SkyboxPanel(QFrame):
    selectionChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._info = None
        self._selected_key = None
        self._titles = {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)
        head = QHBoxLayout()
        head.setSpacing(10)
        self.head_label = QLabel()
        f = QFont(theme.FONT_FALLBACK)
        f.setBold(True)
        f.setPointSize(10)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        self.head_label.setFont(f)
        self.head_label.setStyleSheet("color: %s; background: transparent;" % theme.ACCENT)
        head.addWidget(self.head_label)
        self.summary_chip = QLabel()
        self.summary_chip.setStyleSheet(
            "QLabel { background-color: %s; border: 1px solid %s; border-radius: 0px;"
            " padding: 4px 11px; font-size: 11px; font-weight: 700; color: %s; }"
            % (theme.INPUT, theme.BORDER_STRONG, theme.TEXT_MUTED))
        head.addWidget(self.summary_chip)
        self.hint_label = QLabel()
        self.hint_label.setStyleSheet(
            "QLabel { color: %s; font-size: 10px; font-weight: 700; background: transparent; }"
            % theme.TEXT_FAINT)
        head.addWidget(self.hint_label)
        head.addStretch(1)
        self.status_chip = _chip("", theme.TEXT_FAINT)
        head.addWidget(self.status_chip)
        self.clear_btn = QToolButton()
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid %s; padding: 3px 9px;"
            " font-size: 10px; font-weight: 800; color: %s; }"
            % (theme.BORDER, theme.TEXT_MUTED))
        self.clear_btn.clicked.connect(self._clear_selection)
        self.clear_btn.setVisible(False)
        head.addWidget(self.clear_btn)
        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.DownArrow)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid %s; padding: 4px 10px; }"
            % theme.BORDER)
        self.toggle_btn.clicked.connect(self._toggle_row)
        head.addWidget(self.toggle_btn)
        lay.addLayout(head)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(154)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; }")
        self.row = QWidget()
        row_lay = QHBoxLayout(self.row)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.setSpacing(8)
        self.scroll.setWidget(self.row)
        lay.addWidget(self.scroll)
        self.setVisible(False)

    def _toggle_row(self):
        hidden = self.scroll.isHidden()
        self.scroll.setVisible(hidden)
        self.toggle_btn.setArrowType(Qt.DownArrow if hidden else Qt.RightArrow)

    def _clear_selection(self):
        self._selected_key = None
        self._apply_states()

    def _pick(self, key):
        if not key:
            return
        self._selected_key = None if self._selected_key == key else key
        self._apply_states()

    def selected_key(self):
        return self._selected_key or ""

    def _apply_states(self):
        box = self.row.layout()
        for i in range(box.count()):
            card = box.itemAt(i).widget()
            if isinstance(card, SkyCard):
                card.set_selected(bool(card.key) and card.key == self._selected_key)
        if self._selected_key:
            self.status_chip.setText(i18n.tr("sky_using_chip", self._titles.get(self._selected_key, "")))
            self.status_chip.setStyleSheet(_chip_style(theme.ACCENT))
            self.clear_btn.setText(i18n.tr("sky_clear"))
            self.clear_btn.setVisible(True)
            self.hint_label.setVisible(False)
        else:
            self.status_chip.setText(i18n.tr("sky_auto_chip"))
            self.status_chip.setStyleSheet(_chip_style(theme.TEXT_FAINT))
            self.clear_btn.setVisible(False)
            self.hint_label.setVisible(True)
        self.selectionChanged.emit(self._selected_key or "")

    def set_info(self, info):
        self._info = info
        self._selected_key = None
        self._titles = {}
        while self.row.layout().count():
            item = self.row.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        if self.scroll.isHidden():
            self._toggle_row()
        shown = False
        if info and (info["skies"] or info["environment"]):
            shown = True
            skies = info["skies"]
            envs = info["environment"]
            self.head_label.setText(i18n.tr("sky_title"))
            self.summary_chip.setText(i18n.tr(
                "sky_summary", len(skies), info["total_layers"], len(envs)))
            self.hint_label.setText(i18n.tr("sky_pick_hint"))
            cards = 0
            for group in skies:
                for layer in group["layers"]:
                    if cards >= MAX_CARDS:
                        break
                    card = SkyCard()
                    title = _fill_sky_card(card, layer, group)
                    if layer.get("key"):
                        self._titles[layer["key"]] = title
                        card.picked.connect(self._pick)
                    self.row.layout().addWidget(card)
                    cards += 1
            for env in envs:
                if cards >= MAX_CARDS:
                    break
                card = SkyCard()
                _fill_env_card(card, env)
                self.row.layout().addWidget(card)
                cards += 1
            self._apply_states()
        self.row.layout().addStretch(1)
        self.setVisible(shown)
