# -*- coding: utf-8 -*-
"""
الإطار الرئيسي للتطبيق (PySide6): RTL، شريط علوي، قائمة جانبية قابلة للطي، Workspace بثلاث حاويات.
يرتبط بـ SystemManager لتحميل الوحدات وعرضها.
"""
from __future__ import annotations
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

from ..core.system_manager import SystemManager
from ..core.database import DatabaseManager
from ..config.settings import get_database_config
from .theming import Theme, CATEGORY_COLORS
from .settings_manager import SettingsManager
from .sidebar import Sidebar
from .workspace import Workspace
from .topbar import TopBar

SIDEBAR_ITEMS = [
    ("home", "الشاشة الرئيسية"),
    ("projects", "المشاريع"),
    ("contracts", "المقاولات"),
    ("clients", "العملاء"),
    ("employees", "الموظفون"),
    ("training", "التدريب"),
    ("revenues", "الإيرادات"),
    ("expenses", "المصروفات"),
    ("liabilities", "الالتزامات"),
    ("reports", "تقارير مالية"),
    ("settings", "إعدادات"),
]

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, system_manager: SystemManager, settings: SettingsManager, theme: Theme, parent=None):
        super().__init__(parent)
        self.system_manager = system_manager
        self.settings = settings
        self.theme = theme

        self.setWindowTitle("منظومة المهندس v3")
        self.resize(1400, 900)
        self.setLayoutDirection(QtCore.Qt.RightToLeft if theme.rtl else QtCore.Qt.LeftToRight)

        # شريط علوي
        self.topbar = TopBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.topbar)

        # جسم النافذة: شريط جانبي + مساحة عمل يسار
        central = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(central)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self.sidebar = Sidebar(SIDEBAR_ITEMS, collapsed=self.settings.load()['ui'].get('sidebar_collapsed', False))
        self.sidebar.moduleSelected.connect(self._on_module_selected)

        self.workspace = Workspace()

        h.addWidget(self.sidebar)
        h.addWidget(self.workspace, 1)

        self.setCentralWidget(central)

        # تطبيق الثيم
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(self.theme.qss() + self._category_bars_qss())

    def _category_bars_qss(self) -> str:
        parts = []
        for key, color in CATEGORY_COLORS.items():
            parts.append(f"QFrame#catbar_{key} {{ background: {color}; border-radius: 1px; }}")
        return "\n".join(parts)

    def _on_module_selected(self, key: str):
        # لاحقاً: ربط كل مفتاح بوحدة النظام وإرجاع QWidget خاص بها
        # حالياً: مجرد عنصر نائب
        page = QtWidgets.QLabel(f"واجهة الوحدة: {key}")
        page.setAlignment(QtCore.Qt.AlignCenter)
        idx = self.workspace.content.addWidget(page)
        self.workspace.content.setCurrentIndex(idx)

class Application:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.settings = SettingsManager(self.base_dir)
        ui_cfg = self.settings.load()['ui']
        self.theme = Theme(rtl=ui_cfg.get('rtl', True),
                           dark_mode=ui_cfg.get('dark_mode', True),
                           font_family=ui_cfg.get('font_family', 'Tajawal'),
                           font_size=ui_cfg.get('font_size', 11))

        db_config = get_database_config(test_mode=False)
        self.db_manager = DatabaseManager(**db_config)
        self.db_manager.connect()
        self.db_manager.create_database()
        self.system_manager = SystemManager(self.db_manager)
        self.system_manager.initialize_system()

    def run(self):
        app = QtWidgets.QApplication([])
        # RTL عام
        app.setLayoutDirection(QtCore.Qt.RightToLeft if self.theme.rtl else QtCore.Qt.LeftToRight)
        win = MainWindow(self.system_manager, self.settings, self.theme)
        win.show()
        return app.exec()