#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف الستايلات الموحد لجميع نوافذ الإدارة
يحتوي على جميع التنسيقات المشتركة للنوافذ والتابات والأزرار والجداول
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

# ==================== الألوان الأساسية ====================
PRIMARY_COLOR = "#007bff"
SUCCESS_COLOR = "#28a745"
DANGER_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"
INFO_COLOR = "#17a2b8"
SECONDARY_COLOR = "#6c757d"
DARK_COLOR = "#343a40"
LIGHT_COLOR = "#f8f9fa"

# ألوان إضافية
PURPLE_COLOR = "#6f42c1"
ORANGE_COLOR = "#fd7e14"
TEAL_COLOR = "#20c997"
PINK_COLOR = "#e83e8c"
INDIGO_COLOR = "#6610f2"
CYAN_COLOR = "#17a2b8"

# ==================== الخطوط ====================
MAIN_FONT_FAMILY = "Janna LT"
SECONDARY_FONT_FAMILY = "Arial"
DEFAULT_FONT_SIZE = 11
HEADER_FONT_SIZE = 14
TITLE_FONT_SIZE = 16

# ==================== المسافات والأبعاد ====================
DEFAULT_SPACING = 10
DEFAULT_MARGIN = 15
BUTTON_HEIGHT = 35
INPUT_HEIGHT = 35
TAB_HEIGHT = 40

# ==================== الستايلات الأساسية ====================

# ستايل النافذة الرئيسية للإدارة
def get_management_window_style():
    return f"""
        QDialog, QMainWindow {{
            background-color: {LIGHT_COLOR};
            font-family: '{MAIN_FONT_FAMILY}', '{SECONDARY_FONT_FAMILY}';
            font-size: {DEFAULT_FONT_SIZE}px;
        }}
        
        QDialog[objectName*="ManagementWindow"] {{
            background-color: {LIGHT_COLOR};
            border: none;
        }}
    """

# ستايل التابات الرئيسية
def get_tab_widget_style():
    return f"""
        /* التاب الرئيسي */
        QTabWidget::pane {{
            border: 1px solid #dee2e6;
            background-color: white;
            border-radius: 8px;
            margin-top: -1px;
        }}
        
        QTabWidget::tab-bar {{
            alignment: center;
        }}
        
        /* التابات غير المحددة */
        QTabBar::tab {{
            background-color: #e9ecef;
            color: #495057;
            padding: 8px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            font-size: {DEFAULT_FONT_SIZE}px;
            min-height: {TAB_HEIGHT}px;
        }}
        
        /* التاب المحدد */
        QTabBar::tab:selected {{
            background-color: white;
            color: {PRIMARY_COLOR};
            border-bottom: 3px solid {PRIMARY_COLOR};
        }}
        
        /* التاب عند المرور بالماوس */
        QTabBar::tab:hover {{
            background-color: #f8f9fa;
            color: {PRIMARY_COLOR};
        }}
        
        /* التاب الأول والأخير */
        QTabBar::tab:first {{
            margin-left: 5px;
        }}
        
        QTabBar::tab:last {{
            margin-right: 5px;
        }}
    """

# ستايلات الأزرار
def get_button_styles():
    return f"""
        /* الزر الأساسي */
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: {DEFAULT_FONT_SIZE}px;
            min-height: {BUTTON_HEIGHT}px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: #0056b3;
        }}
        
        QPushButton:pressed {{
            background-color: #004085;
        }}
        
        QPushButton:disabled {{
            background-color: #6c757d;
            color: #dee2e6;
        }}
        
        /* أزرار الإضافة */
        QPushButton[objectName*="add"] {{
            background-color: {SUCCESS_COLOR};
        }}
        
        QPushButton[objectName*="add"]:hover {{
            background-color: #218838;
        }}
        
        /* أزرار التعديل */
        QPushButton[objectName*="edit"] {{
            background-color: {WARNING_COLOR};
            color: #212529;
        }}
        
        QPushButton[objectName*="edit"]:hover {{
            background-color: #e0a800;
        }}
        
        /* أزرار الحذف */
        QPushButton[objectName*="delete"] {{
            background-color: {DANGER_COLOR};
        }}
        
        QPushButton[objectName*="delete"]:hover {{
            background-color: #c82333;
        }}
        
        /* أزرار المعلومات */
        QPushButton[objectName*="info"], QPushButton[objectName*="view"] {{
            background-color: {INFO_COLOR};
        }}
        
        QPushButton[objectName*="info"]:hover, QPushButton[objectName*="view"]:hover {{
            background-color: #138496;
        }}
        
        /* أزرار الطباعة */
        QPushButton[objectName*="print"] {{
            background-color: {SECONDARY_COLOR};
        }}
        
        QPushButton[objectName*="print"]:hover {{
            background-color: #5a6268;
        }}
        
        /* أزرار التصدير */
        QPushButton[objectName*="export"] {{
            background-color: {PURPLE_COLOR};
        }}
        
        QPushButton[objectName*="export"]:hover {{
            background-color: #5a32a3;
        }}
        
        /* الأزرار الصغيرة في الجداول */
        QPushButton[objectName*="table_button"] {{
            padding: 4px 8px;
            min-height: 25px;
            min-width: 60px;
            font-size: 10px;
        }}
    """

# ستايلات حقول الإدخال
def get_input_styles():
    return f"""
        /* حقول الإدخال النصية */
        QLineEdit {{
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background-color: white;
            font-size: {DEFAULT_FONT_SIZE}px;
            min-height: {INPUT_HEIGHT}px;
        }}
        
        QLineEdit:focus {{
            border-color: {PRIMARY_COLOR};
            outline: none;
        }}
        
        QLineEdit:disabled {{
            background-color: #e9ecef;
            color: #6c757d;
        }}
        
        QLineEdit[readOnly="true"] {{
            background-color: #f8f9fa;
        }}
        
        /* حقول البحث */
        QLineEdit[objectName*="search"] {{
            padding-left: 35px;
           /* background-image: url('icons/search.png');*/
            background-repeat: no-repeat;
            background-position: left 10px center;
        }}
        
        /* القوائم المنسدلة */
        QComboBox {{
            padding: 6px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background-color: white;
            font-size: {DEFAULT_FONT_SIZE}px;
            min-height: {INPUT_HEIGHT}px;
        }}
        
        QComboBox:focus {{
            border-color: {PRIMARY_COLOR};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 25px;
        }}
        
        QComboBox::down-arrow {{
            image: url('icons/down-arrow.png');
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            border: 1px solid #ced4da;
            background-color: white;
            selection-background-color: {PRIMARY_COLOR};
            selection-color: white;
        }}
        
        /* حقول التاريخ */
        QDateEdit {{
            padding: 6px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background-color: white;
            font-size: {DEFAULT_FONT_SIZE}px;
            min-height: {INPUT_HEIGHT}px;
        }}
        
        QDateEdit:focus {{
            border-color: {PRIMARY_COLOR};
        }}
        
        QDateEdit::drop-down {{
            border: none;
            width: 25px;
        }}
        
        /* حقول النص الكبيرة */
        QTextEdit {{
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background-color: white;
            font-size: {DEFAULT_FONT_SIZE}px;
        }}
        
        QTextEdit:focus {{
            border-color: {PRIMARY_COLOR};
        }}
        
        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            padding: 6px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background-color: white;
            font-size: {DEFAULT_FONT_SIZE}px;
            min-height: {INPUT_HEIGHT}px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {PRIMARY_COLOR};
        }}
    """

# ستايلات الجداول
def get_table_styles():
    return f"""
        /* الجدول الرئيسي */
        QTableWidget {{
            gridline-color: #e9ecef;
            background-color: white;
            alternate-background-color: #f8f9fa;
            selection-background-color: {PRIMARY_COLOR};
            selection-color: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: {DEFAULT_FONT_SIZE}px;
        }}
        
        /* رأس الجدول */
        QHeaderView::section {{
            background-color: #e9ecef;
            color: #495057;
            padding: 10px;
            border: none;
            font-weight: bold;
            font-size: {DEFAULT_FONT_SIZE}px;
            text-align: center;
        }}
        
        QHeaderView::section:hover {{
            background-color: #dee2e6;
        }}
        
        /* الخلايا */
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        QTableWidget::item:selected {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        
        QTableWidget::item:hover {{
            background-color: #e3f2fd;
        }}
        
        /* الصفوف الزوجية */
        QTableWidget[alternatingRowColors="true"] {{
            alternate-background-color: #f8f9fa;
        }}
        
        /* شريط التمرير */
        QTableWidget QScrollBar:vertical {{
            border: none;
            background-color: #f8f9fa;
            width: 12px;
            border-radius: 6px;
        }}
        
        QTableWidget QScrollBar::handle:vertical {{
            background-color: #ced4da;
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QTableWidget QScrollBar::handle:vertical:hover {{
            background-color: #adb5bd;
        }}
    """

# ستايلات GroupBox
def get_groupbox_styles():
    return f"""
        /* GroupBox الأساسي */
        QGroupBox {{
            font-size: {HEADER_FONT_SIZE}px;
            font-weight: bold;
            color: #495057;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin: 10px 5px;
            padding-top: 20px;
            background-color: white;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 15px;
            background-color: white;
            color: {PRIMARY_COLOR};
        }}
        
        /* GroupBox للمعلومات */
        QGroupBox[objectName*="info_container"] {{
            background-color: #f8f9fa;
            border-color: #dee2e6;
        }}
        
        /* GroupBox للإحصائيات */
        QGroupBox[objectName*="stats_container"] {{
            background-color: transparent;
            border: none;
            padding: 5px;
        }}
        
        /* GroupBox للفلاتر */
        QGroupBox[objectName*="filter_container"] {{
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            padding: 10px;
        }}
    """

# ستايلات التسميات
def get_label_styles():
    return f"""
        /* التسمية الأساسية */
        QLabel {{
            color: #495057;
            font-size: {DEFAULT_FONT_SIZE}px;
        }}
        
        /* تسميات العناوين */
        QLabel[objectName*="title"] {{
            font-size: {TITLE_FONT_SIZE}px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 10px 0;
        }}
        
        /* تسميات المعلومات */
        QLabel[objectName*="info_label"] {{
            background-color: #f8f9fa;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}
        
        /* تسميات القيم */
        QLabel[objectName*="value_label"] {{
            font-weight: bold;
            color: #212529;
        }}
        
        /* تسميات الحالة */
        QLabel[objectName*="status_label"] {{
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        /* تسميات الإحصائيات */
        QLabel[objectName*="stat_value"] {{
            font-size: 24px;
            font-weight: bold;
            color: #212529;
        }}
        
        QLabel[objectName*="stat_title"] {{
            font-size: 12px;
            color: #6c757d;
            font-weight: normal;
        }}
    """

# ستايلات البطاقات
def get_card_styles():
    return f"""
        /* البطاقة الأساسية */
        QFrame[objectName*="card"] {{
            background-color: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
        }}
        
        QFrame[objectName*="card"]:hover {{
            border-color: #dee2e6;
            
        }}
        
        /* بطاقات الإحصائيات */
        QFrame[objectName*="stat_card"] {{
            background-color: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 5px;
            min-height: 100px;
        }}
        
        QFrame[objectName*="stat_card"]:hover {{
            border-color: #007bff;
            
        }}
        
        /* بطاقات المعلومات */
        QFrame[objectName*="info_card"] {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 12px;
            margin: 5px;
        }}
        
        /* بطاقات التحذير */
        QFrame[objectName*="warning_card"] {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 12px;
            margin: 5px;
        }}
        
        /* بطاقات النجاح */
        QFrame[objectName*="success_card"] {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            padding: 12px;
            margin: 5px;
        }}
        
        /* بطاقات الخطأ */
        QFrame[objectName*="error_card"] {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            padding: 12px;
            margin: 5px;
        }}
    """

# ستايلات نوافذ الحوار
def get_dialog_styles():
    return f"""
        /* نافذة الحوار الأساسية */
        QDialog {{
            background-color: white;
            font-family: '{MAIN_FONT_FAMILY}';
        }}
        
        /* عنوان نافذة الحوار */
        QDialog QLabel[objectName="dialog_title"] {{
            font-size: 18px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 15px;
            background-color: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        /* محتوى نافذة الحوار */
        QDialog QWidget[objectName="dialog_content"] {{
            background-color: white;
            padding: 20px;
        }}
        
        /* أزرار نافذة الحوار */
        QDialog QPushButton {{
            min-width: 100px;
            margin: 5px;
        }}
        
        QDialogButtonBox {{
            padding: 10px;
            background-color: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}
    """

# ستايلات أشرطة التمرير
def get_scrollbar_styles():
    return f"""
        /* شريط التمرير العمودي */
        QScrollBar:vertical {{
            border: none;
            background-color: #f8f9fa;
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #ced4da;
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #adb5bd;
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background-color: #6c757d;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
            subcontrol-position: none;
            subcontrol-origin: none;
        }}
        
        /* شريط التمرير الأفقي */
        QScrollBar:horizontal {{
            border: none;
            background-color: #f8f9fa;
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: #ced4da;
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: #adb5bd;
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background-color: #6c757d;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
            subcontrol-position: none;
            subcontrol-origin: none;
        }}
    """

# ستايلات الفواصل
def get_splitter_styles():
    return f"""
        QSplitter::handle {{
            background-color: #e9ecef;
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {PRIMARY_COLOR};
        }}
    """

# ستايلات القوائم
def get_menu_styles():
    return f"""
        /* شريط القوائم */
        QMenuBar {{
            background-color: white;
            border-bottom: 1px solid #e9ecef;
            padding: 5px;
        }}
        
        QMenuBar::item {{
            padding: 8px 15px;
            background-color: transparent;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: #f8f9fa;
        }}
        
        QMenuBar::item:pressed {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        
        /* القوائم المنسدلة */
        QMenu {{
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 5px;
        }}
        
        QMenu::item {{
            padding: 8px 25px;
            border-radius: 4px;
            margin: 2px 5px;
        }}
        
        QMenu::item:selected {{
            background-color: #e3f2fd;
            color: {PRIMARY_COLOR};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: #e9ecef;
            margin: 5px 10px;
        }}
        
        QMenu::icon {{
            margin-left: 10px;
        }}
    """

# ستايلات أشرطة التقدم
def get_progressbar_styles():
    return f"""
        QProgressBar {{
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background-color: #f8f9fa;
            text-align: center;
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background-color: {PRIMARY_COLOR};
            border-radius: 5px;
        }}
        
        QProgressBar[objectName*="success"] ::chunk {{
            background-color: {SUCCESS_COLOR};
        }}
        
        QProgressBar[objectName*="danger"] ::chunk {{
            background-color: {DANGER_COLOR};
        }}
        
        QProgressBar[objectName*="warning"] ::chunk {{
            background-color: {WARNING_COLOR};
        }}
    """

# ستايلات صناديق الاختيار وأزرار الراديو
def get_checkbox_radio_styles():
    return f"""
        /* صناديق الاختيار */
        QCheckBox {{
            spacing: 8px;
            font-size: {DEFAULT_FONT_SIZE}px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid #ced4da;
            border-radius: 4px;
            background-color: white;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {PRIMARY_COLOR};
            border-color: {PRIMARY_COLOR};
            image: url('icons/check-white.png');
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {PRIMARY_COLOR};
        }}
        
        /* أزرار الراديو */
        QRadioButton {{
            spacing: 8px;
            font-size: {DEFAULT_FONT_SIZE}px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid #ced4da;
            border-radius: 9px;
            background-color: white;
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {PRIMARY_COLOR};
            border-color: {PRIMARY_COLOR};
        }}
        
        QRadioButton::indicator:checked::after {{
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 4px;
            background-color: white;
            margin: 5px;
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {PRIMARY_COLOR};
        }}
    """

# دمج جميع الستايلات في ستايل واحد شامل
def get_complete_management_style():
    return "\n".join([
        get_management_window_style(),
        get_tab_widget_style(),
        get_button_styles(),
        get_input_styles(),
        get_table_styles(),
        get_groupbox_styles(),
        get_label_styles(),
        get_card_styles(),
        get_dialog_styles(),
        get_scrollbar_styles(),
        get_splitter_styles(),
        get_menu_styles(),
        get_progressbar_styles(),
        get_checkbox_radio_styles()
    ])

# تطبيق الستايل الموحد على أي ويدجت
def apply_management_style(widget):
    widget.setStyleSheet(get_complete_management_style())
    
    # تطبيق RTL إذا لزم الأمر
    widget.setLayoutDirection(Qt.RightToLeft)
    
    # تطبيق الخط الافتراضي
    from PySide6.QtGui import QFont
    font = QFont(MAIN_FONT_FAMILY, DEFAULT_FONT_SIZE)
    widget.setFont(font)

# الحصول على لون الحالة
def get_status_color(status):
    status_colors = {
        # حالات عامة
        "نشط": SUCCESS_COLOR,
        "غير نشط": SECONDARY_COLOR,
        "معلق": WARNING_COLOR,
        "مكتمل": SUCCESS_COLOR,
        "ملغي": DANGER_COLOR,
        "متأخر": DANGER_COLOR,
        
        # حالات المشاريع
        "قيد الإنجاز": INFO_COLOR,
        "منتهي": SUCCESS_COLOR,
        "تم التسليم": SUCCESS_COLOR,
        "متوقف": WARNING_COLOR,
        "تأكيد التسليم": PURPLE_COLOR,
        
        # حالات الدفع
        "مدفوع": SUCCESS_COLOR,
        "غير مدفوع": DANGER_COLOR,
        "دفع جزئي": WARNING_COLOR,
        
        # حالات المهام
        "لم يبدأ": SECONDARY_COLOR,
        "قيد التنفيذ": INFO_COLOR,
        "مكتملة": SUCCESS_COLOR,
        "متوقفة": WARNING_COLOR,
        
        # حالات الحضور
        "حاضر": SUCCESS_COLOR,
        "متأخر": WARNING_COLOR,
        "غائب": DANGER_COLOR,
        "إجازة": INFO_COLOR,
    }
    
    return status_colors.get(status, SECONDARY_COLOR)

# إنشاء تسمية ملونة
def create_colored_label(text, color):
    from PySide6.QtWidgets import QLabel
    label = QLabel(text)
    label.setStyleSheet(f"""
        QLabel {{
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
        }}
    """)
    return label

# إنشاء بطاقة إحصائية
def create_stat_card(title, value, color, icon=None):
    from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
    from PySide6.QtCore import Qt
    
    card = QFrame()
    card.setObjectName("stat_card")
    card.setProperty("card_color", color)
    
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)
    
    # العنوان
    title_label = QLabel(title)
    title_label.setObjectName("stat_title")
    title_label.setAlignment(Qt.AlignCenter)
    
    # القيمة
    value_label = QLabel(str(value))
    value_label.setObjectName("stat_value")
    value_label.setAlignment(Qt.AlignCenter)
    
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    
    # تطبيق ستايل خاص بالبطاقة
    card.setStyleSheet(f"""
        QFrame#stat_card {{
            background-color: white;
            border: 2px solid {color};
            border-radius: 8px;
        }}
        QFrame#stat_card:hover {{
            background-color: {color}10;
            
        }}
        QLabel#stat_title {{
            color: #6c757d;
            font-size: 12px;
        }}
        QLabel#stat_value {{
            color: {color};
            font-size: 24px;
            font-weight: bold;
        }}
    """)
    
    return card

# تعديل سطوع اللون
def adjust_color_brightness(hex_color, amount):
    color = QColor(hex_color)
    h, s, v, a = color.getHsv()
    v = max(0, min(255, v + amount))
    color.setHsv(h, s, v, a)
    return color.name()

# جعل اللون أغمق
def darken_color(hex_color, amount=30):
    return adjust_color_brightness(hex_color, -amount)

# جعل اللون أفتح
def lighten_color(hex_color, amount=30):
    return adjust_color_brightness(hex_color, amount)

# ==================== دوال مساعدة للجداول ====================

# إعداد ستايل الجدول
def setup_table_style(table):
    from PySide6.QtWidgets import QHeaderView, QAbstractItemView
    from PySide6.QtCore import Qt
    
    # تطبيق الستايل
    table.setStyleSheet(get_table_styles())
    
    # إعدادات الجدول
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setDefaultSectionSize(40)
    table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # إخفاء رقم الصف
    table.verticalHeader().hide()
    
    # تنسيق رأس الجدول
    header = table.horizontalHeader()
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

# إضافة أزرار الإجراءات للجدول
def add_action_buttons_to_table(table, row, edit_callback=None, delete_callback=None, view_callback=None):
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
    from PySide6.QtCore import Qt
    import qtawesome as qta
    
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)
    layout.setAlignment(Qt.AlignCenter)
    
    # زر العرض
    if view_callback:
        view_btn = QPushButton()
        view_btn.setIcon(qta.icon('fa5s.eye', color='#17a2b8'))
        view_btn.setObjectName("table_button_view")
        view_btn.setToolTip("عرض")
        view_btn.clicked.connect(lambda: view_callback(row))
        layout.addWidget(view_btn)
    
    # زر التعديل
    if edit_callback:
        edit_btn = QPushButton()
        edit_btn.setIcon(qta.icon('fa5s.edit', color='#ffc107'))
        edit_btn.setObjectName("table_button_edit")
        edit_btn.setToolTip("تعديل")
        edit_btn.clicked.connect(lambda: edit_callback(row))
        layout.addWidget(edit_btn)
    
    # زر الحذف
    if delete_callback:
        delete_btn = QPushButton()
        delete_btn.setIcon(qta.icon('fa5s.trash', color='#dc3545'))
        delete_btn.setObjectName("table_button_delete")
        delete_btn.setToolTip("حذف")
        delete_btn.clicked.connect(lambda: delete_callback(row))
        layout.addWidget(delete_btn)
    
    return widget

# ==================== دوال التنسيق ====================

# تنسيق المبلغ المالي
def format_currency(amount, currency="ر.س"):
    if amount is None:
        return f"0.00 {currency}"
    return f"{amount:,.2f} {currency}"

# تنسيق التاريخ
def format_date(date_value):
    if not date_value:
        return ""
    
    if isinstance(date_value, str):
        return date_value
    
    try:
        return date_value.strftime("%Y-%m-%d")
    except:
        return str(date_value)

# تنسيق النسبة المئوية
def format_percentage(value):
    if value is None:
        return "0%"
    return f"{value:.1f}%"

# ==================== دوال إنشاء العناصر الموحدة ====================

# إنشاء قسم الفلاتر الموحد
def create_filter_section(filters_dict):
    from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
    import qtawesome as qta
    
    filter_group = QGroupBox("البحث والفلترة")
    filter_group.setObjectName("filter_container")
    filter_layout = QHBoxLayout(filter_group)
    
    # حقل البحث
    if "search" in filters_dict:
        search_label = QLabel("بحث:")
        search_input = QLineEdit()
        search_input.setObjectName("search_input")
        search_input.setPlaceholderText(filters_dict["search"])
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(search_input)
    
    # الفلاتر المنسدلة
    for filter_name, filter_options in filters_dict.items():
        if filter_name != "search" and isinstance(filter_options, list):
            filter_label = QLabel(f"{filter_name}:")
            filter_combo = QComboBox()
            filter_combo.setObjectName(f"filter_{filter_name}")
            filter_combo.addItems(filter_options)
            filter_layout.addWidget(filter_label)
            filter_layout.addWidget(filter_combo)
    
    # زر إعادة تعيين
    reset_btn = QPushButton("إعادة تعيين")
    reset_btn.setIcon(qta.icon('fa5s.redo', color='white'))
    reset_btn.setObjectName("reset_filters_button")
    filter_layout.addWidget(reset_btn)
    
    filter_layout.addStretch()
    
    return filter_group

# إنشاء قسم أزرار الإجراءات الموحد
def create_action_buttons_section(buttons_config):
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
    import qtawesome as qta
    
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)
    
    for btn_config in buttons_config:
        btn = QPushButton(btn_config["text"])
        btn.setObjectName(btn_config["object_name"])
        
        if "icon" in btn_config:
            btn.setIcon(qta.icon(btn_config["icon"], color='white'))
        
        if "callback" in btn_config:
            btn.clicked.connect(btn_config["callback"])
        
        if "style_class" in btn_config:
            btn.setProperty("class", btn_config["style_class"])
        
        layout.addWidget(btn)
    
    layout.addStretch()
    
    return widget

# إنشاء حاوية معلومات موحدة
def create_info_container(title, info_dict):
    from PySide6.QtWidgets import QGroupBox, QFormLayout, QLabel
    
    container = QGroupBox(title)
    container.setObjectName("info_container")
    layout = QFormLayout(container)
    layout.setSpacing(10)
    
    for label_text, value in info_dict.items():
        label = QLabel(f"{label_text}:")
        label.setObjectName("info_label_title")
        
        value_label = QLabel(str(value) if value else "غير محدد")
        value_label.setObjectName("info_label_value")
        
        layout.addRow(label, value_label)
    
    return container

# ==================== تطبيق الستايلات على النوافذ الموجودة ====================

# تطبيق الستايل على نافذة إدارة المشروع
def apply_to_project_management(window):
    apply_management_style(window)
    window.setObjectName("ProjectManagementWindow")

# تطبيق الستايل على نافذة إدارة الموظفين
def apply_to_employee_management(window):
    apply_management_style(window)
    
    # إضافة ستايلات خاصة بإدارة الموظفين
    employee_styles = get_employee_specific_styles()
    current_style = window.styleSheet()
    window.setStyleSheet(current_style + employee_styles)
    window.setObjectName("EmployeeManagementWindow")

# تطبيق الستايل على نافذة إدارة التدريب
def apply_to_training_management(window):
    apply_management_style(window)
    window.setObjectName("TrainingManagementWindow")

# تطبيق الستايل على نافذة إدارة العملاء
def apply_to_client_management(window):
    apply_management_style(window)
    window.setObjectName("ClientManagementWindow")

# تطبيق الستايل على نافذة إدارة الموردين
def apply_to_supplier_management(window):
    apply_management_style(window)
    
    # إضافة ستايلات خاصة بإدارة الموردين
    suppliers_styles = get_suppliers_specific_styles()
    current_style = window.styleSheet()
    window.setStyleSheet(current_style + suppliers_styles)
    window.setObjectName("SupplierManagementWindow")

# تطبيق الستايل على نافذة إدارة الديون
def apply_to_debt_management(window):
    apply_management_style(window)
    
    # إضافة ستايلات خاصة بإدارة الديون
    debt_styles = get_debt_specific_styles()
    current_style = window.styleSheet()
    window.setStyleSheet(current_style + debt_styles)
    window.setObjectName("DebtManagementWindow")

# ==================== الستايلات الخاصة بكل نافذة ====================

# ستايلات خاصة بنافذة إدارة المشاريع
def get_project_specific_styles():
    return """
        /* ستايلات خاصة بإدارة المشاريع */
        QFrame[objectName="phase_card"] {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        
        QLabel[objectName="phase_status_completed"] {
            background-color: #4caf50;
            color: white;
        }
        
        QLabel[objectName="phase_status_pending"] {
            background-color: #ff9800;
            color: white;
        }
    """

# ستايلات خاصة بنافذة إدارة الموظفين
def get_employee_specific_styles():
    return f"""
        /* ستايلات خاصة بإدارة الموظفين */
        QGroupBox[objectName="info_group"] {{
            font-weight: bold;
            font-size: 14px;
            color: #2c3e50;
            border: 2px solid {PRIMARY_COLOR};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #f8f9fa;
        }}
        
        QGroupBox[objectName="info_group"]::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #2c3e50;
            font-weight: bold;
        }}
        
        /* أزرار الحضور والانصراف */
        QPushButton[objectName*="checkin"] {{
            background-color: {SUCCESS_COLOR};
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            min-width: 120px;
        }}
        
        QPushButton[objectName*="checkin"]:hover {{
            background-color: #218838;
        }}
        
        QPushButton[objectName*="checkin"]:disabled {{
            background-color: #6c757d;
            color: #adb5bd;
        }}
        
        QPushButton[objectName*="checkout"] {{
            background-color: {DANGER_COLOR};
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            min-width: 120px;
        }}
        
        QPushButton[objectName*="checkout"]:hover {{
            background-color: #c82333;
        }}
        
        QPushButton[objectName*="checkout"]:disabled {{
            background-color: #6c757d;
            color: #adb5bd;
        }}
        
        /* أزرار الإجراءات */
        QPushButton[objectName="success_button"] {{
            background-color: {SUCCESS_COLOR};
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
        }}
        
        QPushButton[objectName="success_button"]:hover {{
            background-color: #218838;
        }}
        
        QPushButton[objectName="info_button"] {{
            background-color: {PURPLE_COLOR};
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
        }}
        
        QPushButton[objectName="info_button"]:hover {{
            background-color: #5a32a3;
        }}
        
        /* تسميات القيم */
        QLabel[objectName="value_label"] {{
            color: #34495e;
            padding: 8px;
            background-color: #ecf0f1;
            border-radius: 4px;
            font-size: 14px;
            min-height: 25px;
            font-weight: bold;
        }}
        
        QLabel[objectName="title-label"] {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 14px;
        }}
        
        /* إطارات الأنشطة */
        QFrame[objectName*="activities"] {{
            background-color: #f8f9fa;
            border: 2px solid {INFO_COLOR};
            border-radius: 10px;
            padding: 15px;
        }}
        
        QFrame[objectName*="buttons"] {{
            background-color: #e9ecef;
            border-radius: 8px;
            padding: 10px;
        }}
        
        QFrame[objectName*="recent"] {{
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 10px;
        }}
        
        /* تسميات الأنشطة */
        QLabel[objectName*="activity"] {{
            font-size: 13px;
            font-weight: bold;
        }}
        
        QLabel[objectName*="attendance_info"] {{
            color: #0c5460;
        }}
        
        QLabel[objectName*="financial_info"] {{
            color: #155724;
        }}
        
        QLabel[objectName*="task_info"] {{
            color: #856404;
        }}
        
        /* حاويات الإحصائيات */
        QFrame[objectName*="stat_widget"] {{
            border-radius: 8px;
            padding: 10px;
        }}
        
        QLabel[objectName="stat-title"] {{
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        
        QLabel[objectName="stat-value"] {{
            font-size: 14px;
            font-weight: bold;
            color: white;
        }}
        
        /* حقول البحث والفلاتر */
        QLineEdit[objectName*="search"] {{
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        QComboBox[objectName*="filter"] {{
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 12px;
            min-width: 120px;
        }}
        
        QLabel[objectName*="filter"] {{
            font-weight: bold;
            color: #495057;
        }}
        
        /* إطارات الفلاتر */
        QFrame[objectName*="filters"] {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 10px;
        }}
        
        /* عناوين الأقسام */
        QLabel[objectName*="section_title"] {{
            font-size: 16px;
            font-weight: bold;
            color: {INFO_COLOR};
            padding: 5px;
            border-bottom: 2px solid {INFO_COLOR};
        }}
        
        /* حالة الحضور */
        QLabel[objectName*="attendance-status"] {{
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
        }}
        
        /* إطارات الأنشطة المختلفة */
        QFrame[objectName*="attendance_frame"] {{
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 6px;
            padding: 8px;
        }}
        
        QFrame[objectName*="financial_frame"] {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            padding: 8px;
        }}
        
        QFrame[objectName*="task_frame"] {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 8px;
        }}
    """

# ستايلات خاصة بنافذة إدارة التدريب
def get_training_specific_styles():
    return """
        /* ستايلات خاصة بإدارة التدريب */
        QFrame[objectName="training_stat_card"] {
            min-height: 80px;
        }
        
        QLabel[objectName="student_status_paid"] {
            background-color: #4caf50;
            color: white;
        }
        
        QLabel[objectName="student_status_unpaid"] {
            background-color: #f44336;
            color: white;
        }
    """

# ستايلات خاصة بنافذة إدارة الديون
def get_debt_specific_styles():
    return f"""
        /* ستايلات خاصة بإدارة الديون */
        
        /* النافذة الرئيسية */
        QMainWindow[objectName="DebtManagementWindow"] {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #1b3459, stop:1 #57216b
            );
            border: none;
        }}
        
        QWidget[objectName="main_central_widget"] {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            margin: 5px;
        }}
        
        QLabel[objectName="main_title"] {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: transparent;
        }}
        
        /* التابات */
        QTabWidget[objectName="debts_tab_widget"] {{
            background-color: transparent;
            border: none;
        }}
        
        QTabWidget[objectName="debts_tab_widget"]::pane {{
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: white;
            margin-top: -1px;
        }}
        
        QTabWidget[objectName="debts_tab_widget"] QTabBar::tab {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ecf0f1, stop:1 #bdc3c7);
            border: 2px solid #bdc3c7;
            border-bottom-color: #bdc3c7;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 120px;
            padding: 8px 12px;
            margin-right: 2px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        QTabWidget[objectName="debts_tab_widget"] QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
            color: white;
            border-bottom-color: white;
        }}
        
        QTabWidget[objectName="debts_tab_widget"] QTabBar::tab:hover:!selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #d5dbdb, stop:1 #a6acaf);
        }}
        
        /* أزرار الإجراءات */
        QPushButton[objectName="action_button"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
            border: 2px solid #2980b9;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 8px 16px;
            min-width: 100px;
            min-height: 35px;
        }}
        
        QPushButton[objectName="action_button"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5dade2, stop:1 #3498db);
            border: 2px solid #3498db;
        }}
        
        QPushButton[objectName="action_button"]:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2980b9, stop:1 #1f618d);
        }}
        
        /* أزرار التقارير */
        QPushButton[objectName="report_button"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ecf0f1, stop:1 #bdc3c7);
            border: 2px solid #95a5a6;
            border-radius: 10px;
            color: #2c3e50;
            font-weight: bold;
            font-size: 16px;
            padding: 15px;
            text-align: center;
        }}
        
        QPushButton[objectName="report_button"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #d5dbdb, stop:1 #a6acaf);
            border: 2px solid #7f8c8d;
        }}
        
        /* حقول الإدخال والفلاتر */
        QComboBox[objectName="filter_combo"] {{
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 14px;
            min-width: 150px;
            min-height: 30px;
        }}
        
        QComboBox[objectName="filter_combo"]:focus {{
            border: 2px solid #3498db;
        }}
        
        QComboBox[objectName="filter_combo"]::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox[objectName="filter_combo"]::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #7f8c8d;
            margin-right: 5px;
        }}
        
        QLineEdit[objectName="search_input"] {{
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 200px;
            min-height: 30px;
        }}
        
        QLineEdit[objectName="search_input"]:focus {{
            border: 2px solid #3498db;
        }}
        
        /* الجداول */
        QTableWidget[objectName="data_table"] {{
            background-color: white;
            alternate-background-color: #f8f9fa;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            gridline-color: #ecf0f1;
            font-size: 13px;
            selection-background-color: #3498db;
            selection-color: white;
        }}
        
        QTableWidget[objectName="data_table"]::item {{
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        QTableWidget[objectName="data_table"]::item:selected {{
            background-color: #3498db;
            color: white;
        }}
        
        QTableWidget[objectName="data_table"] QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #34495e, stop:1 #2c3e50);
            color: white;
            padding: 10px;
            border: 1px solid #2c3e50;
            font-weight: bold;
            font-size: 14px;
        }}
        
        /* حاويات الإحصائيات */
        QFrame[objectName*="stats_container"] {{
            background-color: transparent;
            border: none;
        }}
        
        /* مجموعة التقارير */
        QGroupBox[objectName="reports_group"] {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox[objectName="reports_group"]::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 10px 0 10px;
            background-color: white;
        }}
        
        QLabel[objectName="reports_title"] {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0;
        }}
        
        /* التسميات العامة */
        QLabel {{
            color: #2c3e50;
            font-size: 14px;
            font-weight: bold;
        }}
        
        /* شريط التمرير */
        QScrollBar:vertical {{
            background-color: #ecf0f1;
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #bdc3c7;
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #95a5a6;
        }}
    """

# ستايلات خاصة بنافذة إدارة الموردين
def get_suppliers_specific_styles():
    return f"""
        /* ستايلات خاصة بإدارة الموردين */
        
        /* النافذة الرئيسية */
        SuppliersManagementWindow {{
            background-color: {LIGHT_COLOR};
            font-family: '{MAIN_FONT_FAMILY}';
        }}

        /* العنوان الرئيسي */
        QLabel[objectName="main_title"] {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #bdc3c7;
            margin-bottom: 10px;
        }}

        /* التابات الرئيسية */
        QTabWidget[objectName="suppliers_tab_widget"]::pane {{
            border: 1px solid #ddd;
            background-color: white;
            border-radius: 8px;
        }}

        QTabWidget[objectName="suppliers_tab_widget"] QTabBar::tab {{
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 12px 20px;
            margin-left: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            min-width: 120px;
        }}

        QTabWidget[objectName="suppliers_tab_widget"] QTabBar::tab:selected {{
            background-color: #3498db;
            color: white;
        }}

        QTabWidget[objectName="suppliers_tab_widget"] QTabBar::tab:hover {{
            background-color: #d5dbdb;
        }}

        /* أزرار الإجراءات */
        QPushButton[objectName="action_button"] {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 120px;
        }}

        QPushButton[objectName="action_button"]:hover {{
            background-color: #2980b9;
        }}

        QPushButton[objectName="action_button"]:pressed {{
            background-color: #21618c;
        }}

        /* أزرار التقارير */
        QPushButton[objectName="report_button"] {{
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 20px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            min-height: 80px;
            min-width: 200px;
        }}

        QPushButton[objectName="report_button"]:hover {{
            background-color: #c0392b;
        }}

        QPushButton[objectName="report_button"]:pressed {{
            background-color: #a93226;
        }}

        /* فلاتر البحث */
        QComboBox[objectName="filter_combo"] {{
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 150px;
        }}

        QComboBox[objectName="filter_combo"]:focus {{
            border-color: #3498db;
        }}

        /* شريط البحث */
        QLineEdit[objectName="search_input"] {{
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 200px;
        }}

        QLineEdit[objectName="search_input"]:focus {{
            border-color: #3498db;
        }}

        /* حاوية الإحصائيات */
        QWidget[objectName="stats_container"] {{
            background-color: transparent;
            margin: 10px 0;
        }}

        /* بطاقات الإحصائيات */
        QFrame[objectName="stat_card"] {{
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }}

        QFrame[objectName="stat_card"]:hover {{
            border-color: #3498db;
        }}

        QLabel[objectName="stat_title"] {{
            color: #7f8c8d;
            font-size: 14px;
            font-weight: normal;
        }}

        QLabel[objectName="stat_value"] {{
            font-size: 16px;
            font-weight: bold;
        }}

        /* الجداول */
        QTableWidget[objectName="data_table"] {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            gridline-color: #e0e0e0;
            font-size: 13px;
        }}

        QTableWidget[objectName="data_table"]::item {{
            padding: 8px;
            border-bottom: 1px solid #f0f0f0;
        }}

        QTableWidget[objectName="data_table"]::item:selected {{
            background-color: #3498db;
            color: white;
        }}

        QTableWidget[objectName="data_table"]::item:alternate {{
            background-color: #f8f9fa;
        }}

        QHeaderView::section {{
            background-color: #34495e;
            color: white;
            padding: 10px;
            border: none;
            font-weight: bold;
            font-size: 14px;
        }}

        QHeaderView::section:hover {{
            background-color: #2c3e50;
        }}

        /* عناوين الأقسام */
        QLabel[objectName="section_title"] {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #bdc3c7;
            margin: 10px 0;
        }}

        /* نوافذ الحوار */
        QDialog {{
            background-color: {LIGHT_COLOR};
            font-family: '{MAIN_FONT_FAMILY}';
        }}

        QLabel[objectName="dialog_title"] {{
            font-size: 18px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #bdc3c7;
        }}

        QLineEdit[objectName="form_input"],
        QComboBox[objectName="form_input"],
        QTextEdit[objectName="form_input"] {{
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
        }}

        QLineEdit[objectName="form_input"]:focus,
        QComboBox[objectName="form_input"]:focus,
        QTextEdit[objectName="form_input"]:focus {{
            border-color: #3498db;
        }}

        QPushButton[objectName="save_button"] {{
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 100px;
        }}

        QPushButton[objectName="save_button"]:hover {{
            background-color: #229954;
        }}

        QPushButton[objectName="cancel_button"] {{
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 100px;
        }}

        QPushButton[objectName="cancel_button"]:hover {{
            background-color: #c0392b;
        }}
    """

# ==================== تصدير الدوال الرئيسية ====================

__all__ = [
    # الألوان
    'PRIMARY_COLOR', 'SUCCESS_COLOR', 'DANGER_COLOR', 'WARNING_COLOR', 
    'INFO_COLOR', 'SECONDARY_COLOR', 'DARK_COLOR', 'LIGHT_COLOR',
    
    # الدوال الرئيسية
    'apply_management_style', 'get_complete_management_style',
    
    # دوال التطبيق على النوافذ
    'apply_to_project_management', 'apply_to_employee_management',
    'apply_to_training_management', 'apply_to_client_management',
    'apply_to_supplier_management', 'apply_to_debt_management',
    'get_suppliers_specific_styles',
    
    # دوال مساعدة
    'get_status_color', 'create_colored_label', 'create_stat_card',
    'setup_table_style', 'add_action_buttons_to_table',
    'format_currency', 'format_date', 'format_percentage',
    'create_filter_section', 'create_action_buttons_section',
    'create_info_container', 'adjust_color_brightness',
    'darken_color', 'lighten_color'
]
