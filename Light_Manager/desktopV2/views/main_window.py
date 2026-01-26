#-*- coding: utf-8 -*-
"""
يحتوي هذا الملف على كود واجهة المستخدم الرسومية للنافذة الرئيسية.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QSizePolicy
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize

class SideButton(QPushButton):
    """
    زر مخصص للقائمة الجانبية مع أيقونة ونص.
    """
    def __init__(self, text, icon_path):
        super().__init__()
        self.setText(text)
        # self.setIcon(QIcon(icon_path)) # سيتم إضافة الأيقونات لاحقاً
        self.setIconSize(QSize(40, 40))
        self.setFixedSize(90, 90)
        self.setObjectName("SideButton")

class MainWindow(QMainWindow):
    """
    النافذة الرئيسية للتطبيق.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("منظومة المهندس 3")
        self.setGeometry(100, 100, 1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """
        تهيئة واجهة المستخدم.
        """
        # Top Bar
        top_bar = self.addToolBar("الشريط العلوي")
        top_bar.setMovable(False)

        # Menus
        top_bar.addAction("ملف")
        top_bar.addAction("حماية")
        top_bar.addAction("تخصيص")
        top_bar.addAction("اختصارات")
        top_bar.addAction("معلومات")
        top_bar.addAction("مساعدة")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        top_bar.addWidget(spacer)

        # Search Bar
        top_bar.addAction("شريط البحث")

        # User Name
        top_bar.addAction("اسم المستخدم")

        # Time and Date
        top_bar.addAction("الوقت والتاريخ")

        # Main Layout
        main_layout = QHBoxLayout()

        # Side Nav Bar
        side_nav_bar_container = QWidget()
        side_nav_bar_container.setFixedWidth(100)
        side_nav_layout = QVBoxLayout(side_nav_bar_container)
        side_nav_layout.setContentsMargins(0, 0, 0, 0)
        side_nav_layout.setSpacing(5)


        buttons = [
            ("الشاشة الرئيسية", "house.png"),
            ("المشاريع", "projects.png"),
            ("المقاولات", "contracts.png"),
            ("العملاء", "clients.png"),
            ("الموظفين", "employees.png"),
            ("التدريب", "training.png"),
            ("الايرادات", "revenue.png"),
            ("المصروفات", "expenses.png"),
            ("الالتزامات", "commitments.png"),
            ("تقارير مالية", "financial_reports.png"),
            ("إعدادات", "settings.png")
        ]

        for name, icon_path in buttons:
            button = SideButton(name, f"assets/icons/{icon_path}")
            side_nav_layout.addWidget(button)

        side_nav_layout.addStretch()


        main_layout.addWidget(side_nav_bar_container)

        # Content Area
        content_area = QVBoxLayout()

        # Filters Container
        filters_container = QWidget()
        filters_container.setFixedHeight(60)
        filters_container.setObjectName("FiltersContainer")
        content_area.addWidget(filters_container)

        # Actions Container
        actions_container = QWidget()
        actions_container.setFixedHeight(100)
        actions_container.setObjectName("ActionsContainer")
        content_area.addWidget(actions_container)

        # Data Container
        data_container = QWidget()
        data_container.setObjectName("DataContainer")
        content_area.addWidget(data_container)

        main_layout.addLayout(content_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def apply_styles(self):
        """
        تطبيق الأنماط من ملف الأنماط.
        """
        try:
            with open("assets/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("ملف الأنماط assets/styles.qss غير موجود.")
