#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة إدارة الإعدادات الموحدة
تدمج إدارة التصنيفات وأسعار المراحل ومواعيد العمل في نافذة واحدة
"""

import sys
import os
from datetime import datetime, date, time
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
from أزرار_الواجهة import table_setting

# نافذة إدارة الإعدادات الموحدة
class UnifiedSettingsWindow(QDialog):
    
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # متغيرات التصنيفات
        self.current_section = None
        self.selected_color = "#3498db"
        
        # متغيرات أسعار المراحل
        self.current_project_type = None
        self.current_section_phases = None
        
        # متغيرات مواعيد العمل
        self.current_schedule_id = None
        self.workday_checkboxes = {}
        
        # إعداد النافذة الأساسية
        self.setup_window()
        
        # إنشاء التابات
        self.create_tabs()
        
        # تحميل البيانات الأولية
        self.load_initial_data()
        
        # تطبيق الستايل
        apply_stylesheet(self)
        
        # تطبيق الأنماط المركزية
        self.apply_unified_settings_styles()

    # إعداد النافذة الأساسية
    def setup_window(self):
        self.setWindowTitle("إدارة الإعدادات الموحدة")
        self.setGeometry(100, 100, 1400, 900)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # العنوان الرئيسي
        title_label = QLabel("إدارة الإعدادات الموحدة")
        title_label.setObjectName("main_title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # إنشاء التابات
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("main_tab_widget")
        main_layout.addWidget(self.tab_widget)
        
    # إنشاء التابات الرئيسية
    def create_tabs(self):
        # تاب إدارة التصنيفات
        self.create_categories_tab()
        
        # تاب إدارة أسعار المراحل
        self.create_phases_pricing_tab()
        
        # تاب إدارة مواعيد العمل
        self.create_work_schedule_tab()

    # إنشاء تاب إدارة التصنيفات
    def create_categories_tab(self):
        tab = QWidget()
        tab.setObjectName("categories_tab")
        layout = QHBoxLayout(tab)
        layout.setSpacing(15)

        # الجانب الأيمن - قائمة الأقسام
        sections_panel = self.create_sections_panel()
        layout.addWidget(sections_panel, 1)

        # الجانب الأيسر - إدارة التصنيفات
        categories_panel = self.create_categories_management_panel()
        layout.addWidget(categories_panel, 3)

        self.tab_widget.addTab(tab, qta.icon('fa5s.tags', color='#e74c3c'), "إدارة التصنيفات")

    # إنشاء لوحة الأقسام
    def create_sections_panel(self):
        panel = QGroupBox("الأقسام المتاحة")
        panel.setObjectName("sections_panel")
        layout = QVBoxLayout(panel)

        # قائمة الأقسام
        self.sections_list = QListWidget()
        self.sections_list.setObjectName("sections_list")
        self.sections_list.itemClicked.connect(self.on_section_selected)
        layout.addWidget(self.sections_list)

        return panel

    # إنشاء لوحة إدارة التصنيفات
    def create_categories_management_panel(self):
        panel = QGroupBox("إدارة التصنيفات")
        panel.setObjectName("categories_management_panel")
        layout = QVBoxLayout(panel)

        # معلومات القسم المحدد
        self.section_info_label = QLabel("اختر قسماً لعرض تصنيفاته")
        self.section_info_label.setObjectName("section_info_label")
        self.section_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.section_info_label)

        # نموذج إضافة تصنيف جديد
        add_form = self.create_add_category_form()
        layout.addWidget(add_form)

        # جدول التصنيفات الموجودة
        categories_table = self.create_categories_table()
        layout.addWidget(categories_table)

        return panel

    # إنشاء نموذج إضافة تصنيف جديد
    def create_add_category_form(self):
        form_group = QGroupBox("إضافة تصنيف جديد")
        form_group.setObjectName("add_category_form")
        layout = QVBoxLayout(form_group)

        # تخطيط النموذج
        form_layout = QFormLayout()

        # اسم التصنيف
        self.category_name_edit = QLineEdit()
        self.category_name_edit.setObjectName("category_name_edit")
        self.category_name_edit.setPlaceholderText("اسم التصنيف الجديد")
        form_layout.addRow("اسم التصنيف:", self.category_name_edit)

        # الوصف
        self.description_edit = QLineEdit()
        self.description_edit.setObjectName("description_edit")
        self.description_edit.setPlaceholderText("وصف التصنيف")
        form_layout.addRow("الوصف:", self.description_edit)

        # اللون
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setObjectName("color_button")
        self.color_button.setFixedSize(40, 30)
        self.color_button.clicked.connect(self.choose_color)
        
        self.color_label = QLabel("#3498db")
        self.color_label.setObjectName("color_label")
        
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        color_layout.addStretch()
        
        form_layout.addRow("اللون:", color_layout)

        layout.addLayout(form_layout)

        # زر الإضافة
        add_button = QPushButton("إضافة التصنيف")
        add_button.setObjectName("add_category_button")
        add_button.clicked.connect(self.add_category)
        layout.addWidget(add_button)

        return form_group

    # إنشاء جدول التصنيفات
    def create_categories_table(self):
        table_group = QGroupBox("التصنيفات الموجودة")
        table_group.setObjectName("categories_table_group")
        layout = QVBoxLayout(table_group)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث:")
        search_label.setObjectName("search_label")
        
        self.categories_search_edit = QLineEdit()
        self.categories_search_edit.setObjectName("categories_search_edit")
        self.categories_search_edit.setPlaceholderText("ابحث في التصنيفات...")
        self.categories_search_edit.textChanged.connect(self.filter_categories)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.categories_search_edit)
        layout.addLayout(search_layout)

        # الجدول
        self.categories_table = QTableWidget()
        self.categories_table.setObjectName("categories_table")
        self.setup_categories_table()
        layout.addWidget(self.categories_table)

        return table_group

    # إعداد جدول التصنيفات
    def setup_categories_table(self):
        headers = ["المعرف", "اسم التصنيف", "الوصف", "اللون", "الإجراءات"]
        self.categories_table.setColumnCount(len(headers))
        self.categories_table.setHorizontalHeaderLabels(headers)
        self.categories_table.setLayoutDirection(Qt.RightToLeft)
        table_setting(self.categories_table)
        
        # إخفاء عمود المعرف
        self.categories_table.setColumnHidden(0, True)

    # إنشاء تاب إدارة أسعار المراحل
    def create_phases_pricing_tab(self):
        tab = QWidget()
        tab.setObjectName("phases_pricing_tab")
        layout = QHBoxLayout(tab)
        layout.setSpacing(15)

        # الجانب الأيمن - قائمة الأقسام وأنواع المشاريع
        sections_phases_panel = self.create_sections_phases_panel()
        layout.addWidget(sections_phases_panel, 1)

        # الجانب الأيسر - إدارة أسعار المراحل
        phases_management_panel = self.create_phases_management_panel()
        layout.addWidget(phases_management_panel, 3)

        self.tab_widget.addTab(tab, qta.icon('fa5s.calculator', color='#f39c12'), "أسعار المراحل")

    # إنشاء لوحة الأقسام وأنواع المشاريع
    def create_sections_phases_panel(self):
        panel = QGroupBox("الأقسام وأنواع المشاريع")
        panel.setObjectName("sections_phases_panel")
        layout = QVBoxLayout(panel)

        # شجرة الأقسام وأنواع المشاريع
        self.sections_tree = QTreeWidget()
        self.sections_tree.setObjectName("sections_tree")
        self.sections_tree.setHeaderLabel("الأقسام وأنواع المشاريع")
        self.sections_tree.itemClicked.connect(self.on_section_item_selected)
        layout.addWidget(self.sections_tree)

        return panel

    # إنشاء لوحة إدارة أسعار المراحل
    def create_phases_management_panel(self):
        panel = QGroupBox("إدارة أسعار المراحل")
        panel.setObjectName("phases_management_panel")
        layout = QVBoxLayout(panel)

        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        
        add_phase_btn = QPushButton("إضافة مرحلة")
        add_phase_btn.setObjectName("add_phase_button")
        add_phase_btn.clicked.connect(self.add_phase)
        
        edit_phase_btn = QPushButton("تعديل مرحلة")
        edit_phase_btn.setObjectName("edit_phase_button")
        edit_phase_btn.clicked.connect(self.edit_phase)
        
        delete_phase_btn = QPushButton("حذف مرحلة")
        delete_phase_btn.setObjectName("delete_phase_button")
        delete_phase_btn.clicked.connect(self.delete_phase)
        
        toolbar_layout.addWidget(add_phase_btn)
        toolbar_layout.addWidget(edit_phase_btn)
        toolbar_layout.addWidget(delete_phase_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث:")
        search_label.setObjectName("phases_search_label")
        
        self.phases_search_edit = QLineEdit()
        self.phases_search_edit.setObjectName("phases_search_edit")
        self.phases_search_edit.setPlaceholderText("ابحث في اسم المرحلة أو الوصف...")
        self.phases_search_edit.textChanged.connect(self.filter_phases)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.phases_search_edit)
        layout.addLayout(search_layout)

        # جدول أسعار المراحل
        self.phases_table = QTableWidget()
        self.phases_table.setObjectName("phases_table")
        self.setup_phases_table()
        layout.addWidget(self.phases_table)

        return panel

    # إعداد جدول أسعار المراحل
    def setup_phases_table(self):
        headers = ["المعرف", "اسم المرحلة", "الوصف", "الوحدة", "السعر", "القسم", "نوع المشروع"]
        self.phases_table.setColumnCount(len(headers))
        self.phases_table.setHorizontalHeaderLabels(headers)
        self.phases_table.setLayoutDirection(Qt.RightToLeft)
        table_setting(self.phases_table)
        
        # إخفاء عمود المعرف
        self.phases_table.setColumnHidden(0, True)

    # إنشاء تاب إدارة مواعيد العمل
    def create_work_schedule_tab(self):
        tab = QWidget()
        tab.setObjectName("work_schedule_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # قسم إعدادات الدوام
        schedule_section = self.create_schedule_settings_section()
        layout.addWidget(schedule_section)

        # قسم أيام العمل
        workdays_section = self.create_workdays_section()
        layout.addWidget(workdays_section)

        # قسم الإعدادات المتقدمة
        advanced_section = self.create_advanced_settings_section()
        layout.addWidget(advanced_section)

        # أزرار الحفظ
        buttons_layout = QHBoxLayout()
        save_schedule_btn = QPushButton("حفظ إعدادات الدوام")
        save_schedule_btn.setObjectName("save_schedule_button")
        save_schedule_btn.clicked.connect(self.save_work_schedule)

        reset_schedule_btn = QPushButton("إعادة تعيين")
        reset_schedule_btn.setObjectName("reset_schedule_button")
        reset_schedule_btn.clicked.connect(self.reset_work_schedule)

        buttons_layout.addWidget(save_schedule_btn)
        buttons_layout.addWidget(reset_schedule_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        self.tab_widget.addTab(tab, qta.icon('fa5s.clock', color='#3498db'), "مواعيد العمل")

    # إنشاء قسم إعدادات الدوام
    def create_schedule_settings_section(self):
        section = QGroupBox("إعدادات الدوام")
        section.setObjectName("schedule_settings_section")
        layout = QVBoxLayout(section)

        # نوع نظام العمل
        system_group = QGroupBox("نوع نظام العمل")
        system_group.setObjectName("system_type_group")
        system_layout = QVBoxLayout(system_group)

        self.single_shift_radio = QRadioButton("فترة واحدة")
        self.single_shift_radio.setObjectName("single_shift_radio")
        self.single_shift_radio.setChecked(True)

        self.double_shift_radio = QRadioButton("فترتين (صباحية ومسائية)")
        self.double_shift_radio.setObjectName("double_shift_radio")

        system_layout.addWidget(self.single_shift_radio)
        system_layout.addWidget(self.double_shift_radio)

        # ربط الإشارات
        self.single_shift_radio.toggled.connect(self.on_system_type_changed)
        self.double_shift_radio.toggled.connect(self.on_system_type_changed)

        layout.addWidget(system_group)

        # الفترة الصباحية
        morning_group = QGroupBox("الفترة الصباحية")
        morning_group.setObjectName("morning_group")
        morning_layout = QFormLayout(morning_group)

        self.morning_start_time = QTimeEdit()
        self.morning_start_time.setObjectName("morning_start_time")
        self.morning_start_time.setDisplayFormat("hh:mm AP")
        self.morning_start_time.setTime(QTime(8, 0))

        self.morning_end_time = QTimeEdit()
        self.morning_end_time.setObjectName("morning_end_time")
        self.morning_end_time.setDisplayFormat("hh:mm AP")
        self.morning_end_time.setTime(QTime(17, 0))

        morning_layout.addRow("وقت بداية الدوام:", self.morning_start_time)
        morning_layout.addRow("وقت نهاية الدوام:", self.morning_end_time)

        layout.addWidget(morning_group)

        # الفترة المسائية
        self.evening_group = QGroupBox("الفترة المسائية")
        self.evening_group.setObjectName("evening_group")
        evening_layout = QFormLayout(self.evening_group)

        self.evening_start_time = QTimeEdit()
        self.evening_start_time.setObjectName("evening_start_time")
        self.evening_start_time.setDisplayFormat("hh:mm AP")
        self.evening_start_time.setTime(QTime(18, 0))

        self.evening_end_time = QTimeEdit()
        self.evening_end_time.setObjectName("evening_end_time")
        self.evening_end_time.setDisplayFormat("hh:mm AP")
        self.evening_end_time.setTime(QTime(22, 0))

        evening_layout.addRow("وقت بداية الدوام:", self.evening_start_time)
        evening_layout.addRow("وقت نهاية الدوام:", self.evening_end_time)

        self.evening_group.setEnabled(False)  # معطل افتراضياً
        layout.addWidget(self.evening_group)

        return section

    # إنشاء قسم أيام العمل
    def create_workdays_section(self):
        section = QGroupBox("أيام الدوام الأسبوعية")
        section.setObjectName("workdays_section")
        layout = QVBoxLayout(section)

        # إنشاء checkboxes لأيام الأسبوع
        self.workday_checkboxes = {}
        days = [
            ("الأحد", "sunday"),
            ("الاثنين", "monday"),
            ("الثلاثاء", "tuesday"),
            ("الأربعاء", "wednesday"),
            ("الخميس", "thursday"),
            ("الجمعة", "friday"),
            ("السبت", "saturday")
        ]

        for arabic_day, english_day in days:
            checkbox = QCheckBox(arabic_day)
            checkbox.setObjectName(f"workday_{english_day}")
            if english_day in ["sunday", "monday", "tuesday", "wednesday", "thursday"]:
                checkbox.setChecked(True)  # أيام العمل الافتراضية
            self.workday_checkboxes[english_day] = checkbox
            layout.addWidget(checkbox)

        return section

    # إنشاء قسم الإعدادات المتقدمة
    def create_advanced_settings_section(self):
        section = QGroupBox("الإعدادات المتقدمة")
        section.setObjectName("advanced_settings_section")
        layout = QFormLayout(section)

        # فترة السماح للتأخير
        self.late_tolerance_spin = QSpinBox()
        self.late_tolerance_spin.setObjectName("late_tolerance_spin")
        self.late_tolerance_spin.setRange(0, 60)
        self.late_tolerance_spin.setValue(15)
        self.late_tolerance_spin.setSuffix(" دقيقة")
        layout.addRow("فترة السماح للتأخير:", self.late_tolerance_spin)

        # فترة السماح للانصراف المبكر
        self.early_leave_tolerance_spin = QSpinBox()
        self.early_leave_tolerance_spin.setObjectName("early_leave_tolerance_spin")
        self.early_leave_tolerance_spin.setRange(0, 60)
        self.early_leave_tolerance_spin.setValue(10)
        self.early_leave_tolerance_spin.setSuffix(" دقيقة")
        layout.addRow("فترة السماح للانصراف المبكر:", self.early_leave_tolerance_spin)

        # الحد الأدنى لساعات العمل اليومية
        self.min_work_hours_spin = QDoubleSpinBox()
        self.min_work_hours_spin.setObjectName("min_work_hours_spin")
        self.min_work_hours_spin.setRange(1.0, 24.0)
        self.min_work_hours_spin.setValue(8.0)
        self.min_work_hours_spin.setSuffix(" ساعة")
        layout.addRow("الحد الأدنى لساعات العمل:", self.min_work_hours_spin)

        # تفعيل نظام الإنذارات
        self.enable_alerts_checkbox = QCheckBox("تفعيل الإنذارات للتأخير والغياب")
        self.enable_alerts_checkbox.setObjectName("enable_alerts_checkbox")
        self.enable_alerts_checkbox.setChecked(True)
        layout.addRow("الإنذارات:", self.enable_alerts_checkbox)

        return section

    # تحميل البيانات الأولية
    def load_initial_data(self):
        self.load_sections()
        self.load_sections_tree()
        self.load_current_work_schedule()

    # دوال معالجة الأحداث
    # معالج اختيار قسم من قائمة الأقسام
    def on_section_selected(self, item):
        if not item:
            return

        section_name = item.text()
        self.current_section = section_name

        # تحديث معلومات القسم
        self.section_info_label.setText(f"إدارة تصنيفات قسم: {section_name}")

        # تحميل تصنيفات القسم المحدد
        self.load_categories()

    # معالج اختيار عنصر من شجرة الأقسام
    def on_section_item_selected(self, item, column):
        if not item:
            return

        # التحقق من نوع العنصر المحدد
        if item.parent():  # إذا كان عنصر فرعي (نوع مشروع)
            self.current_project_type = item.text(0)
            self.current_section_phases = item.parent().text(0)
        else:  # إذا كان عنصر رئيسي (قسم)
            self.current_section_phases = item.text(0)
            self.current_project_type = None

        # تحميل أسعار المراحل للعنصر المحدد
        self.load_phases_pricing()

    # اختيار لون للتصنيف
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}; border-radius: 5px;")
            self.color_label.setText(self.selected_color)

    # إضافة تصنيف جديد
    def add_category(self):
        if not self.current_section:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار قسم أولاً")
            return

        category_name = self.category_name_edit.text().strip()
        description = self.description_edit.text().strip()

        if not category_name:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم التصنيف")
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # التحقق من عدم وجود تصنيف بنفس الاسم في نفس القسم
            cursor.execute("""
                SELECT COUNT(*) FROM التصنيفات
                WHERE اسم_التصنيف = %s AND اسم_القسم = %s
            """, (category_name, self.current_section))

            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "تحذير", "يوجد تصنيف بنفس الاسم في هذا القسم")
                return

            # إضافة التصنيف الجديد
            cursor.execute("""
                INSERT INTO التصنيفات (اسم_القسم, اسم_التصنيف, وصف_التصنيف, لون_التصنيف)
                VALUES (%s, %s, %s, %s)
            """, (self.current_section, category_name, description, self.selected_color))

            conn.commit()
            conn.close()

            # تنظيف النموذج
            self.category_name_edit.clear()
            self.description_edit.clear()
            self.selected_color = "#3498db"
            self.color_button.setStyleSheet("background-color: #3498db; border-radius: 5px;")
            self.color_label.setText("#3498db")

            # تحديث الجدول
            self.load_categories()

            QMessageBox.information(self, "نجح", f"تم إضافة التصنيف '{category_name}' بنجاح")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إضافة التصنيف: {e}")

    # فلترة التصنيفات
    def filter_categories(self):
        search_text = self.categories_search_edit.text().lower()

        for row in range(self.categories_table.rowCount()):
            show_row = False
            for col in range(1, self.categories_table.columnCount() - 1):  # تجاهل عمود المعرف والإجراءات
                item = self.categories_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.categories_table.setRowHidden(row, not show_row)

    # إضافة مرحلة جديدة
    def add_phase(self):
        if not self.current_section_phases:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار قسم أو نوع مشروع أولاً")
            return

        dialog = PhaseDialog(self, mode="add",
                           section=self.current_section_phases,
                           project_type=self.current_project_type)
        if dialog.exec() == QDialog.Accepted:
            self.load_phases_pricing()

    # تعديل مرحلة
    def edit_phase(self):
        current_row = self.phases_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار مرحلة للتعديل")
            return

        phase_id = self.phases_table.item(current_row, 0).text()
        dialog = PhaseDialog(self, mode="edit", phase_id=int(phase_id))
        if dialog.exec() == QDialog.Accepted:
            self.load_phases_pricing()

    # حذف مرحلة
    def delete_phase(self):
        current_row = self.phases_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار مرحلة للحذف")
            return

        phase_name = self.phases_table.item(current_row, 1).text()
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                   f"هل أنت متأكد من حذف المرحلة '{phase_name}'؟")

        if reply == QMessageBox.Yes:
            try:
                phase_id = self.phases_table.item(current_row, 0).text()

                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("DELETE FROM اسعار_المراحل WHERE id = %s", (phase_id,))
                conn.commit()
                conn.close()

                self.load_phases_pricing()
                QMessageBox.information(self, "نجح", "تم حذف المرحلة بنجاح")

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف المرحلة: {e}")

    # فلترة المراحل
    def filter_phases(self):
        search_text = self.phases_search_edit.text().lower()

        for row in range(self.phases_table.rowCount()):
            show_row = False
            for col in range(1, self.phases_table.columnCount()):  # تجاهل عمود المعرف
                item = self.phases_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.phases_table.setRowHidden(row, not show_row)

    # معالج تغيير نوع نظام العمل
    def on_system_type_changed(self):
        if self.double_shift_radio.isChecked():
            self.evening_group.setEnabled(True)
        else:
            self.evening_group.setEnabled(False)

    # حفظ إعدادات مواعيد العمل
    def save_work_schedule(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جمع بيانات الدوام
            system_type = "فترتين" if self.double_shift_radio.isChecked() else "فترة_واحدة"
            morning_start = self.morning_start_time.time().toString("HH:mm:ss")
            morning_end = self.morning_end_time.time().toString("HH:mm:ss")
            evening_start = self.evening_start_time.time().toString("HH:mm:ss") if self.double_shift_radio.isChecked() else None
            evening_end = self.evening_end_time.time().toString("HH:mm:ss") if self.double_shift_radio.isChecked() else None

            # جمع أيام العمل
            sunday = self.workday_checkboxes["sunday"].isChecked()
            monday = self.workday_checkboxes["monday"].isChecked()
            tuesday = self.workday_checkboxes["tuesday"].isChecked()
            wednesday = self.workday_checkboxes["wednesday"].isChecked()
            thursday = self.workday_checkboxes["thursday"].isChecked()
            friday = self.workday_checkboxes["friday"].isChecked()
            saturday = self.workday_checkboxes["saturday"].isChecked()

            # الإعدادات المتقدمة
            late_tolerance = self.late_tolerance_spin.value()

            # حفظ أو تحديث الإعدادات
            if self.current_schedule_id:
                cursor.execute("""
                    UPDATE مواعيد_العمل SET
                        نوع_النظام = %s, وقت_حضور_صباحي = %s, وقت_انصراف_صباحي = %s,
                        وقت_حضور_مسائي = %s, وقت_انصراف_مسائي = %s,
                        الأحد = %s, الاثنين = %s, الثلاثاء = %s, الأربعاء = %s, الخميس = %s, الجمعة = %s, السبت = %s,
                        فترة_التأخير_المسموحة = %s, تاريخ_التحديث = NOW()
                    WHERE id = %s
                """, (system_type, morning_start, morning_end, evening_start, evening_end,
                     sunday, monday, tuesday, wednesday, thursday, friday, saturday,
                     late_tolerance, self.current_schedule_id))
            else:
                cursor.execute("""
                    INSERT INTO مواعيد_العمل
                    (نوع_النظام, وقت_حضور_صباحي, وقت_انصراف_صباحي, وقت_حضور_مسائي, وقت_انصراف_مسائي,
                     الأحد, الاثنين, الثلاثاء, الأربعاء, الخميس, الجمعة, السبت, فترة_التأخير_المسموحة)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (system_type, morning_start, morning_end, evening_start, evening_end,
                     sunday, monday, tuesday, wednesday, thursday, friday, saturday, late_tolerance))

                self.current_schedule_id = cursor.lastrowid

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", "تم حفظ إعدادات مواعيد العمل بنجاح")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ الإعدادات: {e}")

    # إعادة تعيين مواعيد العمل
    def reset_work_schedule(self):
        reply = QMessageBox.question(self, "تأكيد إعادة التعيين",
                                   "هل أنت متأكد من إعادة تعيين جميع إعدادات مواعيد العمل؟")

        if reply == QMessageBox.Yes:
            # إعادة تعيين القيم الافتراضية
            self.single_shift_radio.setChecked(True)
            self.morning_start_time.setTime(QTime(8, 0))
            self.morning_end_time.setTime(QTime(17, 0))
            self.evening_start_time.setTime(QTime(18, 0))
            self.evening_end_time.setTime(QTime(22, 0))

            # إعادة تعيين أيام العمل
            for day, checkbox in self.workday_checkboxes.items():
                if day in ["sunday", "monday", "tuesday", "wednesday", "thursday"]:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)

            # إعادة تعيين الإعدادات المتقدمة
            self.late_tolerance_spin.setValue(15)
            self.early_leave_tolerance_spin.setValue(10)
            self.min_work_hours_spin.setValue(8.0)
            self.enable_alerts_checkbox.setChecked(True)

    # تحميل قائمة الأقسام
    def load_sections(self):
        try:
            self.sections_list.clear()

            # إضافة الأقسام الرئيسية
            sections = ["المشاريع", "المقاولات", "الموظفين", "العملاء", "الحسابات", "التدريب", "الموردين"]

            for section in sections:
                item = QListWidgetItem(section)
                item.setIcon(qta.icon('fa5s.folder', color='#3498db'))
                self.sections_list.addItem(item)

        except Exception as e:
            print(f"خطأ في تحميل الأقسام: {e}")

    # تحميل شجرة الأقسام وأنواع المشاريع
    def load_sections_tree(self):
        try:
            self.sections_tree.clear()

            # إضافة قسم المشاريع
            projects_item = QTreeWidgetItem(["المشاريع"])
            projects_item.setIcon(0, qta.icon('fa5s.building', color='#3498db'))

            project_types = ["تصميم معماري", "تصميم إنشائي", "تصميم كهربائي", "تصميم ميكانيكي"]
            for project_type in project_types:
                type_item = QTreeWidgetItem([project_type])
                type_item.setIcon(0, qta.icon('fa5s.drafting-compass', color='#9b59b6'))
                projects_item.addChild(type_item)

            self.sections_tree.addTopLevelItem(projects_item)

            # إضافة قسم المقاولات
            contracts_item = QTreeWidgetItem(["المقاولات"])
            contracts_item.setIcon(0, qta.icon('fa5s.hard-hat', color='#e67e22'))

            contract_types = ["تأسيس وتشطيب", "بناء عظم", "تشطيب", "صيانة"]
            for contract_type in contract_types:
                type_item = QTreeWidgetItem([contract_type])
                type_item.setIcon(0, qta.icon('fa5s.tools', color='#f39c12'))
                contracts_item.addChild(type_item)

            self.sections_tree.addTopLevelItem(contracts_item)

            # توسيع العقد
            self.sections_tree.expandAll()

        except Exception as e:
            print(f"خطأ في تحميل شجرة الأقسام: {e}")

    # تحميل تصنيفات القسم المحدد
    def load_categories(self):
        if not self.current_section:
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_التصنيف, وصف_التصنيف, لون_التصنيف
                FROM التصنيفات
                WHERE اسم_القسم = %s
                ORDER BY اسم_التصنيف
            """, (self.current_section,))

            categories = cursor.fetchall()

            # تنظيف الجدول
            self.categories_table.setRowCount(0)

            # إضافة البيانات
            for row_num, (cat_id, name, description, color) in enumerate(categories):
                self.categories_table.insertRow(row_num)

                # المعرف (مخفي)
                self.categories_table.setItem(row_num, 0, QTableWidgetItem(str(cat_id)))

                # اسم التصنيف
                self.categories_table.setItem(row_num, 1, QTableWidgetItem(name))

                # الوصف
                self.categories_table.setItem(row_num, 2, QTableWidgetItem(description or ""))

                # اللون
                color_item = QTableWidgetItem(color)
                color_item.setBackground(QColor(color))
                self.categories_table.setItem(row_num, 3, color_item)

                # أزرار الإجراءات
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)

                edit_btn = QPushButton("تعديل")
                edit_btn.setObjectName("edit_category_btn")
                edit_btn.clicked.connect(lambda checked, cid=cat_id, cname=name: self.edit_category(cid, cname))

                delete_btn = QPushButton("حذف")
                delete_btn.setObjectName("delete_category_btn")
                delete_btn.clicked.connect(lambda checked, cid=cat_id, cname=name: self.delete_category(cid, cname))

                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)

                self.categories_table.setCellWidget(row_num, 4, actions_widget)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل التصنيفات: {e}")

    # تحميل أسعار المراحل
    def load_phases_pricing(self):
        if not self.current_section_phases:
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # بناء الاستعلام حسب التحديد
            if self.current_project_type:
                cursor.execute("""
                    SELECT id, اسم_المرحلة, الوصف, الوحدة, السعر, القسم, معرف_التصنيف
                    FROM اسعار_المراحل
                    WHERE القسم = %s AND معرف_التصنيف = %s
                    ORDER BY اسم_المرحلة
                """, (self.current_section_phases, self.current_project_type))
            else:
                cursor.execute("""
                    SELECT id, اسم_المرحلة, الوصف, الوحدة, السعر, القسم, معرف_التصنيف
                    FROM اسعار_المراحل
                    WHERE القسم = %s
                    ORDER BY معرف_التصنيف, اسم_المرحلة
                """, (self.current_section_phases,))

            phases = cursor.fetchall()

            # تنظيف الجدول
            self.phases_table.setRowCount(0)

            # إضافة البيانات
            for row_num, (phase_id, name, description, unit, price, section, project_type) in enumerate(phases):
                self.phases_table.insertRow(row_num)

                # المعرف (مخفي)
                self.phases_table.setItem(row_num, 0, QTableWidgetItem(str(phase_id)))

                # اسم المرحلة
                self.phases_table.setItem(row_num, 1, QTableWidgetItem(name))

                # الوصف
                self.phases_table.setItem(row_num, 2, QTableWidgetItem(description or ""))

                # الوحدة
                self.phases_table.setItem(row_num, 3, QTableWidgetItem(unit or ""))

                # السعر
                price_item = QTableWidgetItem(f"{price:,.2f}" if price else "0.00")
                price_item.setTextAlignment(Qt.AlignCenter)
                self.phases_table.setItem(row_num, 4, price_item)

                # القسم
                self.phases_table.setItem(row_num, 5, QTableWidgetItem(section))

                # نوع المشروع
                self.phases_table.setItem(row_num, 6, QTableWidgetItem(project_type or ""))

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل أسعار المراحل: {e}")

    # تحميل إعدادات مواعيد العمل الحالية
    def load_current_work_schedule(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM مواعيد_العمل WHERE نشط = TRUE ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()

            if result:
                # استخراج البيانات حسب هيكل الجدول الفعلي
                (schedule_id, system_type, morning_start, morning_end, evening_start, evening_end,
                 sunday, monday, tuesday, wednesday, thursday, friday, saturday,
                 late_tolerance, notes, active, created_at, updated_at) = result

                self.current_schedule_id = schedule_id

                # تطبيق نوع النظام
                if system_type == "فترتين":
                    self.double_shift_radio.setChecked(True)
                else:
                    self.single_shift_radio.setChecked(True)

                # تطبيق أوقات الدوام
                if morning_start:
                    self.morning_start_time.setTime(QTime.fromString(str(morning_start), "hh:mm:ss"))
                if morning_end:
                    self.morning_end_time.setTime(QTime.fromString(str(morning_end), "hh:mm:ss"))
                if evening_start:
                    self.evening_start_time.setTime(QTime.fromString(str(evening_start), "hh:mm:ss"))
                if evening_end:
                    self.evening_end_time.setTime(QTime.fromString(str(evening_end), "hh:mm:ss"))

                # تطبيق أيام العمل
                workdays_status = {
                    "sunday": sunday,
                    "monday": monday,
                    "tuesday": tuesday,
                    "wednesday": wednesday,
                    "thursday": thursday,
                    "friday": friday,
                    "saturday": saturday
                }

                for day, checkbox in self.workday_checkboxes.items():
                    checkbox.setChecked(workdays_status.get(day, False))

                # تطبيق الإعدادات المتقدمة
                if late_tolerance is not None:
                    self.late_tolerance_spin.setValue(late_tolerance)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل إعدادات مواعيد العمل: {e}")

    # تعديل تصنيف موجود
    def edit_category(self, category_id, category_name):
        QMessageBox.information(self, "قريباً", "نافذة تعديل التصنيف ستكون متاحة قريباً")

    # حذف تصنيف
    def delete_category(self, category_id, category_name):
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                   f"هل أنت متأكد من حذف التصنيف '{category_name}'؟")

        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("DELETE FROM التصنيفات WHERE id = %s", (category_id,))
                conn.commit()
                conn.close()

                self.load_categories()
                QMessageBox.information(self, "نجح", "تم حذف التصنيف بنجاح")

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف التصنيف: {e}")

    # تطبيق أنماط النافذة الموحدة
    def apply_unified_settings_styles(self):
        self.setStyleSheet("""
            /* النافذة الرئيسية */
            UnifiedSettingsWindow {
                background-color: #f8f9fa;
                font-family: 'Janna LT';
            }

            /* العنوان الرئيسي */
            QLabel[objectName="main_title"] {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
                margin-bottom: 10px;
            }

            /* التابات الرئيسية */
            QTabWidget[objectName="main_tab_widget"]::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 8px;
            }

           
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }

            QTabBar::tab:selected {
                background-color: white;
                color: #007bff;
                border-bottom: 3px solid #007bff;
            }

            QTabBar::tab:hover {
                background-color: #f8f9fa;
            }

            /* المجموعات */
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin: 10px 5px;
                padding-top: 15px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: white;
            }

            /* الأزرار */
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #0056b3;
            }

            QPushButton:pressed {
                background-color: #004085;
            }

            /* أزرار خاصة */
            QPushButton[objectName*="add"] {
                background-color: #28a745;
            }

            QPushButton[objectName*="add"]:hover {
                background-color: #218838;
            }

            QPushButton[objectName*="edit"] {
                background-color: #ffc107;
                color: #212529;
            }

            QPushButton[objectName*="edit"]:hover {
                background-color: #e0a800;
            }

            QPushButton[objectName*="delete"] {
                background-color: #dc3545;
            }

            QPushButton[objectName*="delete"]:hover {
                background-color: #c82333;
            }

            /* حقول الإدخال */
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 12px;
                background-color: white;
            }

            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }

            /* القوائم والجداول */
            QListWidget, QTreeWidget, QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                gridline-color: #e9ecef;
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
            }

            QHeaderView::section {
                background-color: #e9ecef;
                color: #495057;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }

            /* عناصر التحكم في الوقت */
            QTimeEdit, QSpinBox, QDoubleSpinBox {
                padding: 6px 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }

            QTimeEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #007bff;
            }

            /* أزرار الراديو والتحديد */
            QRadioButton, QCheckBox {
                font-size: 12px;
                color: #495057;
                spacing: 8px;
            }

            QRadioButton::indicator, QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }

            QRadioButton::indicator:checked {
                background-color: #007bff;
                border: 2px solid #007bff;
                border-radius: 8px;
            }

            QCheckBox::indicator:checked {
                background-color: #007bff;
                border: 2px solid #007bff;
                border-radius: 3px;
            }
        """)

# كلاس حوار إضافة/تعديل المراحل
# حوار إضافة أو تعديل مرحلة
class PhaseDialog(QDialog):

    # init
    def __init__(self, parent=None, mode="add", phase_id=None, section=None, project_type=None):
        super().__init__(parent)
        self.mode = mode
        self.phase_id = phase_id
        self.section = section
        self.project_type = project_type
        self.setup_ui()

        if mode == "edit" and phase_id:
            self.load_phase_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        title = "إضافة مرحلة جديدة" if self.mode == "add" else "تعديل المرحلة"
        self.setWindowTitle(title)
        self.setFixedSize(500, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # اسم المرحلة
        self.phase_name_edit = QLineEdit()
        self.phase_name_edit.setPlaceholderText("اسم المرحلة")
        form_layout.addRow("اسم المرحلة:", self.phase_name_edit)

        # الوصف
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("وصف المرحلة")
        form_layout.addRow("الوصف:", self.description_edit)

        # الوحدة
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("الوحدة")
        form_layout.addRow("الوحدة:", self.unit_edit)

        # السعر
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("0.00")
        form_layout.addRow("السعر:", self.price_edit)

        layout.addLayout(form_layout)

        # أزرار الإجراءات
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_phase)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    # تحميل بيانات المرحلة للتعديل
    def load_phase_data(self):
        # سيتم تنفيذ هذه الدالة لاحقاً
        pass

    # حفظ بيانات المرحلة
    def save_phase(self):
        # سيتم تنفيذ هذه الدالة لاحقاً
        self.accept()

# دالة فتح النافذة الموحدة
# فتح نافذة الإعدادات الموحدة
def open_unified_settings_window(parent):
    window = UnifiedSettingsWindow(parent)
    window.show()
    return window
