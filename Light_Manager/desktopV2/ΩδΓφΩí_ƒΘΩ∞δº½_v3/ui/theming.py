# -*- coding: utf-8 -*-
"""
الثيم العام للتطبيق ودعم الوضع الداكن/الفاتح وألوان الفئات.
"""
from __future__ import annotations
from dataclasses import dataclass

# ألوان فئات الأزرار (خط سفلي رفيع)
CATEGORY_COLORS = {
    'delete': '#E53935',     # أحمر
    'print': '#9E9E9E',      # رمادي
    'finance': '#1E88E5',    # أزرق
    'status': '#FDD835',     # أصفر
    'expense': '#FB8C00',    # برتقالي
    'manage': '#8E24AA',     # بنفسجي
    'add': '#1B5E20',        # أخضر داكن
}

PRIMARY_BG = '#4A276A'  # الخلفية الأرجوانية الداكنة
PRIMARY_FG = '#FFFFFF'
SECONDARY_BG = '#5C337F'
HOVER_BG = '#6F3E99'
ACTIVE_BG = '#7F48AD'
BORDER_COLOR = '#3B1F57'

@dataclass
class Theme:
    rtl: bool = True
    dark_mode: bool = True
    font_family: str = 'Tajawal'
    font_size: int = 11
    primary_bg: str = PRIMARY_BG
    primary_fg: str = PRIMARY_FG
    secondary_bg: str = SECONDARY_BG
    hover_bg: str = HOVER_BG
    active_bg: str = ACTIVE_BG
    border_color: str = BORDER_COLOR

    def qss(self) -> str:
        """إرجاع QSS كامل للتطبيق"""
        return f"""
        * {{
            font-family: '{self.font_family}';
            font-size: {self.font_size}pt;
            color: {self.primary_fg};
        }}
        QMainWindow {{
            background: {self.primary_bg};
        }}
        QToolBar {{
            background: {self.secondary_bg};
            spacing: 8px;
            padding: 6px;
            border: none;
        }}
        QMenuBar {{
            background: {self.secondary_bg};
        }}
        QMenu {{
            background: {self.secondary_bg};
        }}
        QStatusBar {{
            background: {self.secondary_bg};
        }}
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        QPushButton.sidebar {{
            background: transparent;
            border: none;
            padding: 10px 6px;
        }}
        QPushButton.sidebar:hover {{
            background: {self.hover_bg};
        }}
        QPushButton.sidebar:checked {{
            background: {self.active_bg};
        }}
        QWidget.card-button {{
            background: {self.secondary_bg};
            border: 1px solid {self.border_color};
            border-radius: 8px;
        }}
        QWidget.card-button:hover {{
            background: {self.hover_bg};
        }}
        """