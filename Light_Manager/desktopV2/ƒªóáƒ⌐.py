import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, 
                               QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QStatusBar, QToolBar, 
                               QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, 
                               QComboBox, QCheckBox, QFormLayout, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

# تأكد من وجود ملف db.py (سيتم إنشاؤه لاحقًا)


# إعدادات الواجهة (RTL)
def set_rtl_style():
    return """
        * {
            direction: rtl;
            text-align: right;
            padding: 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            font-size: 16px;
            margin: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QLineEdit {
            font-size: 16px;
            padding: 5px;
        }
        QLabel {
            font-size: 16px;
        }
        QTableWidget {
            font-size: 14px;
            background-color: white;
        }
        QTableWidget QHeaderView::section {
            background-color: #f0f0f0;
            padding: 5px;
            font-weight: bold;
        }
    """

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام المبيعات")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet(set_rtl_style())
        self.init_ui()

    def init_ui(self):
        # 📦 الواجهة الرئيسية (Top Toolbar)
        self.toolbar = QToolBar("القائمة")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # 🔧 القوائم (Menus)
        self.file_menu = self.menu_bar.addMenu("ملف")
        self.info_menu = self.menu_bar.addMenu("معلومات")
        self.security_menu = self.menu_bar.addMenu("حماية")
        self.shortcuts_menu = self.menu_bar.addMenu("اختصارات")
        self.help_menu = self.menu_bar.addMenu("مساعدة")
        self.customize_menu = self.menu_bar.addMenu("تخصيص")

        # 🧱 الواجهة الجانبية (Side Navigation Bar)
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("background-color: #1E3A8A; width: 150px;")
        self.sidebar_layout = QVBoxLayout()

        # 🔗 الأقسام في الواجهة الجانبية (Icons Only)
        sections = ["الشاشة الرئيسية", "نقطة بيع", "العملاء", "المخزن", 
                    "الموظفين", "المصروفات", "الدوين والأقساط", "الموردين", 
                    "البنوك", "الفواتير", "العقود", "تقارير مالية", "الإعدادات"]

        for section in sections:
            btn = QPushButton(section)
            btn.setFixedWidth(150)
            btn.setStyleSheet("background-color: transparent; color: white; border: none; font-size: 14px;")
            self.sidebar_layout.addWidget(btn)

        self.sidebar.setLayout(self.sidebar_layout)

        # 📋 الواجهة الرئيسية (Content Area)
        self.content = QWidget()
        self.content_layout = QVBoxLayout()

        # 📊 شريط الأدوات (Top-right Horizontal Bar)
        self.top_toolbar = QWidget()
        self.top_toolbar_layout = QHBoxLayout()

        # 🔍 البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث...")
        self.top_toolbar_layout.addWidget(self.search_input)

        # 📊 الإحصائيات
        self.stat_card = QLabel("إحصائيات")
        self.top_toolbar_layout.addWidget(self.stat_card)

        self.top_toolbar.setLayout(self.top_toolbar_layout)
        self.top_toolbar.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        self.content_layout.addWidget(self.top_toolbar)

        # 📦 الأزرار (Action Buttons)
        self.action_buttons = QWidget()
        self.action_buttons_layout = QHBoxLayout()

        # 🎨 تصميم الأزرار (مربعات ملونة مع أيقونات)
        buttons = [
            ("إضافة", "green"),
            ("حذف", "red"),
            ("تعديل", "blue"),
            ("طباعة", "gray"),
            ("تقارير", "yellow")
        ]

        for text, color in buttons:
            btn = QPushButton(text)
            btn.setFixedWidth(80)
            btn.setFixedHeight(80)
            btn.setStyleSheet(f"background-color: {color}; color: white; border: none;")
            self.action_buttons_layout.addWidget(btn)

        self.action_buttons.setLayout(self.action_buttons_layout)
        self.content_layout.addWidget(self.action_buttons)

        # 📋 جدول البيانات
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["الاسم", "الكمية", "السعر", "المخزون"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.content_layout.addWidget(self.table)

        self.content.setLayout(self.content_layout)

        # 📦 التجميع
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # 📋 تأسيس الواجهة
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def show_message(self, message):
        self.status_bar.showMessage(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
