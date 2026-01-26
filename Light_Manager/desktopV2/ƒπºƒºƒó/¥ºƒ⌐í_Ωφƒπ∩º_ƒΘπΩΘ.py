from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector
from الإعدادات_العامة import *
from ستايل import *
import qtawesome as qta
from datetime import datetime, time

# نافذة إدارة مواعيد العمل للشركة
class WorkScheduleManagementWindow(QDialog):
    
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_schedule_id = None
        self.is_dark_mode = False  # إضافة خاصية الوضع المظلم
        self.init_ui()
        self.load_current_schedule()
        
    # إنشاء واجهة المستخدم
    def init_ui(self):
        self.setWindowTitle("إدارة مواعيد العمل")
        self.setWindowIcon(QIcon(os.path.join(icons_dir, 'حضور_انصراف.svg')))
        self.setModal(True)
        self.resize(800, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تطبيق الستايل
        try:
            Basic_Styles(self)
        except Exception as e:
            print(f"تحذير: لم يتم تطبيق الستايل: {e}")
            # تطبيق ستايل بسيط كبديل
            self.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                    font-family: 'Janna LT';
                    font-size: 12px;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QPushButton {
                    background-color: #e1e1e1;
                    border: 2px solid #999999;
                    border-radius: 5px;
                    padding: 5px;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #d1d1d1;
                }
                QPushButton:pressed {
                    background-color: #b1b1b1;
                }
            """)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # العنوان الرئيسي
        title_label = QLabel("إدارة مواعيد العمل للشركة")
        title_label.setFont(QFont("Janna LT", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
            }
        """)
        main_layout.addWidget(title_label)
        
        # إنشاء التبويبات
        self.create_tabs(main_layout)
        
        # أزرار التحكم
        self.create_control_buttons(main_layout)
        
    # إنشاء التبويبات
    def create_tabs(self, parent_layout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setLayoutDirection(Qt.RightToLeft)
        
        # تاب إعدادات الدوام
        self.create_schedule_tab()
        
        # تاب أيام العمل
        self.create_workdays_tab()
        
        # تاب الإعدادات المتقدمة
        self.create_advanced_tab()
        
        parent_layout.addWidget(self.tab_widget)
        
    # إنشاء تاب إعدادات الدوام
    def create_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # نوع نظام العمل
        system_group = QGroupBox("نوع نظام العمل")
        system_layout = QVBoxLayout(system_group)
        
        self.single_shift_radio = QRadioButton("فترة واحدة")
        self.double_shift_radio = QRadioButton("فترتين (صباحية ومسائية)")
        self.single_shift_radio.setChecked(True)
        
        system_layout.addWidget(self.single_shift_radio)
        system_layout.addWidget(self.double_shift_radio)
        
        # ربط الإشارات
        self.single_shift_radio.toggled.connect(self.on_system_type_changed)
        self.double_shift_radio.toggled.connect(self.on_system_type_changed)
        
        layout.addWidget(system_group)
        
        # الفترة الصباحية
        morning_group = QGroupBox("الفترة الصباحية")
        morning_layout = QFormLayout(morning_group)
        
        self.morning_start_time = QTimeEdit()
        self.morning_start_time.setDisplayFormat("hh:mm AP")
        self.morning_start_time.setTime(QTime(8, 0))
        
        self.morning_end_time = QTimeEdit()
        self.morning_end_time.setDisplayFormat("hh:mm AP")
        self.morning_end_time.setTime(QTime(17, 0))
        
        morning_layout.addRow("وقت بداية الدوام:", self.morning_start_time)
        morning_layout.addRow("وقت نهاية الدوام:", self.morning_end_time)
        
        layout.addWidget(morning_group)
        
        # الفترة المسائية
        self.evening_group = QGroupBox("الفترة المسائية")
        evening_layout = QFormLayout(self.evening_group)
        
        self.evening_start_time = QTimeEdit()
        self.evening_start_time.setDisplayFormat("hh:mm AP")
        self.evening_start_time.setTime(QTime(18, 0))
        
        self.evening_end_time = QTimeEdit()
        self.evening_end_time.setDisplayFormat("hh:mm AP")
        self.evening_end_time.setTime(QTime(22, 0))
        
        evening_layout.addRow("وقت بداية الدوام:", self.evening_start_time)
        evening_layout.addRow("وقت نهاية الدوام:", self.evening_end_time)
        
        self.evening_group.setEnabled(False)  # معطل افتراضياً
        layout.addWidget(self.evening_group)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.clock', color='#3498db'), "إعدادات الدوام")
        
    # إنشاء تاب أيام العمل
    def create_workdays_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # أيام الدوام
        workdays_group = QGroupBox("أيام الدوام الأسبوعية")
        workdays_layout = QVBoxLayout(workdays_group)
        
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
            if english_day in ["sunday", "monday", "tuesday", "wednesday", "thursday"]:
                checkbox.setChecked(True)  # أيام العمل الافتراضية
            self.workday_checkboxes[english_day] = checkbox
            workdays_layout.addWidget(checkbox)
        
        layout.addWidget(workdays_group)
        
        # أزرار سريعة لتحديد أيام العمل
        quick_buttons_group = QGroupBox("تحديد سريع")
        quick_layout = QHBoxLayout(quick_buttons_group)
        
        all_days_btn = QPushButton("تحديد جميع الأيام")
        weekdays_btn = QPushButton("أيام العمل فقط")
        clear_all_btn = QPushButton("إلغاء التحديد")
        
        all_days_btn.clicked.connect(self.select_all_days)
        weekdays_btn.clicked.connect(self.select_weekdays_only)
        clear_all_btn.clicked.connect(self.clear_all_days)
        
        quick_layout.addWidget(all_days_btn)
        quick_layout.addWidget(weekdays_btn)
        quick_layout.addWidget(clear_all_btn)
        
        layout.addWidget(quick_buttons_group)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.calendar-week', color='#27ae60'), "أيام العمل")
        
    # إنشاء تاب الإعدادات المتقدمة
    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # فترة التأخير المسموحة
        tolerance_group = QGroupBox("فترة التأخير المسموحة")
        tolerance_layout = QFormLayout(tolerance_group)
        
        self.tolerance_spinbox = QSpinBox()
        self.tolerance_spinbox.setRange(0, 120)  # من 0 إلى 120 دقيقة
        self.tolerance_spinbox.setValue(15)  # 15 دقيقة افتراضي
        self.tolerance_spinbox.setSuffix(" دقيقة")
        
        tolerance_layout.addRow("فترة التأخير المسموحة:", self.tolerance_spinbox)
        
        layout.addWidget(tolerance_group)
        
        # ملاحظات
        notes_group = QGroupBox("ملاحظات")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        self.notes_text.setPlaceholderText("أدخل أي ملاحظات إضافية حول مواعيد العمل...")
        
        notes_layout.addWidget(self.notes_text)
        
        layout.addWidget(notes_group)
        
        # معلومات النظام الحالي
        info_group = QGroupBox("معلومات النظام الحالي")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("لم يتم تحميل البيانات بعد...")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
        """)
        
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_group)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.cogs', color='#f39c12'), "إعدادات متقدمة")
        
    # إنشاء أزرار التحكم
    def create_control_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()
        
        # زر الحفظ
        save_btn = QPushButton("حفظ الإعدادات")
        save_btn.setIcon(qta.icon('fa5s.save', color='white'))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_schedule)
        
        # زر الإلغاء
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setIcon(qta.icon('fa5s.times', color='white'))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # زر استعادة الافتراضي
        reset_btn = QPushButton("استعادة الافتراضي")
        reset_btn.setIcon(qta.icon('fa5s.undo', color='white'))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_default)
        
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        parent_layout.addLayout(buttons_layout)

    # تغيير نوع نظام العمل
    def on_system_type_changed(self):
        if self.double_shift_radio.isChecked():
            self.evening_group.setEnabled(True)
        else:
            self.evening_group.setEnabled(False)

    # تحديد جميع أيام الأسبوع
    def select_all_days(self):
        for checkbox in self.workday_checkboxes.values():
            checkbox.setChecked(True)

    # تحديد أيام العمل فقط (الأحد إلى الخميس)
    def select_weekdays_only(self):
        weekdays = ["sunday", "monday", "tuesday", "wednesday", "thursday"]
        for day, checkbox in self.workday_checkboxes.items():
            checkbox.setChecked(day in weekdays)

    # إلغاء تحديد جميع الأيام
    def clear_all_days(self):
        for checkbox in self.workday_checkboxes.values():
            checkbox.setChecked(False)

    # تحميل الجدول الزمني الحالي
    def load_current_schedule(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor(dictionary=True)

            # البحث عن الجدول النشط
            cursor.execute("""
                SELECT * FROM مواعيد_العمل
                WHERE نشط = TRUE
                ORDER BY تاريخ_الإضافة DESC
                LIMIT 1
            """)

            schedule = cursor.fetchone()

            if schedule:
                self.current_schedule_id = schedule['id']
                self.populate_form_with_data(schedule)
            else:
                # إنشاء جدول افتراضي إذا لم يوجد
                self.create_default_schedule()

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل مواعيد العمل: {str(e)}")

    # ملء النموذج بالبيانات المحملة
    def populate_form_with_data(self, schedule):
        try:
            # نوع النظام
            if schedule['نوع_النظام'] == 'فترتين':
                self.double_shift_radio.setChecked(True)
            else:
                self.single_shift_radio.setChecked(True)

            # الأوقات الصباحية
            if schedule['وقت_حضور_صباحي']:
                morning_start = QTime.fromString(str(schedule['وقت_حضور_صباحي']), "hh:mm:ss")
                self.morning_start_time.setTime(morning_start)

            if schedule['وقت_انصراف_صباحي']:
                morning_end = QTime.fromString(str(schedule['وقت_انصراف_صباحي']), "hh:mm:ss")
                self.morning_end_time.setTime(morning_end)

            # الأوقات المسائية
            if schedule['وقت_حضور_مسائي']:
                evening_start = QTime.fromString(str(schedule['وقت_حضور_مسائي']), "hh:mm:ss")
                self.evening_start_time.setTime(evening_start)

            if schedule['وقت_انصراف_مسائي']:
                evening_end = QTime.fromString(str(schedule['وقت_انصراف_مسائي']), "hh:mm:ss")
                self.evening_end_time.setTime(evening_end)

            # أيام العمل
            day_mapping = {
                'sunday': 'الأحد',
                'monday': 'الاثنين',
                'tuesday': 'الثلاثاء',
                'wednesday': 'الأربعاء',
                'thursday': 'الخميس',
                'friday': 'الجمعة',
                'saturday': 'السبت'
            }

            for english_day, arabic_day in day_mapping.items():
                if arabic_day in schedule and schedule[arabic_day]:
                    self.workday_checkboxes[english_day].setChecked(True)
                else:
                    self.workday_checkboxes[english_day].setChecked(False)

            # فترة التأخير
            if schedule['فترة_التأخير_المسموحة']:
                self.tolerance_spinbox.setValue(schedule['فترة_التأخير_المسموحة'])

            # الملاحظات
            if schedule['ملاحظات']:
                self.notes_text.setPlainText(schedule['ملاحظات'])

            # تحديث معلومات النظام
            self.update_system_info(schedule)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل البيانات: {str(e)}")

    # تحديث معلومات النظام الحالي
    def update_system_info(self, schedule):
        try:
            info_text = f"""
            <b>معلومات النظام الحالي:</b><br>
            • نوع النظام: {schedule['نوع_النظام']}<br>
            • الفترة الصباحية: {schedule['وقت_حضور_صباحي']} - {schedule['وقت_انصراف_صباحي']}<br>
            """

            if schedule['نوع_النظام'] == 'فترتين' and schedule['وقت_حضور_مسائي']:
                info_text += f"• الفترة المسائية: {schedule['وقت_حضور_مسائي']} - {schedule['وقت_انصراف_مسائي']}<br>"

            info_text += f"• فترة التأخير المسموحة: {schedule['فترة_التأخير_المسموحة']} دقيقة<br>"
            info_text += f"• تاريخ آخر تحديث: {schedule['تاريخ_التحديث']}<br>"

            # عرض أيام العمل
            work_days = []
            day_mapping = {
                'الأحد': schedule.get('الأحد', False),
                'الاثنين': schedule.get('الاثنين', False),
                'الثلاثاء': schedule.get('الثلاثاء', False),
                'الأربعاء': schedule.get('الأربعاء', False),
                'الخميس': schedule.get('الخميس', False),
                'الجمعة': schedule.get('الجمعة', False),
                'السبت': schedule.get('السبت', False)
            }

            for day, is_work_day in day_mapping.items():
                if is_work_day:
                    work_days.append(day)

            info_text += f"• أيام العمل: {', '.join(work_days)}"

            self.info_label.setText(info_text)

        except Exception as e:
            self.info_label.setText(f"خطأ في عرض المعلومات: {str(e)}")

    # إنشاء جدول زمني افتراضي
    def create_default_schedule(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO مواعيد_العمل
                (نوع_النظام, وقت_حضور_صباحي, وقت_انصراف_صباحي,
                 الأحد, الاثنين, الثلاثاء, الأربعاء, الخميس, الجمعة, السبت,
                 فترة_التأخير_المسموحة, نشط)
                VALUES
                ('فترة_واحدة', '08:00:00', '17:00:00',
                 TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE,
                 15, TRUE)
            """)

            self.current_schedule_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()

            # إعادة تحميل البيانات
            self.load_current_schedule()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء الجدول الافتراضي: {str(e)}")

    # استعادة الإعدادات الافتراضية
    def reset_to_default(self):
        reply = QMessageBox.question(
            self, "استعادة الافتراضي",
            "هل تريد استعادة الإعدادات الافتراضية؟\nسيتم فقدان جميع التغييرات غير المحفوظة.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # إعادة تعيين النموذج للقيم الافتراضية
            self.single_shift_radio.setChecked(True)
            self.morning_start_time.setTime(QTime(8, 0))
            self.morning_end_time.setTime(QTime(17, 0))
            self.evening_start_time.setTime(QTime(18, 0))
            self.evening_end_time.setTime(QTime(22, 0))

            # تحديد أيام العمل الافتراضية
            self.select_weekdays_only()

            # إعادة تعيين فترة التأخير
            self.tolerance_spinbox.setValue(15)

            # مسح الملاحظات
            self.notes_text.clear()

    # التحقق من صحة البيانات المدخلة
    def validate_form(self):
        # التحقق من وجود يوم عمل واحد على الأقل
        has_work_day = any(checkbox.isChecked() for checkbox in self.workday_checkboxes.values())
        if not has_work_day:
            QMessageBox.warning(self, "خطأ في البيانات", "يجب تحديد يوم عمل واحد على الأقل!")
            return False

        # التحقق من صحة أوقات الفترة الصباحية
        morning_start = self.morning_start_time.time()
        morning_end = self.morning_end_time.time()

        if morning_start >= morning_end:
            QMessageBox.warning(self, "خطأ في البيانات", "وقت بداية الدوام الصباحي يجب أن يكون قبل وقت النهاية!")
            return False

        # التحقق من أوقات الفترة المسائية إذا كانت مفعلة
        if self.double_shift_radio.isChecked():
            evening_start = self.evening_start_time.time()
            evening_end = self.evening_end_time.time()

            if evening_start >= evening_end:
                QMessageBox.warning(self, "خطأ في البيانات", "وقت بداية الدوام المسائي يجب أن يكون قبل وقت النهاية!")
                return False

            # التحقق من عدم تداخل الفترات
            if morning_end > evening_start:
                QMessageBox.warning(self, "خطأ في البيانات", "لا يمكن أن تتداخل الفترة الصباحية مع المسائية!")
                return False

        return True

    # حفظ مواعيد العمل
    def save_schedule(self):
        if not self.validate_form():
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إعداد البيانات للحفظ
            system_type = 'فترتين' if self.double_shift_radio.isChecked() else 'فترة_واحدة'

            morning_start = self.morning_start_time.time().toString("hh:mm:ss")
            morning_end = self.morning_end_time.time().toString("hh:mm:ss")

            evening_start = None
            evening_end = None
            if self.double_shift_radio.isChecked():
                evening_start = self.evening_start_time.time().toString("hh:mm:ss")
                evening_end = self.evening_end_time.time().toString("hh:mm:ss")

            # أيام العمل
            workdays = {
                'الأحد': self.workday_checkboxes['sunday'].isChecked(),
                'الاثنين': self.workday_checkboxes['monday'].isChecked(),
                'الثلاثاء': self.workday_checkboxes['tuesday'].isChecked(),
                'الأربعاء': self.workday_checkboxes['wednesday'].isChecked(),
                'الخميس': self.workday_checkboxes['thursday'].isChecked(),
                'الجمعة': self.workday_checkboxes['friday'].isChecked(),
                'السبت': self.workday_checkboxes['saturday'].isChecked()
            }

            tolerance = self.tolerance_spinbox.value()
            notes = self.notes_text.toPlainText()

            if self.current_schedule_id:
                # تحديث الجدول الموجود
                cursor.execute("""
                    UPDATE مواعيد_العمل SET
                    نوع_النظام = %s,
                    وقت_حضور_صباحي = %s,
                    وقت_انصراف_صباحي = %s,
                    وقت_حضور_مسائي = %s,
                    وقت_انصراف_مسائي = %s,
                    الأحد = %s, الاثنين = %s, الثلاثاء = %s, الأربعاء = %s,
                    الخميس = %s, الجمعة = %s, السبت = %s,
                    فترة_التأخير_المسموحة = %s,
                    ملاحظات = %s,
                    تاريخ_التحديث = NOW()
                    WHERE id = %s
                """, (
                    system_type, morning_start, morning_end, evening_start, evening_end,
                    workdays['الأحد'], workdays['الاثنين'], workdays['الثلاثاء'], workdays['الأربعاء'],
                    workdays['الخميس'], workdays['الجمعة'], workdays['السبت'],
                    tolerance, notes, self.current_schedule_id
                ))
            else:
                # إنشاء جدول جديد
                # أولاً، إلغاء تفعيل جميع الجداول الأخرى
                cursor.execute("UPDATE مواعيد_العمل SET نشط = FALSE")

                # إدراج الجدول الجديد
                cursor.execute("""
                    INSERT INTO مواعيد_العمل
                    (نوع_النظام, وقت_حضور_صباحي, وقت_انصراف_صباحي,
                     وقت_حضور_مسائي, وقت_انصراف_مسائي,
                     الأحد, الاثنين, الثلاثاء, الأربعاء, الخميس, الجمعة, السبت,
                     فترة_التأخير_المسموحة, ملاحظات, نشط)
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """, (
                    system_type, morning_start, morning_end, evening_start, evening_end,
                    workdays['الأحد'], workdays['الاثنين'], workdays['الثلاثاء'], workdays['الأربعاء'],
                    workdays['الخميس'], workdays['الجمعة'], workdays['السبت'],
                    tolerance, notes
                ))

                self.current_schedule_id = cursor.lastrowid

            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "نجح الحفظ", "تم حفظ مواعيد العمل بنجاح!")

            # إعادة تحميل البيانات لتحديث المعلومات
            self.load_current_schedule()

        except Exception as e:
            QMessageBox.critical(self, "خطأ في الحفظ", f"فشل في حفظ مواعيد العمل:\n{str(e)}")


# فتح نافذة إدارة مواعيد العمل
def open_work_schedule_management(parent=None):
    dialog = WorkScheduleManagementWindow(parent)
    return dialog.exec()


# الحصول على مواعيد العمل الحالية
def get_current_work_schedule():
    try:
        conn = mysql.connector.connect(
            host=host, user=user_r, password=password_r,
            database="project_manager_V2"
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM مواعيد_العمل
            WHERE نشط = TRUE
            ORDER BY تاريخ_الإضافة DESC
            LIMIT 1
        """)

        schedule = cursor.fetchone()
        cursor.close()
        conn.close()

        return schedule

    except Exception as e:
        print(f"خطأ في الحصول على مواعيد العمل: {e}")
        return None


# التحقق من كون التاريخ المحدد يوم عمل
def is_work_day(date_obj):
    try:
        schedule = get_current_work_schedule()
        if not schedule:
            return True  # افتراضي: جميع الأيام أيام عمل

        # تحويل رقم اليوم إلى اسم اليوم
        day_names = {
            6: 'الأحد',    # Sunday
            0: 'الاثنين',   # Monday
            1: 'الثلاثاء',   # Tuesday
            2: 'الأربعاء',   # Wednesday
            3: 'الخميس',    # Thursday
            4: 'الجمعة',    # Friday
            5: 'السبت'     # Saturday
        }

        weekday = date_obj.weekday()
        day_name = day_names.get(weekday, 'الأحد')

        return schedule.get(day_name, False)

    except Exception as e:
        print(f"خطأ في التحقق من يوم العمل: {e}")
        return True


# حساب حالة الحضور والانصراف بناءً على مواعيد العمل
def calculate_attendance_status(check_in_time, check_out_time, date_obj):
    try:
        schedule = get_current_work_schedule()
        if not schedule:
            return {
                'early_checkin': False,
                'late_checkin': False,
                'early_checkout': False,
                'late_checkout': False
            }

        # تحويل الأوقات
        morning_start = schedule['وقت_حضور_صباحي']
        morning_end = schedule['وقت_انصراف_صباحي']
        tolerance = schedule['فترة_التأخير_المسموحة'] or 15

        # تحويل إلى datetime objects للمقارنة
        from datetime import datetime, timedelta

        if isinstance(morning_start, str):
            morning_start = datetime.strptime(morning_start, '%H:%M:%S').time()
        if isinstance(morning_end, str):
            morning_end = datetime.strptime(morning_end, '%H:%M:%S').time()

        # حساب الحالات
        result = {
            'early_checkin': False,
            'late_checkin': False,
            'early_checkout': False,
            'late_checkout': False
        }

        if check_in_time:
            # حساب الحضور المبكر/المتأخر
            tolerance_time = (datetime.combine(date_obj, morning_start) +
                            timedelta(minutes=tolerance)).time()

            if check_in_time < morning_start:
                result['early_checkin'] = True
            elif check_in_time > tolerance_time:
                result['late_checkin'] = True

        if check_out_time:
            # حساب الانصراف المبكر/المتأخر
            if check_out_time < morning_end:
                result['early_checkout'] = True
            elif check_out_time > morning_end:
                result['late_checkout'] = True

        return result

    except Exception as e:
        print(f"خطأ في حساب حالة الحضور: {e}")
        return {
            'early_checkin': False,
            'late_checkin': False,
            'early_checkout': False,
            'late_checkout': False
        }
