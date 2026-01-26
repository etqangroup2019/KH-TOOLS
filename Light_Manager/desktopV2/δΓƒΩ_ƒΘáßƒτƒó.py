#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime, date
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from المشاريع.إدارة_المشروع import*

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from متغيرات import *
from ستايل import *

# بطاقة عرض عصرية ومطورة للبيانات
class ModernCard(QFrame):
    card_clicked = Signal(dict)
    card_double_clicked = Signal(dict)
    
    # init
    def __init__(self, data, card_type="project", parent=None):
        super().__init__(parent)
        self.data = data
        self.card_type = card_type
        self.setup_ui()
        self.apply_modern_styles()
        self.setup_context_menu()
        
    # إعداد واجهة البطاقة العصرية مع أحجام محسنة للتوزيع الأفقي
    def setup_ui(self):
        # تحديث أحجام البطاقة للتوزيع الأفقي المحسن (بدون أزرار)
        if self.card_type == "project":
            self.setMinimumSize(270, 200)  # ارتفاع أقل بدون أزرار
            self.setMaximumSize(270, 450)  # ارتفاع أقل بدون أزرار
        else:
            self.setMinimumSize(260, 150)  # ارتفاع أقل للأنواع الأخرى
            self.setMaximumSize(260, 400)  # ارتفاع أقل للأنواع الأخرى

        self.setObjectName("ModernCard")

        # تطبيق الاتجاه العربي RTL على البطاقة
        self.setLayoutDirection(Qt.RightToLeft)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # رأس البطاقة
        self.create_header(main_layout)
        
        # المحتوى الرئيسي
        self.create_content(main_layout)
        
    # إنشاء رأس البطاقة
    def create_header(self, layout):
        header_layout = QHBoxLayout()

        # أيقونة ونوع البطاقة
        icon_label = QLabel()
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignCenter)

        # تحديد الأيقونة حسب نوع البطاقة
        if self.card_type == "project":
            icon_label.setText("🏗️")
            title = self.data.get('اسم_المشروع', 'مشروع غير محدد')
        elif self.card_type == "client":
            icon_label.setText("👤")
            title = self.data.get('اسم_العميل', 'عميل غير محدد')
        elif self.card_type == "employee":
            icon_label.setText("👷")
            title = self.data.get('اسم_الموظف', 'موظف غير محدد')
        elif self.card_type == "expense":
            icon_label.setText("💰")
            title = self.data.get('المصروف', 'مصروف غير محدد')
        
        elif self.card_type == "training":
            icon_label.setText("📚")
            title = self.data.get('اسم_الدورة', 'دورة غير محددة')

        elif self.card_type == "supplier":
            icon_label.setText("💼")
            title = self.data.get('اسم_المورد', 'مورد غير محدد')
        else:
            icon_label.setText("📄")
            title = "عنصر غير محدد"

        icon_label.setObjectName("CardIcon")

        # عنوان البطاقة
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(50)

        # إضافة العنوان فقط للمشاريع والمقاولات والموظفين (بدون حالة المشروع أو نوع الموظف)
        #if self.card_type == "project" or self.card_type == "employee":
        header_layout.addWidget(icon_label)
        header_layout.addWidget(self.title_label, 1)
        # else:
        #     # للأقسام الأخرى، احتفظ بعرض الحالة/التصنيف
        #     status = self.get_status_or_classification()
        #     self.status_label = QLabel(status)
        #     self.status_label.setObjectName("CardStatus")
        #     self.status_label.setAlignment(Qt.AlignCenter)
        #     self.status_label.setFixedSize(90, 30)

        #     header_layout.addWidget(icon_label)
        #     header_layout.addWidget(self.title_label, 1)
        #     header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)
        
    # الحصول على الحالة أو التصنيف حسب نوع البطاقة
    def get_status_or_classification(self):
        if self.card_type in ["project", "training"]:
            return self.data.get('الحالة', 'غير محدد')
        else:
            return self.data.get('التصنيف', 'غير محدد')
            
    # إنشاء محتوى البطاقة
    def create_content(self, layout):
        content_frame = QFrame()
        content_frame.setObjectName("CardContent")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        if self.card_type == "project":
            self.create_project_content(content_layout)
        elif self.card_type == "client":
            self.create_client_content(content_layout)
        elif self.card_type == "employee":
            self.create_employee_content(content_layout)
        elif self.card_type == "expense":
            self.create_expense_content(content_layout)
        elif self.card_type == "supplier":
            self.create_supplier_content(content_layout)
        elif self.card_type == "training":
            self.create_training_content(content_layout)
            
        layout.addWidget(content_frame)
    
    #محتوى بطاقة المشروع
    # إنشاء محتوى المشروع
    def create_project_content(self, layout):
        # نوع المشروع (التصنيف) مع تلوين الخلفية
        project_type = self.data.get('التصنيف', 'غير محدد')
        project_type_label = QLabel(f"📋 {project_type}")
        project_type_label.setObjectName("CardInfo")

        # تطبيق تلوين الخلفية حسب نوع المشروع
        type_color = self.get_project_type_color(project_type)
        project_type_label.setObjectName("CategoryLabel")
        project_type_label.setProperty("category_color", type_color)
        layout.addWidget(project_type_label)

        # معلومات العميل
        client_name = self.data.get('اسم_العميل', 'غير محدد')
        client_label = QLabel(f"👤 العميل: {client_name}")
        client_label.setObjectName("CardInfo")
        layout.addWidget(client_label)

        # معلومات المسؤول/المهندس الرئيسي
        manager_name = self.data.get('اسم_المهندس_الرئيسي', 'غير محدد')
        manager_label = QLabel(f"👨‍💼 المسؤول: {manager_name}")
        manager_label.setObjectName("CardInfo")
        layout.addWidget(manager_label)

        # المعلومات المالية
        financial_grid = QGridLayout()

        # جلب المبلغ الإجمالي من الحقل الصحيح
        total_amount = self.data.get('المبلغ', 0)
        remaining_amount = self.data.get('الباقي', 0)

        # عرض الإجمالي
        financial_grid.addWidget(QLabel("💰 الإجمالي:"), 0, 0)
        if total_amount and total_amount > 0:
            total_label = QLabel(f"{total_amount:,.0f}  {Currency_type}")
            total_label.setObjectName("TotalAmount")
        else:
            total_label = QLabel("غير محدد")
            total_label.setObjectName("UndefinedAmount")
        financial_grid.addWidget(total_label, 0, 1)

        # عرض الباقي
        financial_grid.addWidget(QLabel("💳 الباقي:"), 1, 0)
        if remaining_amount and remaining_amount > 0:
            remaining_label = QLabel(f"{remaining_amount:,.0f}  {Currency_type}")
            remaining_label.setObjectName("RemainingAmount")
        else:
            remaining_label = QLabel("خالص")
            remaining_label.setObjectName("PaidAmount")
        financial_grid.addWidget(remaining_label, 1, 1)

        layout.addLayout(financial_grid)

        # الحالة والوقت المتبقي مدموجين
        status_time_info = self.get_combined_status_time()
        status_time_label = QLabel(f"⏰ {status_time_info}")
        status_time_label.setObjectName("TimeInfo")
        status_time_label.setAlignment(Qt.AlignCenter)

        # تطبيق تلوين الخلفية بدلاً من النص (نقل التلوين من العنوان إلى هنا)
        status_color = self.get_status_color()
        status_time_label.setObjectName("StatusTimeLabel")
        status_time_label.setProperty("status_color", status_color)

        layout.addWidget(status_time_label)

    # دمج حالة المشروع مع معلومات التوقيت
    def get_combined_status_time(self):
        status = self.data.get('الحالة', 'غير محدد')

        # إذا كانت الحالة "قيد الإنجاز" - حساب فرق الأيام مع التاريخ الحالي
        if status == 'قيد الإنجاز':
            if self.data.get('تاريخ_التسليم'):
                try:
                    end_date = datetime.strptime(str(self.data['تاريخ_التسليم']), '%Y-%m-%d')
                    today = datetime.now()
                    remaining_days = (end_date - today).days

                    if remaining_days > 0:
                        return f"قيد الإنجاز - {remaining_days} يوم متبقي"
                    elif remaining_days == 0:
                        return "قيد الإنجاز - ينتهي اليوم"
                    else:
                        return f"قيد الإنجاز - متأخر {abs(remaining_days)} يوم"
                except:
                    return f"قيد الإنجاز - غير محدد"
            else:
                return "قيد الإنجاز - غير محدد"

        # لباقي الحالات - عرض الحالة + فرق الأيام بين تاريخ التسليم والاستلام
        else:
            if self.data.get('تاريخ_الإستلام') and self.data.get('تاريخ_التسليم'):
                try:
                    start_date = datetime.strptime(str(self.data['تاريخ_الإستلام']), '%Y-%m-%d')
                    end_date = datetime.strptime(str(self.data['تاريخ_التسليم']), '%Y-%m-%d')
                    duration_days = (end_date - start_date).days
                    return f"{status} - مدة المشروع {duration_days} يوم"
                except:
                    return f"{status}"
            else:
                return f"{status}"

    # تحديد لون الحالة حسب النوع
    def get_status_color(self):
        status = self.data.get('الحالة', '')

        # للحالة "قيد الإنجاز" - تحديد اللون حسب الوقت المتبقي
        if status == 'قيد الإنجاز':
            if self.data.get('تاريخ_التسليم'):
                try:
                    end_date = datetime.strptime(str(self.data['تاريخ_التسليم']), '%Y-%m-%d')
                    today = datetime.now()
                    remaining_days = (end_date - today).days

                    if remaining_days > 0:
                        return "#f39c12"  # برتقالي للوقت المتبقي
                    elif remaining_days == 0:
                        return "#e67e22"  # برتقالي داكن لموعد اليوم
                    else:
                        return "#e74c3c"  # أحمر للمتأخر
                except:
                    return "#3498db"  # أزرق للغير محدد
            else:
                return "#3498db"  # أزرق للغير محدد

        # ألوان ثابتة لباقي الحالات
        status_colors = {
            'تم التسليم': '#27ae60',      # أخضر
            'تأكيد التسليم': '#2ecc71',   # أخضر فاتح
            'منتهي': '#27ae60',           # أخضر
            'معلق': '#3498db',            # أزرق
            'متوقف': '#e74c3c',           # أحمر
        }
        return status_colors.get(status, '#95a5a6')  # رمادي افتراضي

    # الحصول على لون نوع المشروع حسب التصنيف من قاعدة البيانات
    def get_project_type_color(self, project_type):
        try:
            # محاولة جلب اللون من قاعدة البيانات للمشاريع أولاً
            from الإعدادات_العامة import get_categories_with_colors, Currency_type
            categories_with_colors = get_categories_with_colors("المشاريع")

            # البحث عن اللون المطابق للتصنيف
            for name, color in categories_with_colors:
                if name == project_type:
                    return color

            # إذا لم نجد في المشاريع، نبحث في المقاولات
            contracting_categories = get_categories_with_colors("المقاولات")
            for name, color in contracting_categories:
                if name == project_type:
                    return color

        except Exception as e:
            print(f"خطأ في جلب لون التصنيف: {e}")

        # الألوان الافتراضية في حالة عدم وجود التصنيف في قاعدة البيانات
        color_map = {
            # تصنيفات المشاريع
            'تصميم معماري': '#3498db',  # أزرق
            'تصميم داخلي': '#9b59b6',   # بنفسجي
            'إشراف': '#f39c12',         # برتقالي
            'إشراف هندسي': '#f39c12',   # برتقالي
            'إعداد مقايسات': '#e67e22', # برتقالي داكن

            # تصنيفات المقاولات
            'تأسيس وتشطيب': '#8b4513',          # بني
            'بناء عظم': '#a0522d',       # بني فاتح
            'تشطيب': '#cd853f',         # بني ذهبي
            'مقاولات عامة': '#8b4513',  # بني
            'صيانة وترميم': '#bc8f8f',   # وردي بني
            
        }
        return color_map.get(project_type, '#95a5a6')  # رمادي للأنواع الأخرى

    # الحصول على لون التصنيف من قاعدة البيانات لأي قسم
    def get_category_color(self, category_name, section_name):
        try:
            from الإعدادات_العامة import get_categories_with_colors, Currency_type
            categories_with_colors = get_categories_with_colors(section_name)

            # البحث عن اللون المطابق للتصنيف
            for name, color in categories_with_colors:
                if name == category_name:
                    return color

        except Exception as e:
            print(f"خطأ في جلب لون التصنيف {category_name}: {e}")

        # لون افتراضي في حالة عدم العثور على التصنيف
        return '#3498db'

    # تحديد لون حالة الموظف حسب الحالة
    def get_employee_status_color(self, status):
        status_colors = {
            'نشط': '#27ae60',        # أخضر - للموظف النشط
            'غير نشط': '#95a5a6',    # رمادي - للموظف غير النشط
            'إجازة': '#f39c12',      # برتقالي - للموظف في إجازة
            'مستقيل': '#e74c3c',     # أحمر - للموظف المستقيل
            'تم فصله': '#8e44ad'     # بنفسجي - للموظف المفصول
        }
        return status_colors.get(status, '#95a5a6')  # رمادي كلون افتراضي
        
    # محتوى بطاقة العميل
    def create_client_content(self, layout):
        # نوع العميل مع تلوين الخلفية
        client_type = self.data.get('التصنيف', 'غير محدد')
        if client_type != 'غير محدد':
            type_label = QLabel(f"🏢 نوع العميل: {client_type}")
            type_label.setObjectName("CardInfo")

            # تطبيق تلوين الخلفية حسب نوع العميل
            type_color = self.get_category_color(client_type, "العملاء")
            type_label.setObjectName("CategoryLabel")
            type_label.setProperty("category_color", type_color)
            layout.addWidget(type_label)

        phone = self.data.get('رقم_الهاتف', 'غير محدد')
        phone_label = QLabel(f"📞 الهاتف: {phone}")
        phone_label.setObjectName("CardInfo")
        layout.addWidget(phone_label)
        
        address = self.data.get('العنوان', 'غير محدد')
        address_label = QLabel(f"📍 العنوان: {address}")
        address_label.setObjectName("CardInfo")
        address_label.setWordWrap(True)
        layout.addWidget(address_label)
        
        # إحصائيات العميل
        projects_count = self.data.get('عدد_المشاريع', 0)
        total_remaining = self.data.get('إجمالي_الباقي', 0)

        stats_grid = QGridLayout()
        stats_grid.addWidget(QLabel("📊 عدد المشاريع:"), 0, 0)
        stats_grid.addWidget(QLabel(str(projects_count)), 0, 1)
        stats_grid.addWidget(QLabel("💰 إجمالي الباقي:"), 1, 0)

        # تلوين إجمالي الباقي حسب الحالة
        if total_remaining <= 0:
            remaining_label = QLabel("خالص")
            remaining_label.setObjectName("PaidAmount")
        else:
            remaining_label = QLabel(f"{total_remaining:,.0f}  {Currency_type}")
            remaining_label.setObjectName("RemainingAmount")
        stats_grid.addWidget(remaining_label, 1, 1)
        
        layout.addLayout(stats_grid)
        
    # محتوى بطاقة الموظف
    def create_employee_content(self, layout):
        # نوع الموظف (التصنيف) مع تلوين الخلفية
        employee_type = self.data.get('التصنيف', 'غير محدد')
        if employee_type != 'غير محدد':
            type_label = QLabel(f"👤 نوع الموظف: {employee_type}")
            type_label.setObjectName("CardInfo")

            # تطبيق تلوين الخلفية حسب نوع الموظف
            type_color = self.get_category_color(employee_type, "الموظفين")
            type_label.setObjectName("CategoryLabel")
            type_label.setProperty("category_color", type_color)
            layout.addWidget(type_label)

        # معلومات الهاتف
        phone = self.data.get('الهاتف', 'غير محدد')
        phone_label = QLabel(f"📞 الهاتف: {phone}")
        phone_label.setObjectName("CardInfo")
        layout.addWidget(phone_label)

        # معلومات الوظيفة
        job_title = self.data.get('الوظيفة', 'غير محدد')
        job_label = QLabel(f"💼 الوظيفة: {job_title}")
        job_label.setObjectName("CardInfo")
        layout.addWidget(job_label)

        # الرصيد فقط (حذف الراتب)
        balance = self.data.get('الرصيد', 0)

        financial_grid = QGridLayout()
        financial_grid.addWidget(QLabel("💳 الرصيد:"), 0, 0)
        balance_label = QLabel(f"{balance:,.0f}  {Currency_type}")
        balance_label.setObjectName("BalanceAmount")
        financial_grid.addWidget(balance_label, 0, 1)

        layout.addLayout(financial_grid)

        # حالة الموظف مع تلوين الخلفية
        employee_status = self.data.get('الحالة', 'نشط')
        status_label = QLabel(f"📊 الحالة: {employee_status}")
        status_label.setObjectName("CardInfo")

        # تطبيق تلوين الخلفية حسب حالة الموظف
        status_color = self.get_employee_status_color(employee_status)
        status_label.setObjectName("EmployeeStatusLabel")
        status_label.setProperty("status_color", status_color)
        layout.addWidget(status_label)
        
    # محتوى بطاقة المصروف
    def create_expense_content(self, layout):
        # نوع المصروف مع تلوين الخلفية
        expense_type = self.data.get('التصنيف', 'غير محدد')
        if expense_type != 'غير محدد':
            type_label = QLabel(f"📋 نوع المصروف: {expense_type}")
            type_label.setObjectName("CardInfo")

            # تطبيق تلوين الخلفية حسب نوع المصروف
            type_color = self.get_category_color(expense_type, "الحسابات")
            type_label.setObjectName("CategoryLabel")
            type_label.setProperty("category_color", type_color)
            layout.addWidget(type_label)

        amount = self.data.get('المبلغ', 0)
        date_str = self.data.get('تاريخ_المصروف', 'غير محدد')

        amount_label = QLabel(f"💰 المبلغ: {amount:,.0f}  {Currency_type}")
        amount_label.setObjectName("ExpenseAmount")
        layout.addWidget(amount_label)

        date_label = QLabel(f"📅 التاريخ: {date_str}")
        date_label.setObjectName("CardInfo")
        layout.addWidget(date_label)
        
        description = self.data.get('ملاحظات', 'لا يوجد وصف')
        desc_label = QLabel(f"📝 الوصف: {description}")
        desc_label.setObjectName("CardInfo")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        
    # محتوى بطاقة التدريب
    def create_training_content(self, layout):
        # نوع الدورة مع تلوين الخلفية
        course_type = self.data.get('التصنيف', 'غير محدد')
        if course_type != 'غير محدد':
            type_label = QLabel(f"📚 نوع الدورة: {course_type}")
            type_label.setObjectName("CardInfo")

            # تطبيق تلوين الخلفية حسب نوع الدورة
            type_color = self.get_category_color(course_type, "التدريب")
            type_label.setObjectName("CategoryLabel")
            type_label.setProperty("category_color", type_color)
            layout.addWidget(type_label)

        trainer = self.data.get('المدرب', 'غير محدد')
        duration = self.data.get('المدة', 'غير محدد')
        participants = self.data.get('عدد_المشاركين', 0)

        trainer_label = QLabel(f"👨‍🏫 المدرب: {trainer}")
        trainer_label.setObjectName("CardInfo")
        layout.addWidget(trainer_label)
        
        duration_label = QLabel(f"⏱️ المدة: {duration}")
        duration_label.setObjectName("CardInfo")
        layout.addWidget(duration_label)
        
        participants_label = QLabel(f"👥 المشاركين: {participants}")
        participants_label.setObjectName("CardInfo")
        layout.addWidget(participants_label)

    # محتوى بطاقة المورد

    def create_supplier_content(self, layout):
        # نوع المورد مع تلوين الخلفية
        supplier_type = self.data.get('التصنيف', 'غير محدد')
        if supplier_type != 'غير محدد':
            type_label = QLabel(f"💼 نوع المورد: {supplier_type}")
            type_label.setObjectName("CardInfo")

            # تطبيق تلوين الخلفية حسب نوع المورد
            type_color = self.get_category_color(supplier_type, "الموردين")
            type_label.setObjectName("CategoryLabel")
            type_label.setProperty("category_color", type_color)
            layout.addWidget(type_label)

        phone = self.data.get('رقم_الهاتف', 'غير محدد')
        phone_label = QLabel(f"📞 الهاتف: {phone}")
        phone_label.setObjectName("CardInfo")
        layout.addWidget(phone_label)
        
        address = self.data.get('العنوان', 'غير محدد')
        address_label = QLabel(f"📍 العنوان: {address}")
        address_label.setObjectName("CardInfo")
        address_label.setWordWrap(True)
        layout.addWidget(address_label)
        
    
    # إعداد قائمة السياق للبطاقة
    def setup_context_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    # عرض قائمة السياق
    def show_context_menu(self, position):
        context_menu = QMenu(self)

        # إضافة الخيارات حسب نوع البطاقة
        if self.card_type == "project":
            # خيارات المشاريع
            view_action = QAction("👁️ عرض", self)
            view_action.triggered.connect(self.view_project)
            context_menu.addAction(view_action)

            edit_action = QAction("✏️ تعديل", self)
            edit_action.triggered.connect(self.edit_project)
            context_menu.addAction(edit_action)

            delete_action = QAction("🗑️ حذف", self)
            delete_action.triggered.connect(self.delete_project)
            context_menu.addAction(delete_action)
        else:
            # خيارات الأقسام الأخرى
            view_action = QAction("👁️ عرض", self)
            view_action.triggered.connect(self.show_details)
            context_menu.addAction(view_action)

            edit_action = QAction("✏️ تعديل", self)
            edit_action.triggered.connect(self.edit_item)
            context_menu.addAction(edit_action)

            delete_action = QAction("🗑️ حذف", self)
            delete_action.triggered.connect(self.delete_item)
            context_menu.addAction(delete_action)

        # عرض القائمة في الموضع المحدد
        context_menu.exec(self.mapToGlobal(position))


        
    # تطبيق الأنماط العصرية على البطاقة
    def apply_modern_styles(self):
        # استدعاء الدالة المركزية لتطبيق الأنماط
        self.setup_card_styles()
        
    # تحديد لون الحدود حسب التصنيف لكل نوع بطاقة
    def get_border_color(self):
        if self.card_type == "project":
            # للمشاريع والمقاولات: استخدام لون التصنيف
            project_type = self.data.get('التصنيف', 'غير محدد')
            return self.get_project_type_color(project_type)

        elif self.card_type == "client":
            # للعملاء: استخدام لون تصنيف العميل
            client_type = self.data.get('التصنيف', 'غير محدد')
            return self.get_category_color(client_type, "العملاء")

        elif self.card_type == "employee":
            # للموظفين: استخدام لون تصنيف الموظف
            employee_type = self.data.get('التصنيف', 'غير محدد')
            return self.get_category_color(employee_type, "الموظفين")

        elif self.card_type == "expense":
            # للحسابات: استخدام لون تصنيف المصروف
            expense_type = self.data.get('التصنيف', 'غير محدد')
            return self.get_category_color(expense_type, "الحسابات")

        elif self.card_type == "supplier":
            # للموردين: استخدام لون تصنيف المورد
            supplier_type = self.data.get('التصنيف', 'غير محدد')
            return self.get_category_color(supplier_type, "الموردين")

        elif self.card_type == "training":
            # للتدريب: استخدام لون تصنيف الدورة
            course_type = self.data.get('التصنيف', 'غير محدد')
            return self.get_category_color(course_type, "التدريب")

        else:
            return "#95a5a6"  # رمادي افتراضي للأنواع غير المعرفة
            
    # معالجة النقر على البطاقة
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.data)
        super().mousePressEvent(event)
        
    # معالجة النقر المزدوج على البطاقة
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.card_double_clicked.emit(self.data)
            self.view_project()
        super().mouseDoubleClickEvent(event)

        
        
    # عرض تفاصيل العنصر
    def show_details(self):
        self.card_clicked.emit(self.data)

    # تعديل العنصر
    def edit_item(self):
        self.card_double_clicked.emit(self.data)

    # طباعة العنصر
    def print_item(self):
        # يمكن إضافة منطق الطباعة هنا
        pass

    # حذف العنصر مع رسالة تأكيد
    def delete_item(self):
        try:
            from PySide6.QtWidgets import QMessageBox

            # تحديد نوع العنصر للرسالة
            item_type = "العنصر"
            if self.card_type == "client":
                item_type = "العميل"
            elif self.card_type == "employee":
                item_type = "الموظف"
            elif self.card_type == "expense":
                item_type = "الحساب"
            elif self.card_type == "supplier":
                item_type = "المورد"
            elif self.card_type == "training":
                item_type = "الدورة التدريبية"

            # رسالة التأكيد
            reply = QMessageBox.question(
                self.parent(),
                "تأكيد الحذف",
                f"هل أنت متأكد من حذف {item_type}؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # إرسال إشارة للحذف مع البيانات
                self.card_clicked.emit({"action": "حذف", "data": self.data})

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في حذف العنصر: {str(e)}")

    # تعديل المشروع
    def edit_project(self):
        try:
            # إرسال إشارة للتعديل مع البيانات
            self.card_clicked.emit({"action": "تعديل", "data": self.data})

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في تعديل المشروع: {str(e)}")

    # حذف المشروع مع رسالة تأكيد
    def delete_project(self):
        try:
            from PySide6.QtWidgets import QMessageBox

            project_name = self.data.get('اسم_المشروع', 'المشروع')

            # رسالة التأكيد
            reply = QMessageBox.question(
                self.parent(),
                "تأكيد الحذف",
                f"هل أنت متأكد من حذف المشروع:\n{project_name}؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # إرسال إشارة للحذف مع البيانات
                self.card_clicked.emit({"action": "حذف", "data": self.data})

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في حذف المشروع: {str(e)}")

    # ==================== دوال الأزرار الجديدة للمشاريع ====================

    # عرض تفاصيل العنصر حسب نوع البطاقة
    def view_project(self):
        try:
            # معالجة خاصة لكل نوع من البطاقات
            if self.card_type == "project":
                # فتح نافذة مراحل المشروع للمشاريع والمقاولات فقط
                #from إدارة_المشروع import open_project_phases_window
                project_type = self.data.get('اسم_القسم', 'المشاريع')
                self.project_phases_window = open_project_phases_window(
                    self.parent(), self.data, project_type
                )
            elif self.card_type == "client":
                # فتح نافذة إدارة العميل
                try:
                    from ادارة_العملاء import open_client_management_window
                    self.client_management_window = open_client_management_window(
                        self.parent(), self.data
                    )
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح نافذة إدارة العميل: {str(e)}")
            elif self.card_type == "employee":
                # فتح نافذة إدارة الموظف
                try:
                    from إدارة_الموظفين import open_employee_management_window
                    self.employee_management_window = open_employee_management_window(
                        self.parent(), self.data
                    )
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح نافذة إدارة الموظف: {str(e)}")
            elif self.card_type == "training":
                # فتح نافذة إدارة التدريب
                try:
                    from إدارة_التدريب import open_training_management_window
                    self.training_management_window = open_training_management_window(
                        self.parent(), self.data
                    )
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح نافذة إدارة التدريب: {str(e)}")
                    # في حالة الفشل، عرض تفاصيل عامة
                    self.show_general_details()

            elif self.card_type == "supplier":
                # فتح نافذة إدارة المورد
                try:
                    from إدارة_الموردين import open_supplier_management_window
                    self.supplier_management_window = open_supplier_management_window(
                        self.parent(), self.data
                    )
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح نافذة إدارة المورد: {str(e)}")
                    # في حالة الفشل، عرض تفاصيل عامة
                    self.show_general_details()
            else:
                # للأنواع الأخرى، عرض تفاصيل عامة
                self.show_general_details()

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح النافذة المناسبة: {str(e)}")
            # في حالة الفشل للمشاريع، استخدم النافذة القديمة كبديل
            if self.card_type == "project":
                try:
                    #from إدارة_المشروع import open_project_phases_window
                    project_type = self.data.get('التصنيف', 'تصميم معماري')
                    self.project_management_window = open_project_phases_window(
                        self.parent(), self.data, project_type
                    )
                except:
                    pass

    # عرض تفاصيل عامة للعنصر
    def show_general_details(self):
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea

            dialog = QDialog(self.parent())
            dialog.setWindowTitle(f"تفاصيل العنصر")
            dialog.setMinimumSize(400, 300)
            dialog.setLayoutDirection(Qt.RightToLeft)

            layout = QVBoxLayout(dialog)

            # منطقة التمرير
            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            # عرض البيانات
            for key, value in self.data.items():
                if value is not None and str(value).strip():
                    label = QLabel(f"<b>{key}:</b> {value}")
                    label.setWordWrap(True)
                    label.setObjectName("DetailLabel")
                    scroll_layout.addWidget(label)

            scroll.setWidget(scroll_widget)
            layout.addWidget(scroll)

            dialog.exec()

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في عرض التفاصيل: {str(e)}")

    # إدارة المشروع
    def manage_project(self):
        try:
            #from إدارة_المشروع import open_project_phases_window
            project_type = self.data.get('اسم_القسم', 'المشاريع')

            # فتح نافذة مراحل المشروع
            self.project_phases_window = open_project_phases_window(
                self.parent(), self.data, project_type
            )

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح نافذة إدارة المشروع: {str(e)}")
            # في حالة الفشل، استخدم النافذة القديمة كبديل
            try:
                #from إدارة_المشروع import open_project_phases_window
                project_type = self.data.get('التصنيف', 'تصميم معماري')
                self.project_management_window = open_project_phases_window(
                    self.parent(), self.data, project_type
                )
            except:
                pass

    # إدارة المدفوعات والدفعات
    def manage_payments(self):
        pass

    # إدارة مصروفات المشروع
    def manage_expenses(self):
        pass

    # إدارة العهد المالية
    def manage_custody(self):
        pass

    # إدارة وتحديث حالة المشروع
    def manage_status(self):
        try:
            project_id = self.data.get('id')
            project_code = self.data.get('رقم_المشروع', str(project_id))
            year = self.data.get('السنة', QDate.currentDate().year())

            if not project_id:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self.parent(), "خطأ", "معرف المشروع غير متوفر")
                return

            # فتح نافذة تحديث حالة المشروع
            try:
                from منظومة_المهندس import ProjectStatusDialog
                dialog = ProjectStatusDialog(
                    self.parent(), project_id, project_code, year, self.data
                )
                if dialog.exec() == QDialog.Accepted:
                    # تحديث البيانات المحلية
                    # يمكن إضافة منطق تحديث البطاقة هنا
                    pass
            except ImportError:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self.parent(), "حالة المشروع",
                                      f"سيتم فتح نافذة حالة المشروع رقم {project_code}")

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent(), "خطأ", f"فشل في فتح نافذة حالة المشروع: {str(e)}")

#حاوية البطاقات العصرية مع إمكانيات البحث والفلترة
# ModerncardsContainer
class ModernCardsContainer(QScrollArea):
    
    # init
    def __init__(self, card_type="project", parent=None):
        super().__init__(parent)
        self.card_type = card_type
        self.cards = []
        self.all_data = []

        # تهيئة متغيرات التحكم في التوزيع أولاً
        self.card_width = 270  # عرض البطاقة الأساسي
        self.card_spacing = 15  # المسافة بين البطاقات
        self.min_margin = 20   # الهامش الأدنى من الجوانب
        self.cards_per_row_cache = 1  # تخزين مؤقت لعدد البطاقات في الصف
        self._current_filter_data = []  # البيانات المفلترة الحالية

        self.setup_ui()

    #إعداد واجهة حاوية البطاقات المحسنة مع دعم RTL
    # إعداد واجهة المستخدم
    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # تطبيق الاتجاه العربي RTL
        self.setLayoutDirection(Qt.RightToLeft)

        # الحاوية الرئيسية
        main_widget = QWidget()
        main_widget.setLayoutDirection(Qt.RightToLeft)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # هوامش محسنة
        main_layout.setSpacing(8)

        # شريط البحث والفلترة
        self.create_search_bar(main_layout)

        # منطقة البطاقات المحسنة
        self.cards_widget = QWidget()
        self.cards_widget.setLayoutDirection(Qt.RightToLeft)

        # استخدام FlowLayout محسن بدلاً من GridLayout
        self.cards_layout = self.create_enhanced_flow_layout()
        self.cards_widget.setLayout(self.cards_layout)

        main_layout.addWidget(self.cards_widget)
        main_layout.addStretch()

        self.setWidget(main_widget)

    # إنشاء تخطيط تدفق محسن للبطاقات مع دعم RTL
    def create_enhanced_flow_layout(self):
        # استخدام QGridLayout محسن مع إعدادات RTL
        layout = QGridLayout()
        layout.setSpacing(self.card_spacing)
        layout.setContentsMargins(self.min_margin, 10, self.min_margin, 10)
        layout.setAlignment(Qt.AlignTop | Qt.AlignRight)  # محاذاة لليمين للـ RTL

        return layout

    # حساب العدد الأمثل للأعمدة مع دعم محسن للشاشات العريضة
    def calculate_optimal_columns(self, container_width=None):
        if container_width is None:
            container_width = self.width()

        # التأكد من وجود عرض صالح
        if container_width <= 0:
            container_width = 800  # قيمة افتراضية

        # التحقق من التخزين المؤقت لتجنب الحسابات المتكررة
        cache_key = f"{container_width}_{self.card_width}_{self.card_spacing}_{self.min_margin}_widescreen"
        if hasattr(self, '_columns_cache') and cache_key in self._columns_cache:
            return self._columns_cache[cache_key]

        # حساب العرض المتاح للبطاقات (مع خصم الهوامش وشريط التمرير)
        scrollbar_width = 20  # عرض شريط التمرير
        available_width = container_width - (2 * self.min_margin) - scrollbar_width

        # حساب عدد البطاقات التي يمكن وضعها في صف واحد
        single_card_space = self.card_width + self.card_spacing
        cards_per_row = max(1, available_width // single_card_space)

        # حساب العرض الفعلي المطلوب للتحقق من الدقة
        total_cards_width = cards_per_row * self.card_width
        total_spacing_width = max(0, (cards_per_row - 1) * self.card_spacing)
        required_width = total_cards_width + total_spacing_width

        # إذا كان العرض المطلوب أكبر من المتاح، قلل عدد البطاقات
        if required_width > available_width and cards_per_row > 1:
            cards_per_row -= 1

        # ===== تحسين خاص للشاشات العريضة =====
        # للشاشات العريضة (أكبر من 1900px)، فرض حد أدنى 6 بطاقات
        if container_width > 1900:
            min_cards_for_widescreen = 6

            if cards_per_row < min_cards_for_widescreen:
                # التحقق من إمكانية عرض 6 بطاقات على الأقل
                required_width_for_6 = (min_cards_for_widescreen * self.card_width) + \
                                     ((min_cards_for_widescreen - 1) * self.card_spacing)

                if required_width_for_6 <= available_width:
                    cards_per_row = min_cards_for_widescreen
                    print(f"🖥️ شاشة عريضة ({container_width}px): فرض عرض {min_cards_for_widescreen} بطاقات")
                else:
                    # إذا لم تكن هناك مساحة كافية لـ 6 بطاقات، استخدم الحساب الطبيعي
                    print(f"⚠️ شاشة عريضة ({container_width}px): مساحة غير كافية لـ {min_cards_for_widescreen} بطاقات، استخدام {cards_per_row}")

        # تخزين النتيجة في التخزين المؤقت
        if not hasattr(self, '_columns_cache'):
            self._columns_cache = {}
        self._columns_cache[cache_key] = cards_per_row

        # تحديث التخزين المؤقت للصفوف
        self.cards_per_row_cache = cards_per_row

        # إضافة معلومات تشخيصية
        self._last_calculation_info = {
            'container_width': container_width,
            'available_width': available_width,
            'cards_per_row': cards_per_row,
            'is_widescreen': container_width > 1900,
            'required_width': (cards_per_row * self.card_width) + ((cards_per_row - 1) * self.card_spacing)
        }

        return max(1, cards_per_row)

    # الحصول على معلومات تشخيصية حول تخطيط البطاقات
    def get_layout_info(self):
        if hasattr(self, '_last_calculation_info'):
            info = self._last_calculation_info.copy()
            info['card_width'] = self.card_width
            info['card_spacing'] = self.card_spacing
            info['min_margin'] = self.min_margin
            return info
        return None

    # التحقق من وضع الشاشة العريضة
    def is_widescreen_mode(self):
        return self.width() > 1900

    # الحصول على حد الشاشة العريضة
    def get_widescreen_threshold(self):
        return 1900

    # الحصول على الحد الأدنى للبطاقات في الشاشات العريضة
    def get_min_cards_for_widescreen(self):
        return 6

    #إنشاء شريط البحث والفلترة
    # إنشاء شريط البحث
    def create_search_bar(self, layout):
        
        search_frame = QFrame()
        search_frame.setObjectName("SearchFrame")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 10, 15, 10)
        
        # أيقونة البحث
        search_icon = QLabel("🔍")
        search_icon.setFixedSize(30, 30)
        search_icon.setAlignment(Qt.AlignCenter)
        
        # مربع البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث في البيانات...")
        self.search_input.setObjectName("SearchInput")
        self.search_input.textChanged.connect(self.filter_cards)
        
        # فلتر الحالة/التصنيف
        self.status_filter = QComboBox()
        self.status_filter.setObjectName("StatusFilter")
        self.status_filter.currentTextChanged.connect(self.filter_cards)
        
        # زر إعادة تعيين
        reset_btn = QPushButton("🔄")
        reset_btn.setObjectName("ResetBtn")
        reset_btn.setFixedSize(40, 35)
        reset_btn.setToolTip("إعادة تعيين الفلاتر")
        reset_btn.clicked.connect(self.reset_filters)
        
        # search_layout.addWidget(search_icon)
        # search_layout.addWidget(self.search_input, 1)
        # search_layout.addWidget(self.status_filter)
        # search_layout.addWidget(reset_btn)
        
        # layout.addWidget(search_frame)
        
        # تطبيق الأنماط من خلال الدالة المركزية
        self.setup_search_styles(search_frame)
    
    #إضافة البطاقات من قائمة البيانات
    # أضف البطاقات
    def add_cards(self, data_list):
        self.clear_cards()
        self.all_data = data_list
        # تحديث فلتر الحالة/التصنيف
        self.update_status_filter()
        
        # إضافة البطاقات
        self.display_cards(data_list)

    #عرض البطاقات في الشبكة المحسنة مع دعم RTL
    # عرض البطاقات
    def display_cards(self, data_list):
        self.clear_cards()
        if not data_list:
            # عرض رسالة عدم وجود بيانات
            self.show_empty_state()
            return

        # حساب العدد الأمثل للأعمدة
        cols = self.calculate_optimal_columns()

        # عرض البطاقات مع التوزيع الأفقي المحسن
        for i, data in enumerate(data_list):
            card = ModernCard(data, self.card_type)
            card.card_clicked.connect(self.on_card_clicked)
            card.card_double_clicked.connect(self.on_card_double_clicked)

            # حساب الموضع مع الاتجاه العربي RTL
            row = i // cols
            col = i % cols

            # إضافة البطاقة إلى التخطيط
            self.cards_layout.addWidget(card, row, col)
            self.cards.append(card)

        # تطبيق التوزيع المتوازن للأعمدة
        self.apply_column_stretch(cols)

    # تطبيق التوزيع المتوازن للأعمدة
    def apply_column_stretch(self, cols):
        # إزالة أي stretch سابق
        for i in range(self.cards_layout.columnCount()):
            self.cards_layout.setColumnStretch(i, 0)

        # تطبيق stretch متساوي للأعمدة المستخدمة
        for i in range(cols):
            self.cards_layout.setColumnStretch(i, 1)

        # إضافة stretch إضافي للمساحة المتبقية إذا لزم الأمر
        if cols < 10:  # حد أقصى معقول للأعمدة
            self.cards_layout.setColumnStretch(cols, 0)

    #عرض حالة عدم وجود بيانات
    # أظهر حالة فارغة
    def show_empty_state(self):
        
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        empty_icon = QLabel("📭")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_icon.setObjectName("EmptyIcon")

        empty_text = QLabel("لا توجد بيانات للعرض")
        empty_text.setAlignment(Qt.AlignCenter)
        empty_text.setObjectName("EmptyText")
        
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_text)
        
        self.cards_layout.addWidget(empty_widget, 0, 0, 1, -1)
    
    #عرض حالة عدم وجود بيانات
    # بطاقات واضحة
    def clear_cards(self):
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
        
        # مسح جميع العناصر من التخطيط
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    #تحديث خيارات فلتر الحالة/التصنيف
    # تحديث مرشح حالة
    def update_status_filter(self):

        self.status_filter.clear()

        if self.card_type in ["project", "training"]:
            self.status_filter.addItem("كل الحالات")
            statuses = set()
            for data in self.all_data:
                status = data.get('الحالة', '')
                if status:
                    statuses.add(status)
            for status in sorted(statuses):
                self.status_filter.addItem(status)
        elif self.card_type == "employee":
            # للموظفين، نستخدم فلتر الحالة
            self.status_filter.addItem("كل الحالات")
            statuses = set()
            for data in self.all_data:
                status = data.get('الحالة', '')
                if status:
                    statuses.add(status)
            for status in sorted(statuses):
                self.status_filter.addItem(status)
        else:
            self.status_filter.addItem("كل التصنيفات")
            classifications = set()
            for data in self.all_data:
                classification = data.get('التصنيف', '')
                if classification:
                    classifications.add(classification)
            for classification in sorted(classifications):
                self.status_filter.addItem(classification)

    # تم نقل دالة filter_cards المحسنة إلى الأسفل

    #إعادة تعيين جميع الفلاتر - محسن
    # إعادة تعيين جميع الفلاتر وعرض جميع البيانات
    def reset_filters(self):
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)

        # إعادة تعيين البيانات المفلترة
        self._current_filter_data = self.all_data
        self.display_cards(self.all_data)

    #معالجة النقر على البطاقة
    # معالجة النقر على البطاقة - يتضمن الإجراءات من الأزرار
    def on_card_clicked(self, data):
        try:
            # التحقق من وجود إجراء محدد من الأزرار
            if isinstance(data, dict) and "action" in data:
                action = data["action"]
                actual_data = data["data"]

                # معالجة الإجراءات المختلفة
                if action == "عرض":
                    self.handle_view_action(actual_data)
                elif action == "تعديل":
                    self.handle_edit_action(actual_data)
                elif action == "حذف":
                    self.handle_delete_action(actual_data)
            else:
                # النقر العادي على البطاقة - عرض التفاصيل
                self.handle_view_action(data)

        except Exception as e:
            print(f"خطأ في معالجة النقر على البطاقة: {e}")

    #معالجة النقر المزدوج على البطاقة
    # معالجة النقر المزدوج على البطاقة - فتح نافذة التعديل
    def on_card_double_clicked(self, data):
        try:
            self.handle_edit_action(data)
        except Exception as e:
            print(f"خطأ في معالجة النقر المزدوج على البطاقة: {e}")

    # معالجة إجراء العرض
    def handle_view_action(self, data):
        try:
            # إرسال إشارة للنظام الرئيسي لمعالجة العرض
            if hasattr(self.parent(), 'handle_card_action'):
                self.parent().handle_card_action("عرض", self.card_type, data)
        except Exception as e:
            print(f"خطأ في معالجة إجراء العرض: {e}")

    # معالجة إجراء التعديل
    def handle_edit_action(self, data):
        try:
            # إرسال إشارة للنظام الرئيسي لمعالجة التعديل
            if hasattr(self.parent(), 'handle_card_action'):
                self.parent().handle_card_action("تعديل", self.card_type, data)
        except Exception as e:
            print(f"خطأ في معالجة إجراء التعديل: {e}")

    # معالجة إجراء الحذف
    def handle_delete_action(self, data):
        try:
            # إرسال إشارة للنظام الرئيسي لمعالجة الحذف
            if hasattr(self.parent(), 'handle_card_action'):
                self.parent().handle_card_action("حذف", self.card_type, data)
        except Exception as e:
            print(f"خطأ في معالجة إجراء الحذف: {e}")

    #إعادة ترتيب البطاقات عند تغيير حجم النافذة - محسن
    # إعادة ترتيب البطاقات تلقائياً عند تغيير حجم النافذة
    def resizeEvent(self, event):
        super().resizeEvent(event)

        # تأخير إعادة الترتيب لتجنب الاستدعاءات المتكررة
        if hasattr(self, '_resize_timer'):
            self._resize_timer.stop()

        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_timeout)
        self._resize_timer.start(150)  # تأخير 150ms

    # معالجة تغيير الحجم بعد التأخير
    def _on_resize_timeout(self):
        if hasattr(self, 'all_data') and self.all_data:
            # إعادة عرض البطاقات مع التوزيع الجديد
            current_filter = getattr(self, '_current_filter_data', self.all_data)
            self.display_cards(current_filter)

    # فلترة البطاقات حسب النص والحالة - محسن
    def filter_cards(self):
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()

        filtered_data = []

        for data in self.all_data:
            # فلترة النص
            text_match = True
            if search_text:
                # البحث في جميع القيم النصية
                text_match = any(
                    search_text in str(value).lower()
                    for value in data.values()
                    if isinstance(value, (str, int, float))
                )

            # فلترة الحالة/التصنيف
            status_match = True
            if status_filter not in ["كل الحالات", "كل التصنيفات"]:
                if self.card_type in ["project", "training", "employee"]:
                    status_match = data.get('الحالة', '') == status_filter
                else:
                    status_match = data.get('التصنيف', '') == status_filter

            if text_match and status_match:
                filtered_data.append(data)

        # حفظ البيانات المفلترة الحالية
        self._current_filter_data = filtered_data
        self.display_cards(filtered_data)

    # مزامنة الفلاتر من الواجهة الرئيسية
    def sync_filters_from_main(self, search_text="", classification_filter="", status_filter=""):
        try:
            # تحديث نص البحث
            if search_text != self.search_input.text():
                self.search_input.setText(search_text)

            # تحديث فلتر التصنيف/الحالة
            current_status_filter = self.status_filter.currentText()

            # تحديد الفلتر المناسب حسب نوع البطاقة
            if self.card_type in ["project", "training", "employee", "supplier"]:
                # للمشاريع والتدريب والموظفين نستخدم فلتر الحالة
                if status_filter and status_filter != "كل الحالات" and status_filter != current_status_filter:
                    index = self.status_filter.findText(status_filter)
                    if index >= 0:
                        self.status_filter.setCurrentIndex(index)
            else:
                # للأقسام الأخرى نستخدم فلتر التصنيف
                if classification_filter and classification_filter != "كل التصنيفات" and classification_filter != current_status_filter:
                    index = self.status_filter.findText(classification_filter)
                    if index >= 0:
                        self.status_filter.setCurrentIndex(index)

            # تطبيق الفلاتر
            self.filter_cards()

        except Exception as e:
            print(f"خطأ في مزامنة الفلاتر: {e}")

    # تطبيق الفلاتر الموحدة من النظام الرئيسي
    def apply_unified_filters(self, search_text="", classification_filter="", status_filter="", job_filter="", year_filter=""):
        try:
            # حفظ الفلاتر الحالية
            self._unified_filters = {
                'search': search_text,
                'classification': classification_filter,
                'status': status_filter,
                'job_filter': job_filter,
                'year': year_filter
            }

            filtered_data = []

            for data in self.all_data:
                # فلترة النص
                text_match = True
                if search_text:
                    text_match = any(
                        search_text.lower() in str(value).lower()
                        for value in data.values()
                        if isinstance(value, (str, int, float))
                    )

                # فلترة التصنيف
                classification_match = True
                if classification_filter and classification_filter != "كل التصنيفات":
                    classification_match = data.get('التصنيف', '') == classification_filter

                # فلترة الحالة
                status_match = True
                if status_filter and status_filter != "كل الحالات":
                    status_match = data.get('الحالة', '') == status_filter

                # فلترة الوظيفة (للموظفين فقط)
                job_match = True
                if job_filter and job_filter != "كل الوظائف" and self.card_type == "employee":
                    job_match = data.get('الوظيفة', '') == job_filter

                # فلترة السنة (إذا كانت متوفرة في البيانات)
                year_match = True
                if year_filter and hasattr(data, 'get'):
                    # محاولة استخراج السنة من تاريخ الإضافة أو أي حقل تاريخ
                    date_fields = ['تاريخ_الإضافة', 'تاريخ_البدء', 'التاريخ']
                    for date_field in date_fields:
                        if date_field in data and data[date_field]:
                            try:
                                # استخراج السنة من التاريخ
                                date_str = str(data[date_field])
                                if year_filter in date_str:
                                    break
                            except:
                                continue
                    else:
                        # إذا لم نجد تطابق في أي حقل تاريخ
                        if year_filter != str(datetime.now().year):
                            year_match = False

                if text_match and classification_match and status_match and job_match and year_match:
                    filtered_data.append(data)

            # حفظ البيانات المفلترة وعرضها
            self._current_filter_data = filtered_data
            self.display_cards(filtered_data)

        except Exception as e:
            print(f"خطأ في تطبيق الفلاتر الموحدة: {e}")

    # الحصول على الفلاتر الحالية
    def get_current_filters(self):
        return {
            'search': self.search_input.text(),
            'status': self.status_filter.currentText(),
            'unified_filters': getattr(self, '_unified_filters', {})
        }

# ==================== الدوال المركزية لتطبيق الأنماط ====================

# دالة مركزية لتطبيق أنماط البطاقات العصرية مع دعم RTL
def setup_card_styles(card_instance):
    border_color = card_instance.get_border_color()

    card_instance.setStyleSheet(f"""
        /* أنماط البطاقة الرئيسية */
        QFrame#ModernCard {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: 2px solid {border_color};
            border-radius: 15px;
            margin: 5px;
        }}
        QFrame#ModernCard:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
            border: 3px solid {border_color};
        }}

        /* أنماط أيقونة البطاقة */
        QLabel#CardIcon {{
            font-size: 24px;
            background-color: {border_color};
            border-radius: 20px;
            color: white;
        }}

        /* أنماط عنوان البطاقة */
        QLabel#CardTitle {{
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin: 0 10px;
        }}

        /* أنماط حالة البطاقة */
        QLabel#CardStatus {{
            background-color: {border_color};
            color: white;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
        }}

        /* أنماط محتوى البطاقة */
        QFrame#CardContent {{
            background-color: rgba(255,255,255,0.8);
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }}

        /* أنماط معلومات البطاقة العامة */
        QLabel#CardInfo {{
            font-size: 13px;
            color: #495057;
            margin: 2px 0;
        }}

        /* أنماط المبالغ المالية */
        QLabel#TotalAmount {{
            color: #3498db;
            font-weight: bold;
        }}
        QLabel#UndefinedAmount {{
            color: #95a5a6;
            font-weight: bold;
        }}
        QLabel#RemainingAmount {{
            font-weight: bold;
            color: #e74c3c;
        }}
        QLabel#PaidAmount {{
            color: #27ae60;
            font-weight: bold;
        }}
        QLabel#BalanceAmount {{
            font-weight: bold;
            color: #27ae60;
        }}
        QLabel#ExpenseAmount {{
            font-weight: bold;
            color: #f39c12;
            font-size: 14px;
        }}
        QLabel#PropertyPrice {{
            font-weight: bold;
            color: #8e44ad;
            font-size: 14px;
        }}

        /* أنماط معلومات الوقت والحالة */
        QLabel#TimeInfo {{
            font-size: 12px;
            color: #6c757d;
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 5px;
        }}

        /* أنماط شريط التقدم */
        QProgressBar#ProjectProgress {{
            border: 2px solid #dee2e6;
            border-radius: 8px;
            text-align: center;
            height: 20px;
        }}
        QProgressBar#ProjectProgress::chunk {{
            background-color: {border_color};
            border-radius: 6px;
        }}

        /* أنماط التفاصيل العامة */
        QLabel#DetailLabel {{
            padding: 5px;
            border-bottom: 1px solid #eee;
        }}

        /* أنماط حالة عدم وجود البيانات */
        QLabel#EmptyIcon {{
            font-size: 64px;
            color: #6c757d;
            margin: 20px;
        }}
        QLabel#EmptyText {{
            font-size: 18px;
            color: #6c757d;
            font-weight: bold;
        }}
    """)

    # تطبيق الأنماط الديناميكية للعناصر ذات الألوان المخصصة
    apply_dynamic_styles(card_instance)

# تطبيق الأنماط الديناميكية للعناصر ذات الألوان المخصصة
def apply_dynamic_styles(card_instance):
    # البحث عن العناصر ذات الخصائص المخصصة وتطبيق الأنماط عليها
    for child in card_instance.findChildren(QLabel):
        # تطبيق أنماط التصنيفات
        if child.objectName() == "CategoryLabel" and child.property("category_color"):
            color = child.property("category_color")
            child.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }}
            """)

        # تطبيق أنماط حالة الموظف
        elif child.objectName() == "EmployeeStatusLabel" and child.property("status_color"):
            color = child.property("status_color")
            child.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                    text-align: center;
                }}
            """)

        # تطبيق أنماط حالة المشروع والوقت
        elif child.objectName() == "StatusTimeLabel" and child.property("status_color"):
            color = child.property("status_color")
            child.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: {color};
                    font-size: 12px;
                }}
            """)

# دالة مركزية لتطبيق أنماط شريط البحث والفلترة
def setup_search_styles(search_frame):
    search_frame.setStyleSheet("""
        /* أنماط إطار البحث */
        QFrame#SearchFrame {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
        }

        /* أنماط مربع البحث */
        QLineEdit#SearchInput {
            border: 2px solid #ced4da;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: white;
        }
        QLineEdit#SearchInput:focus {
            border-color: #80bdff;
            outline: none;
        }

        /* أنماط فلتر الحالة */
        QComboBox#StatusFilter {
            border: 2px solid #ced4da;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: white;
            min-width: 150px;
        }

        /* أنماط زر إعادة التعيين */
        QPushButton#ResetBtn {
            background-color: #6c757d;
            border: none;
            border-radius: 17px;
            font-size: 16px;
            color: white;
        }
        QPushButton#ResetBtn:hover {
            background-color: #5a6268;
        }
    """)

# إضافة الدوال المركزية إلى الكلاسات
ModernCard.setup_card_styles = lambda self: setup_card_styles(self)
ModernCardsContainer.setup_search_styles = lambda self, frame: setup_search_styles(frame)
