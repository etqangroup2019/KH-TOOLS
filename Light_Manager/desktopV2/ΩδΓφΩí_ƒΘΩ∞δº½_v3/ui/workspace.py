# -*- coding: utf-8 -*-
"""
مساحة العمل: ثلاثة حاويات رأسية (فلاتر 60px قابلة للطي، شريط إجراءات 100px قابل للطي، ومنطقة محتوى).
"""
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets

class Collapsible(QtWidgets.QWidget):
    """حاوية قابلة للطي لأعلى بارتفاع ثابت."""
    def __init__(self, title: str, fixed_height: int, content: QtWidgets.QWidget, parent=None):
        super().__init__(parent)
        self._fixed_height = fixed_height
        self._content = content

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        header = QtWidgets.QToolButton(text=title)
        header.setCheckable(True)
        header.setChecked(True)
        header.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        header.setArrowType(QtCore.Qt.DownArrow)
        header.toggled.connect(self._on_toggle)

        root.addWidget(header)
        root.addWidget(content)

        content.setFixedHeight(self._fixed_height)

    def _on_toggle(self, checked: bool):
        self._content.setVisible(checked)

class ActionCard(QtWidgets.QWidget):
    """زر إجراء على هيئة بطاقة مربعة 90x90 مع أيقونة 40px ونص أسفلها."""
    def __init__(self, text: str, icon: str = '⚙️', category: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName('cardButton')
        self.setProperty('class', 'card-button')
        self.setFixedSize(90, 90)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(6, 6, 2, 2)
        root.setSpacing(4)

        icon_lbl = QtWidgets.QLabel(icon)
        f = icon_lbl.font()
        f.setPointSize(24)  # ~40px visual
        icon_lbl.setFont(f)
        icon_lbl.setAlignment(QtCore.Qt.AlignCenter)

        text_lbl = QtWidgets.QLabel(text)
        text_lbl.setAlignment(QtCore.Qt.AlignCenter)

        root.addWidget(icon_lbl)
        root.addWidget(text_lbl)

        # شريط سفلي رفيع حسب الفئة
        if category:
            bar = QtWidgets.QFrame()
            bar.setFixedHeight(3)
            bar.setObjectName(f'catbar_{category}')
            root.addWidget(bar)

class Workspace(QtWidgets.QWidget):
    """مساحة العمل المقسمة لثلاث حاويات قابلة للطي + منطقة محتوى."""
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # 1) فلاتر (60px) مع سكرول أفقي
        filters_content = QtWidgets.QWidget()
        h1 = QtWidgets.QHBoxLayout(filters_content)
        h1.setContentsMargins(0, 0, 0, 0)
        h1.setSpacing(6)
        scroll_filters = QtWidgets.QScrollArea()
        scroll_filters.setWidgetResizable(True)
        scroll_filters.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_filters.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        filt_inner = QtWidgets.QWidget()
        filt_lay = QtWidgets.QHBoxLayout(filt_inner)
        for i in range(8):
            cb = QtWidgets.QComboBox()
            cb.addItems([f"خيار {j+1}" for j in range(5)])
            filt_lay.addWidget(cb)
        scroll_filters.setWidget(filt_inner)
        h1.addWidget(scroll_filters)
        filters = Collapsible("فلاتر", 60, filters_content)

        # 2) شريط الإجراءات (100px) مع بطاقات 90x90 وسكرول أفقي
        actions_content = QtWidgets.QWidget()
        h2 = QtWidgets.QHBoxLayout(actions_content)
        h2.setContentsMargins(0, 0, 0, 0)
        h2.setSpacing(6)
        scroll_actions = QtWidgets.QScrollArea()
        scroll_actions.setWidgetResizable(True)
        scroll_actions.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_actions.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        actions_inner = QtWidgets.QWidget()
        actions_lay = QtWidgets.QHBoxLayout(actions_inner)
        actions = [
            ("إضافة", '➕', 'add'),
            ("حذف", '🗑️', 'delete'),
            ("تعديل", '✏️', 'manage'),
            ("طباعة", '🖨️', 'print'),
            ("تقارير", '📊', 'finance'),
            ("حالة", '⚠️', 'status'),
            ("مصروف", '💸', 'expense'),
        ]
        for text, icon, cat in actions:
            actions_lay.addWidget(ActionCard(text, icon, cat))
        scroll_actions.setWidget(actions_inner)
        h2.addWidget(scroll_actions)
        actions_bar = Collapsible("إجراءات", 100, actions_content)

        # 3) منطقة المحتوى (باقي المساحة)
        content = QtWidgets.QStackedWidget()
        placeholder = QtWidgets.QLabel("منطقة المحتوى")
        placeholder.setAlignment(QtCore.Qt.AlignCenter)
        content.addWidget(placeholder)

        root.addWidget(filters)
        root.addWidget(actions_bar)
        root.addWidget(content, 1)

        self.content = content