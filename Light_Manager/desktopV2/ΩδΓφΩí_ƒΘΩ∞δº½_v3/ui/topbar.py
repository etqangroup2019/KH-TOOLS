# -*- coding: utf-8 -*-
"""
الشريط العلوي: قوائم ملف/حماية/تخصيص/اختصارات/معلومات/مساعدة + أقصى اليسار بحث ومستخدم وتاريخ/وقت/اليوم.
"""
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets
import datetime

class TopBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)

        # قوائم
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_file = self.menu_bar.addMenu("ملف")
        self.menu_security = self.menu_bar.addMenu("حماية")
        self.menu_customize = self.menu_bar.addMenu("تخصيص")
        self.menu_shortcuts = self.menu_bar.addMenu("اختصارات")
        self.menu_info = self.menu_bar.addMenu("معلومات")
        self.menu_help = self.menu_bar.addMenu("مساعدة")

        # عناصر عينة
        self.menu_file.addAction("إنهاء")
        self.menu_help.addAction("حول النظام")

        w = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        lay.addWidget(self.menu_bar)
        lay.addStretch(1)

        # يسار: بحث + اسم المستخدم + الوقت/التاريخ/اليوم
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("بحث...")
        self.user_label = QtWidgets.QLabel("المستخدم: admin")
        self.datetime_label = QtWidgets.QLabel()
        lay.addWidget(self.search)
        lay.addWidget(self.user_label)
        lay.addWidget(self.datetime_label)

        self.addWidget(w)

        # مؤقت للتاريخ والوقت بالعربي
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)
        self._update_datetime()

    def _update_datetime(self):
        now = datetime.datetime.now()
        days_ar = ['الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد']
        # Python: Monday=0 ... Sunday=6; أعلاه يبدأ الاثنين
        day_name = days_ar[now.weekday()]
        self.datetime_label.setText(f"{day_name} - {now:%Y/%m/%d %H:%M:%S}")