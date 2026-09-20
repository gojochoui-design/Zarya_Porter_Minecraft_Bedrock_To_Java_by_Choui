import os
import sys

from PySide6.QtCore import QThread, Qt, QPropertyAnimation, QEasingCurve, QPoint, QUrl, QTimer, Signal
from PySide6.QtGui import (
    QColor, QDesktopServices, QDragEnterEvent, QDropEvent, QPainter, QFont, QKeySequence,
    QShortcut, QIcon,
)
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea, QVBoxLayout,
    QWidget,
)

from zarya import skybox
from zarya import version_detect
from zarya.engine import Porter
from . import config
from . import i18n
from . import theme
from .settings_dialog import SettingsDialog
from .skybox_panel import SkyboxPanel
from .widgets import GlowButton, PillButton, Segmented, ToggleSwitch

APP_VERSION = "9.2"

_ACTIVE_WINDOW = None

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(PROJECT_ROOT, "icon.png")

OPTION_GROUPS = [
    ("sec_textures", [
        ("blocks", "opt_blocks_t", "opt_blocks_d", True),
        ("entities", "opt_entities_t", "opt_entities_d", True),
        ("flipbook", "opt_flipbook_t", "opt_flipbook_d", True),
        ("lowercase", "opt_lowercase_t", "opt_lowercase_d", True),
        ("pack_icon", "opt_pack_icon_t", "opt_pack_icon_d", True),
    ]),
    ("sec_world", [
        ("environment", "opt_environment_t", "opt_environment_d", True),
        ("panorama", "opt_panorama_t", "opt_panorama_d", True),
        ("sounds", "opt_sounds_t", "opt_sounds_d", True),
        ("fonts", "opt_fonts_t", "opt_fonts_d", True),
    ]),
    ("sec_hud", [
        ("hud", "opt_hud_t", "opt_hud_d", True),
        ("chouiui", "opt_chouiui_t", "opt_chouiui_d", False),
    ]),
]


class Worker(QThread):
    logLine = Signal(str, int)
    stage = Signal(str)
    done = Signal(bool, str)

    def __init__(self, source, out_path, options):
        super().__init__()
        self.source = source
        self.out_path = out_path
        self.options = options

    def run(self):
        porter = Porter()
        porter.run(
            self.source, self.out_path, self.options,
            lambda msg: self.logLine.emit(str(msg), 0),
            lambda text: self.stage.emit(str(text)),
            lambda ok, err: self.done.emit(ok, err or ""),
        )


def _add_shadow(widget):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setColor(QColor(0, 0, 0, theme.SHADOW_ALPHA))
    eff.setBlurRadius(28)
    eff.setOffset(0, 8)
    widget.setGraphicsEffect(eff)


class SourceCard(QFrame):
    filePicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setAcceptDrops(True)
        self.source_path = None
        self.info = None
        self.probe_root = None
        self._probe_dir = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 14, 22, 14)
        lay.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(14)
        self.icon_label = QLabel("PACK")
        f = QFont(theme.FONT_FALLBACK)
        f.setBold(True)
        f.setPointSize(10)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        self.icon_label.setFont(f)
        self.icon_label.setStyleSheet("color: %s;" % theme.ACCENT)
        top.addWidget(self.icon_label)
        self.name_label = QLabel(i18n.tr("drop_hint"))
        self.name_label.setStyleSheet("color: %s; font-size: 14px; font-weight: 700;" % theme.TEXT)
        top.addWidget(self.name_label, 1)
        self.chip = QLabel(i18n.tr("chip_no_pack"))
        self.chip.setObjectName("chip")
        top.addWidget(self.chip)
        lay.addLayout(top)
        self.hint_label = QLabel(i18n.tr("supported_hint"))
        self.hint_label.setObjectName("muted")
        lay.addWidget(self.hint_label)
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch(1)
        self.file_btn = PillButton(i18n.tr("choose_file"))
        self.file_btn.clicked.connect(self._browse_file)
        row.addWidget(self.file_btn)
        self.folder_btn = PillButton(i18n.tr("choose_folder"))
        self.folder_btn.clicked.connect(self._browse_folder)
        row.addWidget(self.folder_btn)
        lay.addLayout(row)

    def retranslate(self):
        if not self.source_path:
            self.name_label.setText(i18n.tr("drop_hint"))
        self.chip.setText(i18n.tr("chip_no_pack") if not self.source_path else self.chip.text())
        self.hint_label.setText(i18n.tr("supported_hint") if not self.source_path
                                else i18n.tr("hint_change"))
        self.file_btn.setText(i18n.tr("choose_file"))
        self.folder_btn.setText(i18n.tr("choose_folder"))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.underMouse() and not self.source_path:
            p = QPainter(self)
            p.setRenderHint(QPainter.Antialiasing)
            p.setPen(QColor(theme.ACCENT))
            p.setBrush(Qt.NoBrush)
            p.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def set_pack(self, path):
        self.source_path = path
        self.info = None
        self.probe_root = None
        try:
            from zarya.utils import safe_extract, find_pack_root
            import tempfile
            name = os.path.basename(path.rstrip("/\\"))
            if os.path.isdir(path):
                root = find_pack_root(path)
            else:
                tmp = tempfile.mkdtemp(prefix="zarya_probe_")
                safe_extract(path, tmp)
                root = find_pack_root(tmp)
                self._release_probe()
                self._probe_dir = tmp
            self.probe_root = root
            self.info = version_detect.detect(root, name_hint=name)
        except Exception:
            self.info = None
        self.name_label.setText(name)
        version = self.info["version"] if self.info else i18n.tr("no_version_read")
        classic = bool(self.info and self.info["classic"])
        self.chip.setText(version)
        color = theme.SUCCESS if classic else (theme.WARN if self.info else theme.TEXT_FAINT)
        self.chip.setStyleSheet(
            "QLabel#chip { background-color: %s; border: 1px solid %s; border-radius: 0px;"
            " padding: 5px 13px; font-size: 12px; font-weight: 700; color: %s; }"
            % (theme.INPUT, color, color)
        )
        self.hint_label.setText(i18n.tr("hint_change"))
        self.filePicked.emit(path)

    def _release_probe(self):
        import shutil
        if self._probe_dir:
            shutil.rmtree(self._probe_dir, ignore_errors=True)
        self._probe_dir = None

    def _cleanup(self, tmp):
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    def _browse_file(self):
        start = os.path.dirname(self.source_path) if self.source_path else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.tr("pick_pack_dialog"), start,
            "Resource packs (*.zip *.mcpack);;All files (*)",
        )
        if path:
            self.set_pack(path)

    def _browse_folder(self):
        start = self.source_path if self.source_path and os.path.isdir(self.source_path) else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, i18n.tr("pick_dir_dialog"), start)
        if path:
            self.set_pack(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path and (os.path.isdir(path) or os.path.splitext(path)[1].lower() in (".zip", ".mcpack")):
            self.set_pack(path)


class OptionRow(QWidget):
    def __init__(self, key, title, desc, default_on):
        super().__init__()
        self.key = key
        self.title_key = title
        self.desc_key = desc
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 9, 0, 9)
        lay.setSpacing(18)
        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        self.title_label = QLabel(i18n.tr(title))
        self.title_label.setStyleSheet(
            "font-size: 13px; color: %s; font-weight: 700; background: transparent;" % theme.TEXT)
        self.desc_label = QLabel(i18n.tr(desc))
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(
            "font-size: 11px; color: %s; background: transparent;" % theme.TEXT_MUTED)
        text_col.addWidget(self.title_label)
        text_col.addWidget(self.desc_label)
        lay.addLayout(text_col, 1)
        self.switch = ToggleSwitch()
        self.switch.setChecked(default_on)
        self.switch._t = 1.0 if default_on else 0.0
        self.switch._glow = 0.88 if default_on else 0.62
        lay.addWidget(self.switch, 0, Qt.AlignVCenter)

    def retranslate(self):
        self.title_label.setText(i18n.tr(self.title_key))
        self.desc_label.setText(i18n.tr(self.desc_key))


class SectionHeader(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("secHead")


def _hline():
    line = QFrame()
    line.setObjectName("hline")
    line.setFixedHeight(1)
    return line


class MainWindow(QMainWindow):
    def __init__(self, cfg, carry=None, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle("Zarya Porter by Choui")
        self.setMinimumSize(840, 540)
        self.resize(1240, 860)
        self.setAcceptDrops(False)
        self.worker = None
        self.out_path = ""
        self.finished_path = ""
        self._intro_done = False
        self._fit_done = False
        self._carried = bool(carry and carry.get("options"))
        self._section_headers = []
        self._build_ui()
        if os.path.isfile(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        carry = carry or {}
        if carry.get("source_path"):
            self.source_card.set_pack(carry["source_path"])
        if carry.get("options"):
            for key, value in carry["options"].items():
                if key in self.rows:
                    self.rows[key].switch.setCheckedState(bool(value), animate=False)
        if carry.get("out_path"):
            self.out_path = carry["out_path"]
            self.path_edit.setText(self.out_path)
        self._restore_saved_options()
        sc = QShortcut(QKeySequence(Qt.Key_F11), self)
        sc.activated.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _card(self):
        card = QFrame()
        card.setObjectName("card")
        _add_shadow(card)
        return card

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.body_scroll = QScrollArea()
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setFrameShape(QFrame.NoFrame)
        self.body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.body_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.body_scroll.setStyleSheet(
            "QScrollArea { background: transparent; }"
            "QWidget#central { background: transparent; }")
        content = QWidget()
        content.setObjectName("central")
        root = QVBoxLayout(content)
        root.setContentsMargins(30, 22, 30, 16)
        root.setSpacing(16)

        root.addLayout(self._build_header())
        self.source_card = SourceCard()
        self.source_card.setFixedHeight(124)
        self.source_card.filePicked.connect(self.on_file_picked)
        root.addWidget(self.source_card)
        self.skybox_panel = SkyboxPanel()
        root.addWidget(self.skybox_panel)

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addLayout(self._build_left_column(), 5)
        body.addWidget(self._build_options_card(), 6)
        root.addLayout(body, 1)

        root.addLayout(self._build_footer())
        root.addStretch(0)
        self.body_scroll.setWidget(content)
        outer.addWidget(self.body_scroll)

    def _build_header(self):
        header = QHBoxLayout()
        header.setSpacing(10)
        brand_box = QVBoxLayout()
        brand_box.setSpacing(2)
        brand = QLabel("Z A R Y A   P O R T E R")
        brand.setObjectName("brand")
        self.sub = QLabel(i18n.tr("brand_sub"))
        self.sub.setObjectName("brandSub")
        brand_box.addWidget(brand)
        brand_box.addWidget(self.sub)
        header.addLayout(brand_box)
        header.addStretch(1)
        dots = QLabel("  ".join(
            "<span style='color:%s'>\u25cf</span>" % c for c in theme.DOTS
        ))
        dots.setTextFormat(Qt.RichText)
        dots.setStyleSheet("font-size: 12px; letter-spacing: 4px;")
        header.addWidget(dots)
        settings_btn = QPushButton(i18n.tr("settings"))
        settings_btn.setObjectName("ghost")
        settings_btn.setFixedHeight(40)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)
        full_btn = QPushButton(i18n.tr("full_screen"))
        full_btn.setObjectName("ghost")
        full_btn.setFixedHeight(40)
        full_btn.setToolTip("F11")
        full_btn.setCursor(Qt.PointingHandCursor)
        full_btn.clicked.connect(self.toggle_fullscreen)
        header.addSpacing(6)
        header.addWidget(full_btn)
        ver = QLabel("v%s" % APP_VERSION)
        ver.setStyleSheet("color: %s; font-size: 11px; font-weight: 800;" % theme.TEXT_FAINT)
        header.addSpacing(6)
        header.addWidget(ver)
        return header

    def _build_left_column(self):
        left = QVBoxLayout()
        left.setSpacing(14)

        self.out_card = self._card()
        self.out_card.setFixedHeight(104)
        out_lay = QVBoxLayout(self.out_card)
        out_lay.setContentsMargins(14, 12, 14, 12)
        out_lay.setSpacing(8)
        out_top = QHBoxLayout()
        out_top.setSpacing(12)
        fmt_label = QLabel(i18n.tr("save_as"))
        fmt_label.setObjectName("section")
        out_top.addWidget(fmt_label)
        out_top.addStretch(1)
        self.fmt = Segmented(["MCPACK", "ZIP"], height=34)
        self.fmt.setFixedWidth(200)
        self.fmt.changed.connect(self.on_format_changed)
        out_top.addWidget(self.fmt)
        out_lay.addLayout(out_top)
        self.path_edit = QPushButton(i18n.tr("path_placeholder"))
        self.path_edit.setObjectName("pathEdit")
        self.path_edit.setFixedHeight(34)
        self.path_edit.setCursor(Qt.PointingHandCursor)
        self.path_edit.clicked.connect(self.browse_save)
        out_lay.addWidget(self.path_edit)
        left.addWidget(self.out_card)

        self.convert_btn = GlowButton(i18n.tr("convert"))
        self.convert_btn.clicked.connect(self.on_convert)
        left.addWidget(self.convert_btn)

        self.log_card = self._card()
        log_lay = QVBoxLayout(self.log_card)
        log_lay.setContentsMargins(12, 12, 12, 12)
        log_lay.setSpacing(8)
        prog_row = QHBoxLayout()
        prog_row.setSpacing(12)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(7)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar { background-color: %s; border: none; border-radius: 0px; }"
            "QProgressBar::chunk { border-radius: 0px; background-color: %s; }"
            % (theme.INPUT, theme.ACCENT)
        )
        self.status = QLabel(i18n.tr("status_ready"))
        self.status.setStyleSheet("color: %s; font-size: 12px; font-weight: 600;" % theme.TEXT_MUTED)
        prog_row.addWidget(self.progress, 1)
        prog_row.addWidget(self.status)
        log_lay.addLayout(prog_row)
        self.log_box = self._make_log()
        self.log_box.setMinimumHeight(110)
        log_lay.addWidget(self.log_box, 1)
        left.addWidget(self.log_card, 1)
        return left

    def _build_options_card(self):
        self.opt_card = self._card()
        self.opt_card.setMinimumHeight(220)
        outer = QVBoxLayout(self.opt_card)
        outer.setContentsMargins(4, 10, 4, 10)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        inner = QWidget()
        inner.setObjectName("optInner")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(20, 8, 20, 12)
        lay.setSpacing(0)

        first_section = True
        self.rows = {}
        self._section_headers = []
        for section_key, rows in OPTION_GROUPS:
            if not first_section:
                lay.addSpacing(22)
            first_section = False
            head = SectionHeader(i18n.tr(section_key))
            self._section_headers.append((section_key, head))
            lay.addWidget(head)
            lay.addSpacing(8)
            for i, (key, title_key, desc_key, default) in enumerate(rows):
                if i:
                    lay.addWidget(_hline())
                row = OptionRow(key, title_key, desc_key, default)
                self.rows[key] = row
                lay.addWidget(row)
        lay.addStretch(1)

        scroll.setWidget(inner)
        outer.addWidget(scroll)
        self.rows["chouiui"].switch.switched.connect(self._on_chouiui_toggled)
        return self.opt_card

    def _build_footer(self):
        footer = QHBoxLayout()
        foot_btn = QPushButton(i18n.tr("footer_by"))
        foot_btn.setObjectName("footer")
        foot_btn.setCursor(Qt.PointingHandCursor)
        footer.addWidget(foot_btn)
        footer.addStretch(1)
        self.reset_btn = QPushButton(i18n.tr("reset_options"))
        self.reset_btn.setObjectName("footer")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_options)
        footer.addWidget(self.reset_btn)
        return footer

    def _make_log(self):
        from PySide6.QtWidgets import QTextEdit
        box = QTextEdit()
        box.setObjectName("log")
        box.setReadOnly(True)
        box.document().setMaximumBlockCount(500)
        return box

    def showEvent(self, event):
        super().showEvent(event)
        if not self._fit_done:
            self._fit_done = True
            screen = self.screen() or QApplication.primaryScreen()
            if screen:
                avail = screen.availableGeometry()
                self.resize(min(self.width(), avail.width() - 40),
                            min(self.height(), avail.height() - 40))
        if not self._intro_done:
            self._intro_done = True
            QTimer.singleShot(40, self._animate_intro)

    def _animate_intro(self):
        cards = [self.source_card, self.out_card, self.convert_btn,
                 self.log_card, self.opt_card]
        for i, card in enumerate(cards):
            target = card.pos()
            slide = QPropertyAnimation(card, b"pos", card)
            slide.setStartValue(target + QPoint(0, 18))
            slide.setEndValue(target)
            slide.setDuration(480)
            slide.setEasingCurve(QEasingCurve.OutCubic)
            QTimer.singleShot(70 * i, slide.start)

    def log(self, text, level=0):
        color = theme.TEXT_MUTED
        if level == 1:
            color = theme.SUCCESS_DARK
        elif level == 2:
            color = theme.WARN
        elif level == 3:
            color = theme.ERROR
        elif level == 4:
            color = theme.TEXT
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.log_box.append("<span style='color:%s'>%s</span>" % (color, safe))

    def open_settings(self):
        dlg = SettingsDialog(self.cfg, self)
        dlg.themeChanged.connect(self._on_theme_changed)
        dlg.languageChanged.connect(self._on_language_changed)
        dlg.saveDirChanged.connect(self._on_save_dir_changed)
        dlg.exec()

    def _on_theme_changed(self, name):
        theme.apply(QApplication.instance(), name)

    def _on_language_changed(self, code):
        if self.worker:
            QMessageBox.information(self, "Zarya Porter", i18n.tr("msg_wait_convert"))
            return
        i18n.set_language(code)
        carry = {
            "source_path": self.source_card.source_path,
            "out_path": self.out_path,
            "options": {key: row.switch.isChecked() for key, row in self.rows.items()},
            "reopen_settings": True,
        }
        global _ACTIVE_WINDOW
        new_win = MainWindow(self.cfg, carry=carry)
        _ACTIVE_WINDOW = new_win
        new_win.show()
        self.close()
        if carry.get("reopen_settings"):
            QTimer.singleShot(140, new_win.open_settings)

    def _on_save_dir_changed(self, _path):
        if self.source_card.source_path:
            self.out_path = self.default_out_path(self.source_card.source_path)
            self.path_edit.setText(self.out_path)

    def _on_chouiui_toggled(self, on):
        self._persist_options()

    def _persist_options(self):
        self.cfg["options"] = {key: row.switch.isChecked() for key, row in self.rows.items()}
        config.save(self.cfg)

    def _restore_saved_options(self):
        saved = self.cfg.get("options") or {}
        if not saved:
            return
        for key, row in self.rows.items():
            if key in saved and not self._carried:
                row.switch.setCheckedState(bool(saved[key]), animate=False)

    def on_file_picked(self, path):
        self.out_path = self.default_out_path(path)
        self.path_edit.setText(self.out_path)
        self.log(i18n.tr("log_selected", os.path.basename(path.rstrip("/\\"))), 4)
        info = self.source_card.info
        if info:
            self.log(i18n.tr("log_detected", info["version"]), 1)
            for note in info.get("notes", []):
                self.log(i18n.tr("log_detection", note), 0)
        sky_info = None
        root = self.source_card.probe_root
        if root and os.path.isdir(root):
            try:
                sky_info = skybox.detect(root)
            except Exception:
                sky_info = None
        self.skybox_panel.set_info(sky_info)
        summary = skybox.summarize(sky_info)
        if summary:
            self.log("Skyboxes: " + summary, 4)

    def default_out_path(self, source):
        base = os.path.splitext(os.path.basename(source.rstrip("/\\")))[0] or "PortedPack"
        name = "".join(c for c in base if c.isalnum() or c in "-_ .").strip() or "PortedPack"
        ext = ".mcpack" if self.fmt.value() == "MCPACK" else ".zip"
        save_dir = (self.cfg.get("save_dir") or "").strip()
        directory = save_dir if save_dir and os.path.isdir(save_dir) else \
            (os.path.dirname(source) or os.path.expanduser("~"))
        return os.path.join(directory, name + "-Bedrock" + ext)

    def on_format_changed(self, value):
        self.out_path = self._with_ext(self.out_path or (self.source_card.source_path and
                                                          self.default_out_path(self.source_card.source_path)) or "", value)
        self.path_edit.setText(self.out_path)

    def _with_ext(self, path, value):
        if not path:
            return path
        root, _ = os.path.splitext(path)
        return root + (".mcpack" if value == "MCPACK" else ".zip")

    def browse_save(self):
        start = self.out_path
        if not start and self.source_card.source_path:
            start = self.default_out_path(self.source_card.source_path)
        if not start:
            start = os.path.join(self.cfg.get("save_dir") or os.path.expanduser("~"),
                                 "Converted-Bedrock.mcpack")
        directory = os.path.dirname(start) if start else os.path.expanduser("~")
        fname = os.path.basename(start) if start else "Converted-Bedrock.mcpack"
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("save_dialog_title"), os.path.join(directory, fname),
            "Minecraft Pack (*.mcpack);;ZIP Archive (*.zip)",
        )
        if path:
            self.out_path = path
            self.path_edit.setText(path)
            ext = os.path.splitext(path)[1].lower()
            self.fmt.setIndex(0 if ext != ".zip" else 1)

    def on_convert(self):
        if self.finished_path and not self.worker:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self.finished_path)))
            return
        if self.worker:
            return
        source = self.source_card.source_path
        if not source:
            QMessageBox.information(self, "Zarya Porter", i18n.tr("msg_pick_pack"))
            return
        if not self.out_path:
            self.browse_save()
            if not self.out_path:
                return
        options = {key: row.switch.isChecked() for key, row in self.rows.items()}
        options["mcpack"] = self.out_path.lower().endswith(".mcpack")
        options["sky_key"] = self.skybox_panel.selected_key()
        if options["sky_key"]:
            self.log(i18n.tr("log_sky_selected", self.skybox_panel._titles.get(options["sky_key"], "")), 4)
        else:
            self.log(i18n.tr("log_sky_auto"), 0)
        self._persist_options()
        self.log(i18n.tr("log_starting"), 4)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText(i18n.tr("converting"))
        self.convert_btn.setPulsing(True)
        self.progress.setValue(0)
        self.status.setText(i18n.tr("stage_Preparing..."))
        self.worker = Worker(source, self.out_path, options)
        self.worker.logLine.connect(self._on_worker_log)
        self.worker.stage.connect(self._on_stage)
        self.worker.done.connect(self._on_done)
        self.worker.start()

    def _on_worker_log(self, text, _level):
        low = text.lower()
        level = 0
        if low.startswith("error"):
            level = 3
        elif low.startswith("port complete"):
            level = 1
        elif "no " in low[:6]:
            level = 2
        self.log(text, level)

    def _on_stage(self, text):
        for key, engine_text in i18n.STAGE_ENGINE.items():
            if text == engine_text:
                self.status.setText(i18n.tr(key))
                keys = i18n.STAGE_KEYS
                idx = keys.index(key)
                self.progress.setValue(int((idx + 1) / len(keys) * 100))
                return
        self.status.setText(text)
        self.progress.setValue(min(99, self.progress.value() + 1))

    def _on_done(self, ok, err):
        self.convert_btn.setEnabled(True)
        self.convert_btn.setPulsing(False)
        self.worker = None
        if ok:
            self.progress.setValue(100)
            self.status.setText(i18n.tr("status_done"))
            self.finished_path = self.out_path
            self.convert_btn.setText(i18n.tr("open_folder"))
            self.log(i18n.tr("log_all_set"), 1)
        else:
            self.progress.setValue(0)
            self.status.setText(i18n.tr("status_failed"))
            self.convert_btn.setText(i18n.tr("convert"))
            self.log(i18n.tr("log_failed", err), 3)

    def reset_options(self):
        defaults = {}
        for _section, rows in OPTION_GROUPS:
            for key, _title, _desc, default in rows:
                defaults[key] = default
        for key, row in self.rows.items():
            row.switch.setCheckedState(defaults[key])
        self._persist_options()
        self.log(i18n.tr("log_reset"), 2)


def launch():
    app = QApplication.instance() or QApplication(sys.argv)
    cfg = config.load()
    i18n.set_language(cfg.get("language") or i18n.DEFAULT_LANG)
    theme.apply(app, cfg.get("theme") or theme.DEFAULT_THEME)
    if os.path.isfile(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    global _ACTIVE_WINDOW
    win = MainWindow(cfg)
    _ACTIVE_WINDOW = win
    win._carried = False
    win.show()
    return app.exec()
