# -*- coding: utf-8 -*-
"""
الشريط الجانبي الرأسي القابل للطي مع أزرار الوحدات.
"""
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets
from typing import Callable, List, Tuple

SidebarItem = Tuple[str, str]  # (key, label)

class Sidebar(QtWidgets.QWidget):
    moduleSelected = QtCore.Signal(str)

    def __init__(self, items: List[SidebarItem], collapsed: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName('sidebar')
        self.setFixedWidth(100 if not collapsed else 60)
        self._collapsed = collapsed
        self._items = items

        self._root = QtWidgets.QVBoxLayout(self)
        self._root.setContentsMargins(6, 6, 6, 6)
        self._root.setSpacing(6)

        # Scroll area for buttons
        self._scroll = QtWidgets.QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        content = QtWidgets.QWidget()
        self._list_layout = QtWidgets.QVBoxLayout(content)
        self._list_layout.setAlignment(QtCore.Qt.AlignTop)
        self._list_layout.setSpacing(8)

        for key, label in items:
            btn = self._create_button(key, label)
            self._list_layout.addWidget(btn)

        self._scroll.setWidget(content)
        self._root.addWidget(self._scroll)

        # Collapse/expand button
        self._toggle_btn = QtWidgets.QToolButton()
        self._toggle_btn.setText('⟷')
        self._toggle_btn.clicked.connect(self.toggle)
        self._root.addWidget(self._toggle_btn)

    def _create_button(self, key: str, label: str) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton()
        btn.setCheckable(True)
        btn.setObjectName('sidebarButton')
        btn.setProperty('class', 'sidebar')
        btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        btn.setFixedHeight(80)

        # Layout inside the button to show icon + label stacked
        w = QtWidgets.QWidget()
        w.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        lay = QtWidgets.QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        icon_lbl = QtWidgets.QLabel('🧭')
        icon_lbl.setAlignment(QtCore.Qt.AlignCenter)
        icon_lbl.setFixedHeight(40)
        text_lbl = QtWidgets.QLabel(label)
        text_lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(icon_lbl)
        lay.addWidget(text_lbl)
        proxy = QtWidgets.QHBoxLayout(btn)
        proxy.setContentsMargins(0, 0, 0, 0)
        proxy.addWidget(w)

        btn.clicked.connect(lambda: self.moduleSelected.emit(key))
        return btn

    def toggle(self):
        self._collapsed = not self._collapsed
        self.setFixedWidth(60 if self._collapsed else 100)

    def set_active(self, key: str):
        # Optional: highlight active button if needed
        pass