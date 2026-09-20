import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from . import config
from . import i18n
from . import theme
from .widgets import PillButton, Segmented


class Swatch(QPushButton):
    chosen = Signal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.theme_name = name
        pal = theme.THEMES[name]
        self.setFixedSize(34, 34)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(name)
        self.setStyleSheet(
            "QPushButton { background-color: %s; border: 2px solid %s; border-radius: 0px; }"
            "QPushButton:hover { border: 2px solid %s; }"
            % (pal["ACCENT"], pal["BG"], theme.TEXT)
        )
        self.clicked.connect(lambda: self.chosen.emit(self.theme_name))

    def mark_selected(self, selected):
        pal = theme.THEMES[self.theme_name]
        border = theme.TEXT if selected else pal["BG"]
        self.setStyleSheet(
            "QPushButton { background-color: %s; border: 2px solid %s; border-radius: 0px; }"
            "QPushButton:hover { border: 2px solid %s; }"
            % (pal["ACCENT"], border, theme.TEXT)
        )


class SettingsDialog(QDialog):
    languageChanged = Signal(str)
    themeChanged = Signal(str)
    saveDirChanged = Signal(str)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(i18n.tr("settings"))
        self.setMinimumWidth(600)
        self.resize(600, 640)
        self.setStyleSheet("QDialog { background-color: %s; }" % theme.BG)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(14)
        scroll.setWidget(body)
        outer.addWidget(scroll)

        theme_label = QLabel(i18n.tr("set_theme"))
        theme_label.setObjectName("secHead")
        lay.addWidget(theme_label)

        grid_holder = QWidget()
        grid_holder.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_holder)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        self.swatches = []
        for i, name in enumerate(theme.names()):
            sw = Swatch(name)
            sw.chosen.connect(self._on_theme)
            grid.addWidget(sw, i // 10, i % 10)
            self.swatches.append(sw)
        lay.addWidget(grid_holder)
        self._mark_theme()

        line = QFrame()
        line.setObjectName("hline")
        line.setFixedHeight(1)
        lay.addWidget(line)

        lang_label = QLabel(i18n.tr("set_language"))
        lang_label.setObjectName("secHead")
        lay.addWidget(lang_label)
        self.lang_seg = Segmented([i18n.lang_name(code) for code, _ in i18n.LANGS])
        self.lang_seg.setFixedWidth(420)
        codes = [code for code, _ in i18n.LANGS]
        if cfg["language"] in codes:
            self.lang_seg.setIndex(codes.index(cfg["language"]), animate=False)
        self.lang_seg.changed.connect(self._on_language)
        lay.addWidget(self.lang_seg)

        line2 = QFrame()
        line2.setObjectName("hline")
        line2.setFixedHeight(1)
        lay.addWidget(line2)

        folder_label = QLabel(i18n.tr("set_save_folder"))
        folder_label.setObjectName("secHead")
        lay.addWidget(folder_label)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.folder_btn = QPushButton(self.cfg.get("save_dir") or i18n.tr("path_placeholder"))
        self.folder_btn.setObjectName("pathEdit")
        self.folder_btn.setCursor(Qt.PointingHandCursor)
        self.folder_btn.clicked.connect(self._pick_folder)
        row.addWidget(self.folder_btn, 1)
        clear_btn = PillButton(i18n.tr("set_clear"))
        clear_btn.clicked.connect(self._clear_folder)
        row.addWidget(clear_btn)
        lay.addLayout(row)
        hint = QLabel(i18n.tr("set_savefolder_hint"))
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        note = QLabel(i18n.tr("set_hint"))
        note.setObjectName("muted")
        lay.addWidget(note)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(26, 10, 26, 16)
        bottom.addStretch(1)
        close_btn = PillButton(i18n.tr("set_close"))
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(close_btn)
        outer.addLayout(bottom)

    def _mark_theme(self):
        current = self.cfg.get("theme", theme.DEFAULT_THEME)
        for sw in self.swatches:
            sw.mark_selected(sw.theme_name == current)

    def _on_theme(self, name):
        self.cfg["theme"] = name
        config.save(self.cfg)
        self._mark_theme()
        self.setStyleSheet("QDialog { background-color: %s; }" % theme.BG)
        self.themeChanged.emit(name)

    def _on_language(self, _label):
        codes = [code for code, _ in i18n.LANGS]
        idx = self.lang_seg._index
        code = codes[idx] if 0 <= idx < len(codes) else i18n.DEFAULT_LANG
        self.cfg["language"] = code
        config.save(self.cfg)
        self.done(QDialog.Accepted)
        self.languageChanged.emit(code)

    def _pick_folder(self):
        start = self.cfg.get("save_dir") or os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, i18n.tr("set_save_folder"), start)
        if path:
            self._set_folder(path)

    def _clear_folder(self):
        self._set_folder("")

    def _set_folder(self, path):
        self.cfg["save_dir"] = path
        config.save(self.cfg)
        self.folder_btn.setText(path or i18n.tr("path_placeholder"))
        self.saveDirChanged.emit(path)
