#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام التقارير المالية الشهرية والسنوية
يعرض ملخص السنة والبيانات الشهرية في شكل بطاقات مع دعم RTL
"""

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import Currency_type
from ستايل import Basic_Styles


# نافذة التقارير المالية الشهرية والسنوية
class MonthlyAnnualReportsWindow(QMainWindow):
    
    # init
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("التقارير المالية الشهرية والسنوية")
        self.setGeometry(100, 100, 1600, 900)
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
        
    # إعداد واجهة المستخدم
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان النافذة
        title_label = QLabel("التقارير المالية الشهرية والسنوية")
        title_label.setObjectName("main_title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # شريط التحكم العلوي
        control_layout = self.create_control_bar()
        main_layout.addLayout(control_layout)
        
        # منطقة البطاقات مع التمرير
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setLayoutDirection(Qt.RightToLeft)
        
        # حاوية البطاقات
        self.cards_container = QWidget()
        self.cards_container.setLayoutDirection(Qt.RightToLeft)
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)
        
    # إنشاء شريط التحكم العلوي
    def create_control_bar(self):
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # اختيار السنة المالية
        year_label = QLabel("السنة المالية:")
        year_label.setObjectName("control_label")
        
        self.year_combo = QComboBox()
        self.year_combo.setObjectName("year_combo")
        # إضافة السنوات (السنة الحالية ± 5 سنوات)
        for year in range(self.current_year - 5, self.current_year + 6):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.on_year_changed)
        
        # زر التحديث
        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setObjectName("refresh_button")
        refresh_btn.clicked.connect(self.refresh_data)
        
        # زر الطباعة
        print_btn = QPushButton("🖨️ طباعة")
        print_btn.setObjectName("print_button")
        print_btn.clicked.connect(self.print_reports)
        
        # زر التصدير
        export_btn = QPushButton("📊 تصدير Excel")
        export_btn.setObjectName("export_button")
        export_btn.clicked.connect(self.export_to_excel)
        
        control_layout.addWidget(year_label)
        control_layout.addWidget(self.year_combo)
        control_layout.addStretch()
        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(print_btn)
        control_layout.addWidget(export_btn)
        
        return control_layout
        
    # تحميل البيانات السنوية وإنشاء البطاقات
    def load_annual_data(self):
        try:
            # مسح البطاقات الموجودة
            self.clear_cards()
            
            # إنشاء بطاقة ملخص السنة أولاً
            annual_summary = self.get_annual_summary()
            annual_card = self.create_annual_summary_card(annual_summary)
            self.cards_layout.addWidget(annual_card)
            
            # إنشاء البطاقات الشهرية (من يناير إلى ديسمبر)
            for month_num in range(1, 13):
                month_data = self.get_monthly_data(month_num)
                month_card = self.create_monthly_card(month_num, month_data)
                self.cards_layout.addWidget(month_card)
                
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
    
    # الحصول على ملخص السنة المالية
    def get_annual_summary(self):
        try:
            conn = self.main_window.get_db_connection()
            cursor = conn.cursor()
            
            year = int(self.year_combo.currentText())
            
            # إجمالي الإيرادات من المشاريع والعقود
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_revenue
                FROM المشاريع 
                WHERE YEAR(تاريخ_الإستلام) = %s
            """, (year,))
            total_revenue = cursor.fetchone()[0] or 0
            
            # إجمالي المدفوعات من العملاء
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_payments
                FROM دفعات_المشروع 
                WHERE YEAR(تاريخ_الدفعة) = %s
            """, (year,))
            total_payments = cursor.fetchone()[0] or 0
            
            # إجمالي المصروفات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_expenses
                FROM الحسابات 
                WHERE YEAR(تاريخ_المصروف) = %s
            """, (year,))
            total_expenses = cursor.fetchone()[0] or 0
            
            # إجمالي رواتب الموظفين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as total_salaries
                FROM الموظفين_معاملات_مالية 
                WHERE نوع_المعاملة = 'راتب' AND YEAR(تاريخ_المعاملة) = %s
            """, (year,))
            total_salaries = cursor.fetchone()[0] or 0
            
            # عدد المشاريع
            cursor.execute("""
                SELECT COUNT(*) as projects_count
                FROM المشاريع 
                WHERE YEAR(تاريخ_الإستلام) = %s
            """, (year,))
            projects_count = cursor.fetchone()[0] or 0
            
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
                WHERE YEAR(تاريخ_الإستلام) = %s AND الباقي > 0
            """, (year,))
            total_remaining = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            # حساب صافي الربح
            net_profit = total_payments - total_expenses - total_salaries
            
            return {
                'total_revenue': total_revenue,
                'total_payments': total_payments,
                'total_expenses': total_expenses,
                'total_salaries': total_salaries,
                'net_profit': net_profit,
                'projects_count': projects_count,
                'active_employees': active_employees,
                'total_remaining': total_remaining
            }
            
        except Exception as e:
            print(f"خطأ في الحصول على ملخص السنة: {e}")
            return {
                'total_revenue': 0, 'total_payments': 0, 'total_expenses': 0,
                'total_salaries': 0, 'net_profit': 0, 'projects_count': 0,
                'active_employees': 0, 'total_remaining': 0
            }

    # الحصول على البيانات الشهرية
    def get_monthly_data(self, month_num):
        try:
            conn = self.main_window.get_db_connection()
            cursor = conn.cursor()

            year = int(self.year_combo.currentText())

            # إيرادات الشهر من المدفوعات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as monthly_revenue
                FROM دفعات_المشروع
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month_num))
            monthly_revenue = cursor.fetchone()[0] or 0

            # مصروفات الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as monthly_expenses
                FROM الحسابات
                WHERE YEAR(تاريخ_المصروف) = %s AND MONTH(تاريخ_المصروف) = %s
            """, (year, month_num))
            monthly_expenses = cursor.fetchone()[0] or 0

            # رواتب الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as monthly_salaries
                FROM الموظفين_معاملات_مالية
                WHERE نوع_المعاملة = 'راتب'
                AND YEAR(تاريخ_المعاملة) = %s AND MONTH(تاريخ_المعاملة) = %s
            """, (year, month_num))
            monthly_salaries = cursor.fetchone()[0] or 0

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

            # عدد الموظفين النشطين في نهاية الشهر
            cursor.execute("""
                SELECT COUNT(*) as active_employees_month
                FROM الموظفين
                WHERE الحالة = 'نشط'
            """, ())
            active_employees_month = cursor.fetchone()[0] or 0

            # مدفوعات العملاء في الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as client_payments
                FROM دفعات_المشروع
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month_num))
            client_payments = cursor.fetchone()[0] or 0

            # مدفوعات الموردين في الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) as supplier_payments
                FROM دفعات_الموردين
                WHERE YEAR(تاريخ_الدفعة) = %s AND MONTH(تاريخ_الدفعة) = %s
            """, (year, month_num))
            supplier_payments = cursor.fetchone()[0] or 0

            # مستحقات من العملاء في نهاية الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي), 0) as client_receivables
                FROM المشاريع
                WHERE الباقي > 0 AND تاريخ_الإستلام <= %s
            """, (f"{year}-{month_num:02d}-31",))
            client_receivables = cursor.fetchone()[0] or 0

            # مستحقات للموردين في نهاية الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي), 0) as supplier_payables
                FROM حسابات_الموردين
                WHERE الباقي > 0
            """, ())
            supplier_payables = cursor.fetchone()[0] or 0

            # مستحقات الموظفين (الأرصدة الموجبة)
            cursor.execute("""
                SELECT COALESCE(SUM(الرصيد), 0) as employee_receivables
                FROM الموظفين
                WHERE الرصيد > 0
            """, ())
            employee_receivables = cursor.fetchone()[0] or 0

            cursor.close()

            # حساب صافي ربح الشهر
            monthly_net_profit = monthly_revenue - monthly_expenses - monthly_salaries

            return {
                'monthly_revenue': monthly_revenue,
                'monthly_expenses': monthly_expenses,
                'monthly_salaries': monthly_salaries,
                'monthly_net_profit': monthly_net_profit,
                'new_projects': new_projects,
                'completed_projects': completed_projects,
                'active_employees_month': active_employees_month,
                'client_payments': client_payments,
                'supplier_payments': supplier_payments,
                'client_receivables': client_receivables,
                'supplier_payables': supplier_payables,
                'employee_receivables': employee_receivables
            }

        except Exception as e:
            print(f"خطأ في الحصول على البيانات الشهرية للشهر {month_num}: {e}")
            return {
                'monthly_revenue': 0, 'monthly_expenses': 0, 'monthly_salaries': 0,
                'monthly_net_profit': 0, 'new_projects': 0, 'completed_projects': 0,
                'active_employees_month': 0, 'client_payments': 0, 'supplier_payments': 0,
                'client_receivables': 0, 'supplier_payables': 0, 'employee_receivables': 0
            }

    # إنشاء بطاقة ملخص السنة
    def create_annual_summary_card(self, data):
        card = QFrame()
        card.setObjectName("annual_summary_card")
        card.setFixedSize(320, 480)
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)

        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # عنوان البطاقة
        title = QLabel(f"ملخص السنة {self.year_combo.currentText()}")
        title.setObjectName("card_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # خط فاصل
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # المعلومات المالية
        financial_info = [
            ("💰 إجمالي الإيرادات:", data['total_revenue'], "#3498db"),
            ("💳 إجمالي المدفوعات:", data['total_payments'], "#27ae60"),
            ("💸 إجمالي المصروفات:", data['total_expenses'], "#e74c3c"),
            ("💼 إجمالي الرواتب:", data['total_salaries'], "#f39c12"),
            ("📊 صافي الربح:", data['net_profit'], "#2ecc71" if data['net_profit'] >= 0 else "#e74c3c")
        ]

        for label_text, value, color in financial_info:
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

        # المعلومات الإحصائية
        stats_info = [
            ("🏗️ عدد المشاريع:", data['projects_count']),
            ("👥 عدد الموظفين:", data['active_employees']),
            ("📋 إجمالي المستحقات:", f"{data['total_remaining']:,.0f} {Currency_type}")
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

    # إنشاء بطاقة شهرية
    def create_monthly_card(self, month_num, data):
        card = QFrame()
        card.setObjectName("monthly_card")
        card.setFixedSize(300, 460)
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(1)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # عنوان الشهر
        month_name = self.months_arabic[month_num - 1]
        title = QLabel(month_name)
        title.setObjectName("month_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # خط فاصل
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # ملخص مالي
        financial_section = QLabel("💰 الملخص المالي")
        financial_section.setObjectName("section_title")
        layout.addWidget(financial_section)

        financial_info = [
            ("الإيرادات:", data['monthly_revenue'], "#3498db"),
            ("المصروفات:", data['monthly_expenses'], "#e74c3c"),
            ("صافي الربح:", data['monthly_net_profit'], "#27ae60" if data['monthly_net_profit'] >= 0 else "#e74c3c")
        ]

        for label_text, value, color in financial_info:
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

        # ملخص إحصائي
        stats_section = QLabel("📊 الملخص الإحصائي")
        stats_section.setObjectName("section_title")
        layout.addWidget(stats_section)

        stats_info = [
            ("مشاريع جديدة:", data['new_projects']),
            ("مشاريع مكتملة:", data['completed_projects']),
            ("موظفين نشطين:", data['active_employees_month'])
        ]

        for label_text, value in stats_info:
            info_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setObjectName("monthly_info_label")

            value_label = QLabel(str(value))
            value_label.setObjectName("monthly_info_value")
            value_label.setAlignment(Qt.AlignLeft)

            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        # ملخص المدفوعات
        payments_section = QLabel("💳 ملخص المدفوعات")
        payments_section.setObjectName("section_title")
        layout.addWidget(payments_section)

        payments_info = [
            ("مدفوعات العملاء:", data['client_payments']),
            ("مدفوعات الموردين:", data['supplier_payments']),
            ("رواتب الموظفين:", data['monthly_salaries'])
        ]

        for label_text, value in payments_info:
            info_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setObjectName("monthly_info_label")

            value_label = QLabel(f"{value:,.0f} {Currency_type}")
            value_label.setObjectName("monthly_info_value")
            value_label.setAlignment(Qt.AlignLeft)

            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        # ملخص المستحقات
        receivables_section = QLabel("📋 ملخص المستحقات")
        receivables_section.setObjectName("section_title")
        layout.addWidget(receivables_section)

        receivables_info = [
            ("مستحقات من العملاء:", data['client_receivables']),
            ("مستحقات للموردين:", data['supplier_payables']),
            ("مستحقات الموظفين:", data['employee_receivables'])
        ]

        for label_text, value in receivables_info:
            info_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setObjectName("monthly_info_label")

            value_label = QLabel(f"{value:,.0f} {Currency_type}")
            value_label.setObjectName("monthly_info_value")
            value_label.setAlignment(Qt.AlignLeft)

            info_layout.addWidget(label)
            info_layout.addWidget(value_label)
            layout.addLayout(info_layout)

        layout.addStretch()
        return card

    # تطبيق الأنماط على البطاقات
    def apply_styles(self):
        Basic_Styles(self)
        self.setStyleSheet("""
            /* العنوان الرئيسي */
            QLabel#main_title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }

            /* بطاقة ملخص السنة */
            QFrame#annual_summary_card {
                background-color: #f8f9fa;
                border: 3px solid #3498db;
                border-radius: 12px;
                margin: 5px;
            }

            /* البطاقات الشهرية */
            QFrame#monthly_card {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin: 3px;
            }

            QFrame#monthly_card:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }

            /* عناوين البطاقات */
            QLabel#card_title {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background-color: #3498db;
                color: white;
                border-radius: 6px;
            }

            QLabel#month_title {
                font-size: 18px;
                font-weight: bold;
                color: #34495e;
                padding: 6px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }

            /* عناوين الأقسام */
            QLabel#section_title {
                font-size: 14px;
                font-weight: bold;
                color: #7f8c8d;
                margin-top: 8px;
                margin-bottom: 5px;
                padding: 3px;
                background-color: #f1f2f6;
                border-radius: 3px;
            }

            /* تسميات المعلومات */
            QLabel#info_label, QLabel#monthly_info_label {
                font-size: 13px;
                color: #2c3e50;
                font-weight: normal;
                padding: 2px;
            }

            /* قيم المعلومات */
            QLabel#info_value, QLabel#monthly_info_value {
                font-size: 13px;
                font-weight: bold;
                padding: 2px;
            }

            /* أزرار التحكم */
            QPushButton#refresh_button {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#refresh_button:hover {
                background-color: #229954;
            }

            QPushButton#print_button {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#print_button:hover {
                background-color: #d35400;
            }

            QPushButton#export_button {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#export_button:hover {
                background-color: #7d3c98;
            }

            /* تسميات التحكم */
            QLabel#control_label {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }

            /* كومبو بوكس السنة */
            QComboBox#year_combo {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 120px;
                font-size: 14px;
                font-weight: bold;
            }

            QComboBox#year_combo:focus {
                border-color: #3498db;
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


# فتح نافذة التقارير المالية الشهرية والسنوية
def open_monthly_annual_reports_window(main_window):
    try:
        window = MonthlyAnnualReportsWindow(main_window)
        window.show()
        return window
    except Exception as e:
        error_msg = f"فشل في فتح نافذة التقارير الشهرية والسنوية:\n{str(e)}"
        if hasattr(main_window, 'show'):
            QMessageBox.critical(main_window, "خطأ", error_msg)
        else:
            print(f"خطأ: {error_msg}")
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # محاكاة النافذة الرئيسية
    # mockmainwindow
    class MockMainWindow:
        # احصل على اتصال DB
        def get_db_connection(self):
            return None

    main_window = MockMainWindow()
    window = MonthlyAnnualReportsWindow(main_window)
    window.show()

    sys.exit(app.exec())
