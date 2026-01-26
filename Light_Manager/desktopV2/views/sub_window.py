#-*- coding: utf-8 -*-
"""
يحتوي هذا الملف على النافذة الفرعية العامة القابلة للتخصيص.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton
from PySide6.QtCore import Qt

class SubWindow(QWidget):
    """
    نافذة فرعية عامة قابلة للتخصيص على مستوى التطبيق.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("نافذة فرعية")
        self.setLayoutDirection(Qt.RightToLeft)
        self.init_ui()

    def init_ui(self):
        """
        تهيئة واجهة المستخدم للنافذة الفرعية.
        """
        main_layout = QVBoxLayout(self)
        
        # Tab Widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Tab 1: Main Info
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        # Horizontal containers
        info_container = QHBoxLayout()
        basic_info = QWidget()
        basic_info.setStyleSheet("background-color: #8A67AA;")
        financial_info = QWidget()
        financial_info.setStyleSheet("background-color: #9A77BA;")
        additional_info = QWidget()
        additional_info.setStyleSheet("background-color: #AA87CA;")
        info_container.addWidget(basic_info)
        info_container.addWidget(financial_info)
        info_container.addWidget(additional_info)
        tab1_layout.addLayout(info_container)
        
        # Quick actions and stats container
        quick_actions_container = QWidget()
        quick_actions_container.setStyleSheet("background-color: #Baa7DA;")
        quick_actions_container.setFixedHeight(100)
        tab1_layout.addWidget(quick_actions_container)
        
        tab_widget.addTab(tab1, "البيانات الأساسية")

        # Tab 2: Generic Tab
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        
        # Title
        title_label = QLabel("عنوان النافذة")
        title_label.setAlignment(Qt.AlignCenter)
        tab2_layout.addWidget(title_label)
        
        # Stats cards
        stats_container = QHBoxLayout()
        stats_container.addWidget(QLabel("إحصائية 1"))
        stats_container.addWidget(QLabel("إحصائية 2"))
        stats_container.addWidget(QLabel("إحصائية 3"))
        tab2_layout.addLayout(stats_container)
        
        # Filters and search
        filters_container = QWidget()
        filters_container.setStyleSheet("background-color: #8A67AA;")
        filters_container.setFixedHeight(60)
        tab2_layout.addWidget(filters_container)
        
        # Action buttons
        actions_container = QWidget()
        actions_container.setStyleSheet("background-color: #9A77BA;")
        actions_container.setFixedHeight(80)
        tab2_layout.addWidget(actions_container)
        
        # Data table/grid area
        data_area = QWidget()
        data_area.setStyleSheet("background-color: #AA87CA;")
        tab2_layout.addWidget(data_area)
        
        tab_widget.addTab(tab2, "تفاصيل إضافية")

        self.setLayout(main_layout)
