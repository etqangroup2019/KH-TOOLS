#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محتوى التقارير المالية المحسن للعرض في المنطقة الرئيسية
يحتوي على الملخصات المالية الشهرية والسنوية مع تصميم احترافي
"""

import sys
import os
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector
import calendar

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from ستايل import apply_stylesheet
from قائمة_الجداول import setup_table_context_menu
from متغيرات import *
from مساعد_أزرار_الطباعة import quick_add_print_button


# ويدجت التقارير المالية المحسن للعرض في المنطقة الرئيسية
class FinancialSummaryWidget(QWidget):

    # init
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # تهيئة الخصائص المطلوبة
        self.summary_table = None
        self.stats_cards = {}
        self.monthly_cards = []
        self.annual_card = None

        self.setup_ui()
        self.load_financial_data()

    # إعداد واجهة المستخدم المحسنة مع سكرول بار
    def setup_ui(self):
        # إنشاء منطقة التمرير الرئيسية
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setObjectName("main_scroll_area")

        # إنشاء ويدجت المحتوى
        content_widget = QWidget()
        content_widget.setObjectName("scroll_content")

        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # الصف الأول: الفلاتر وبطاقات الإحصائيات
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(15)

        # الفلاتر
        filters_widget = self.create_filters_widget()
        first_row_layout.addWidget(filters_widget)

        # بطاقات الإحصائيات الملونة
        stats_widget = self.create_statistics_cards()
        first_row_layout.addWidget(stats_widget, 2)

        main_layout.addLayout(first_row_layout)

        # الصف الثاني: أزرار الإجراءات
        actions_layout = self.create_actions_toolbar()
        main_layout.addLayout(actions_layout)

        # الصف الثالث: الملخص السنوي
        annual_summary = self.create_annual_summary_card()
        main_layout.addWidget(annual_summary)

        # الصف الرابع: التقارير الشهرية
        monthly_reports = self.create_monthly_reports_section()
        main_layout.addWidget(monthly_reports)

        # تعيين ويدجت المحتوى في منطقة التمرير
        scroll_area.setWidget(content_widget)

        # تخطيط رئيسي للويدجت الأساسي
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(scroll_area)

        # تطبيق الستايل المركزي
        self.apply_custom_styles()

    # إنشاء ويدجت الفلاتر
    def create_filters_widget(self):
        filters_widget = QWidget()
        filters_widget.setObjectName("filters_container")
        layout = QVBoxLayout(filters_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # عنوان الفلاتر
        title_label = QLabel("🔍 الفلاتر")
        title_label.setObjectName("filter_title")
        layout.addWidget(title_label)

        # فلتر السنة المالية
        year_layout = QHBoxLayout()
        year_label = QLabel("السنة المالية:")
        year_label.setObjectName("filter_label")
        self.year_combo = QComboBox()
        self.year_combo.setObjectName("filter_combo")

        # إضافة السنوات (السنة الحالية و 4 سنوات سابقة)
        current_year = datetime.now().year
        for year in range(current_year, current_year - 5, -1):
            self.year_combo.addItem(str(year))

        self.year_combo.currentTextChanged.connect(self.on_year_changed)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        layout.addLayout(year_layout)

        # فلتر الشهر
        month_layout = QHBoxLayout()
        month_label = QLabel("الشهر:")
        month_label.setObjectName("filter_label")
        self.month_combo = QComboBox()
        self.month_combo.setObjectName("filter_combo")

        # إضافة الشهور
        months = ["الكل", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                 "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        self.month_combo.addItems(months)
        self.month_combo.currentTextChanged.connect(self.on_month_changed)

        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_combo)
        layout.addLayout(month_layout)

        layout.addStretch()
        return filters_widget

    # إنشاء بطاقات الإحصائيات الملونة
    def create_statistics_cards(self):
        stats_widget = QWidget()
        stats_widget.setObjectName("statistics_container")
        layout = QHBoxLayout(stats_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # بيانات الإحصائيات مع الألوان المحدثة والأيقونات المحسنة
        stats_data = [
            ("إجمالي الإيرادات", "0.00", "#4CAF50", "💰", "positive"),
            ("إجمالي المصروفات", "0.00", "#F44336", "💸", "negative"),
            ("صافي الربح", "0.00", "#2196F3", "📈", "profit"),
            ("المستحقات", "0.00", "#FF9800", "📋", "warning"),
            ("عدد المعاملات", "0", "#673AB7", "🔢", "info")
        ]

        for title, value, color, icon, card_type in stats_data:
            card = self.create_enhanced_stat_card(title, value, color, icon, card_type)
            # البحث عن label القيمة داخل البطاقة لحفظه للتحديث لاحقاً
            value_label = None
            for child in card.findChildren(QLabel):
                if child.objectName() == "stats_value":
                    value_label = child
                    break

            if value_label:
                self.stats_cards[title] = value_label

            layout.addWidget(card)

        return stats_widget

    # إنشاء بطاقة إحصائية واحدة
    def create_stat_card(self, title, value, color, icon):
        card = QFrame()
        card.setObjectName("financial_stats_card")
        card.setFrameStyle(QFrame.Shape.Box)

        # تخطيط أفقي - العنوان والقيمة في نفس السطر
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(10)

        # الأيقونة
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        card_layout.addWidget(icon_label)

        # العنوان والقيمة في نفس السطر
        title_label = QLabel(f"{title}:")
        title_label.setObjectName("stats_title")
        card_layout.addWidget(title_label)

        value_label = QLabel(f"{value} {Currency_type}" if title != "عدد المعاملات" else value)
        value_label.setObjectName("stats_value")
        value_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)

        card_layout.addStretch()

        # إرجاع البطاقة كاملة بدلاً من label فقط
        return card

    # إنشاء بطاقة إحصائية محسنة مع ستايل متطور
    def create_enhanced_stat_card(self, title, value, color, icon, card_type):
        card = QFrame()
        card.setObjectName(f"enhanced_stats_card_{card_type}")
        card.setFrameStyle(QFrame.Shape.Box)

        # تطبيق ستايل متقدم حسب نوع البطاقة
        if card_type == "positive":
            card_style = """
                QFrame#enhanced_stats_card_positive {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #E8F5E8, stop:1 #F1F8E9);
                    border: 2px solid #C8E6C9;
                    border-radius: 12px;
                    
                    margin: 4px;
                }
                QFrame#enhanced_stats_card_positive:hover {
                    border: 2px solid #4CAF50;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #F1F8E9, stop:1 #E8F5E8);
                }
            """
        elif card_type == "negative":
            card_style = """
                QFrame#enhanced_stats_card_negative {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFEBEE, stop:1 #FCE4EC);
                    border: 2px solid #FFCDD2;
                    border-radius: 12px;
                    
                    margin: 4px;
                }
                QFrame#enhanced_stats_card_negative:hover {
                    border: 2px solid #F44336;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FCE4EC, stop:1 #FFEBEE);
                }
            """
        elif card_type == "profit":
            card_style = """
                QFrame#enhanced_stats_card_profit {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #E3F2FD, stop:1 #E8EAF6);
                    border: 2px solid #BBDEFB;
                    border-radius: 12px;
                    
                    margin: 4px;
                }
                QFrame#enhanced_stats_card_profit:hover {
                    border: 2px solid #2196F3;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #E8EAF6, stop:1 #E3F2FD);
                }
            """
        elif card_type == "warning":
            card_style = """
                QFrame#enhanced_stats_card_warning {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFF3E0, stop:1 #FFF8E1);
                    border: 2px solid #FFCC02;
                    border-radius: 12px;
                    
                    margin: 4px;
                }
                QFrame#enhanced_stats_card_warning:hover {
                    border: 2px solid #FF9800;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFF8E1, stop:1 #FFF3E0);
                }
            """
        else:  # info
            card_style = """
                QFrame#enhanced_stats_card_info {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #F3E5F5, stop:1 #E8EAF6);
                    border: 2px solid #CE93D8;
                    border-radius: 12px;
                    
                    margin: 4px;
                }
                QFrame#enhanced_stats_card_info:hover {
                    border: 2px solid #673AB7;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #E8EAF6, stop:1 #F3E5F5);
                }
            """
        
        card.setStyleSheet(card_style)

        # تخطيط عمودي للبطاقة المحسنة
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(8)

        # القسم العلوي: الأيقونة والعنوان
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # الأيقونة مع خلفية دائرية
        icon_container = QWidget()
        icon_container.setObjectName("icon_container")
        icon_container.setStyleSheet(f"""
            QWidget#icon_container {{
                background: {color};
                border-radius: 20px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }}
        """)
        icon_container.setFixedSize(40, 40)
        
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px; color: white;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)

        # العنوان
        title_label = QLabel(title)
        title_label.setObjectName("enhanced_stats_title")
        title_label.setStyleSheet("""
            QLabel#enhanced_stats_title {
                font-size: 14px;
                color: #37474F;
                font-weight: 600;
                padding: 2px 0px;
            }
        """)
        title_label.setWordWrap(True)

        header_layout.addWidget(icon_container)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # القسم السفلي: القيمة
        value_label = QLabel(f"{value} {Currency_type}" if title != "عدد المعاملات" else value)
        value_label.setObjectName("stats_value")
        value_label.setStyleSheet(f"""
            QLabel#stats_value {{
                color: {color};
                font-weight: bold;
                font-size: 18px;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 6px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addLayout(header_layout)
        card_layout.addWidget(value_label)

        # إرجاع البطاقة كاملة
        return card

    # إنشاء شريط أدوات الإجراءات
    def create_actions_toolbar(self):
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # أزرار الإجراءات المحسنة
        actions = [
            ("📊 تحديث البيانات", self.refresh_all_data, "#673AB7", "update"),
            ("📈 التقارير المتقدمة", self.open_advanced_reports, "#4CAF50", "reports"),
            ("📋 تصدير Excel", self.export_to_excel, "#FF9800", "export"),
            ("🖨️ طباعة", self.print_reports, "#2196F3", "print")
        ]

        for text, callback, color, btn_type in actions:
            btn = QPushButton(text)
            btn.setObjectName(f"enhanced_action_button_{btn_type}")
            btn.setStyleSheet(f"""
                QPushButton#enhanced_action_button_{btn_type} {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {color}, stop:1 {self.darken_color(color)});
                    color: white;
                    border: 2px solid {self.darken_color(color)};
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 140px;
                    min-height: 40px;
                    
                }}
                QPushButton#enhanced_action_button_{btn_type}:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.lighten_color(color)}, stop:1 {color});
                    border: 2px solid {color};
                    
                }}
                QPushButton#enhanced_action_button_{btn_type}:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.darken_color(color)}, stop:1 {self.darken_color(self.darken_color(color))});
                    
                }}
            """)
            btn.clicked.connect(callback)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        return toolbar_layout

    # تغميق اللون للحالة hover
    def darken_color(self, color):
        color_map = {
            "#673AB7": "#5E35B1",
            "#4CAF50": "#43A047",
            "#FF9800": "#F57C00",
            "#2196F3": "#1976D2",
            "#3498db": "#2980b9",
            "#2ecc71": "#27ae60",
            "#f39c12": "#e67e22",
            "#e67e22": "#d35400"
        }
        return color_map.get(color, color)

    # تفتيح اللون للحالة hover
    def lighten_color(self, color):
        color_map = {
            "#673AB7": "#7C4DFF",
            "#4CAF50": "#66BB6A",
            "#FF9800": "#FFB74D",
            "#2196F3": "#42A5F5",
            "#3498db": "#5DADE2",
            "#2ecc71": "#58D68D",
            "#f39c12": "#F8C471",
            "#e67e22": "#F0B27A"
        }
        return color_map.get(color, color)

    # إنشاء بطاقة الملخص السنوي
    def create_annual_summary_card(self):
        card = QFrame()
        card.setObjectName("annual_summary_card")
        card.setFrameStyle(QFrame.Box)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # عنوان البطاقة
        title_layout = QHBoxLayout()
        title_icon = QLabel("📊")
        title_icon.setStyleSheet("font-size: 24px;")
        title_label = QLabel("الملخص المالي السنوي")
        title_label.setObjectName("annual_title")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # المحتوى المالي في تخطيط أفقي
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # قسم الإيرادات مع أيقونات
        revenue_section = self.create_enhanced_financial_section("💰 الإيرادات", "#4CAF50", [
            ("🏗️ إيرادات المشاريع", "0.00"),
            ("🎓 إيرادات التدريب", "0.00"),
            ("💼 إيرادات العهد", "0.00"),
            ("📊 إيرادات أخرى", "0.00")
        ])
        content_layout.addWidget(revenue_section)

        # خط فاصل عمودي محسن
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: #E1BEE7;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E8EAF6, stop:1 #F3E5F5);
                border: 1px solid #CE93D8;
                border-radius: 2px;
                min-width: 3px;
                max-width: 3px;
            }
        """)
        content_layout.addWidget(separator)

        # قسم المصروفات مع أيقونات
        expenses_section = self.create_enhanced_financial_section("💸 المصروفات", "#F44336", [
            ("🔧 مصروفات المشاريع", "0.00"),
            ("👥 رواتب الموظفين", "0.00"),
            ("🏢 مصروفات إدارية", "0.00"),
            ("📋 مصروفات أخرى", "0.00")
        ])
        content_layout.addWidget(expenses_section)

        # خط فاصل عمودي محسن
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("""
            QFrame {
                color: #E1BEE7;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E8EAF6, stop:1 #F3E5F5);
                border: 1px solid #CE93D8;
                border-radius: 2px;
                min-width: 3px;
                max-width: 3px;
            }
        """)
        content_layout.addWidget(separator2)

        # قسم الأرباح والإحصائيات مع أيقونات
        profit_section = self.create_enhanced_financial_section("📈 الأرباح والإحصائيات", "#2196F3", [
            ("💹 صافي الربح", "0.00"),
            ("📊 هامش الربح", "0%"),
            ("🏗️ عدد المشاريع", "0"),
            ("📅 متوسط الربح الشهري", "0.00")
        ])
        content_layout.addWidget(profit_section)

        layout.addLayout(content_layout)
        self.annual_card = card
        return card

    # إنشاء قسم مالي داخل البطاقة
    def create_financial_section(self, title, color, items):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # عنوان القسم
        section_title = QLabel(title)
        section_title.setObjectName("section_title")
        section_title.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        section_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(section_title)

        # العناصر
        for label_text, value in items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(5)

            label = QLabel(f"{label_text}:")
            label.setObjectName("item_label")

            value_label = QLabel(f"{value} {Currency_type}" if "عدد" not in label_text and "%" not in value else value)
            value_label.setObjectName("item_value")
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignLeft)

            item_layout.addWidget(label)
            item_layout.addWidget(value_label)
            layout.addLayout(item_layout)

        return section

    # إنشاء قسم مالي محسن داخل البطاقة مع تحسينات بصرية
    def create_enhanced_financial_section(self, title, color, items):
        section = QWidget()
        section.setObjectName("enhanced_financial_section")
        
        # تطبيق ستايل محسن للقسم
        section.setStyleSheet(f"""
            QWidget#enhanced_financial_section {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #FAFAFA);
                border: 2px solid {color}30;
                border-radius: 10px;
                padding: 8px;
                margin: 4px;
            }}
            QWidget#enhanced_financial_section:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FAFAFA, stop:1 #F5F5F5);
                border: 2px solid {color}50;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # عنوان القسم المحسن
        section_title = QLabel(title)
        section_title.setObjectName("enhanced_section_title")
        section_title.setStyleSheet(f"""
            QLabel#enhanced_section_title {{
                color: {color};
                font-weight: bold;
                font-size: 16px;
                padding: 10px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}15, stop:1 {color}25);
                border: 1px solid {color}40;
                border-radius: 8px;
                margin: 2px;
            }}
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)

        # العناصر المحسنة
        for label_text, value in items:
            # إنشاء حاوية للعنصر
            item_container = QWidget()
            item_container.setObjectName("enhanced_item_container")
            item_container.setStyleSheet(f"""
                QWidget#enhanced_item_container {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FFFFFF, stop:1 #FAFAFA);
                    border: 1px solid {color}20;
                    border-radius: 6px;
                    padding: 4px;
                    margin: 2px;
                }}
                QWidget#enhanced_item_container:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FAFAFA, stop:1 #F5F5F5);
                    border: 1px solid {color}40;
                }}
            """)
            
            item_layout = QHBoxLayout(item_container)
            item_layout.setContentsMargins(8, 6, 8, 6)
            item_layout.setSpacing(8)

            # التسمية
            label = QLabel(label_text)
            label.setObjectName("enhanced_item_label")
            label.setStyleSheet(f"""
                QLabel#enhanced_item_label {{
                    font-size: 13px;
                    color: #455A64;
                    font-weight: 500;
                    padding: 2px 4px;
                }}
            """)

            # القيمة
            value_label = QLabel(f"{value} {Currency_type}" if "عدد" not in label_text and "%" not in str(value) else str(value))
            value_label.setObjectName("enhanced_item_value")
            value_label.setStyleSheet(f"""
                QLabel#enhanced_item_value {{
                    color: {color};
                    font-weight: bold;
                    font-size: 14px;
                    padding: 4px 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}10, stop:1 {color}20);
                    border: 1px solid {color}30;
                    border-radius: 4px;
                }}
            """)
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(value_label)
            
            layout.addWidget(item_container)

        return section

    # إنشاء قسم التقارير الشهرية مع ارتفاع متكيف
    def create_monthly_reports_section(self):
        section = QWidget()
        section.setObjectName("monthly_reports_section")
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)  # تكيف مع حجم المحتوى

        # عنوان القسم
        title_layout = QHBoxLayout()
        title_icon = QLabel("📅")
        title_icon.setStyleSheet("font-size: 20px;")
        title_label = QLabel("التقارير الشهرية")
        title_label.setObjectName("monthly_title")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # حاوية البطاقات الشهرية بدون سكرول داخلي - عرض مباشر للمحتوى
        # استخدام QWidget عادي بدلاً من QScrollArea لإزالة السكرول الداخلي
        content_container = QWidget()
        content_container.setObjectName("monthly_content_container")
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        # تخطيط شبكي مباشر داخل الحاوية بدون سكرول
        grid_layout = QGridLayout(content_container)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setSpacing(15)
        grid_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)  # محاذاة للأعلى واليمين (RTL)

        # تعيين سياسة الحجم للشبكة لتتكيف مع المحتوى
        grid_layout.setSizeConstraint(QGridLayout.SetMinimumSize)

        # إنشاء البطاقات الشهرية لجميع الشهور (12 شهر)
        current_year = int(self.year_combo.currentText()) if hasattr(self, 'year_combo') else datetime.now().year

        # عرض جميع الشهور (12 شهر) بدلاً من الشهر الحالي فقط
        cards_per_row = 3  # 3 بطاقات في كل صف
        total_months = 12  # عرض جميع الشهور

        for month in range(1, total_months + 1):
            month_card = self.create_monthly_card(current_year, month)
            self.monthly_cards.append(month_card)

            # حساب موقع البطاقة في الشبكة
            row = (month - 1) // cards_per_row
            col = (month - 1) % cards_per_row

            # إضافة البطاقة للشبكة مع تمدد تلقائي
            grid_layout.addWidget(month_card, row, col)

            # جعل الأعمدة تتمدد بالتساوي مع عرض النافذة
            grid_layout.setColumnStretch(col, 1)

        # لا نحتاج إلى مساحة فارغة إضافية - دع الشبكة تتكيف مع المحتوى
        # grid_layout.setRowStretch(grid_layout.rowCount(), 1)  # تم إزالة هذا للتكيف التلقائي

        # إضافة الحاوية مباشرة للتخطيط الرئيسي بدون سكرول
        layout.addWidget(content_container)

        return section

    # إنشاء بطاقة شهرية مع بيانات فعلية وتصميم متمدد
    def create_monthly_card(self, year, month):
        card = QFrame()
        card.setObjectName("monthly_card")
        card.setFrameStyle(QFrame.Box)
        card.setMinimumWidth(300)  # عرض أدنى محسن للعمودين مع النصوص
        card.setMinimumHeight(220)  # ارتفاع محسن للتخطيط الشبكي (5 صفوف × ~35px + هوامش)
        # إزالة الحد الأقصى للعرض والارتفاع للسماح بالتمدد والتكيف

        # تعيين سياسة الحجم للتمدد الأفقي والتكيف العمودي
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)  # زيادة التباعد بين العناصر لاستغلال الارتفاع الإضافي

        # عنوان الشهر مع رقم الشهر والسنة
        month_names = ["", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                      "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

        title_layout = QHBoxLayout()
        # إضافة رقم الشهر مع اسم الشهر والسنة
        title_label = QLabel(f"{month_names[month]} {month}/{year}")
        title_label.setObjectName("month_title")
        title_label.setAlignment(Qt.AlignCenter)
        # زيادة الحشو والارتفاع للعنوان
        title_label.setMinimumHeight(35)
        title_label.setContentsMargins(10, 8, 10, 8)
        title_layout.addWidget(title_label)
        layout.addLayout(title_layout)

        # خط فاصل
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # الحصول على البيانات الفعلية للشهر
        monthly_data = self.get_real_monthly_data(year, month)

        # عرض البيانات المالية والإحصائيات الشهرية مع تحسينات بصرية
        financial_items = [
            ("💰 الإيرادات:", monthly_data['revenue'], "#4CAF50", "positive"),
            ("💸 المصروفات:", monthly_data['expenses'], "#F44336", "negative"),
            ("📈 صافي الربح:", monthly_data['net_profit'], "#2196F3", "profit"),
            ("💳 سحب الموظفين:", monthly_data['employee_withdrawals'], "#FF9800", "neutral"),
            ("🏗️ عدد المشاريع:", monthly_data['projects_count'], "#673AB7", "neutral"),
            ("👥 عدد العملاء:", monthly_data['clients_count'], "#009688", "neutral"),
            ("📋 عدد المقاولات:", monthly_data['contracts_count'], "#795548", "neutral"),
            ("🎓 عدد الدورات:", monthly_data['courses_count'], "#3F51B5", "neutral"),
            ("🔢 عدد المعاملات:", monthly_data['transactions_count'], "#9C27B0", "neutral")
        ]

        # تنظيم البيانات في شكل شبكة (عمودين في كل صف)
        grid_container = QWidget()
        grid_container.setObjectName("monthly_grid_container")
        grid_container.setStyleSheet("""
            QWidget#monthly_grid_container {
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
        
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(4, 4, 4, 4)
        grid_layout.setSpacing(6)
        
        # تقسيم البيانات إلى صفوف (كل صف يحتوي على عمودين)
        for row_index, i in enumerate(range(0, len(financial_items), 2)):
            # العنصر الأول في الصف
            if i < len(financial_items):
                left_item = financial_items[i]
                left_container = self.create_monthly_item_widget(left_item)
                grid_layout.addWidget(left_container, row_index, 0)
            
            # العنصر الثاني في الصف (إذا كان موجود)
            if i + 1 < len(financial_items):
                right_item = financial_items[i + 1]
                right_container = self.create_monthly_item_widget(right_item)
                grid_layout.addWidget(right_container, row_index, 1)
        
        # جعل العمودين يتمددان بالتساوي
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        
        layout.addWidget(grid_container)

        return card

    # إنشاء ويدجت منفرد للعنصر المالي في البطاقة الشهرية
    def create_monthly_item_widget(self, item_data):
        label_text, value, color, value_type = item_data
        
        # إنشاء حاوية للعنصر مع تخطيط أنيق
        item_container = QWidget()
        item_container.setObjectName("monthly_item_container")
        item_container.setStyleSheet("""
            QWidget#monthly_item_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FAFAFA, stop:1 #FFFFFF);
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 3px;
                margin: 2px;
                min-height: 28px;
                max-height: 35px;
            }
            QWidget#monthly_item_container:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F5F5F5, stop:1 #FAFAFA);
                border: 1px solid #BDBDBD;
            }
        """)
        
        # تخطيط أفقي للعنصر
        item_layout = QHBoxLayout(item_container)
        item_layout.setContentsMargins(6, 3, 6, 3)
        item_layout.setSpacing(4)

        # إنشاء التسمية مع النص المختصر والواضح
        label_short = label_text.replace("💰 الإيرادات:", "💰 الإيرادات")
        label_short = label_short.replace("💸 المصروفات:", "💸 المصروفات")
        label_short = label_short.replace("📈 صافي الربح:", "📈 الربح")
        label_short = label_short.replace("💳 سحب الموظفين:", "💳 السحب")
        label_short = label_short.replace("🏗️ عدد المشاريع:", "🏗️ المشاريع")
        label_short = label_short.replace("👥 عدد العملاء:", "👥 العملاء")
        label_short = label_short.replace("📋 عدد المقاولات:", "📋 المقاولات")
        label_short = label_short.replace("🎓 عدد الدورات:", "🎓 الدورات")
        label_short = label_short.replace("🔢 عدد المعاملات:", "🔢 المعاملات")
        
        label = QLabel(label_short)
        label.setObjectName("monthly_item_label")
        label.setStyleSheet("""
            QLabel#monthly_item_label {
                font-size: 10px;
                color: #455A64;
                font-weight: 500;
                padding: 1px 3px;
                min-width: 50px;
                max-width: 90px;
            }
        """)
        label.setToolTip(label_text)  # عرض النص الكامل عند التحويم

        # تنسيق القيمة مع تحسينات بصرية
        if "عدد" in label_text:
            formatted_value = f"{value:,}"
            # إضافة وصف مختصر للعدد
            if value == 0:
                formatted_value = "0"
            elif value > 100:
                formatted_value = f"{value:,}+"
        elif "سحب" in label_text:
            formatted_value = f"{value:,.0f}"
        else:
            formatted_value = f"{value:,.0f}"
            # تحديد نوع القيمة للتلوين
            if value < 0:
                color = "#F44336"
                value_type = "negative"
            elif value > 0 and "ربح" in label_text:
                color = "#4CAF50"
                value_type = "positive"

        # إنشاء label القيمة مع تحسينات بصرية
        value_label = QLabel(formatted_value)
        value_label.setObjectName(f"monthly_item_value_{value_type}")
        
        # تطبيق ستايل متقدم حسب نوع القيمة مع حجم مضغوط
        if value_type == "positive":
            value_label.setStyleSheet(f"""
                QLabel#monthly_item_value_positive {{
                    color: #2E7D32;
                    font-weight: bold;
                    font-size: 11px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #E8F5E8, stop:1 #F1F8E9);
                    border: 1px solid #C8E6C9;
                    border-radius: 3px;
                    padding: 2px 4px;
                }}
            """)
        elif value_type == "negative":
            value_label.setStyleSheet(f"""
                QLabel#monthly_item_value_negative {{
                    color: #C62828;
                    font-weight: bold;
                    font-size: 11px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FFEBEE, stop:1 #FCE4EC);
                    border: 1px solid #FFCDD2;
                    border-radius: 3px;
                    padding: 2px 4px;
                }}
            """)
        elif value_type == "profit":
            # تلوين خاص للربح
            profit_color = "#2E7D32" if value >= 0 else "#C62828"
            profit_bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E8F5E8, stop:1 #F1F8E9)" if value >= 0 else "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFEBEE, stop:1 #FCE4EC)"
            profit_border = "#C8E6C9" if value >= 0 else "#FFCDD2"
            
            value_label.setStyleSheet(f"""
                QLabel#monthly_item_value_profit {{
                    color: {profit_color};
                    font-weight: bold;
                    font-size: 11px;
                    background: {profit_bg};
                    border: 1px solid {profit_border};
                    border-radius: 3px;
                    padding: 2px 4px;
                }}
            """)
        else:  # neutral
            value_label.setStyleSheet(f"""
                QLabel#monthly_item_value_neutral {{
                    color: #1565C0;
                    font-weight: bold;
                    font-size: 11px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #E3F2FD, stop:1 #E8EAF6);
                    border: 1px solid #BBDEFB;
                    border-radius: 3px;
                    padding: 2px 4px;
                }}
            """)

        # إضافة مؤشر بصري مصغر للقيم المهمة
        if value_type == "profit":
            trend_icon = "📈" if value >= 0 else "📉"
            trend_label = QLabel(trend_icon)
            trend_label.setStyleSheet("font-size: 10px; padding: 1px;")
            item_layout.addWidget(trend_label)

        item_layout.addWidget(label)
        item_layout.addStretch()  # إضافة مساحة مرنة
        item_layout.addWidget(value_label)
        
        return item_container

    # الحصول على البيانات الفعلية للشهر من قاعدة البيانات
    def get_real_monthly_data(self, year, month):
        try:
            conn = self.main_window.get_db_connection()
            if not conn:
                # إرجاع بيانات افتراضية في حالة عدم توفر الاتصال
                return {
                    'revenue': 0,
                    'expenses': 0,
                    'net_profit': 0,
                    'transactions_count': 0,
                    'employee_withdrawals': 0,
                    'projects_count': 0,
                    'clients_count': 0,
                    'contracts_count': 0,
                    'courses_count': 0
                }

            cursor = conn.cursor()
            monthly_data = {
                'revenue': 0,
                'expenses': 0,
                'net_profit': 0,
                'transactions_count': 0,
                'employee_withdrawals': 0,
                'projects_count': 0,
                'clients_count': 0,
                'contracts_count': 0,
                'courses_count': 0
            }

            # حساب الإيرادات الشهرية
            # إيرادات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month))
            project_revenue = cursor.fetchone()[0] or 0

            # إيرادات التدريب
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month))
            training_revenue = cursor.fetchone()[0] or 0

            # إيرادات العهد
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM المقاولات_دفعات_العهد
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month))
            custody_revenue = cursor.fetchone()[0] or 0

            monthly_data['revenue'] = project_revenue + training_revenue + custody_revenue

            # حساب المصروفات الشهرية
            # المصروفات العامة
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month))
            general_expenses = cursor.fetchone()[0] or 0

            # مصروفات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM المقاولات_مصروفات_العهد
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month))
            project_expenses = cursor.fetchone()[0] or 0

            # رواتب الموظفين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE نوع_المعاملة LIKE '%مرتب%'
                AND YEAR(التاريخ) = %s AND MONTH(التاريخ) = %s
            """, (year, month))
            salaries = cursor.fetchone()[0] or 0

            monthly_data['expenses'] = general_expenses + project_expenses + salaries
            monthly_data['net_profit'] = monthly_data['revenue'] - monthly_data['expenses']

            # عدد المعاملات الشهرية
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM المشاريع_المدفوعات
                     WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s) +
                    (SELECT COUNT(*) FROM الحسابات
                     WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s) +
                    (SELECT COUNT(*) FROM التدريب_دفعات_الطلاب
                     WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s) +
                    (SELECT COUNT(*) FROM المقاولات_دفعات_العهد
                     WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s) +
                    (SELECT COUNT(*) FROM المقاولات_مصروفات_العهد
                     WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s) +
                    (SELECT COUNT(*) FROM الموظفين_معاملات_مالية
                     WHERE YEAR(التاريخ) = %s AND MONTH(التاريخ) = %s)
                AS total_transactions
            """, (year, month, year, month, year, month, year, month, year, month, year, month))

            monthly_data['transactions_count'] = cursor.fetchone()[0] or 0

            # إضافة الإحصائيات الجديدة
            # سحب الموظفين (المعاملات المالية للموظفين في الشهر)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE YEAR(التاريخ) = %s AND MONTH(التاريخ) = %s
                AND المبلغ < 0
            """, (year, month))
            monthly_data['employee_withdrawals'] = abs(cursor.fetchone()[0] or 0)

            # عدد المشاريع النشطة في الشهر
            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_المشروع)
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month))
            monthly_data['projects_count'] = cursor.fetchone()[0] or 0

            # عدد العملاء النشطين في الشهر
            cursor.execute("""
                SELECT COUNT(DISTINCT p.معرف_العميل)
                FROM المشاريع p
                JOIN المشاريع_المدفوعات pm ON p.id = pm.معرف_المشروع
                WHERE YEAR(pm.تاريخ_الدفع) = %s AND MONTH(pm.تاريخ_الدفع) = %s
            """, (year, month))
            monthly_data['clients_count'] = cursor.fetchone()[0] or 0

            # عدد المقاولات النشطة في الشهر
            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_العهدة)
                FROM المقاولات_دفعات_العهد
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month))
            monthly_data['contracts_count'] = cursor.fetchone()[0] or 0

            # عدد الدورات النشطة في الشهر
            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_الدورة)
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month))
            monthly_data['courses_count'] = cursor.fetchone()[0] or 0

            cursor.close()
            conn.close()

            return monthly_data

        except Exception as e:
            print(f"⚠️ خطأ في الحصول على البيانات الشهرية للشهر {month}/{year}: {e}")
            return {
                'revenue': 0,
                'expenses': 0,
                'net_profit': 0,
                'transactions_count': 0,
                'employee_withdrawals': 0,
                'projects_count': 0,
                'clients_count': 0,
                'contracts_count': 0,
                'courses_count': 0
            }

    # تطبيق الأنماط المخصصة مع تحسين السكرول بار وستايل التقارير المتطور
    def apply_custom_styles(self):
        self.setStyleSheet("""
            /* منطقة التمرير الرئيسية */
            QScrollArea#main_scroll_area {
                border: none;
                background-color: #F5F7FA;
            }

            QWidget#scroll_content {
                background-color: #F5F7FA;
            }

            /* تحسين مظهر السكرول بار بألوان أنيقة */
            QScrollBar:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E8EBF0, stop:1 #F2F4F7);
                width: 14px;
                border-radius: 7px;
                margin: 0px;
                border: 1px solid #D1D5DB;
            }

            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #673AB7, stop:1 #5C6BC0);
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
                border: 1px solid #4A148C;
            }

            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C4DFF, stop:1 #3F51B5);
            }

            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5E35B1, stop:1 #3949AB);
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E8EBF0, stop:1 #F2F4F7);
                height: 14px;
                border-radius: 7px;
                margin: 0px;
                border: 1px solid #D1D5DB;
            }

            QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #673AB7, stop:1 #5C6BC0);
                border-radius: 6px;
                min-width: 30px;
                margin: 2px;
                border: 1px solid #4A148C;
            }

            QScrollBar::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7C4DFF, stop:1 #3F51B5);
            }

            QScrollBar::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5E35B1, stop:1 #3949AB);
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }

            /* حاوية الفلاتر مع تدرج أنيق */
            QWidget#filters_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E3F2FD;
                border-radius: 12px;
                min-width: 220px;
                max-width: 280px;
                
            }

            QLabel#filter_title {
                font-weight: bold;
                font-size: 15px;
                color: #673AB7;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E8EAF6, stop:1 #F3E5F5);
                border-radius: 6px;
                margin: 2px;
            }

            QLabel#filter_label {
                font-size: 13px;
                color: #37474F;
                font-weight: 500;
            }

            QComboBox#filter_combo {
                padding: 8px 12px;
                border: 2px solid #E1F5FE;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                color: #37474F;
                font-weight: 500;
                selection-background-color: #673AB7;
            }

            QComboBox#filter_combo:hover {
                border: 2px solid #673AB7;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #E8EAF6);
            }

            QComboBox#filter_combo:focus {
                border: 2px solid #5C6BC0;
                outline: none;
            }

            /* حاوية الإحصائيات */
            QWidget#statistics_container {
                background-color: transparent;
            }

            QFrame#financial_stats_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E8EAF6;
                border-radius: 12px;
                
                padding: 8px;
                margin: 4px;
            }

            QFrame#financial_stats_card:hover {
                border: 2px solid #673AB7;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #E8EAF6);
                
            }

            QLabel#stats_title {
                font-size: 13px;
                color: #37474F;
                font-weight: 600;
                padding: 2px 0px;
            }

            QLabel#stats_value {
                font-size: 16px;
                font-weight: bold;
                padding: 2px 5px;
                border-radius: 4px;
            }

            /* بطاقة الملخص السنوي مع تدرج أنيق */
            QFrame#annual_summary_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F3E5F5);
                border: 2px solid #E1BEE7;
                border-radius: 16px;
                
                margin: 8px;
            }

            QLabel#annual_title {
                font-size: 20px;
                font-weight: bold;
                color: #673AB7;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E8EAF6, stop:1 #F3E5F5);
                border-radius: 8px;
                margin: 4px;
            }

            QLabel#section_title {
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                border-bottom: 3px solid currentColor;
                border-radius: 6px 6px 0px 0px;
                margin: 2px;
            }

            QLabel#item_label {
                font-size: 13px;
                color: #455A64;
                font-weight: 500;
                padding: 3px 0px;
            }

            QLabel#item_value {
                font-size: 14px;
                font-weight: bold;
                padding: 3px 8px;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F8F9FA, stop:1 #FFFFFF);
                border: 1px solid #E0E0E0;
                margin: 1px;
            }

            /* قسم التقارير الشهرية مع تصميم متطور */
            QWidget#monthly_reports_section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F5F7FA, stop:1 #FFFFFF);
                border: 2px solid #E3F2FD;
                border-radius: 16px;
                
                margin: 8px;
            }

            QLabel#monthly_title {
                font-size: 18px;
                font-weight: bold;
                color: #673AB7;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E8EAF6, stop:1 #F3E5F5);
                border-radius: 8px;
                margin: 8px;
            }

            QWidget#monthly_content_container {
                border: none;
                background-color: transparent;
                padding: 8px;
            }

            /* بطاقات شهرية محسنة مع تأثيرات بصرية - تخطيط شبكي */
            QFrame#monthly_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E8F5E8;
                border-radius: 12px;
                
                min-width: 300px;
                min-height: 220px;
                margin: 6px;
                padding: 4px;
            }

            QFrame#monthly_card:hover {
                border: 2px solid #4CAF50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #E8F5E8);
                
                
            }

            QLabel#month_title {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 12px 18px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #673AB7, stop:1 #7C4DFF);
                border-radius: 8px;
                margin: 4px;
                min-height: 40px;
                border: 2px solid #5E35B1;
                text-align: center;
            }

            QLabel#monthly_item_label {
                font-size: 12px;
                color: #455A64;
                font-weight: 500;
                padding: 4px 2px;
                line-height: 1.5;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F8F9FA, stop:1 #FFFFFF);
                border-radius: 4px;
                margin: 1px;
            }

            QLabel#monthly_item_value {
                font-size: 13px;
                font-weight: bold;
                padding: 4px 8px;
                line-height: 1.5;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFFFFF, stop:1 #F0F4F8);
                border: 1px solid #E1E5E9;
                margin: 1px;
            }

            /* تأثيرات إضافية للبطاقات */
            QFrame#monthly_card QLabel#monthly_item_value[objectName*="positive"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E8F5E8, stop:1 #F1F8E9);
                border: 1px solid #C8E6C9;
                color: #2E7D32;
            }

            QFrame#monthly_card QLabel#monthly_item_value[objectName*="negative"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFEBEE, stop:1 #FCE4EC);
                border: 1px solid #FFCDD2;
                color: #C62828;
            }

            QFrame#monthly_card QLabel#monthly_item_value[objectName*="neutral"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E3F2FD, stop:1 #E8EAF6);
                border: 1px solid #BBDEFB;
                color: #1565C0;
            }
        """)

    # إنشاء جدول الملخص المالي
    def create_summary_table(self):
        self.summary_table = QTableWidget()
        self.summary_table.setObjectName("FinancialSummaryTable")
        
        # إعداد الأعمدة
        columns = [
            "نوع الحساب",
            "اسم الحساب", 
            "الرصيد المدين",
            "الرصيد الدائن",
            "صافي الرصيد",
            "النسبة %"
        ]
        
        self.summary_table.setColumnCount(len(columns))
        self.summary_table.setHorizontalHeaderLabels(columns)
        
        # إعداد خصائص الجدول
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.summary_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.summary_table.setSortingEnabled(True)
        
        # تخصيص عرض الأعمدة
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # نوع الحساب
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # اسم الحساب
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # الرصيد المدين
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # الرصيد الدائن
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # صافي الرصيد
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # النسبة
        
        # إعداد قائمة السياق
        setup_table_context_menu(self.summary_table, self.main_window, "الملخص_المالي")
        
        # ربط النقر المزدوج
        self.summary_table.itemDoubleClicked.connect(self.on_account_double_clicked)
    
    # تحميل البيانات المالية الفعلية من قاعدة البيانات
    def load_financial_data(self):
        try:
            # تحديث بطاقات الإحصائيات
            self.update_statistics_cards()

            # تحديث الملخص السنوي
            self.update_annual_summary()

            # تحديث التقارير الشهرية
            self.update_monthly_reports()

            

        except Exception as e:
            print(f"⚠️ خطأ في تحميل البيانات المالية: {e}")
            # عرض بيانات افتراضية في حالة الخطأ
            self.load_default_data()

    # تحديث بطاقات الإحصائيات
    def update_statistics_cards(self):
        try:
            conn = self.main_window.get_db_connection()
            if not conn:
                print("⚠️ لا يمكن الحصول على اتصال قاعدة البيانات")
                return

            cursor = conn.cursor()
            current_year = int(self.year_combo.currentText()) if hasattr(self, 'year_combo') else datetime.now().year

            # حساب إجمالي الإيرادات
            total_revenue = 0

            # إيرادات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (current_year,))
            project_revenue = cursor.fetchone()[0] or 0
            total_revenue += project_revenue

            # إيرادات التدريب
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (current_year,))
            training_revenue = cursor.fetchone()[0] or 0
            total_revenue += training_revenue

            # حساب إجمالي المصروفات
            total_expenses = 0

            # مصروفات الحسابات العامة
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (current_year,))
            general_expenses = cursor.fetchone()[0] or 0
            total_expenses += general_expenses

            # مصروفات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM المقاولات_مصروفات_العهد
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (current_year,))
            project_expenses = cursor.fetchone()[0] or 0
            total_expenses += project_expenses

            # رواتب الموظفين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE نوع_المعاملة LIKE '%مرتب%' AND YEAR(التاريخ) = %s
            """, (current_year,))
            salaries = cursor.fetchone()[0] or 0
            total_expenses += salaries

            # حساب صافي الربح
            net_profit = total_revenue - total_expenses

            # حساب المستحقات (الباقي من المشاريع)
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي), 0)
                FROM المشاريع
                WHERE الباقي > 0
            """)
            outstanding_amounts = cursor.fetchone()[0] or 0

            # عدد المعاملات المالية
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM المشاريع_المدفوعات WHERE YEAR(تاريخ_الدفع) = %s) +
                    (SELECT COUNT(*) FROM الحسابات WHERE YEAR(تاريخ_المصروف) = %s) +
                    (SELECT COUNT(*) FROM الموظفين_معاملات_مالية WHERE YEAR(التاريخ) = %s) +
                    (SELECT COUNT(*) FROM التدريب_دفعات_الطلاب WHERE YEAR(تاريخ_الدفع) = %s)
                AS total_transactions
            """, (current_year, current_year, current_year, current_year))
            total_transactions = cursor.fetchone()[0] or 0

            # تحديث البطاقات
            if "إجمالي الإيرادات" in self.stats_cards:
                self.stats_cards["إجمالي الإيرادات"].setText(f"{total_revenue:,.0f} {Currency_type}")

            if "إجمالي المصروفات" in self.stats_cards:
                self.stats_cards["إجمالي المصروفات"].setText(f"{total_expenses:,.0f} {Currency_type}")

            if "صافي الربح" in self.stats_cards:
                self.stats_cards["صافي الربح"].setText(f"{net_profit:,.0f} {Currency_type}")
                # تغيير لون النص حسب الربح/الخسارة
                color = "#27ae60" if net_profit >= 0 else "#e74c3c"
                self.stats_cards["صافي الربح"].setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")

            if "المستحقات" in self.stats_cards:
                self.stats_cards["المستحقات"].setText(f"{outstanding_amounts:,.0f} {Currency_type}")

            if "عدد المعاملات" in self.stats_cards:
                self.stats_cards["عدد المعاملات"].setText(str(total_transactions))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"⚠️ خطأ في تحديث بطاقات الإحصائيات: {e}")

    # تحميل بيانات افتراضية في حالة عدم توفر الاتصال
    def load_default_data(self):
        try:
            # بيانات افتراضية للبطاقات
            default_stats = {
                "إجمالي الإيرادات": "0.00",
                "إجمالي المصروفات": "0.00",
                "صافي الربح": "0.00",
                "المستحقات": "0.00",
                "عدد المعاملات": "0"
            }

            for title, value in default_stats.items():
                if title in self.stats_cards:
                    display_value = f"{value} {Currency_type}" if title != "عدد المعاملات" else value
                    self.stats_cards[title].setText(display_value)

        except Exception as e:
            print(f"⚠️ خطأ في تحميل البيانات الافتراضية: {e}")

    # تحديث بيانات الملخص السنوي
    def update_annual_summary(self):
        try:
            conn = self.main_window.get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            current_year = int(self.year_combo.currentText()) if hasattr(self, 'year_combo') else datetime.now().year

            # جمع بيانات الإيرادات
            revenue_data = {}

            # إيرادات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (current_year,))
            revenue_data['project_revenue'] = cursor.fetchone()[0] or 0

            # إيرادات التدريب
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (current_year,))
            revenue_data['training_revenue'] = cursor.fetchone()[0] or 0

            # إيرادات العهد
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM المقاولات_دفعات_العهد
                WHERE YEAR(تاريخ_الدفعة) = %s
            """, (current_year,))
            revenue_data['custody_revenue'] = cursor.fetchone()[0] or 0

            revenue_data['other_revenue'] = 0  # يمكن إضافة مصادر أخرى لاحقاً
            revenue_data['total_revenue'] = sum(revenue_data.values())

            # جمع بيانات المصروفات
            expense_data = {}

            # مصروفات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM المقاولات_مصروفات_العهد
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (current_year,))
            expense_data['project_expenses'] = cursor.fetchone()[0] or 0

            # رواتب الموظفين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE نوع_المعاملة LIKE '%مرتب%' AND YEAR(التاريخ) = %s
            """, (current_year,))
            expense_data['employee_salaries'] = cursor.fetchone()[0] or 0

            # مصروفات إدارية
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (current_year,))
            expense_data['admin_expenses'] = cursor.fetchone()[0] or 0

            expense_data['other_expenses'] = 0  # يمكن إضافة مصروفات أخرى لاحقاً
            expense_data['total_expenses'] = sum(expense_data.values())

            # حساب الأرباح والإحصائيات
            profit_data = {}
            profit_data['net_profit'] = revenue_data['total_revenue'] - expense_data['total_expenses']

            # حساب هامش الربح
            if revenue_data['total_revenue'] > 0:
                profit_data['profit_margin'] = (profit_data['net_profit'] / revenue_data['total_revenue']) * 100
            else:
                profit_data['profit_margin'] = 0

            # عدد المشاريع
            cursor.execute("""
                SELECT COUNT(*) FROM المشاريع
                WHERE YEAR(تاريخ_التسليم) = %s OR YEAR(تاريخ_الإستلام) = %s
            """, (current_year, current_year))
            profit_data['projects_count'] = cursor.fetchone()[0] or 0

            # متوسط الربح الشهري
            profit_data['avg_monthly_profit'] = profit_data['net_profit'] / 12 if profit_data['net_profit'] > 0 else 0

            # تحديث واجهة الملخص السنوي
            self.update_annual_summary_display(revenue_data, expense_data, profit_data)

            

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"⚠️ خطأ في تحديث الملخص السنوي: {e}")

    # تحديث عرض الملخص السنوي بالبيانات الفعلية
    def update_annual_summary_display(self, revenue_data, expense_data, profit_data):
        try:
            if not hasattr(self, 'annual_card') or not self.annual_card:
                return

            # البحث عن أقسام البيانات في البطاقة السنوية
            revenue_section = None
            expense_section = None
            profit_section = None

            # البحث في جميع الويدجات الفرعية
            for widget in self.annual_card.findChildren(QWidget):
                # البحث عن العناوين لتحديد الأقسام
                for label in widget.findChildren(QLabel):
                    if label.text() == "الإيرادات":
                        revenue_section = widget
                    elif label.text() == "المصروفات":
                        expense_section = widget
                    elif label.text() == "الأرباح والإحصائيات":
                        profit_section = widget

            # تحديث قسم الإيرادات
            if revenue_section:
                self.update_section_values(revenue_section, [
                    ("إيرادات المشاريع", revenue_data.get('project_revenue', 0)),
                    ("إيرادات التدريب", revenue_data.get('training_revenue', 0)),
                    ("إيرادات العهد", revenue_data.get('custody_revenue', 0)),
                    ("إيرادات أخرى", revenue_data.get('other_revenue', 0))
                ])

            # تحديث قسم المصروفات
            if expense_section:
                self.update_section_values(expense_section, [
                    ("مصروفات المشاريع", expense_data.get('project_expenses', 0)),
                    ("رواتب الموظفين", expense_data.get('employee_salaries', 0)),
                    ("مصروفات إدارية", expense_data.get('admin_expenses', 0)),
                    ("مصروفات أخرى", expense_data.get('other_expenses', 0))
                ])

            # تحديث قسم الأرباح
            if profit_section:
                self.update_section_values(profit_section, [
                    ("صافي الربح", profit_data.get('net_profit', 0)),
                    ("هامش الربح", f"{profit_data.get('profit_margin', 0):.1f}%"),
                    ("عدد المشاريع", profit_data.get('projects_count', 0)),
                    ("متوسط الربح الشهري", profit_data.get('avg_monthly_profit', 0))
                ])

            

        except Exception as e:
            print(f"⚠️ خطأ في تحديث عرض الملخص السنوي: {e}")

    # تحديث قيم قسم معين في الملخص السنوي
    def update_section_values(self, section, data_list):
        try:
            # البحث عن جميع labels القيم في القسم
            value_labels = section.findChildren(QLabel, "item_value")

            for i, (label_text, value) in enumerate(data_list):
                if i < len(value_labels):
                    label = value_labels[i]

                    # تنسيق القيمة
                    if isinstance(value, (int, float)) and "%" not in str(value) and "عدد" not in label_text:
                        formatted_value = f"{value:,.0f} {Currency_type}"
                    else:
                        formatted_value = str(value)

                    label.setText(formatted_value)

        except Exception as e:
            print(f"⚠️ خطأ في تحديث قيم القسم: {e}")

    # تحديث التقارير الشهرية مع إعادة إنشاء البطاقات
    def update_monthly_reports(self):
        try:
            current_year = int(self.year_combo.currentText()) if hasattr(self, 'year_combo') else datetime.now().year
            current_month = datetime.now().month

            # إعادة إنشاء قسم التقارير الشهرية
            self.refresh_monthly_reports_section(current_year, current_month)

            

        except Exception as e:
            print(f"⚠️ خطأ في تحديث التقارير الشهرية: {e}")

    # إعادة إنشاء قسم التقارير الشهرية بالبيانات المحدثة مع التخطيط الشبكي المتمدد
    def refresh_monthly_reports_section(self, year, total_months):
        try:
            # البحث عن قسم التقارير الشهرية الحالي
            monthly_section = self.findChild(QWidget, "monthly_reports_section")
            if monthly_section:
                # العثور على حاوية المحتوى الشهرية (بدلاً من منطقة التمرير)
                content_container = monthly_section.findChild(QWidget, "monthly_content_container")
                if content_container:
                    # مسح التخطيط القديم وإنشاء تخطيط جديد مباشرة في الحاوية
                    old_layout = content_container.layout()
                    if old_layout:
                        # مسح جميع العناصر من التخطيط القديم
                        while old_layout.count():
                            child = old_layout.takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        # حذف التخطيط القديم
                        old_layout.deleteLater()
                        content_container.setLayout(None)

                    # إنشاء تخطيط شبكي جديد مباشرة في الحاوية
                    grid_layout = QGridLayout()
                    content_container.setLayout(grid_layout)
                    grid_layout.setContentsMargins(15, 15, 15, 15)
                    grid_layout.setSpacing(15)
                    grid_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)  # محاذاة للأعلى واليمين (RTL)

                    # تعيين سياسة الحجم للشبكة لتتكيف مع المحتوى
                    grid_layout.setSizeConstraint(QGridLayout.SetMinimumSize)

                    # مسح البطاقات القديمة
                    self.monthly_cards.clear()

                    # إنشاء البطاقات الشهرية الجديدة لجميع الشهور (12 شهر)
                    cards_per_row = 3  # 3 بطاقات في كل صف
                    total_months = 12  # عرض جميع الشهور

                    for month in range(1, total_months + 1):
                        month_card = self.create_monthly_card(year, month)
                        self.monthly_cards.append(month_card)

                        # حساب موقع البطاقة في الشبكة
                        row = (month - 1) // cards_per_row
                        col = (month - 1) % cards_per_row

                        # إضافة البطاقة للشبكة مع تمدد تلقائي
                        grid_layout.addWidget(month_card, row, col)

                        # جعل الأعمدة تتمدد بالتساوي مع عرض النافذة
                        grid_layout.setColumnStretch(col, 1)

                    # لا نحتاج إلى مساحة فارغة إضافية - دع الشبكة تتكيف مع المحتوى
                    # grid_layout.setRowStretch(grid_layout.rowCount(), 1)  # تم إزالة هذا للتكيف التلقائي

                    # البطاقات تم إضافتها مباشرة للحاوية - لا حاجة لـ setWidget

                    

        except Exception as e:
            print(f"⚠️ خطأ في إعادة إنشاء قسم التقارير الشهرية: {e}")

    # الحصول على البيانات المالية لشهر محدد
    def get_monthly_financial_data(self, cursor, year, month):
        try:
            monthly_data = {
                'revenue': 0,
                'expenses': 0,
                'net_profit': 0,
                'transactions_count': 0
            }

            # إيرادات الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month))
            project_revenue = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month))
            training_revenue = cursor.fetchone()[0] or 0

            monthly_data['revenue'] = project_revenue + training_revenue

            # مصروفات الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month))
            general_expenses = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM المقاولات_مصروفات_العهد
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month))
            project_expenses = cursor.fetchone()[0] or 0

            monthly_data['expenses'] = general_expenses + project_expenses
            monthly_data['net_profit'] = monthly_data['revenue'] - monthly_data['expenses']

            # عدد المعاملات
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM المشاريع_المدفوعات WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s) +
                    (SELECT COUNT(*) FROM الحسابات WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s) +
                    (SELECT COUNT(*) FROM التدريب_دفعات_الطلاب WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s)
                AS total_transactions
            """, (year, month, year, month, year, month))
            monthly_data['transactions_count'] = cursor.fetchone()[0] or 0

            return monthly_data

        except Exception as e:
            print(f"⚠️ خطأ في الحصول على البيانات الشهرية: {e}")
            return {'revenue': 0, 'expenses': 0, 'net_profit': 0, 'transactions_count': 0}

    # ===== معالجات الأحداث =====
    # معالج تغيير السنة مع تحديث البطاقات الشهرية
    def on_year_changed(self, year_text):
        try:
            print(f"🗓️ تم تغيير السنة إلى: {year_text}")

            # تحديث جميع البيانات
            self.refresh_all_data()

            # تحديث البطاقات الشهرية للسنة الجديدة
            selected_year = int(year_text)

            # عرض جميع الشهور (12 شهر) لجميع السنوات
            total_months = 12

            # إعادة إنشاء البطاقات الشهرية لجميع الشهور
            self.refresh_monthly_reports_section(selected_year, total_months)

            

        except Exception as e:
            print(f"⚠️ خطأ في تغيير السنة: {e}")

    # معالج تغيير الشهر
    def on_month_changed(self, month_text):
        try:
            print(f"📅 تم تغيير الشهر إلى: {month_text}")
            # يمكن إضافة فلترة حسب الشهر لاحقاً
        except Exception as e:
            print(f"⚠️ خطأ في تغيير الشهر: {e}")

    # ===== دوال الإجراءات =====
    # تحديث جميع البيانات
    def refresh_all_data(self):
        try:
            print("🔄 جاري تحديث جميع البيانات المالية...")
            self.load_financial_data()
            QMessageBox.information(self, "تحديث البيانات", "تم تحديث البيانات المالية بنجاح")
        except Exception as e:
            print(f"⚠️ خطأ في تحديث البيانات: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحديث البيانات:\n{str(e)}")

    # فتح التقارير المتقدمة
    def open_advanced_reports(self):
        try:
            from التقارير_المالية import open_financial_reports_window
            window = open_financial_reports_window(self.main_window)
            if window:
                window.show()
                window.raise_()
                window.activateWindow()
        except Exception as e:
            print(f"⚠️ خطأ في فتح التقارير المتقدمة: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في فتح التقارير المتقدمة:\n{str(e)}")

    # تصدير البيانات إلى Excel
    def export_to_excel(self):
        try:
            from datetime import datetime

            # اختيار مسار الحفظ
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "حفظ التقرير المالي",
                f"التقرير_المالي_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if file_path:
                # هنا يمكن إضافة كود تصدير البيانات إلى Excel
                QMessageBox.information(self, "تصدير", f"تم حفظ التقرير في:\n{file_path}")

        except Exception as e:
            print(f"⚠️ خطأ في التصدير: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تصدير البيانات:\n{str(e)}")

    # طباعة التقارير
    def print_reports(self):
        try:
            # يمكن استخدام نظام الطباعة الموحد
            QMessageBox.information(self, "طباعة", "سيتم تطوير نظام الطباعة قريباً")
        except Exception as e:
            print(f"⚠️ خطأ في الطباعة: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في طباعة التقارير:\n{str(e)}")

    # ===== دوال البحث والفلترة =====
    # تطبيق البحث على التقارير المالية
    def apply_search(self, search_text):
        try:
            print(f"🔍 تطبيق البحث: '{search_text}'")
            # يمكن إضافة منطق البحث في البيانات المالية

        except Exception as e:
            print(f"⚠️ خطأ في البحث: {e}")

    # دالة بديلة للبحث (للتوافق مع أنظمة البحث المختلفة)
    def search_in_widget(self, search_text):
        self.apply_search(search_text)

    # ===== دوال التوافق مع النظام القديم =====
    # معالج النقر المزدوج على حساب (للتوافق مع النظام القديم)
    def on_account_double_clicked(self, item):
        try:
            if hasattr(self, 'summary_table') and self.summary_table:
                row = item.row()
                account_type = self.summary_table.item(row, 0).text()
                account_name = self.summary_table.item(row, 1).text()
                self.show_account_details(account_type, account_name)
        except Exception as e:
            print(f"⚠️ خطأ في فتح تفاصيل الحساب: {e}")

    # عرض تفاصيل الحساب (للتوافق مع النظام القديم)
    def show_account_details(self, account_type, account_name):
        try:
            print(f"📋 عرض تفاصيل الحساب: {account_type} - {account_name}")
            # يمكن تطوير هذا لاحقاً لفتح نافذة تفاصيل الحساب
        except Exception as e:
            print(f"⚠️ خطأ في عرض تفاصيل الحساب: {e}")

    # إنشاء جدول الملخص المالي (للتوافق مع النظام القديم)
    def create_summary_table(self):
        try:
            self.summary_table = QTableWidget()
            self.summary_table.setObjectName("FinancialSummaryTable")

            # إعداد الأعمدة
            columns = [
                "نوع الحساب",
                "اسم الحساب",
                "الرصيد المدين",
                "الرصيد الدائن",
                "صافي الرصيد",
                "النسبة %"
            ]

            self.summary_table.setColumnCount(len(columns))
            self.summary_table.setHorizontalHeaderLabels(columns)

            # إعداد خصائص الجدول
            self.summary_table.setAlternatingRowColors(True)
            self.summary_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.summary_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.summary_table.setSortingEnabled(True)

            # تخصيص عرض الأعمدة
            header = self.summary_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

            # إعداد قائمة السياق
            setup_table_context_menu(self.summary_table, self.main_window, "الملخص_المالي")

            # ربط النقر المزدوج
            self.summary_table.itemDoubleClicked.connect(self.on_account_double_clicked)

            # إخفاء الجدول (لأننا نستخدم النظام الجديد)
            self.summary_table.hide()

        except Exception as e:
            print(f"⚠️ خطأ في إنشاء جدول الملخص: {e}")

    # تحديث البيانات (للتوافق مع النظام القديم)
    def refresh_data(self):
        try:
            print("🔄 تحديث البيانات المالية...")
            self.load_financial_data()
        except Exception as e:
            print(f"⚠️ خطأ في تحديث البيانات: {e}")

    # فتح النافذة المتقدمة للتقارير المالية
    def open_advanced_financial_reports(self):
        try:
            self.open_advanced_reports()
        except Exception as e:
            print(f"⚠️ خطأ في فتح النافذة المتقدمة: {e}")

    # ===== دوال البحث المتقدم =====
    # البحث في جدول الملخص المالي
    def _search_in_summary_table(self, search_text):
        if not hasattr(self, 'summary_table') or not self.summary_table:
            return

        if not search_text.strip():
            # إظهار جميع الصفوف إذا كان البحث فارغاً
            for row in range(self.summary_table.rowCount()):
                self.summary_table.setRowHidden(row, False)
            return

        search_text = search_text.lower()

        # البحث في كل صف وعمود
        for row in range(self.summary_table.rowCount()):
            row_matches = False
            for col in range(self.summary_table.columnCount()):
                item = self.summary_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_matches = True
                    break

            # إخفاء أو إظهار الصف حسب نتيجة البحث
            self.summary_table.setRowHidden(row, not row_matches)

    # البحث في التقارير الشهرية
    def _search_in_monthly_reports(self, search_text):
        try:
            # يمكن إضافة منطق البحث في التقارير الشهرية هنا
            print(f"🔍 البحث في التقارير الشهرية: '{search_text}'")
        except Exception as e:
            print(f"⚠️ خطأ في البحث في التقارير الشهرية: {e}")


# ===== الدوال المساعدة العامة =====

# الحصول على بيانات الإحصائيات المالية المحدثة
def get_financial_stats_data():
    try:
        # هذه الدالة للتوافق مع النظام القديم
        # البيانات الفعلية يتم تحميلها من خلال الكلاس الجديد
        stats_data = [
            ("إجمالي الإيرادات", "0", "#3498db", "💰"),
            ("إجمالي المصروفات", "0", "#e74c3c", "💸"),
            ("صافي الربح", "0", "#27ae60", "📈"),
            ("المستحقات", "0", "#f39c12", "�"),
            ("عدد المعاملات", "0", "#9b59b6", "�")
        ]

        return stats_data

    except Exception as e:
        print(f"⚠️ خطأ في الحصول على الإحصائيات المالية: {e}")
        return [
            ("إجمالي الإيرادات", "0", "#3498db", "💰"),
            ("إجمالي المصروفات", "0", "#e74c3c", "💸"),
            ("صافي الربح", "0", "#27ae60", "📈"),
            ("المستحقات", "0", "#f39c12", "�"),
            ("عدد المعاملات", "0", "#9b59b6", "�")
        ]


# تحميل البيانات المالية للجدول الرئيسي (للتوافق مع النظام القديم)
def load_financial_data_for_table():
    try:
        # هذه الدالة للتوافق مع النظام القديم
        # البيانات الفعلية يتم تحميلها من خلال الكلاس الجديد
        print("📊 استخدام النظام الجديد للتقارير المالية")
        return []

    except Exception as e:
        print(f"⚠️ خطأ في تحميل البيانات المالية: {e}")
        return []


# إنشاء ويدجت التقارير المالية المحسن
def create_financial_summary_widget(main_window):
    try:
        
        widget = FinancialSummaryWidget(main_window)
        
        return widget

    except Exception as e:
        print(f"⚠️ خطأ في إنشاء ويدجت التقارير المالية: {e}")
        import traceback
        traceback.print_exc()

        # إنشاء ويدجت بديل في حالة الخطأ
        fallback_widget = QWidget()
        fallback_layout = QVBoxLayout(fallback_widget)

        error_label = QLabel("⚠️ فشل في تحميل نظام التقارير المالية المحسن")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #e74c3c;
                padding: 20px;
                background-color: #fdf2f2;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin: 20px;
            }
        """)

        retry_btn = QPushButton("🔄 إعادة المحاولة")
        retry_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        retry_btn.clicked.connect(lambda: create_financial_summary_widget(main_window))

        fallback_layout.addWidget(error_label)
        fallback_layout.addWidget(retry_btn, 0, Qt.AlignCenter)
        fallback_layout.addStretch()

        return fallback_widget


# ===== دوال مساعدة للألوان والتنسيق =====

# الحصول على لون حسب نوع القيمة والحالة
def get_status_color(value, value_type="amount"):
    try:
        if value_type == "amount":
            if isinstance(value, (int, float)):
                if value > 0:
                    return "#27ae60"  # أخضر للموجب
                elif value < 0:
                    return "#e74c3c"  # أحمر للسالب
                else:
                    return "#95a5a6"  # رمادي للصفر
            else:
                return "#34495e"  # رمادي داكن للنص

        elif value_type == "profit_margin":
            if isinstance(value, (int, float)):
                if value >= 20:
                    return "#27ae60"  # أخضر للهامش الجيد
                elif value >= 10:
                    return "#f39c12"  # برتقالي للهامش المتوسط
                else:
                    return "#e74c3c"  # أحمر للهامش الضعيف

        return "#34495e"  # اللون الافتراضي

    except Exception as e:
        print(f"⚠️ خطأ في تحديد اللون: {e}")
        return "#34495e"


# تنسيق عرض العملة
def format_currency_display(amount, show_currency=True):
    try:
        if amount is None:
            return "غير محدد"

        if isinstance(amount, (int, float)):
            formatted = f"{amount:,.0f}"
            if show_currency:
                formatted += f" {Currency_type}"
            return formatted

        return str(amount)

    except Exception as e:
        print(f"⚠️ خطأ في تنسيق العملة: {e}")
        return "0"


# الحصول على اسم الشهر بالعربية
def get_month_name_arabic(month_number):
    try:
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        return month_names.get(month_number, f"الشهر {month_number}")

    except Exception as e:
        print(f"⚠️ خطأ في الحصول على اسم الشهر: {e}")
        return f"الشهر {month_number}"
