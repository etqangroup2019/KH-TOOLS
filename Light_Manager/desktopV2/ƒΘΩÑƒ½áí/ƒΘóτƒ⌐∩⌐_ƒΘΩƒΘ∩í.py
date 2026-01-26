#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة التقارير المالية المتكاملة
تحتوي على نظام محاسبي شامل مع شجرة الحسابات والربط التلقائي للمعاملات
"""

import sys
import os
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector
import qtawesome as qta

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from ستايل import apply_stylesheet
from قائمة_الجداول import setup_table_context_menu
from متغيرات import *
# from نظام_البطاقات import ModernCard, ModernCardsContainer
from أزرار_الواجهة import table_setting
from مساعد_أزرار_الطباعة import quick_add_print_button
from التقارير_المالية_المتقدمة import AdvancedFinancialReports


# نافذة التقارير المالية الشاملة
class FinancialReportsWindow(QMainWindow):
    
    # init
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("التقارير المالية - النظام المحاسبي المتكامل")
        self.setGeometry(100, 100, 1400, 900)
        self.setLayoutDirection(Qt.RightToLeft)

        # إنشاء مولد التقارير المتقدمة
        self.advanced_reports = AdvancedFinancialReports(main_window)

        # إعداد الواجهة
        self.setup_ui()

        # تطبيق الستايل
        apply_stylesheet(self)

        # تحميل البيانات الأولية
        self.load_initial_data()

    # إنشاء تبويب التقارير الشهرية والسنوية
    def create_monthly_annual_reports_tab(self):
        monthly_reports_widget = MonthlyAnnualReportsWidget(self)
        self.tab_widget.addTab(monthly_reports_widget, "التقارير الشهرية والسنوية")
    
    # إعداد واجهة المستخدم
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان النافذة
        title_label = QLabel("التقارير المالية والنظام المحاسبي")
        title_label.setObjectName("main_title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # شريط الأدوات العلوي
        toolbar_layout = self.create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # بطاقات الإحصائيات المالية
        stats_layout = self.create_financial_stats()
        main_layout.addLayout(stats_layout)
        
        # التبويبات الرئيسية
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("financial_tabs")
        self.create_tabs()
        main_layout.addWidget(self.tab_widget)

        # إضافة تبويب التقارير الشهرية والسنوية
        self.create_monthly_annual_reports_tab()
    
    # إنشاء شريط الأدوات العلوي
    def create_toolbar(self):
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        
        # أزرار الإجراءات الرئيسية
        actions = [
            ("شجرة الحسابات", "fa5s.sitemap", self.open_chart_of_accounts, "#2ecc71"),
            ("القيود المحاسبية", "fa5s.book", self.open_journal_entries, "#3498db"),
            ("ربط المعاملات", "fa5s.link", self.open_transaction_linking, "#f39c12"),
            ("التقارير المالية", "fa5s.chart-line", self.open_financial_reports, "#9b59b6"),
            ("التقارير الشهرية", "fa5s.calendar-alt", self.open_monthly_reports, "#e74c3c"),
            ("إعدادات النظام", "fa5s.cog", self.open_system_settings, "#34495e")
        ]
        
        for text, icon, callback, color in actions:
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon, color=color))
            btn.setObjectName("toolbar_button")
            btn.clicked.connect(callback)
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addStretch()
        
        # زر الطباعة
        print_btn = QPushButton("طباعة")
        print_btn.setIcon(qta.icon('fa5s.print', color='white'))
        print_btn.setObjectName("print_button")
        print_btn.clicked.connect(self.print_reports)
        toolbar_layout.addWidget(print_btn)
        
        return toolbar_layout
    
    # إنشاء بطاقات الإحصائيات المالية مع التخطيط الأفقي المحسن
    def create_financial_stats(self):
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # بيانات الإحصائيات مع الألوان الموحدة
        stats_data = [
            ("إجمالي الإيرادات", "0.00", "#3498db", "fa5s.arrow-up"),
            ("إجمالي المصروفات", "0.00", "#e74c3c", "fa5s.arrow-down"),
            ("صافي الربح", "0.00", "#27ae60", "fa5s.chart-line"),
            ("الأرصدة المدينة", "0.00", "#f39c12", "fa5s.coins"),
            ("الأرصدة الدائنة", "0.00", "#9b59b6", "fa5s.wallet")
        ]

        self.stats_cards = {}

        for title, value, color, icon in stats_data:
            card = QFrame()
            card.setObjectName("financial_stats_card")
            card.setFrameStyle(QFrame.Box)

            # تخطيط أفقي للبطاقة - العنوان والقيمة في نفس السطر
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            card_layout.setSpacing(10)

            # الأيقونة
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(icon, color=color).pixmap(24, 24))
            card_layout.addWidget(icon_label)

            # النص والقيمة في نفس السطر
            title_label = QLabel(title + ":")
            title_label.setObjectName("stats_title")
            card_layout.addWidget(title_label)

            value_label = QLabel(f"{value} {Currency_type}")
            value_label.setObjectName("stats_value")
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(value_label)

            card_layout.addStretch()

            # حفظ مرجع للتحديث لاحقاً
            self.stats_cards[title] = value_label

            stats_layout.addWidget(card)

        return stats_layout
    
    # إنشاء التبويبات الرئيسية
    def create_tabs(self):
        # تبويب الملخص المالي
        self.create_financial_summary_tab()
        
        # تبويب شجرة الحسابات
        self.create_chart_of_accounts_tab()
        
        # تبويب القيود المحاسبية
        self.create_journal_entries_tab()
        
        # تبويب ربط المعاملات
        self.create_transaction_linking_tab()
        
        # تبويب التقارير المالية
        self.create_financial_reports_tab()
        
        # تبويب الإعدادات
        self.create_settings_tab()
    
    # إنشاء تبويب الملخص المالي
    def create_financial_summary_tab(self):
        tab = QWidget()
        tab.setObjectName("financial_summary_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # عنوان التبويب
        title = QLabel("الملخص المالي العام")
        title.setObjectName("tab_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # فلاتر التاريخ والفترة
        filters_layout = self.create_date_filters()
        layout.addLayout(filters_layout)
        
        # جدول الملخص المالي
        self.summary_table = QTableWidget()
        self.summary_table.setObjectName("financial_summary_table")
        self.setup_summary_table()
        layout.addWidget(self.summary_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.chart-pie', color='#3498db'), "الملخص المالي")
    
    # إنشاء تبويب شجرة الحسابات
    def create_chart_of_accounts_tab(self):
        tab = QWidget()
        tab.setObjectName("chart_of_accounts_tab")
        layout = QHBoxLayout(tab)
        layout.setSpacing(15)
        
        # الجانب الأيمن - شجرة الحسابات
        tree_panel = self.create_accounts_tree_panel()
        layout.addWidget(tree_panel, 2)
        
        # الجانب الأيسر - تفاصيل الحساب
        details_panel = self.create_account_details_panel()
        layout.addWidget(details_panel, 1)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.sitemap', color='#2ecc71'), "شجرة الحسابات")
    
    # إنشاء تبويب القيود المحاسبية
    def create_journal_entries_tab(self):
        tab = QWidget()
        tab.setObjectName("journal_entries_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # شريط أدوات القيود
        entries_toolbar = self.create_journal_entries_toolbar()
        layout.addLayout(entries_toolbar)
        
        # جدول القيود المحاسبية
        self.journal_entries_table = QTableWidget()
        self.journal_entries_table.setObjectName("journal_entries_table")
        self.setup_journal_entries_table()
        layout.addWidget(self.journal_entries_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.book', color='#e74c3c'), "القيود المحاسبية")
    
    # إنشاء تبويب ربط المعاملات
    def create_transaction_linking_tab(self):
        tab = QWidget()
        tab.setObjectName("transaction_linking_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # شريط أدوات الربط
        linking_toolbar = self.create_linking_toolbar()
        layout.addLayout(linking_toolbar)
        
        # جدول المعاملات غير المربوطة
        self.unlinked_transactions_table = QTableWidget()
        self.unlinked_transactions_table.setObjectName("unlinked_transactions_table")
        self.setup_unlinked_transactions_table()
        layout.addWidget(self.unlinked_transactions_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.link', color='#f39c12'), "ربط المعاملات")
    
    # إنشاء تبويب التقارير المالية
    def create_financial_reports_tab(self):
        tab = QWidget()
        tab.setObjectName("financial_reports_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # أزرار التقارير المختلفة
        reports_grid = QGridLayout()
        reports_grid.setSpacing(15)
        
        reports = [
            ("قائمة الدخل", "fa5s.chart-line", self.generate_income_statement, 0, 0),
            ("الميزانية العمومية", "fa5s.balance-scale", self.generate_balance_sheet, 0, 1),
            ("التدفقات النقدية", "fa5s.money-bill-wave", self.generate_cash_flow, 0, 2),
            ("دفتر الأستاذ", "fa5s.book-open", self.generate_ledger, 1, 0),
            ("ميزان المراجعة", "fa5s.calculator", self.generate_trial_balance, 1, 1),
            ("تقرير الأرباح والخسائر", "fa5s.chart-bar", self.generate_profit_loss, 1, 2)
        ]
        
        for text, icon, callback, row, col in reports:
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon, color='white'))
            btn.setObjectName("report_button")
            btn.clicked.connect(callback)
            reports_grid.addWidget(btn, row, col)
        
        layout.addLayout(reports_grid)
        
        # منطقة عرض التقرير
        self.report_display = QTextEdit()
        self.report_display.setObjectName("report_display")
        self.report_display.setReadOnly(True)
        layout.addWidget(self.report_display)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.file-alt', color='#9b59b6'), "التقارير المالية")
    
    # إنشاء تبويب الإعدادات
    def create_settings_tab(self):
        tab = QWidget()
        tab.setObjectName("settings_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # إعدادات النظام المحاسبي
        settings_label = QLabel("إعدادات النظام المحاسبي")
        settings_label.setObjectName("tab_title")
        settings_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(settings_label)
        
        # نموذج الإعدادات
        settings_form = QFormLayout()
        
        # إعدادات العملة
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["ريال سعودي", "دولار أمريكي", "يورو", "جنيه مصري"])
        settings_form.addRow("العملة الأساسية:", self.currency_combo)
        
        # إعدادات السنة المالية
        self.fiscal_year_start = QDateEdit()
        self.fiscal_year_start.setDate(QDate.currentDate().addDays(-QDate.currentDate().dayOfYear() + 1))
        self.fiscal_year_start.setDisplayFormat("dd/MM/yyyy")
        settings_form.addRow("بداية السنة المالية:", self.fiscal_year_start)
        
        # إعدادات الربط التلقائي
        self.auto_linking_enabled = QCheckBox("تفعيل الربط التلقائي للمعاملات")
        self.auto_linking_enabled.setChecked(True)
        settings_form.addRow("", self.auto_linking_enabled)
        
        layout.addLayout(settings_form)
        layout.addStretch()
        
        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ الإعدادات")
        save_btn.setObjectName("save_button")
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("إعادة تعيين")
        reset_btn.setObjectName("reset_button")
        reset_btn.clicked.connect(self.reset_settings)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.cog', color='#34495e'), "الإعدادات")

    # إنشاء فلاتر التاريخ والفترة
    def create_date_filters(self):
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)

        # فلتر من تاريخ
        filters_layout.addWidget(QLabel("من تاريخ:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setDisplayFormat("dd/MM/yyyy")
        self.from_date.setCalendarPopup(True)
        filters_layout.addWidget(self.from_date)

        # فلتر إلى تاريخ
        filters_layout.addWidget(QLabel("إلى تاريخ:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setDisplayFormat("dd/MM/yyyy")
        self.to_date.setCalendarPopup(True)
        filters_layout.addWidget(self.to_date)

        # زر التحديث
        refresh_btn = QPushButton("تحديث")
        refresh_btn.setIcon(qta.icon('fa5s.sync', color='white'))
        refresh_btn.setObjectName("refresh_button")
        refresh_btn.clicked.connect(self.refresh_financial_data)
        filters_layout.addWidget(refresh_btn)

        filters_layout.addStretch()

        return filters_layout

    # إعداد جدول الملخص المالي
    def setup_summary_table(self):
        headers = ["البيان", "الشهر الحالي", "الشهر السابق", "السنة الحالية", "السنة السابقة", "النسبة %"]
        self.summary_table.setColumnCount(len(headers))
        self.summary_table.setHorizontalHeaderLabels(headers)

        # تعيين عرض الأعمدة
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        # إعداد قائمة السياق
        setup_table_context_menu(self.summary_table, self.main_window, "التقارير_المالية")

    # إنشاء لوحة شجرة الحسابات
    def create_accounts_tree_panel(self):
        panel = QGroupBox("شجرة الحسابات")
        panel.setObjectName("accounts_tree_panel")
        layout = QVBoxLayout(panel)

        # شريط أدوات الشجرة
        tree_toolbar = QHBoxLayout()

        add_account_btn = QPushButton("إضافة حساب")
        add_account_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_account_btn.setObjectName("add_button")
        add_account_btn.clicked.connect(self.add_new_account)
        tree_toolbar.addWidget(add_account_btn)

        edit_account_btn = QPushButton("تعديل حساب")
        edit_account_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        edit_account_btn.setObjectName("edit_button")
        edit_account_btn.clicked.connect(self.edit_selected_account)
        tree_toolbar.addWidget(edit_account_btn)

        delete_account_btn = QPushButton("حذف حساب")
        delete_account_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        delete_account_btn.setObjectName("delete_button")
        delete_account_btn.clicked.connect(self.delete_selected_account)
        tree_toolbar.addWidget(delete_account_btn)

        tree_toolbar.addStretch()
        layout.addLayout(tree_toolbar)

        # شجرة الحسابات
        self.accounts_tree = QTreeWidget()
        self.accounts_tree.setObjectName("accounts_tree")
        self.accounts_tree.setHeaderLabel("الحسابات")
        self.accounts_tree.itemClicked.connect(self.on_account_selected)
        self.setup_accounts_tree()
        layout.addWidget(self.accounts_tree)

        return panel

    # إنشاء لوحة تفاصيل الحساب
    def create_account_details_panel(self):
        panel = QGroupBox("تفاصيل الحساب")
        panel.setObjectName("account_details_panel")
        layout = QVBoxLayout(panel)

        # معلومات الحساب
        self.account_info_label = QLabel("اختر حساباً لعرض تفاصيله")
        self.account_info_label.setObjectName("account_info")
        self.account_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.account_info_label)

        # جدول حركات الحساب
        self.account_movements_table = QTableWidget()
        self.account_movements_table.setObjectName("account_movements_table")
        self.setup_account_movements_table()
        layout.addWidget(self.account_movements_table)

        return panel

    # إنشاء شريط أدوات القيود المحاسبية
    def create_journal_entries_toolbar(self):
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # أزرار الإجراءات
        add_entry_btn = QPushButton("إضافة قيد")
        add_entry_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_entry_btn.setObjectName("add_button")
        add_entry_btn.clicked.connect(self.add_journal_entry)
        toolbar_layout.addWidget(add_entry_btn)

        edit_entry_btn = QPushButton("تعديل قيد")
        edit_entry_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        edit_entry_btn.setObjectName("edit_button")
        edit_entry_btn.clicked.connect(self.edit_journal_entry)
        toolbar_layout.addWidget(edit_entry_btn)

        delete_entry_btn = QPushButton("حذف قيد")
        delete_entry_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        delete_entry_btn.setObjectName("delete_button")
        delete_entry_btn.clicked.connect(self.delete_journal_entry)
        toolbar_layout.addWidget(delete_entry_btn)

        toolbar_layout.addStretch()

        # فلتر نوع القيد
        toolbar_layout.addWidget(QLabel("نوع القيد:"))
        self.entry_type_filter = QComboBox()
        self.entry_type_filter.addItems(["الكل", "يدوي", "تلقائي", "تسوية"])
        self.entry_type_filter.currentTextChanged.connect(self.filter_journal_entries)
        toolbar_layout.addWidget(self.entry_type_filter)

        return toolbar_layout

    # إعداد جدول القيود المحاسبية
    def setup_journal_entries_table(self):
        headers = ["رقم القيد", "التاريخ", "البيان", "الحساب", "مدين", "دائن", "النوع", "المرجع"]
        self.journal_entries_table.setColumnCount(len(headers))
        self.journal_entries_table.setHorizontalHeaderLabels(headers)

        # تعيين عرض الأعمدة
        header = self.journal_entries_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # البيان
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # الحساب

        # إعداد قائمة السياق
        setup_table_context_menu(self.journal_entries_table, self.main_window, "القيود_المحاسبية")

    # إنشاء شريط أدوات ربط المعاملات
    def create_linking_toolbar(self):
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # زر الربط التلقائي
        auto_link_btn = QPushButton("ربط تلقائي")
        auto_link_btn.setIcon(qta.icon('fa5s.magic', color='white'))
        auto_link_btn.setObjectName("auto_link_button")
        auto_link_btn.clicked.connect(self.auto_link_transactions)
        toolbar_layout.addWidget(auto_link_btn)

        # زر الربط اليدوي
        manual_link_btn = QPushButton("ربط يدوي")
        manual_link_btn.setIcon(qta.icon('fa5s.hand-point-right', color='white'))
        manual_link_btn.setObjectName("manual_link_button")
        manual_link_btn.clicked.connect(self.manual_link_transaction)
        toolbar_layout.addWidget(manual_link_btn)

        # زر إلغاء الربط
        unlink_btn = QPushButton("إلغاء ربط")
        unlink_btn.setIcon(qta.icon('fa5s.unlink', color='white'))
        unlink_btn.setObjectName("unlink_button")
        unlink_btn.clicked.connect(self.unlink_transaction)
        toolbar_layout.addWidget(unlink_btn)

        toolbar_layout.addStretch()

        # فلتر القسم
        toolbar_layout.addWidget(QLabel("القسم:"))
        self.section_filter = QComboBox()
        self.section_filter.addItems(["الكل", "المشاريع", "المقاولات", "الموظفين", "العملاء", "الموردين", "المصروفات", "التدريب", "الديون"])
        self.section_filter.currentTextChanged.connect(self.filter_unlinked_transactions)
        toolbar_layout.addWidget(self.section_filter)

        return toolbar_layout

    # إعداد جدول المعاملات غير المربوطة
    def setup_unlinked_transactions_table(self):
        headers = ["المعرف", "القسم", "النوع", "الوصف", "المبلغ", "التاريخ", "الحالة", "الإجراء"]
        self.unlinked_transactions_table.setColumnCount(len(headers))
        self.unlinked_transactions_table.setHorizontalHeaderLabels(headers)

        # تعيين عرض الأعمدة
        header = self.unlinked_transactions_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # الوصف

        # إعداد قائمة السياق
        setup_table_context_menu(self.unlinked_transactions_table, self.main_window, "المعاملات_غير_المربوطة")

    # إعداد جدول حركات الحساب
    def setup_account_movements_table(self):
        headers = ["التاريخ", "البيان", "المرجع", "مدين", "دائن", "الرصيد"]
        self.account_movements_table.setColumnCount(len(headers))
        self.account_movements_table.setHorizontalHeaderLabels(headers)

        # تعيين عرض الأعمدة
        header = self.account_movements_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # البيان

        # إعداد قائمة السياق
        setup_table_context_menu(self.account_movements_table, self.main_window, "حركات_الحساب")

    # إعداد شجرة الحسابات الخماسية
    def setup_accounts_tree(self):
        self.accounts_tree.clear()

        # الحسابات الرئيسية الخمسة
        main_accounts = [
            ("1", "الأصول", "fa5s.building", "#2ecc71"),
            ("2", "الخصوم", "fa5s.credit-card", "#e74c3c"),
            ("3", "حقوق الملكية", "fa5s.user-tie", "#3498db"),
            ("4", "الإيرادات", "fa5s.arrow-up", "#27ae60"),
            ("5", "المصروفات", "fa5s.arrow-down", "#e67e22")
        ]

        for code, name, icon, color in main_accounts:
            item = QTreeWidgetItem(self.accounts_tree)
            item.setText(0, f"{code} - {name}")
            item.setIcon(0, qta.icon(icon, color=color))
            item.setData(0, Qt.UserRole, {"code": code, "name": name, "level": 1})

            # إضافة الحسابات الفرعية
            self.add_sub_accounts(item, code)

        # توسيع الشجرة
        self.accounts_tree.expandAll()

    # إضافة الحسابات الفرعية
    def add_sub_accounts(self, parent_item, parent_code):
        sub_accounts = {
            "1": [  # الأصول
                ("11", "الأصول المتداولة"),
                ("12", "الأصول الثابتة"),
                ("13", "الأصول غير الملموسة")
            ],
            "2": [  # الخصوم
                ("21", "الخصوم المتداولة"),
                ("22", "الخصوم طويلة الأجل")
            ],
            "3": [  # حقوق الملكية
                ("31", "رأس المال"),
                ("32", "الأرباح المحتجزة"),
                ("33", "الاحتياطيات")
            ],
            "4": [  # الإيرادات
                ("41", "إيرادات المشاريع"),
                ("42", "إيرادات المقاولات"),
                ("43", "إيرادات التدريب"),
                ("44", "إيرادات أخرى")
            ],
            "5": [  # المصروفات
                ("51", "مصروفات المشاريع"),
                ("52", "مصروفات الموظفين"),
                ("53", "مصروفات إدارية"),
                ("54", "مصروفات أخرى")
            ]
        }

        if parent_code in sub_accounts:
            for code, name in sub_accounts[parent_code]:
                sub_item = QTreeWidgetItem(parent_item)
                sub_item.setText(0, f"{code} - {name}")
                sub_item.setIcon(0, qta.icon('fa5s.folder', color='#95a5a6'))
                sub_item.setData(0, Qt.UserRole, {"code": code, "name": name, "level": 2})

                # إضافة حسابات فرعية من المستوى الثالث
                self.add_detailed_accounts(sub_item, code)

    # إضافة الحسابات التفصيلية
    def add_detailed_accounts(self, parent_item, parent_code):
        detailed_accounts = {
            "11": [  # الأصول المتداولة
                ("111", "النقدية والبنوك"),
                ("112", "العملاء والذمم المدينة"),
                ("113", "المخزون"),
                ("114", "المصروفات المدفوعة مقدماً")
            ],
            "12": [  # الأصول الثابتة
                ("121", "الأراضي والمباني"),
                ("122", "المعدات والآلات"),
                ("123", "الأثاث والتجهيزات"),
                ("124", "وسائل النقل")
            ],
            "21": [  # الخصوم المتداولة
                ("211", "الموردين والذمم الدائنة"),
                ("212", "المصروفات المستحقة"),
                ("213", "القروض قصيرة الأجل"),
                ("214", "الضرائب المستحقة")
            ],
            "41": [  # إيرادات المشاريع
                ("411", "إيرادات مشاريع التصميم"),
                ("412", "إيرادات مشاريع التنفيذ"),
                ("413", "إيرادات مشاريع الإشراف")
            ],
            "51": [  # مصروفات المشاريع
                ("511", "مصروفات المواد"),
                ("512", "مصروفات العمالة"),
                ("513", "مصروفات المعدات"),
                ("514", "مصروفات النقل")
            ]
        }

        if parent_code in detailed_accounts:
            for code, name in detailed_accounts[parent_code]:
                detail_item = QTreeWidgetItem(parent_item)
                detail_item.setText(0, f"{code} - {name}")
                detail_item.setIcon(0, qta.icon('fa5s.file', color='#7f8c8d'))
                detail_item.setData(0, Qt.UserRole, {"code": code, "name": name, "level": 3})

    # تحميل البيانات الأولية
    def load_initial_data(self):
        try:
            self.refresh_financial_data()
            self.load_unlinked_transactions()
            self.load_journal_entries()
        except Exception as e:
            print(f"خطأ في تحميل البيانات الأولية: {e}")

    # تحديث البيانات المالية
    def refresh_financial_data(self):
        try:
            # تحديث الإحصائيات
            self.update_financial_stats()

            # تحديث جدول الملخص المالي
            self.update_financial_summary()

        except Exception as e:
            print(f"خطأ في تحديث البيانات المالية: {e}")

    # تحديث إحصائيات البطاقات المالية
    def update_financial_stats(self):
        try:
            conn = self.main_window.get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()

            # حساب إجمالي الإيرادات من المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المدفوع), 0) as total_revenue
                FROM المشاريع
                WHERE YEAR(تاريخ_التسليم) = YEAR(CURDATE())
            """)
            total_revenue = cursor.fetchone()[0] or 0

            # حساب إجمالي المصروفات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_expenses
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = YEAR(CURDATE())
            """)
            total_expenses = cursor.fetchone()[0] or 0

            # حساب صافي الربح
            net_profit = total_revenue - total_expenses

            # حساب الأرصدة المدينة (العملاء)
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي), 0) as debit_balance
                FROM المشاريع
                WHERE الباقي > 0
            """)
            debit_balance = cursor.fetchone()[0] or 0

            # حساب الأرصدة الدائنة (الموردين)
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي_للمورد), 0) as credit_balance
                FROM الموردين
                WHERE الباقي_للمورد > 0
            """)
            credit_balance = cursor.fetchone()[0] or 0

            # تحديث البطاقات
            self.stats_cards["إجمالي الإيرادات"].setText(f"{total_revenue:,.2f} {Currency_type}")
            self.stats_cards["إجمالي المصروفات"].setText(f"{total_expenses:,.2f} {Currency_type}")
            self.stats_cards["صافي الربح"].setText(f"{net_profit:,.2f} {Currency_type}")
            self.stats_cards["الأرصدة المدينة"].setText(f"{debit_balance:,.2f} {Currency_type}")
            self.stats_cards["الأرصدة الدائنة"].setText(f"{credit_balance:,.2f} {Currency_type}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات المالية: {e}")

    # تحديث جدول الملخص المالي
    def update_financial_summary(self):
        try:
            # بيانات الملخص المالي
            summary_data = [
                ["إيرادات المشاريع", "0.00", "0.00", "0.00", "0.00", "0%"],
                ["إيرادات المقاولات", "0.00", "0.00", "0.00", "0.00", "0%"],
                ["إيرادات التدريب", "0.00", "0.00", "0.00", "0.00", "0%"],
                ["مصروفات المشاريع", "0.00", "0.00", "0.00", "0.00", "0%"],
                ["مصروفات الموظفين", "0.00", "0.00", "0.00", "0.00", "0%"],
                ["مصروفات إدارية", "0.00", "0.00", "0.00", "0.00", "0%"],
                ["صافي الربح", "0.00", "0.00", "0.00", "0.00", "0%"]
            ]

            self.summary_table.setRowCount(len(summary_data))

            for row, data in enumerate(summary_data):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value))
                    if col == 0:  # البيان
                        item.setFont(QFont("Arial", 10, QFont.Bold))
                    elif col > 0 and col < 5:  # الأرقام
                        item.setTextAlignment(Qt.AlignCenter)
                        if "إيرادات" in data[0]:
                            item.setForeground(QBrush(QColor("#27ae60")))
                        elif "مصروفات" in data[0]:
                            item.setForeground(QBrush(QColor("#e74c3c")))
                        elif "صافي" in data[0]:
                            item.setForeground(QBrush(QColor("#3498db")))

                    self.summary_table.setItem(row, col, item)

        except Exception as e:
            print(f"خطأ في تحديث الملخص المالي: {e}")

    # ===== وظائف شريط الأدوات =====
    # فتح نافذة شجرة الحسابات
    def open_chart_of_accounts(self):
        self.tab_widget.setCurrentIndex(1)  # التبويب الثاني

    # فتح نافذة القيود المحاسبية
    def open_journal_entries(self):
        self.tab_widget.setCurrentIndex(2)  # التبويب الثالث

    # فتح نافذة ربط المعاملات
    def open_transaction_linking(self):
        self.tab_widget.setCurrentIndex(3)  # التبويب الرابع

    # فتح نافذة التقارير المالية
    def open_financial_reports(self):
        self.tab_widget.setCurrentIndex(4)  # التبويب الخامس

    # فتح نافذة التقارير الشهرية والسنوية
    def open_monthly_reports(self):
        try:
            from التقارير_الشهرية_والسنوية import open_monthly_annual_reports_window
            self.monthly_reports_window = open_monthly_annual_reports_window(self.main_window)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح التقارير الشهرية: {str(e)}")

    # فتح نافذة إعدادات النظام
    def open_system_settings(self):
        self.tab_widget.setCurrentIndex(5)  # التبويب السادس

    # طباعة التقارير
    def print_reports(self):
        try:
            from الطباعة_والتصدير import print_manager
            current_tab = self.tab_widget.currentIndex()

            if current_tab == 0:  # الملخص المالي
                print_manager.open_print_dialog(self, self.summary_table, "الملخص المالي")
            elif current_tab == 2:  # القيود المحاسبية
                print_manager.open_print_dialog(self, self.journal_entries_table, "القيود المحاسبية")
            elif current_tab == 3:  # ربط المعاملات
                print_manager.open_print_dialog(self, self.unlinked_transactions_table, "المعاملات غير المربوطة")
            else:
                QMessageBox.information(self, "طباعة", "يرجى اختيار تبويب قابل للطباعة")

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة الطباعة:\n{str(e)}")

    # ===== وظائف شجرة الحسابات =====
    # عند اختيار حساب من الشجرة
    def on_account_selected(self, item):
        try:
            account_data = item.data(0, Qt.UserRole)
            if account_data:
                account_info = f"رمز الحساب: {account_data['code']}\n"
                account_info += f"اسم الحساب: {account_data['name']}\n"
                account_info += f"المستوى: {account_data['level']}"

                self.account_info_label.setText(account_info)
                self.load_account_movements(account_data['code'])
        except Exception as e:
            print(f"خطأ في اختيار الحساب: {e}")

    # تحميل حركات الحساب
    def load_account_movements(self, account_code):
        try:
            # هنا يمكن إضافة استعلام لتحميل حركات الحساب من قاعدة البيانات
            # حالياً سنعرض بيانات وهمية
            movements_data = [
                ["01/01/2024", "رصيد افتتاحي", "REF001", "1000.00", "0.00", "1000.00"],
                ["15/01/2024", "دفعة من عميل", "REF002", "500.00", "0.00", "1500.00"],
                ["20/01/2024", "مصروف إداري", "REF003", "0.00", "200.00", "1300.00"]
            ]

            self.account_movements_table.setRowCount(len(movements_data))

            for row, data in enumerate(movements_data):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value))
                    if col in [3, 4, 5]:  # الأعمدة المالية
                        item.setTextAlignment(Qt.AlignCenter)
                        if col == 3 and float(value) > 0:  # مدين
                            item.setForeground(QBrush(QColor("#27ae60")))
                        elif col == 4 and float(value) > 0:  # دائن
                            item.setForeground(QBrush(QColor("#e74c3c")))

                    self.account_movements_table.setItem(row, col, item)

        except Exception as e:
            print(f"خطأ في تحميل حركات الحساب: {e}")

    # إضافة حساب جديد
    def add_new_account(self):
        try:
            dialog = AddAccountDialog(self)
            if dialog.exec() == QDialog.Accepted:
                self.setup_accounts_tree()
                QMessageBox.information(self, "نجح", "تم إضافة الحساب بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة الحساب:\n{str(e)}")

    # تعديل الحساب المحدد
    def edit_selected_account(self):
        try:
            current_item = self.accounts_tree.currentItem()
            if not current_item:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار حساب للتعديل")
                return

            account_data = current_item.data(0, Qt.UserRole)
            if account_data:
                dialog = AddAccountDialog(self, account_data)
                if dialog.exec() == QDialog.Accepted:
                    self.setup_accounts_tree()
                    QMessageBox.information(self, "نجح", "تم تعديل الحساب بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تعديل الحساب:\n{str(e)}")

    # حذف الحساب المحدد
    def delete_selected_account(self):
        try:
            current_item = self.accounts_tree.currentItem()
            if not current_item:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار حساب للحذف")
                return

            account_data = current_item.data(0, Qt.UserRole)
            if account_data:
                reply = QMessageBox.question(
                    self, "تأكيد الحذف",
                    f"هل أنت متأكد من حذف الحساب:\n{account_data['name']}؟",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # هنا يمكن إضافة كود حذف الحساب من قاعدة البيانات
                    self.setup_accounts_tree()
                    QMessageBox.information(self, "نجح", "تم حذف الحساب بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حذف الحساب:\n{str(e)}")

    # ===== وظائف القيود المحاسبية =====
    # تحميل القيود المحاسبية
    def load_journal_entries(self):
        try:
            # بيانات وهمية للقيود المحاسبية
            entries_data = [
                ["001", "01/01/2024", "رصيد افتتاحي", "النقدية", "10000.00", "0.00", "يدوي", "INIT001"],
                ["001", "01/01/2024", "رصيد افتتاحي", "رأس المال", "0.00", "10000.00", "يدوي", "INIT001"],
                ["002", "15/01/2024", "دفعة من مشروع", "النقدية", "5000.00", "0.00", "تلقائي", "PRJ001"],
                ["002", "15/01/2024", "دفعة من مشروع", "إيرادات المشاريع", "0.00", "5000.00", "تلقائي", "PRJ001"]
            ]

            self.journal_entries_table.setRowCount(len(entries_data))

            for row, data in enumerate(entries_data):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value))
                    if col in [4, 5]:  # مدين ودائن
                        item.setTextAlignment(Qt.AlignCenter)
                        if col == 4 and float(value) > 0:  # مدين
                            item.setForeground(QBrush(QColor("#27ae60")))
                        elif col == 5 and float(value) > 0:  # دائن
                            item.setForeground(QBrush(QColor("#e74c3c")))
                    elif col == 6:  # نوع القيد
                        if value == "تلقائي":
                            item.setForeground(QBrush(QColor("#3498db")))
                        elif value == "يدوي":
                            item.setForeground(QBrush(QColor("#f39c12")))

                    self.journal_entries_table.setItem(row, col, item)

        except Exception as e:
            print(f"خطأ في تحميل القيود المحاسبية: {e}")

    # فلترة القيود المحاسبية حسب النوع
    def filter_journal_entries(self):
        try:
            filter_type = self.entry_type_filter.currentText()
            # هنا يمكن إضافة كود الفلترة
            self.load_journal_entries()
        except Exception as e:
            print(f"خطأ في فلترة القيود: {e}")

    # إضافة قيد محاسبي جديد
    def add_journal_entry(self):
        try:
            dialog = AddJournalEntryDialog(self)
            if dialog.exec() == QDialog.Accepted:
                self.load_journal_entries()
                QMessageBox.information(self, "نجح", "تم إضافة القيد بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة القيد:\n{str(e)}")

    # تعديل قيد محاسبي
    def edit_journal_entry(self):
        try:
            current_row = self.journal_entries_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار قيد للتعديل")
                return

            # الحصول على بيانات القيد المحدد
            entry_data = {}
            for col in range(self.journal_entries_table.columnCount()):
                header = self.journal_entries_table.horizontalHeaderItem(col).text()
                item = self.journal_entries_table.item(current_row, col)
                entry_data[header] = item.text() if item else ""

            dialog = AddJournalEntryDialog(self, entry_data)
            if dialog.exec() == QDialog.Accepted:
                self.load_journal_entries()
                QMessageBox.information(self, "نجح", "تم تعديل القيد بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تعديل القيد:\n{str(e)}")

    # حذف قيد محاسبي
    def delete_journal_entry(self):
        try:
            current_row = self.journal_entries_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار قيد للحذف")
                return

            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا القيد؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # هنا يمكن إضافة كود حذف القيد من قاعدة البيانات
                self.load_journal_entries()
                QMessageBox.information(self, "نجح", "تم حذف القيد بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حذف القيد:\n{str(e)}")

    # ===== وظائف ربط المعاملات =====
    # تحميل المعاملات غير المربوطة
    def load_unlinked_transactions(self):
        try:
            conn = self.main_window.get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            unlinked_data = []

            # المشاريع - المدفوعات
            cursor.execute("""
                SELECT
                    CONCAT('PRJ_', p.id) as id,
                    'المشاريع' as section,
                    'دفعة مشروع' as type,
                    CONCAT('دفعة من مشروع: ', pr.اسم_المشروع) as description,
                    p.المبلغ_المدفوع as amount,
                    p.تاريخ_الدفع as date,
                    'غير مربوط' as status
                FROM المشاريع_المدفوعات p
                JOIN المشاريع pr ON p.معرف_المشروع = pr.id
                WHERE p.id NOT IN (SELECT معرف_المعاملة FROM القيود_المحاسبية WHERE نوع_المعاملة = 'دفعة_مشروع')
                LIMIT 10
            """)

            for row in cursor.fetchall():
                unlinked_data.append(list(row))

            # الموظفين - المعاملات المالية
            cursor.execute("""
                SELECT
                    CONCAT('EMP_', m.id) as id,
                    'الموظفين' as section,
                    m.نوع_المعاملة as type,
                    CONCAT(m.الوصف, ' - ', e.اسم_الموظف) as description,
                    m.المبلغ as amount,
                    m.التاريخ as date,
                    'غير مربوط' as status
                FROM الموظفين_معاملات_مالية m
                JOIN الموظفين e ON m.معرف_الموظف = e.id
                WHERE m.id NOT IN (SELECT معرف_المعاملة FROM القيود_المحاسبية WHERE نوع_المعاملة = 'معاملة_موظف')
                LIMIT 10
            """)

            for row in cursor.fetchall():
                unlinked_data.append(list(row))

            # المصروفات
            cursor.execute("""
                SELECT
                    CONCAT('EXP_', id) as id,
                    'الحسابات' as section,
                    'مصروف' as type,
                    المصروف as description,
                    المبلغ as amount,
                    تاريخ_المصروف as date,
                    'غير مربوط' as status
                FROM الحسابات
                WHERE id NOT IN (SELECT معرف_المعاملة FROM القيود_المحاسبية WHERE نوع_المعاملة = 'مصروف')
                LIMIT 10
            """)

            for row in cursor.fetchall():
                unlinked_data.append(list(row))

            # تحديث الجدول
            self.unlinked_transactions_table.setRowCount(len(unlinked_data))

            for row, data in enumerate(unlinked_data):
                for col, value in enumerate(data):
                    if col < 7:  # العمود الأخير للإجراء
                        item = QTableWidgetItem(str(value))
                        if col == 4:  # المبلغ
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setForeground(QBrush(QColor("#2ecc71")))
                        elif col == 6:  # الحالة
                            item.setForeground(QBrush(QColor("#e74c3c")))

                        self.unlinked_transactions_table.setItem(row, col, item)

                # إضافة زر الربط
                link_btn = QPushButton("ربط")
                link_btn.setIcon(qta.icon('fa5s.link', color='white'))
                link_btn.setObjectName("link_button")
                link_btn.clicked.connect(lambda checked, r=row: self.link_single_transaction(r))
                self.unlinked_transactions_table.setCellWidget(row, 7, link_btn)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل المعاملات غير المربوطة: {e}")

    # فلترة المعاملات غير المربوطة حسب القسم
    def filter_unlinked_transactions(self):
        try:
            filter_section = self.section_filter.currentText()
            # هنا يمكن إضافة كود الفلترة
            self.load_unlinked_transactions()
        except Exception as e:
            print(f"خطأ في فلترة المعاملات: {e}")

    # الربط التلقائي للمعاملات
    def auto_link_transactions(self):
        try:
            reply = QMessageBox.question(
                self, "تأكيد الربط التلقائي",
                "هل تريد ربط جميع المعاملات تلقائياً؟\nسيتم إنشاء قيود محاسبية تلقائية.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # هنا يمكن إضافة كود الربط التلقائي
                linked_count = 0  # عدد المعاملات المربوطة

                # محاكاة عملية الربط
                QMessageBox.information(
                    self, "نجح الربط التلقائي",
                    f"تم ربط {linked_count} معاملة تلقائياً"
                )

                self.load_unlinked_transactions()
                self.load_journal_entries()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في الربط التلقائي:\n{str(e)}")

    # الربط اليدوي للمعاملة
    def manual_link_transaction(self):
        try:
            current_row = self.unlinked_transactions_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار معاملة للربط")
                return

            self.link_single_transaction(current_row)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في الربط اليدوي:\n{str(e)}")

    # ربط معاملة واحدة
    def link_single_transaction(self, row):
        try:
            # الحصول على بيانات المعاملة
            transaction_data = {}
            for col in range(7):  # العمود الأخير للإجراء
                header = self.unlinked_transactions_table.horizontalHeaderItem(col).text()
                item = self.unlinked_transactions_table.item(row, col)
                transaction_data[header] = item.text() if item else ""

            dialog = LinkTransactionDialog(self, transaction_data)
            if dialog.exec() == QDialog.Accepted:
                self.load_unlinked_transactions()
                self.load_journal_entries()
                QMessageBox.information(self, "نجح", "تم ربط المعاملة بنجاح")

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في ربط المعاملة:\n{str(e)}")

    # إلغاء ربط معاملة
    def unlink_transaction(self):
        try:
            current_row = self.journal_entries_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار قيد لإلغاء ربطه")
                return

            reply = QMessageBox.question(
                self, "تأكيد إلغاء الربط",
                "هل أنت متأكد من إلغاء ربط هذا القيد؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # هنا يمكن إضافة كود إلغاء الربط
                self.load_unlinked_transactions()
                self.load_journal_entries()
                QMessageBox.information(self, "نجح", "تم إلغاء ربط القيد بنجاح")

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إلغاء الربط:\n{str(e)}")

    # ===== وظائف التقارير المالية =====
    # إنشاء قائمة الدخل
    def generate_income_statement(self):
        try:
            # الحصول على التواريخ من الفلاتر
            from_date = self.from_date.date().toPython()
            to_date = self.to_date.date().toPython()

            # إنشاء التقرير باستخدام النظام المتقدم
            report_html = self.advanced_reports.generate_income_statement(from_date, to_date)

            self.report_display.setHtml(report_html)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء قائمة الدخل:\n{str(e)}")

    # إنشاء الميزانية العمومية
    def generate_balance_sheet(self):
        try:
            # الحصول على تاريخ الميزانية
            as_of_date = self.to_date.date().toPython()

            # إنشاء التقرير باستخدام النظام المتقدم
            report_html = self.advanced_reports.generate_balance_sheet(as_of_date)

            self.report_display.setHtml(report_html)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء الميزانية العمومية:\n{str(e)}")

    # إنشاء تقرير التدفقات النقدية
    def generate_cash_flow(self):
        try:
            # الحصول على التواريخ من الفلاتر
            from_date = self.from_date.date().toPython()
            to_date = self.to_date.date().toPython()

            # إنشاء التقرير باستخدام النظام المتقدم
            report_html = self.advanced_reports.generate_cash_flow_statement(from_date, to_date)

            self.report_display.setHtml(report_html)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء تقرير التدفقات النقدية:\n{str(e)}")

    # إنشاء دفتر الأستاذ
    def generate_ledger(self):
        try:
            self.report_display.setPlainText("دفتر الأستاذ - قيد التطوير")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء دفتر الأستاذ:\n{str(e)}")

    # إنشاء ميزان المراجعة
    def generate_trial_balance(self):
        try:
            self.report_display.setPlainText("ميزان المراجعة - قيد التطوير")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء ميزان المراجعة:\n{str(e)}")

    # إنشاء تقرير الأرباح والخسائر
    def generate_profit_loss(self):
        try:
            self.report_display.setPlainText("تقرير الأرباح والخسائر - قيد التطوير")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء تقرير الأرباح والخسائر:\n{str(e)}")

    # ===== وظائف الإعدادات =====
    # حفظ إعدادات النظام
    def save_settings(self):
        try:
            # حفظ الإعدادات في قاعدة البيانات أو ملف الإعدادات
            QMessageBox.information(self, "نجح", "تم حفظ الإعدادات بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حفظ الإعدادات:\n{str(e)}")

    # إعادة تعيين الإعدادات
    def reset_settings(self):
        try:
            reply = QMessageBox.question(
                self, "تأكيد إعادة التعيين",
                "هل أنت متأكد من إعادة تعيين جميع الإعدادات؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # إعادة تعيين الإعدادات للقيم الافتراضية
                self.currency_combo.setCurrentIndex(0)
                self.fiscal_year_start.setDate(QDate.currentDate().addDays(-QDate.currentDate().dayOfYear() + 1))
                self.auto_linking_enabled.setChecked(True)

                QMessageBox.information(self, "نجح", "تم إعادة تعيين الإعدادات بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إعادة تعيين الإعدادات:\n{str(e)}")


# ===== نوافذ الحوار المساعدة =====

# نافذة حوار إضافة/تعديل حساب
class AddAccountDialog(QDialog):

    # init
    def __init__(self, parent, account_data=None):
        super().__init__(parent)
        self.account_data = account_data
        self.setWindowTitle("إضافة حساب جديد" if not account_data else "تعديل حساب")
        self.setModal(True)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(400, 300)

        self.setup_ui()

        if account_data:
            self.load_account_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # نموذج البيانات
        form_layout = QFormLayout()

        self.account_code_edit = QLineEdit()
        self.account_code_edit.setPlaceholderText("أدخل رمز الحساب")
        form_layout.addRow("رمز الحساب:", self.account_code_edit)

        self.account_name_edit = QLineEdit()
        self.account_name_edit.setPlaceholderText("أدخل اسم الحساب")
        form_layout.addRow("اسم الحساب:", self.account_name_edit)

        self.parent_account_combo = QComboBox()
        self.parent_account_combo.addItems(["1 - الأصول", "2 - الخصوم", "3 - حقوق الملكية", "4 - الإيرادات", "5 - المصروفات"])
        form_layout.addRow("الحساب الأب:", self.parent_account_combo)

        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems(["حساب رئيسي", "حساب فرعي", "حساب تفصيلي"])
        form_layout.addRow("نوع الحساب:", self.account_type_combo)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("أدخل وصف الحساب")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("الوصف:", self.description_edit)

        layout.addLayout(form_layout)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.setObjectName("save_button")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setObjectName("cancel_button")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    # تحميل بيانات الحساب للتعديل
    def load_account_data(self):
        if self.account_data:
            self.account_code_edit.setText(self.account_data.get('code', ''))
            self.account_name_edit.setText(self.account_data.get('name', ''))


# نافذة حوار إضافة/تعديل قيد محاسبي
class AddJournalEntryDialog(QDialog):

    # init
    def __init__(self, parent, entry_data=None):
        super().__init__(parent)
        self.entry_data = entry_data
        self.setWindowTitle("إضافة قيد محاسبي" if not entry_data else "تعديل قيد محاسبي")
        self.setModal(True)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(500, 400)

        self.setup_ui()

        if entry_data:
            self.load_entry_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # معلومات القيد الأساسية
        basic_info_layout = QFormLayout()

        self.entry_number_edit = QLineEdit()
        self.entry_number_edit.setPlaceholderText("رقم القيد")
        basic_info_layout.addRow("رقم القيد:", self.entry_number_edit)

        self.entry_date_edit = QDateEdit()
        self.entry_date_edit.setDate(QDate.currentDate())
        self.entry_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.entry_date_edit.setCalendarPopup(True)
        basic_info_layout.addRow("التاريخ:", self.entry_date_edit)

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("وصف القيد")
        basic_info_layout.addRow("البيان:", self.description_edit)

        layout.addLayout(basic_info_layout)

        # جدول تفاصيل القيد
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(4)
        self.entries_table.setHorizontalHeaderLabels(["الحساب", "البيان", "مدين", "دائن"])
        self.entries_table.setRowCount(2)  # صفين افتراضيين
        layout.addWidget(self.entries_table)

        # أزرار إضافة وحذف صف
        table_buttons_layout = QHBoxLayout()

        add_row_btn = QPushButton("إضافة صف")
        add_row_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_row_btn.clicked.connect(self.add_row)
        table_buttons_layout.addWidget(add_row_btn)

        remove_row_btn = QPushButton("حذف صف")
        remove_row_btn.setIcon(qta.icon('fa5s.minus', color='white'))
        remove_row_btn.clicked.connect(self.remove_row)
        table_buttons_layout.addWidget(remove_row_btn)

        table_buttons_layout.addStretch()
        layout.addLayout(table_buttons_layout)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.setObjectName("save_button")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setObjectName("cancel_button")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    # إضافة صف جديد للجدول
    def add_row(self):
        current_rows = self.entries_table.rowCount()
        self.entries_table.setRowCount(current_rows + 1)

    # حذف الصف المحدد
    def remove_row(self):
        current_row = self.entries_table.currentRow()
        if current_row >= 0 and self.entries_table.rowCount() > 2:
            self.entries_table.removeRow(current_row)

    # تحميل بيانات القيد للتعديل
    def load_entry_data(self):
        if self.entry_data:
            self.entry_number_edit.setText(self.entry_data.get('رقم القيد', ''))
            self.description_edit.setText(self.entry_data.get('البيان', ''))


# نافذة حوار ربط معاملة
class LinkTransactionDialog(QDialog):

    # init
    def __init__(self, parent, transaction_data):
        super().__init__(parent)
        self.transaction_data = transaction_data
        self.setWindowTitle("ربط معاملة مالية")
        self.setModal(True)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(450, 350)

        self.setup_ui()
        self.load_transaction_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # معلومات المعاملة
        transaction_info = QGroupBox("معلومات المعاملة")
        transaction_layout = QFormLayout(transaction_info)

        self.transaction_id_label = QLabel()
        transaction_layout.addRow("معرف المعاملة:", self.transaction_id_label)

        self.transaction_type_label = QLabel()
        transaction_layout.addRow("نوع المعاملة:", self.transaction_type_label)

        self.transaction_amount_label = QLabel()
        transaction_layout.addRow("المبلغ:", self.transaction_amount_label)

        layout.addWidget(transaction_info)

        # إعدادات الربط
        linking_settings = QGroupBox("إعدادات الربط")
        linking_layout = QFormLayout(linking_settings)

        self.debit_account_combo = QComboBox()
        self.debit_account_combo.addItems(["111 - النقدية والبنوك", "112 - العملاء والذمم المدينة", "411 - إيرادات المشاريع"])
        linking_layout.addRow("الحساب المدين:", self.debit_account_combo)

        self.credit_account_combo = QComboBox()
        self.credit_account_combo.addItems(["411 - إيرادات المشاريع", "211 - الموردين والذمم الدائنة", "111 - النقدية والبنوك"])
        linking_layout.addRow("الحساب الدائن:", self.credit_account_combo)

        self.entry_description_edit = QLineEdit()
        self.entry_description_edit.setPlaceholderText("وصف القيد المحاسبي")
        linking_layout.addRow("وصف القيد:", self.entry_description_edit)

        layout.addWidget(linking_settings)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()

        link_btn = QPushButton("ربط")
        link_btn.setObjectName("save_button")
        link_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(link_btn)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setObjectName("cancel_button")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    # تحميل بيانات المعاملة
    def load_transaction_data(self):
        if self.transaction_data:
            self.transaction_id_label.setText(self.transaction_data.get('المعرف', ''))
            self.transaction_type_label.setText(self.transaction_data.get('النوع', ''))
            self.transaction_amount_label.setText(f"{self.transaction_data.get('المبلغ', '0')} {Currency_type}")
            self.entry_description_edit.setText(self.transaction_data.get('الوصف', ''))


# فتح نافذة التقارير المالية
def open_financial_reports_window(main_window):
    try:
        # التحقق من وجود النافذة الرئيسية
        if not main_window:
            raise Exception("النافذة الرئيسية غير موجودة")

        # إنشاء النافذة
        window = FinancialReportsWindow(main_window)
        window.show()

        # حفظ مرجع للنافذة في النافذة الرئيسية لمنع إغلاقها تلقائياً
        if hasattr(main_window, 'financial_reports_window'):
            main_window.financial_reports_window = window

        return window

    except ImportError as e:
        error_msg = f"خطأ في استيراد المكتبات المطلوبة:\n{str(e)}\n\nتأكد من تثبيت جميع المتطلبات"
        if hasattr(main_window, 'show'):
            QMessageBox.critical(main_window, "خطأ في الاستيراد", error_msg)
        else:
            print(f"خطأ: {error_msg}")
        return None

    except Exception as e:
        error_msg = f"فشل في فتح نافذة التقارير المالية:\n{str(e)}"
        if hasattr(main_window, 'show'):
            QMessageBox.critical(main_window, "خطأ", error_msg)
        else:
            print(f"خطأ: {error_msg}")
        return None


# ويدجت التقارير المالية الشهرية والسنوية
class MonthlyAnnualReportsWidget(QWidget):

    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setLayoutDirection(Qt.RightToLeft)

        # متغيرات التحكم
        self.current_year = datetime.now().year
        self.months_arabic = [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ]

        self.setup_ui()
        self.apply_styles()
        self.load_annual_data()

    # إعداد واجهة المستخدم مع التخطيط الأفقي المحسن
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # الصف الأول: أزرار الإجراءات والفلاتر
        control_layout = self.create_control_bar()
        main_layout.addLayout(control_layout)

        # الصف الثاني: بطاقات الإحصائيات الملونة
        stats_layout = self.create_statistics_cards()
        main_layout.addLayout(stats_layout)

        # منطقة البطاقات الشهرية مع دعم RTL
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setLayoutDirection(Qt.RightToLeft)
        self.scroll_area.setObjectName("monthly_cards_scroll")

        # حاوية البطاقات مع ترتيب RTL
        self.cards_container = QWidget()
        self.cards_container.setLayoutDirection(Qt.RightToLeft)
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)

    # إنشاء شريط التحكم العلوي مع التخطيط الأفقي
    def create_control_bar(self):
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        # فلتر السنة مع تخطيط أفقي
        year_label = QLabel("السنة المالية:")
        year_label.setObjectName("filter_label")

        self.year_combo = QComboBox()
        self.year_combo.setObjectName("year_filter")
        # إضافة السنوات (السنة الحالية ± 5 سنوات)
        for year in range(self.current_year - 5, self.current_year + 6):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.on_year_changed)

        # أزرار الإجراءات
        refresh_btn = QPushButton("تحديث البيانات")
        refresh_btn.setIcon(qta.icon('fa5s.sync', color='white'))
        refresh_btn.setObjectName("refresh_button")
        refresh_btn.clicked.connect(self.refresh_data)

        export_btn = QPushButton("تصدير Excel")
        export_btn.setIcon(qta.icon('fa5s.file-excel', color='white'))
        export_btn.setObjectName("export_button")
        export_btn.clicked.connect(self.export_to_excel)

        # زر الطباعة البرتقالي الموحد
        print_btn = QPushButton("طباعة")
        print_btn.setIcon(qta.icon('fa5s.print', color='white'))
        print_btn.setObjectName("print_button")
        print_btn.clicked.connect(self.print_reports)

        # ترتيب العناصر أفقياً
        control_layout.addWidget(year_label)
        control_layout.addWidget(self.year_combo)
        control_layout.addStretch()
        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(export_btn)
        control_layout.addWidget(print_btn)

        return control_layout

    # إنشاء بطاقات الإحصائيات الملونة مع التخطيط الأفقي
    def create_statistics_cards(self):
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # بيانات الإحصائيات مع الألوان الموحدة
        stats_data = [
            ("إجمالي الإيرادات السنوية", "0.00", "#3498db", "fa5s.arrow-up"),
            ("إجمالي المصروفات السنوية", "0.00", "#e74c3c", "fa5s.arrow-down"),
            ("صافي الربح السنوي", "0.00", "#27ae60", "fa5s.chart-line"),
            ("متوسط الربح الشهري", "0.00", "#f39c12", "fa5s.calculator"),
            ("عدد المشاريع المكتملة", "0", "#9b59b6", "fa5s.check-circle")
        ]

        self.stats_cards = {}

        for title, value, color, icon in stats_data:
            card = self.create_stat_card(title, value, color, icon)
            self.stats_cards[title] = card
            stats_layout.addWidget(card)

        return stats_layout

    # إنشاء بطاقة إحصائية واحدة مع التخطيط الأفقي
    def create_stat_card(self, title, value, color, icon):
        card = QFrame()
        card.setObjectName("financial_stats_card")
        card.setFrameStyle(QFrame.Box)

        # تخطيط أفقي للبطاقة - العنوان والقيمة في نفس السطر
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(10)

        # الأيقونة
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(24, 24))
        card_layout.addWidget(icon_label)

        # النص والقيمة في نفس السطر
        title_label = QLabel(title + ":")
        title_label.setObjectName("stats_title")
        card_layout.addWidget(title_label)

        value_label = QLabel(f"{value} {Currency_type}")
        value_label.setObjectName("stats_value")
        value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(value_label)

        card_layout.addStretch()

        return card

    # تحميل البيانات السنوية وإنشاء البطاقات
    def load_annual_data(self):
        try:
            # مسح البطاقات الموجودة
            self.clear_cards()

            # تحديث الإحصائيات السنوية
            self.update_annual_statistics()

            # إنشاء بطاقة ملخص السنة أولاً
            annual_summary = self.get_annual_summary()
            annual_card = self.create_annual_summary_card(annual_summary)
            self.cards_layout.addWidget(annual_card)

            # تحديد الشهور المراد عرضها
            selected_year = int(self.year_combo.currentText())
            current_year = datetime.now().year
            current_month = datetime.now().month

            # إذا كانت السنة المختارة هي السنة الحالية، عرض الشهور حتى الشهر الحالي
            # إذا كانت سنة سابقة، عرض جميع الشهور
            if selected_year == current_year:
                end_month = current_month
            else:
                end_month = 12

            # إنشاء البطاقات الشهرية (من يناير إلى الشهر المحدد)
            cards_added = 0
            for month_num in range(1, end_month + 1):
                month_data = self.get_monthly_data(month_num)
                # عرض البطاقة فقط إذا كان هناك بيانات (إيرادات أو مصروفات)
                if (month_data['monthly_revenue'] > 0 or month_data['monthly_expenses'] > 0 or
                    month_data['new_projects'] > 0 or month_data['completed_projects'] > 0):
                    month_card = self.create_monthly_card(month_num, month_data)
                    self.cards_layout.addWidget(month_card)
                    cards_added += 1

            # إذا لم تتم إضافة أي بطاقات شهرية، عرض رسالة
            if cards_added == 0:
                no_data_card = self.create_no_data_card()
                self.cards_layout.addWidget(no_data_card)

            # إضافة مساحة مرنة في النهاية
            self.cards_layout.addStretch()

        except Exception as e:
            print(f"خطأ في تحميل البيانات السنوية: {e}")
            self.show_error_message("فشل في تحميل البيانات السنوية")

    # مسح جميع البطاقات الموجودة
    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # تحديث الإحصائيات السنوية
    def update_annual_statistics(self):
        try:
            # محاولة الحصول على اتصال قاعدة البيانات
            if hasattr(self.parent_window, 'get_db_connection'):
                conn = self.parent_window.get_db_connection()
            elif hasattr(self.parent_window, 'main_window') and hasattr(self.parent_window.main_window, 'get_db_connection'):
                conn = self.parent_window.main_window.get_db_connection()
            else:
                print("لا يمكن الحصول على اتصال قاعدة البيانات")
                return

            if not conn:
                return

            cursor = conn.cursor()

            # حساب إجمالي الإيرادات السنوية من جميع الأقسام
            cursor.execute("""
                SELECT COALESCE(SUM(المدفوع), 0) as total_revenue
                FROM المشاريع
                WHERE YEAR(تاريخ_التسليم) = %s
            """, (self.current_year,))
            total_revenue = cursor.fetchone()[0] or 0

            # إضافة إيرادات التدريب
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0) as training_revenue
                FROM التدريب_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (self.current_year,))
            training_revenue = cursor.fetchone()[0] or 0
            total_revenue += training_revenue

            # حساب إجمالي المصروفات السنوية
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_expenses
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (self.current_year,))
            total_expenses = cursor.fetchone()[0] or 0

            # حساب صافي الربح
            net_profit = total_revenue - total_expenses

            # حساب متوسط الربح الشهري
            avg_monthly_profit = net_profit / 12

            # حساب عدد المشاريع المكتملة
            cursor.execute("""
                SELECT COUNT(*) as completed_projects
                FROM المشاريع
                WHERE حالة_المشروع = 'مكتمل' AND YEAR(تاريخ_التسليم) = %s
            """, (self.current_year,))
            completed_projects = cursor.fetchone()[0] or 0

            # تحديث البطاقات
            self.update_stat_card("إجمالي الإيرادات السنوية", f"{total_revenue:,.2f}")
            self.update_stat_card("إجمالي المصروفات السنوية", f"{total_expenses:,.2f}")
            self.update_stat_card("صافي الربح السنوي", f"{net_profit:,.2f}")
            self.update_stat_card("متوسط الربح الشهري", f"{avg_monthly_profit:,.2f}")
            self.update_stat_card("عدد المشاريع المكتملة", str(completed_projects))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات السنوية: {e}")

    # تحديث قيمة بطاقة إحصائية
    def update_stat_card(self, title, value):
        if hasattr(self, 'stats_cards') and title in self.stats_cards:
            card = self.stats_cards[title]
            # البحث عن label القيمة وتحديثه
            for child in card.findChildren(QLabel):
                if child.objectName() == "stats_value":
                    if title == "عدد المشاريع المكتملة":
                        child.setText(value)
                    else:
                        child.setText(f"{value} {Currency_type}")
                    break

    # الحصول على ملخص السنة المالية الشامل من جميع أقسام التطبيق
    def get_annual_summary(self):
        try:
            # محاولة الحصول على اتصال قاعدة البيانات
            if hasattr(self.parent_window, 'get_db_connection'):
                conn = self.parent_window.get_db_connection()
            elif hasattr(self.parent_window, 'main_window') and hasattr(self.parent_window.main_window, 'get_db_connection'):
                conn = self.parent_window.main_window.get_db_connection()
            else:
                print("⚠️ لا يمكن الحصول على اتصال قاعدة البيانات")
                return self.get_default_annual_summary()
            cursor = conn.cursor()

            year = int(self.year_combo.currentText())

            # === حساب الإيرادات من جميع الأقسام ===

            # إيرادات المشاريع والمقاولات (من المدفوعات الفعلية)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0) as project_payments
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (year,))
            project_payments = cursor.fetchone()[0] or 0

            # إيرادات التدريب (من دفعات الطلاب)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0) as training_revenue
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s
            """, (year,))
            training_revenue = cursor.fetchone()[0] or 0

            # إيرادات العهد المالية (دفعات العهد)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as custody_revenue
                FROM المقاولات_دفعات_العهد
                WHERE YEAR(تاريخ_الدفعة) = %s
            """, (year,))
            custody_revenue = cursor.fetchone()[0] or 0

            # إجمالي الإيرادات
            total_revenue = project_payments + training_revenue + custody_revenue

            # === حساب المصروفات من جميع الأقسام ===

            # المصروفات الإدارية العامة
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as admin_expenses
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (year,))
            admin_expenses = cursor.fetchone()[0] or 0

            # رواتب الموظفين (جميع أنواع المعاملات المالية للموظفين)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as employee_expenses
                FROM الموظفين_معاملات_مالية
                WHERE نوع_العملية IN ('إيداع', 'خصم') AND YEAR(التاريخ) = %s
            """, (year,))
            employee_expenses = cursor.fetchone()[0] or 0

            # مصروفات المشاريع والعهد
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as project_expenses
                FROM المقاولات_مصروفات_العهد
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (year,))
            project_expenses = cursor.fetchone()[0] or 0

            # مصروفات التدريب
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as training_expenses
                FROM التدريب_مصروفات
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (year,))
            training_expenses = cursor.fetchone()[0] or 0

            # مدفوعات الموردين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as supplier_payments
                FROM الحسابات_دفعات_الموردين
                WHERE YEAR(تاريخ_الدفعة) = %s
            """, (year,))
            supplier_payments = cursor.fetchone()[0] or 0

            # إجمالي المصروفات
            total_expenses = admin_expenses + employee_expenses + project_expenses + training_expenses + supplier_payments

            # === حساب الإحصائيات الإضافية ===

            # عدد المشاريع الجديدة
            cursor.execute("""
                SELECT COUNT(*) as projects_count
                FROM المشاريع
                WHERE YEAR(تاريخ_الإستلام) = %s
            """, (year,))
            projects_count = cursor.fetchone()[0] or 0

            # عدد الدورات التدريبية
            cursor.execute("""
                SELECT COUNT(*) as training_courses
                FROM التدريب
                WHERE YEAR(تاريخ_البدء) = %s
            """, (year,))
            training_courses = cursor.fetchone()[0] or 0

            # عدد الموظفين النشطين
            cursor.execute("""
                SELECT COUNT(*) as active_employees
                FROM الموظفين
                WHERE الحالة = 'نشط'
            """, ())
            active_employees = cursor.fetchone()[0] or 0

            # إجمالي المستحقات (الباقي من المشاريع)
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي), 0) as total_remaining
                FROM المشاريع
                WHERE الباقي > 0
            """, ())
            total_remaining = cursor.fetchone()[0] or 0

            # إجمالي الخسائر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_losses
                FROM المقاولات_مصروفات_العهد
                WHERE نوع_المصروف = 'خسائر' AND YEAR(تاريخ_المصروف) = %s
            """, (year,))
            total_losses = cursor.fetchone()[0] or 0

            # إجمالي المردودات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_returns
                FROM المقاولات_مصروفات_العهد
                WHERE نوع_المصروف = 'مردودات' AND YEAR(تاريخ_المصروف) = %s
            """, (year,))
            total_returns = cursor.fetchone()[0] or 0

            cursor.close()

            # حساب صافي الربح
            net_profit = total_revenue - total_expenses

            return {
                'total_revenue': total_revenue,
                'project_payments': project_payments,
                'training_revenue': training_revenue,
                'custody_revenue': custody_revenue,
                'total_expenses': total_expenses,
                'admin_expenses': admin_expenses,
                'employee_expenses': employee_expenses,
                'project_expenses': project_expenses,
                'training_expenses': training_expenses,
                'supplier_payments': supplier_payments,
                'net_profit': net_profit,
                'projects_count': projects_count,
                'training_courses': training_courses,
                'active_employees': active_employees,
                'total_remaining': total_remaining,
                'total_losses': total_losses,
                'total_returns': total_returns
            }

        except Exception as e:
            print(f"خطأ في الحصول على ملخص السنة: {e}")
            return {
                'total_revenue': 0, 'project_payments': 0, 'training_revenue': 0, 'custody_revenue': 0,
                'total_expenses': 0, 'admin_expenses': 0, 'employee_expenses': 0, 'project_expenses': 0,
                'training_expenses': 0, 'supplier_payments': 0, 'net_profit': 0, 'projects_count': 0,
                'training_courses': 0, 'active_employees': 0, 'total_remaining': 0, 'total_losses': 0,
                'total_returns': 0
            }

    # إرجاع بيانات افتراضية للملخص السنوي
    def get_default_annual_summary(self):
        return {
            'total_revenue': 0, 'project_payments': 0, 'training_revenue': 0, 'custody_revenue': 0,
            'total_expenses': 0, 'admin_expenses': 0, 'employee_expenses': 0, 'project_expenses': 0,
            'training_expenses': 0, 'supplier_payments': 0, 'net_profit': 0, 'projects_count': 0,
            'training_courses': 0, 'active_employees': 0, 'total_remaining': 0, 'total_losses': 0,
            'total_returns': 0
        }

    # الحصول على البيانات الشهرية الشاملة من جميع أقسام التطبيق
    def get_monthly_data(self, month_num):
        try:
            # محاولة الحصول على اتصال قاعدة البيانات
            if hasattr(self.parent_window, 'get_db_connection'):
                conn = self.parent_window.get_db_connection()
            elif hasattr(self.parent_window, 'main_window') and hasattr(self.parent_window.main_window, 'get_db_connection'):
                conn = self.parent_window.main_window.get_db_connection()
            else:
                print("⚠️ لا يمكن الحصول على اتصال قاعدة البيانات")
                return self.get_default_monthly_data()
            cursor = conn.cursor()

            year = int(self.year_combo.currentText())

            # === حساب الإيرادات الشهرية من جميع الأقسام ===

            # إيرادات المشاريع والمقاولات (من المدفوعات الفعلية)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0) as project_revenue
                FROM المشاريع_المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month_num))
            project_revenue = cursor.fetchone()[0] or 0

            # إيرادات التدريب (من دفعات الطلاب)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0) as training_revenue
                FROM التدريب_دفعات_الطلاب
                WHERE YEAR(تاريخ_الدفع) = %s AND MONTH(تاريخ_الدفع) = %s
            """, (year, month_num))
            training_revenue = cursor.fetchone()[0] or 0

            # إيرادات العهد المالية
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as custody_revenue
                FROM المقاولات_دفعات_العهد
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month_num))
            custody_revenue = cursor.fetchone()[0] or 0

            # إجمالي الإيرادات الشهرية
            monthly_revenue = project_revenue + training_revenue + custody_revenue

            # === حساب المصروفات الشهرية من جميع الأقسام ===

            # المصروفات الإدارية العامة
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as admin_expenses
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month_num))
            admin_expenses = cursor.fetchone()[0] or 0

            # مصروفات الموظفين (رواتب ومعاملات مالية)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as employee_expenses
                FROM الموظفين_معاملات_مالية
                WHERE نوع_العملية IN ('إيداع', 'خصم')
                AND YEAR(التاريخ) = %s AND MONTH(التاريخ) = %s
            """, (year, month_num))
            employee_expenses = cursor.fetchone()[0] or 0

            # مصروفات المشاريع والعهد
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as project_expenses
                FROM المقاولات_مصروفات_العهد
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month_num))
            project_expenses = cursor.fetchone()[0] or 0

            # مصروفات التدريب
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as training_expenses
                FROM التدريب_مصروفات
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month_num))
            training_expenses = cursor.fetchone()[0] or 0

            # مدفوعات الموردين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as supplier_payments
                FROM الحسابات_دفعات_الموردين
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month_num))
            supplier_payments = cursor.fetchone()[0] or 0

            # إجمالي المصروفات الشهرية
            monthly_expenses = admin_expenses + employee_expenses + project_expenses + training_expenses + supplier_payments

            # === حساب الإحصائيات الشهرية ===

            # عدد المشاريع الجديدة في الشهر
            cursor.execute("""
                SELECT COUNT(*) as new_projects
                FROM المشاريع
                WHERE YEAR(تاريخ_الإستلام) = %s AND MONTH(تاريخ_الإستلام) = %s
            """, (year, month_num))
            new_projects = cursor.fetchone()[0] or 0

            # عدد المشاريع المكتملة في الشهر
            cursor.execute("""
                SELECT COUNT(*) as completed_projects
                FROM المشاريع
                WHERE الحالة IN ('تم التسليم', 'منتهي')
                AND YEAR(تاريخ_التسليم) = %s AND MONTH(تاريخ_التسليم) = %s
            """, (year, month_num))
            completed_projects = cursor.fetchone()[0] or 0

            # عدد الدورات التدريبية الجديدة
            cursor.execute("""
                SELECT COUNT(*) as new_training_courses
                FROM التدريب
                WHERE YEAR(تاريخ_البدء) = %s AND MONTH(تاريخ_البدء) = %s
            """, (year, month_num))
            new_training_courses = cursor.fetchone()[0] or 0

            # الخسائر الشهرية
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as monthly_losses
                FROM المقاولات_مصروفات_العهد
                WHERE نوع_المصروف = 'خسائر'
                AND YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month_num))
            monthly_losses = cursor.fetchone()[0] or 0

            # المردودات الشهرية
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as monthly_returns
                FROM المقاولات_مصروفات_العهد
                WHERE نوع_المصروف = 'مردودات'
                AND YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month_num))
            monthly_returns = cursor.fetchone()[0] or 0

            cursor.close()

            # حساب صافي ربح الشهر
            monthly_net_profit = monthly_revenue - monthly_expenses

            return {
                'monthly_revenue': monthly_revenue,
                'project_revenue': project_revenue,
                'training_revenue': training_revenue,
                'custody_revenue': custody_revenue,
                'monthly_expenses': monthly_expenses,
                'admin_expenses': admin_expenses,
                'employee_expenses': employee_expenses,
                'project_expenses': project_expenses,
                'training_expenses': training_expenses,
                'supplier_payments': supplier_payments,
                'monthly_net_profit': monthly_net_profit,
                'new_projects': new_projects,
                'completed_projects': completed_projects,
                'new_training_courses': new_training_courses,
                'monthly_losses': monthly_losses,
                'monthly_returns': monthly_returns
            }

        except Exception as e:
            print(f"خطأ في الحصول على البيانات الشهرية للشهر {month_num}: {e}")
            return {
                'monthly_revenue': 0, 'project_revenue': 0, 'training_revenue': 0, 'custody_revenue': 0,
                'monthly_expenses': 0, 'admin_expenses': 0, 'employee_expenses': 0, 'project_expenses': 0,
                'training_expenses': 0, 'supplier_payments': 0, 'monthly_net_profit': 0, 'new_projects': 0,
                'completed_projects': 0, 'new_training_courses': 0, 'monthly_losses': 0, 'monthly_returns': 0
            }

    # إرجاع بيانات افتراضية للبيانات الشهرية
    def get_default_monthly_data(self):
        return {
            'monthly_revenue': 0, 'project_revenue': 0, 'training_revenue': 0, 'custody_revenue': 0,
            'monthly_expenses': 0, 'admin_expenses': 0, 'employee_expenses': 0, 'project_expenses': 0,
            'training_expenses': 0, 'supplier_payments': 0, 'monthly_net_profit': 0, 'new_projects': 0,
            'completed_projects': 0, 'new_training_courses': 0, 'monthly_losses': 0, 'monthly_returns': 0
        }

    # إنشاء بطاقة ملخص السنة الشاملة
    def create_annual_summary_card(self, data):
        card = QFrame()
        card.setObjectName("annual_summary_card")
        card.setFixedSize(350, 600)
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # عنوان البطاقة
        title = QLabel(f"📊 ملخص السنة {self.year_combo.currentText()}")
        title.setObjectName("card_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # خط فاصل
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # قسم الإيرادات
        revenue_section = QLabel("💰 الإيرادات")
        revenue_section.setObjectName("section_title")
        layout.addWidget(revenue_section)

        revenue_info = [
            ("إيرادات المشاريع:", data['project_payments'], "#3498db"),
            ("إيرادات التدريب:", data['training_revenue'], "#9b59b6"),
            ("إيرادات العهد:", data['custody_revenue'], "#1abc9c"),
            ("إجمالي الإيرادات:", data['total_revenue'], "#2980b9")
        ]

        for label_text, value, color in revenue_info:
            info_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("info_label")
            value_label = QLabel(f"{value:,.0f} {Currency_type}")
            value_label.setObjectName("info_value")
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignLeft)
            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        # خط فاصل
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # قسم المصروفات
        expenses_section = QLabel("💸 المصروفات")
        expenses_section.setObjectName("section_title")
        layout.addWidget(expenses_section)

        expenses_info = [
            ("المصروفات الإدارية:", data['admin_expenses'], "#e74c3c"),
            ("مصروفات الموظفين:", data['employee_expenses'], "#f39c12"),
            ("مصروفات المشاريع:", data['project_expenses'], "#e67e22"),
            ("مصروفات التدريب:", data['training_expenses'], "#8e44ad"),
            ("مدفوعات الموردين:", data['supplier_payments'], "#c0392b"),
            ("إجمالي المصروفات:", data['total_expenses'], "#a93226")
        ]

        for label_text, value, color in expenses_info:
            info_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("info_label")
            value_label = QLabel(f"{value:,.0f} {Currency_type}")
            value_label.setObjectName("info_value")
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignLeft)
            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        # خط فاصل
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line3)

        # صافي الربح
        profit_layout = QHBoxLayout()
        profit_label = QLabel("📈 صافي الربح:")
        profit_label.setObjectName("profit_label")
        profit_value = QLabel(f"{data['net_profit']:,.0f} {Currency_type}")
        profit_value.setObjectName("profit_value")
        profit_color = "#27ae60" if data['net_profit'] >= 0 else "#e74c3c"
        profit_value.setStyleSheet(f"color: {profit_color}; font-weight: bold; font-size: 14px;")
        profit_value.setAlignment(Qt.AlignLeft)
        profit_layout.addWidget(profit_label)
        profit_layout.addWidget(profit_value)
        layout.addLayout(profit_layout)

        # خط فاصل
        line4 = QFrame()
        line4.setFrameShape(QFrame.HLine)
        line4.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line4)

        # الإحصائيات
        stats_section = QLabel("📊 الإحصائيات")
        stats_section.setObjectName("section_title")
        layout.addWidget(stats_section)

        stats_info = [
            ("🏗️ عدد المشاريع:", data['projects_count']),
            ("🎓 عدد الدورات:", data['training_courses']),
            ("👥 عدد الموظفين:", data['active_employees']),
            ("📋 المستحقات:", f"{data['total_remaining']:,.0f} {Currency_type}"),
            ("⚠️ الخسائر:", f"{data['total_losses']:,.0f} {Currency_type}"),
            ("🔄 المردودات:", f"{data['total_returns']:,.0f} {Currency_type}")
        ]

        for label_text, value in stats_info:
            info_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("info_label")
            if isinstance(value, str):
                value_label = QLabel(value)
            else:
                value_label = QLabel(str(value))
            value_label.setObjectName("info_value")
            value_label.setAlignment(Qt.AlignLeft)
            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        layout.addStretch()
        return card

    # إنشاء بطاقة شهرية شاملة
    def create_monthly_card(self, month_num, data):
        card = QFrame()
        card.setObjectName("monthly_card")
        card.setFixedSize(320, 550)
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(1)

        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # عنوان الشهر
        month_name = self.months_arabic[month_num - 1]
        title = QLabel(f"📅 {month_name}")
        title.setObjectName("month_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # خط فاصل
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # قسم الإيرادات
        revenue_section = QLabel("💰 الإيرادات")
        revenue_section.setObjectName("section_title")
        layout.addWidget(revenue_section)

        revenue_info = [
            ("إيرادات المشاريع:", data['project_revenue'], "#3498db"),
            ("إيرادات التدريب:", data['training_revenue'], "#9b59b6"),
            ("إيرادات العهد:", data['custody_revenue'], "#1abc9c"),
            ("إجمالي الإيرادات:", data['monthly_revenue'], "#2980b9")
        ]

        for label_text, value, color in revenue_info:
            info_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("monthly_info_label")
            value_label = QLabel(f"{value:,.0f} {Currency_type}")
            value_label.setObjectName("monthly_info_value")
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignLeft)
            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        # قسم المصروفات
        expenses_section = QLabel("💸 المصروفات")
        expenses_section.setObjectName("section_title")
        layout.addWidget(expenses_section)

        expenses_info = [
            ("المصروفات الإدارية:", data['admin_expenses'], "#e74c3c"),
            ("مصروفات الموظفين:", data['employee_expenses'], "#f39c12"),
            ("مصروفات المشاريع:", data['project_expenses'], "#e67e22"),
            ("مصروفات التدريب:", data['training_expenses'], "#8e44ad"),
            ("مدفوعات الموردين:", data['supplier_payments'], "#c0392b"),
            ("إجمالي المصروفات:", data['monthly_expenses'], "#a93226")
        ]

        for label_text, value, color in expenses_info:
            info_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("monthly_info_label")
            value_label = QLabel(f"{value:,.0f} {Currency_type}")
            value_label.setObjectName("monthly_info_value")
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignLeft)
            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        # صافي الربح
        profit_layout = QHBoxLayout()
        profit_label = QLabel("📈 صافي الربح:")
        profit_label.setObjectName("monthly_info_label")
        profit_value = QLabel(f"{data['monthly_net_profit']:,.0f} {Currency_type}")
        profit_value.setObjectName("monthly_info_value")
        profit_color = "#27ae60" if data['monthly_net_profit'] >= 0 else "#e74c3c"
        profit_value.setStyleSheet(f"color: {profit_color}; font-weight: bold; font-size: 13px;")
        profit_value.setAlignment(Qt.AlignLeft)
        profit_layout.addWidget(profit_label)
        profit_layout.addWidget(profit_value)
        layout.addLayout(profit_layout)

        # خط فاصل
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # الإحصائيات
        stats_section = QLabel("📊 الإحصائيات")
        stats_section.setObjectName("section_title")
        layout.addWidget(stats_section)

        stats_info = [
            ("🏗️ مشاريع جديدة:", data['new_projects']),
            ("✅ مشاريع مكتملة:", data['completed_projects']),
            ("🎓 دورات جديدة:", data['new_training_courses']),
            ("⚠️ خسائر:", f"{data['monthly_losses']:,.0f} {Currency_type}"),
            ("🔄 مردودات:", f"{data['monthly_returns']:,.0f} {Currency_type}")
        ]

        for label_text, value in stats_info:
            info_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("monthly_info_label")
            if isinstance(value, str):
                value_label = QLabel(value)
            else:
                value_label = QLabel(str(value))
            value_label.setObjectName("monthly_info_value")
            value_label.setAlignment(Qt.AlignLeft)
            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        layout.addStretch()
        return card

    # إنشاء بطاقة عدم وجود بيانات
    def create_no_data_card(self):
        card = QFrame()
        card.setObjectName("no_data_card")
        card.setFixedSize(300, 200)
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(1)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # أيقونة
        icon_label = QLabel("📊")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label)

        # رسالة
        message_label = QLabel("لا توجد بيانات مالية\nللشهور المنقضية")
        message_label.setObjectName("no_data_message")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            font-weight: bold;
            line-height: 1.5;
        """)
        layout.addWidget(message_label)

        # نصيحة
        tip_label = QLabel("ابدأ بإدخال المعاملات المالية\nلعرض التقارير الشهرية")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("""
            font-size: 12px;
            color: #95a5a6;
            font-style: italic;
        """)
        layout.addWidget(tip_label)

        layout.addStretch()
        return card

    # تطبيق الأنماط المحسنة مع نظام الأسلوب المركزي
    def apply_styles(self):
        # تطبيق الأسلوب المركزي من ملف ستايل.py
        apply_stylesheet(self)

        # إضافة أنماط خاصة بالتقارير المالية
        self.setStyleSheet("""
            /* بطاقات الإحصائيات المالية */
            QFrame#financial_stats_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
            }

            QFrame#financial_stats_card:hover {
                border-color: #3498db;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f8ff, stop: 1 #e6f3ff);
            }

            /* بطاقة ملخص السنة */
            QFrame#annual_summary_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                border: 3px solid #3498db;
                border-radius: 12px;
                margin: 8px;
                border-bottom: 4px solid rgba(52, 152, 219, 0.3);
                border-right: 2px solid rgba(52, 152, 219, 0.2);
            }

            /* البطاقات الشهرية */
            QFrame#monthly_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin: 5px;
            }

            QFrame#monthly_card:hover {
                border-color: #3498db;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f8ff, stop: 1 #e6f3ff);
            }

            /* عناوين البطاقات */
            QLabel#card_title {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border-radius: 6px;
                margin-bottom: 5px;
            }

            QLabel#month_title {
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                border-radius: 5px;
                margin-bottom: 3px;
            }

            /* عناوين الأقسام */
            QLabel#section_title {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                margin-top: 8px;
                margin-bottom: 4px;
                padding: 3px 6px;
                background-color: #ecf0f1;
                border-radius: 3px;
                border-left: 3px solid #3498db;
            }

            /* تسميات المعلومات */
            QLabel#info_label, QLabel#monthly_info_label {
                font-size: 11px;
                color: #2c3e50;
                font-weight: normal;
                padding: 2px;
            }

            /* قيم المعلومات */
            QLabel#info_value, QLabel#monthly_info_value {
                font-size: 11px;
                font-weight: bold;
                padding: 2px;
            }

            /* تسميات الربح */
            QLabel#profit_label {
                font-size: 13px;
                color: #2c3e50;
                font-weight: bold;
                padding: 3px;
            }

            QLabel#profit_value {
                font-size: 13px;
                font-weight: bold;
                padding: 3px;
            }

            /* أزرار التحكم */
            QPushButton#refresh_button {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #229954);
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton#refresh_button:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ecc71, stop: 1 #27ae60);
            }

            QPushButton#print_button {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e67e22, stop: 1 #d35400);
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton#print_button:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f39c12, stop: 1 #e67e22);
            }

            QPushButton#export_button {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8e44ad, stop: 1 #7d3c98);
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton#export_button:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #9b59b6, stop: 1 #8e44ad);
            }

            /* تسميات التحكم */
            QLabel#control_label {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }

            /* كومبو بوكس السنة */
            QComboBox#year_combo {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 120px;
                font-size: 13px;
                font-weight: bold;
            }

            QComboBox#year_combo:focus {
                border-color: #3498db;
            }

            /* منطقة التمرير */
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }

            /* بطاقة عدم وجود البيانات */
            QFrame#no_data_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                margin: 5px;
            }

            QLabel#no_data_message {
                font-size: 14px;
                color: #7f8c8d;
                font-weight: bold;
            }
        """)

    # معالجة تغيير السنة المالية
    def on_year_changed(self):
        self.load_annual_data()

    # تحديث البيانات
    def refresh_data(self):
        self.load_annual_data()
        self.show_success_message("تم تحديث البيانات بنجاح")

    # طباعة التقارير
    def print_reports(self):
        try:
            # يمكن إضافة نظام الطباعة الموحد هنا
            self.show_info_message("سيتم تطوير نظام الطباعة قريباً")
        except Exception as e:
            self.show_error_message(f"خطأ في الطباعة: {str(e)}")

    # تصدير التقارير إلى Excel
    def export_to_excel(self):
        try:
            # يمكن إضافة نظام التصدير هنا
            self.show_info_message("سيتم تطوير نظام التصدير قريباً")
        except Exception as e:
            self.show_error_message(f"خطأ في التصدير: {str(e)}")

    # عرض رسالة نجاح
    def show_success_message(self, message):
        QMessageBox.information(self, "نجح", message)

    # عرض رسالة خطأ
    def show_error_message(self, message):
        QMessageBox.critical(self, "خطأ", message)

    # عرض رسالة معلومات
    def show_info_message(self, message):
        QMessageBox.information(self, "معلومات", message)

    # عند تغيير السنة المالية
    def on_year_changed(self):
        try:
            self.current_year = int(self.year_combo.currentText())
            self.load_annual_data()
        except Exception as e:
            print(f"خطأ في تغيير السنة: {e}")

    # تحديث البيانات
    def refresh_data(self):
        try:
            self.load_annual_data()
            self.show_success_message("تم تحديث البيانات بنجاح")
        except Exception as e:
            self.show_error_message(f"فشل في تحديث البيانات: {str(e)}")

    # طباعة التقارير
    def print_reports(self):
        try:
            # يمكن إضافة نظام الطباعة الموحد هنا
            self.show_info_message("سيتم تطوير نظام الطباعة قريباً")
        except Exception as e:
            self.show_error_message(f"خطأ في الطباعة: {str(e)}")

    # عرض رسالة معلومات
    def show_info_message(self, message):
        QMessageBox.information(self, "معلومات", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # محاكاة النافذة الرئيسية
    # mockmainwindow
    class MockMainWindow:
        # احصل على اتصال DB
        def get_db_connection(self):
            return None

    main_window = MockMainWindow()
    window = FinancialReportsWindow(main_window)
    window.show()

    sys.exit(app.exec())
