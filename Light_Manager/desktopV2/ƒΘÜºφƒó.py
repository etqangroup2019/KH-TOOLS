from النسخة_التجريبية import*
from متغيرات import*

# إعداد تنسيق QDateEdit لعرض التاريخ بصيغة dd/MM/yyyy
def setup_date_edit_format(date_edit):
    if isinstance(date_edit, QDateEdit):
        date_edit.setDisplayFormat("dd/MM/yyyy")
        if not date_edit.calendarPopup():
            date_edit.setCalendarPopup(True)

# addentrydialog
class AddEntryDialog(QDialog):
    # init
    def __init__(self, main_window, section_name, parent=None, entry_data=None, row_id=None):
        super().__init__(parent)
        self.is_dark_mode = settings.value("dark_mode", False, type=bool)
        self.main_window = main_window
        self.section_name = section_name
        self.entry_data = entry_data
        self.row_id = row_id
        self.setWindowTitle(f"تعديل {section_name}" if entry_data else f"إضافة {section_name} جديد")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(500, 400)  # يسمح بتغيير الحجم

        layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(20, 20, 20, 20)
        self.form_layout.setVerticalSpacing(10)
        self.form_layout.setHorizontalSpacing(10)

        self.inputs = {}
        self.setup_fields()

        layout.addLayout(self.form_layout)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 10)
        save_button = QPushButton("حفظ")
        save_button.clicked.connect(self.save_data)
        cancel_button = QPushButton("إلغاء")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        center_all_widgets(self)
        center_all_widgets(layout)
        center_all_widgets(self.form_layout)

        # Apply initial styling
        self.apply_dialog_style()

        # تحميل بيانات العملاء إذا كان القسم هو المشاريع أو المقاولات
        if self.section_name == "المشاريع" or self.section_name == "المقاولات":
            self.load_clients_to_combo()

        
        # If in edit mode, populate fields
        if self.entry_data:
            self.populate_fields()

    # تحميل التصنيفات الموجودة من قاعدة البيانات مع الألوان
    def load_existing_classifications(self, section_name):
        try:
            from الإعدادات_العامة import get_categories_with_colors
            categories_with_colors = get_categories_with_colors(section_name)
            return [name for name, color in categories_with_colors]

        except Exception as e:
            print(f"خطأ في تحميل التصنيفات: {e}")
            # الطريقة القديمة كبديل
            try:
                conn = self.main_window.get_db_connection()
                if conn is None:
                    return []

                cursor = conn.cursor()

                # تحديد اسم الجدول في قاعدة البيانات
                db_table_name = self.main_window.get_db_table_name(section_name)

                # جلب التصنيفات الفريدة من عمود التصنيف
                cursor.execute(f"SELECT DISTINCT `التصنيف` FROM `{db_table_name}` WHERE `التصنيف` IS NOT NULL AND `التصنيف` != '' ORDER BY `التصنيف`")
                classifications = cursor.fetchall()

                cursor.close()
                conn.close()

                # تحويل النتائج إلى قائمة
                return [classification[0] for classification in classifications]

            except Exception as e2:
                print(f"خطأ في الطريقة البديلة لتحميل التصنيفات: {e2}")
                return []

    # إضافة حقل التصنيف/النوع لجميع الأقسام
    def add_classification_field(self):
        
        if self.section_name == "المشاريع":
            # نوع المشروع
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)
            
            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name)
            
            # إضافة التصنيفات الافتراضية
            default_items = [
                "تصميم معماري",
                "تصميم داخلي",
            ]
            
            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)
            
            self.form_layout.addRow("نوع المشروع:", self.inputs["classification"])

        elif self.section_name == "العملاء":
            # نوع العميل
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)
            
            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name)
            
            # إضافة التصنيفات الافتراضية
            default_items = [
                "مواطن",
                "مهندس",
                "شركة",
                "شركة هندسية",
                "مكتب هندسي",
                "مؤسسة حكومية",
                "مؤسسة خاصة"
            ]
            
            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)
            
            self.form_layout.addRow("نوع العميل:", self.inputs["classification"])

        elif self.section_name == "الحسابات":
            # نوع المصروف
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)
            
            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name)
            
            # إضافة التصنيفات الافتراضية
            default_items = [
                "مصاريف إدارية",
                "مصاريف تشغيلية",
                "مصاريف مكتبية",
                "مصاريف مشاريع",
                "مصاريف تسويق",
                "مصاريف سفر وتنقل",
            ]
            
            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)
            
            self.form_layout.addRow("نوع المصروف:", self.inputs["classification"])

        elif self.section_name == "الموظفين":
            # نوع الحساب
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)
            
            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name)
            
            # إضافة التصنيفات الافتراضية
            default_items = [
                "موظف",
                "مهندس",
                "مقاول",
                "عامل",
                "متعاون"
            ]
            
            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)
            
            self.form_layout.addRow("نوع الحساب:", self.inputs["classification"])


        elif self.section_name == "التدريب":
            # نوع الدورة
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)
            
            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name)
            
            # إضافة التصنيفات الافتراضية
            default_items = [
                "دورة هندسية",
                "دورة تقنية",
                "دورة إدارية",
                "ورشة عمل",
                "مؤتمر"
            ]
            
            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)
            
            self.form_layout.addRow("نوع الدورة:", self.inputs["classification"])
        
        elif self.section_name == "الموردين":
            # نوع المورد
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)
            
            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name) 

            # إضافة التصنيفات الافتراضية
            default_items = [
                "مورد",
                "مورد موحد",
                "مورد موحد مع موردين"
            ]
            
            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)
            
            self.form_layout.addRow("نوع المورد:", self.inputs["classification"])

        elif self.section_name == "المقاولات":
            # نوع المقاولات
            self.inputs["classification"] = QComboBox()
            self.inputs["classification"].setEditable(True)

            # تحميل التصنيفات الموجودة من قاعدة البيانات
            existing_classifications = self.load_existing_classifications(self.section_name)

            # إضافة التصنيفات الافتراضية للمقاولات
            default_items = [
                "تأسيس وتشطيب",
                "بناء عظم",
                "تشطيب",
                "إشراف هندسي",
                "مقاولات عامة",
                "صيانة وترميم"
            ]

            # دمج التصنيفات الموجودة مع الافتراضية (بدون تكرار)
            all_items = list(dict.fromkeys(default_items + existing_classifications))
            self.inputs["classification"].addItems(all_items)

            self.form_layout.addRow("نوع المقاولات:", self.inputs["classification"])

    # حقول الإعداد بناءً على القسم
    def setup_fields(self):
        # إضافة حقل التصنيف/النوع لجميع الأقسام
        self.add_classification_field()

        if self.section_name == "المشاريع":

            self.inputs["client_name"] = QComboBox()
            self.inputs["client_name"].setPlaceholderText("أدخل اسم العميل")
            self.inputs["client_name"].addItem("")

            # إضافة اختيار المهندس المسؤول
            self.inputs["responsible_engineer"] = QComboBox()
            self.inputs["responsible_engineer"].setEditable(True)
            self.inputs["responsible_engineer"].setPlaceholderText("اختر المهندس المسؤول")
            # تحميل المهندسين من جدول الموظفين
            self.load_engineers_to_combo()

            self.inputs["phone"] = QLineEdit()
            self.inputs["phone"].setPlaceholderText("أدخل رقم الهاتف")

            self.inputs["project_name"] = QLineEdit()
            self.inputs["project_name"].setPlaceholderText("أدخل اسم المشروع")

            self.inputs["description"] = QLineEdit()
            self.inputs["description"].setPlaceholderText("أدخل وصف المشروع")

            self.inputs["amount"] = QLineEdit()
            self.inputs["amount"].setPlaceholderText("أدخل قيمة المبلغ")
            self.inputs["amount"].setText("0")

            self.inputs["receive_date"] = QDateEdit()
            self.inputs["receive_date"].setCalendarPopup(True)
            self.inputs["receive_date"].setDate(QDate.currentDate())
            self.inputs["receive_date"].setDisplayFormat("dd/MM/yyyy")

            self.inputs["delivery_date"] = QDateEdit()
            self.inputs["delivery_date"].setCalendarPopup(True)
            self.inputs["delivery_date"].setDate(QDate.currentDate())
            self.inputs["delivery_date"].setDisplayFormat("dd/MM/yyyy")

            self.inputs["duration"] = QLineEdit()
            self.inputs["duration"].setPlaceholderText("مدة الإنجاز بالأيام")

            self.inputs["notes"] = QLineEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات إضافية")

            self.form_layout.addRow("اسم المشروع:", self.inputs["project_name"])
            self.form_layout.addRow("اسم العميل:", self.inputs["client_name"])
            self.form_layout.addRow("المهندس المسؤول:", self.inputs["responsible_engineer"])
            self.form_layout.addRow("رقم الهاتف:", self.inputs["phone"])
            self.form_layout.addRow("المبلغ:", self.inputs["amount"])
            self.form_layout.addRow("تاريخ الاستلام:", self.inputs["receive_date"])
            self.form_layout.addRow("تاريخ التسليم:", self.inputs["delivery_date"])
            self.form_layout.addRow("مدة الإنجاز (يوم):", self.inputs["duration"])
            self.form_layout.addRow("وصف تفصيلي:", self.inputs["description"])
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])

            # مدة التحديث
            def update_duration():
                start = self.inputs["receive_date"].date()
                end = self.inputs["delivery_date"].date()
                days = start.daysTo(end)
                self.inputs["duration"].setText(str(days if days >= 0 else 0))

            # تحديث تاريخ التسليم
            def update_delivery_date():
                start = self.inputs["receive_date"].date()
                try:
                    days = int(self.inputs["duration"].text())
                    new_delivery = start.addDays(days)
                    self.inputs["delivery_date"].setDate(new_delivery)
                except ValueError:
                    pass

            self.inputs["receive_date"].dateChanged.connect(update_duration)
            self.inputs["delivery_date"].dateChanged.connect(update_duration)
            self.inputs["duration"].textChanged.connect(update_delivery_date)

        elif self.section_name == "المقاولات":
            # نفس حقول المشاريع مع إضافة المهندس المسؤول
            self.inputs["client_name"] = QComboBox()
            self.inputs["client_name"].setPlaceholderText("أدخل اسم العميل")
            self.inputs["client_name"].addItem("")

            # إضافة اختيار المهندس المسؤول
            self.inputs["responsible_engineer"] = QComboBox()
            self.inputs["responsible_engineer"].setEditable(True)
            self.inputs["responsible_engineer"].setPlaceholderText("اختر المهندس المسؤول")
            # تحميل المهندسين من جدول الموظفين
            self.load_engineers_to_combo()

            self.inputs["phone"] = QLineEdit()
            self.inputs["phone"].setPlaceholderText("أدخل رقم الهاتف")

            self.inputs["project_name"] = QLineEdit()
            self.inputs["project_name"].setPlaceholderText("أدخل اسم المشروع")

            self.inputs["description"] = QLineEdit()
            self.inputs["description"].setPlaceholderText("أدخل وصف المشروع")

            self.inputs["amount"] = QLineEdit()
            self.inputs["amount"].setPlaceholderText("أدخل قيمة المبلغ")
            self.inputs["amount"].setText("0")

            self.inputs["receive_date"] = QDateEdit()
            self.inputs["receive_date"].setCalendarPopup(True)
            self.inputs["receive_date"].setDate(QDate.currentDate())
            self.inputs["receive_date"].setDisplayFormat("dd/MM/yyyy")

            self.inputs["delivery_date"] = QDateEdit()
            self.inputs["delivery_date"].setCalendarPopup(True)
            self.inputs["delivery_date"].setDate(QDate.currentDate())
            self.inputs["delivery_date"].setDisplayFormat("dd/MM/yyyy")

            self.inputs["duration"] = QLineEdit()
            self.inputs["duration"].setPlaceholderText("مدة الإنجاز بالأيام")

            self.inputs["notes"] = QLineEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات إضافية")

            self.form_layout.addRow("اسم المشروع:", self.inputs["project_name"])
            self.form_layout.addRow("اسم العميل:", self.inputs["client_name"])
            self.form_layout.addRow("المهندس المسؤول:", self.inputs["responsible_engineer"])
            self.form_layout.addRow("رقم الهاتف:", self.inputs["phone"])
            self.form_layout.addRow("المبلغ:", self.inputs["amount"])
            self.form_layout.addRow("تاريخ الاستلام:", self.inputs["receive_date"])
            self.form_layout.addRow("تاريخ التسليم:", self.inputs["delivery_date"])
            self.form_layout.addRow("مدة الإنجاز (يوم):", self.inputs["duration"])
            self.form_layout.addRow("وصف تفصيلي:", self.inputs["description"])
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])

            # نفس دوال حساب المدة كما في المشاريع
            # تحديث مدة التعاقد
            def update_duration_contracting():
                start = self.inputs["receive_date"].date()
                end = self.inputs["delivery_date"].date()
                days = start.daysTo(end)
                self.inputs["duration"].setText(str(days if days >= 0 else 0))

            # تحديث تاريخ التسليم
            def update_delivery_date_contracting():
                start = self.inputs["receive_date"].date()
                try:
                    days = int(self.inputs["duration"].text())
                    new_delivery = start.addDays(days)
                    self.inputs["delivery_date"].setDate(new_delivery)
                except ValueError:
                    pass

            self.inputs["receive_date"].dateChanged.connect(update_duration_contracting)
            self.inputs["delivery_date"].dateChanged.connect(update_duration_contracting)
            self.inputs["duration"].textChanged.connect(update_delivery_date_contracting)

        elif self.section_name == "العملاء":
            self.inputs["client_name"] = QLineEdit()
            self.inputs["client_name"].setPlaceholderText("أدخل اسم العميل الكامل")

            self.inputs["phone"] = QLineEdit()
            self.inputs["phone"].setPlaceholderText("مثال: 0912345678 (اختياري)")

            self.inputs["address"] = QLineEdit()
            self.inputs["address"].setPlaceholderText("أدخل العنوان الكامل (اختياري)")

            self.inputs["add_date"] = QDateEdit()
            self.inputs["add_date"].setCalendarPopup(True)
            self.inputs["add_date"].setDate(QDate.currentDate())
            self.inputs["add_date"].setDisplayFormat("dd/MM/yyyy")

            self.inputs["notes"] = QLineEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات إضافية")

            self.form_layout.addRow("اسم العميل:", self.inputs["client_name"])
            self.form_layout.addRow("رقم الهاتف (اختياري):", self.inputs["phone"])
            self.form_layout.addRow("العنوان (اختياري):", self.inputs["address"])
            self.form_layout.addRow("تاريخ الإضافة:", self.inputs["add_date"])
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])

        elif self.section_name == "الحسابات":
            self.inputs["description"] = QLineEdit()
            self.inputs["description"].setPlaceholderText("مثال: شراء مواد بناء")

            self.inputs["amount"] = QLineEdit()
            self.inputs["amount"].setPlaceholderText("أدخل المبلغ بالدينار")

            self.inputs["expense_date"] = QDateEdit()
            self.inputs["expense_date"].setCalendarPopup(True)
            self.inputs["expense_date"].setDate(QDate.currentDate())
            self.inputs["expense_date"].setDisplayFormat("dd/MM/yyyy")

            self.inputs["recipient"] = QLineEdit()
            self.inputs["recipient"].setPlaceholderText("اسم المستلم إن وجد")

            self.inputs["phone"] = QLineEdit()
            self.inputs["phone"].setPlaceholderText("رقم هاتف المستلم إن وجد")

            self.inputs["invoice_number"] = QLineEdit()
            self.inputs["invoice_number"].setPlaceholderText("أدخل رقم الفاتورة إن وجد")

            self.inputs["notes"] = QLineEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات إضافية")

            self.form_layout.addRow("وصف المصروف:", self.inputs["description"])
            self.form_layout.addRow("المبلغ:", self.inputs["amount"])
            self.form_layout.addRow("التاريخ:", self.inputs["expense_date"])
            self.form_layout.addRow("المستلم (اختياري):", self.inputs["recipient"])
            self.form_layout.addRow("رقم الهاتف (اختياري):", self.inputs["phone"])
            self.form_layout.addRow("رقم الفاتورة (اختياري):", self.inputs["invoice_number"])
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])

        elif self.section_name == "الموظفين":
            self.inputs["employee_name"] = QLineEdit()
            self.inputs["employee_name"].setPlaceholderText("أدخل اسم الموظف الكامل")

            self.inputs["phone"] = QLineEdit()
            self.inputs["phone"].setPlaceholderText("أدخل رقم الهاتف (اختياري)")

            self.inputs["address"] = QLineEdit()
            self.inputs["address"].setPlaceholderText("أدخل العنوان (اختياري)")

            self.inputs["job_title"] = QLineEdit()
            self.inputs["job_title"].setPlaceholderText("أدخل المسمى الوظيفي")

            self.inputs["salary"] = QLineEdit()
            self.inputs["salary"].setPlaceholderText("أدخل قيمة المرتب الشهري")
            self.inputs["salary"].setText("0")

            self.inputs["commission"] = QLineEdit()
            self.inputs["commission"].setPlaceholderText("أدخل نسبة العمولة إن وجدت (اختياري)")

            self.inputs["start_date"] = QDateEdit()
            self.inputs["start_date"].setCalendarPopup(True)
            self.inputs["start_date"].setDate(QDate.currentDate())
            self.inputs["start_date"].setDisplayFormat("dd/MM/yyyy")

            # إضافة التشك بوكسات الجديدة
            self.inputs["auto_salary_schedule"] = QCheckBox("إدراج الراتب تلقائياً شهرياً")
            self.inputs["auto_salary_schedule"].setEnabled(False)  # معطل في البداية

            self.inputs["attendance_system"] = QCheckBox("خاضع لنظام الحضور والانصراف")
            self.inputs["attendance_system"].setChecked(True)  # مفعل افتراضياً

            self.inputs["notes"] = QLineEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات عن الموظف")

            self.form_layout.addRow("اسم الموظف:", self.inputs["employee_name"])
            self.form_layout.addRow("رقم الهاتف:", self.inputs["phone"])
            self.form_layout.addRow("العنوان:", self.inputs["address"])
            self.form_layout.addRow("الوظيفة:", self.inputs["job_title"])
            self.form_layout.addRow("المرتب:", self.inputs["salary"])
            self.form_layout.addRow("النسبة:", self.inputs["commission"])
            self.form_layout.addRow("تاريخ المباشرة:", self.inputs["start_date"])
            self.form_layout.addRow("", self.inputs["auto_salary_schedule"])  # بدون تسمية لأن التشك بوكس يحتوي على النص
            self.form_layout.addRow("", self.inputs["attendance_system"])  # بدون تسمية لأن التشك بوكس يحتوي على النص
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])

            # ربط تغيير قيمة الراتب بتفعيل/إلغاء تفعيل تشك بوكس الراتب التلقائي
            # على الراتب تغير
            def on_salary_changed():
                try:
                    salary_value = float(self.inputs["salary"].text() or "0")
                    self.inputs["auto_salary_schedule"].setEnabled(salary_value > 0)
                    if salary_value <= 0:
                        self.inputs["auto_salary_schedule"].setChecked(False)
                except ValueError:
                    self.inputs["auto_salary_schedule"].setEnabled(False)
                    self.inputs["auto_salary_schedule"].setChecked(False)

            self.inputs["salary"].textChanged.connect(on_salary_changed)

            # تفعيل التشك بوكس عند التحميل الأولي إذا كان هناك راتب
            on_salary_changed()

        
        elif self.section_name == "التدريب":
            # عنوان الدورة
            self.inputs["course_title"] = QLineEdit()
            self.inputs["course_title"].setPlaceholderText("أدخل عنوان الدورة التدريبية")

            # التكلفة
            self.inputs["cost"] = QLineEdit()
            self.inputs["cost"].setPlaceholderText("أدخل تكلفة الدورة")
            # إضافة validator للأرقام فقط
            cost_validator = QDoubleValidator(0.0, 999999.99, 2)
            cost_validator.setNotation(QDoubleValidator.StandardNotation)
            self.inputs["cost"].setValidator(cost_validator)

            # تاريخ البدء
            self.inputs["start_date"] = QDateEdit()
            self.inputs["start_date"].setCalendarPopup(True)
            self.inputs["start_date"].setDate(QDate.currentDate())
            setup_date_edit_format(self.inputs["start_date"])

            # تاريخ الانتهاء
            self.inputs["end_date"] = QDateEdit()
            self.inputs["end_date"].setCalendarPopup(True)
            self.inputs["end_date"].setDate(QDate.currentDate().addDays(30))
            setup_date_edit_format(self.inputs["end_date"])

            # الحالة - تطابق ENUM في قاعدة البيانات
            self.inputs["status"] = QComboBox()
            self.inputs["status"].addItems([
                "قيد التسجيل",
                "جارية",
                "منتهية",
                "ملغاه",
                "معلق "
            ])

            # ملاحظات
            self.inputs["notes"] = QTextEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات إضافية عن الدورة")
            self.inputs["notes"].setMaximumHeight(100)

            # إضافة الحقول إلى النموذج
            self.form_layout.addRow("عنوان الدورة:", self.inputs["course_title"])
            self.form_layout.addRow("التكلفة:", self.inputs["cost"])
            self.form_layout.addRow("تاريخ البدء:", self.inputs["start_date"])
            self.form_layout.addRow("تاريخ الإنتهاء:", self.inputs["end_date"])
            self.form_layout.addRow("الحالة:", self.inputs["status"])
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])
        
        elif self.section_name == "الموردين":
            # اسم المورد
            self.inputs["supplier_name"] = QLineEdit()
            self.inputs["supplier_name"].setPlaceholderText("أدخل اسم المورد")

            # رقم الهاتف
            self.inputs["phone"] = QLineEdit()
            self.inputs["phone"].setPlaceholderText("أدخل رقم الهاتف")

            # العنوان
            self.inputs["address"] = QLineEdit()
            self.inputs["address"].setPlaceholderText("أدخل العنوان")

            # البريد الإلكتروني
            self.inputs["email"] = QLineEdit()
            self.inputs["email"].setPlaceholderText("أدخل البريد الإلكتروني")

            # تاريخ الإضافة
            self.inputs["add_date"] = QDateEdit()
            self.inputs["add_date"].setCalendarPopup(True)
            self.inputs["add_date"].setDate(QDate.currentDate())
            self.inputs["add_date"].setDisplayFormat("dd/MM/yyyy")

            # ملاحظات
            self.inputs["notes"] = QLineEdit()
            self.inputs["notes"].setPlaceholderText("أدخل أي ملاحظات إضافية")

            # إضافة الحقول إلى النموذج
            self.form_layout.addRow("اسم المورد:", self.inputs["supplier_name"])
            self.form_layout.addRow("رقم الهاتف:", self.inputs["phone"])
            self.form_layout.addRow("العنوان:", self.inputs["address"])
            self.form_layout.addRow("البريد الإلكتروني:", self.inputs["email"])
            self.form_layout.addRow("تاريخ الإضافة:", self.inputs["add_date"])
            self.form_layout.addRow("ملاحظات:", self.inputs["notes"])

    #تعبئة البيانات للتعديل
    # ملء الحقول ببيانات موجودة في وضع التعديل
    def populate_fields(self):
        if not self.entry_data:
            print("لا توجد بيانات للتعبئة!")
            return

        # جلب تعريف الأعمدة للقسم الحالي من TABLE_COLUMNS
        column_defs = TABLE_COLUMNS.get(self.section_name, [])

        # إنشاء تعيين بين مفاتيح الحقول وأسماء الأعمدة في قاعدة البيانات
        db_mapping = {}
        for col in column_defs:
            # استخدام المفتاح كاسم عمود في قاعدة البيانات
            db_mapping[col["key"]] = col["key"]

        # تعيينات خاصة للحقول التي تختلف أسماؤها عن أسماء الأعمدة
        # إضافة تعيين عام لحقل التصنيف الجديد
        db_mapping["classification"] = "التصنيف"

        if self.section_name == "المشاريع":
            db_mapping["classification"] = "التصنيف"  # حقل التصنيف الجديد
            db_mapping["client_name"] = "اسم_العميل"
            db_mapping["responsible_engineer"] = "معرف_المهندس"  # حقل المهندس المسؤول الجديد
            db_mapping["phone"] = "رقم_الهاتف"
            db_mapping["project_name"] = "اسم_المشروع"
            db_mapping["description"] = "وصف_المشروع"
            db_mapping["amount"] = "المبلغ"
            db_mapping["receive_date"] = "تاريخ_الإستلام"
            db_mapping["delivery_date"] = "تاريخ_التسليم"
            db_mapping["notes"] = "ملاحظات"
        elif self.section_name == "المقاولات":
            db_mapping["classification"] = "التصنيف"  # حقل التصنيف الجديد
            db_mapping["client_name"] = "اسم_العميل"
            db_mapping["responsible_engineer"] = "معرف_المهندس"  # حقل المهندس المسؤول الجديد
            db_mapping["phone"] = "رقم_الهاتف"
            db_mapping["project_name"] = "اسم_المشروع"  # نفس الحقل للمقاولات
            db_mapping["description"] = "وصف_المشروع"
            db_mapping["amount"] = "المبلغ"
            db_mapping["receive_date"] = "تاريخ_الإستلام"
            db_mapping["delivery_date"] = "تاريخ_التسليم"
            db_mapping["notes"] = "ملاحظات"
        elif self.section_name == "العملاء":
            db_mapping["client_code"] = "التصنيف"
            db_mapping["client_name"] = "اسم_العميل"
            db_mapping["phone"] = "رقم_الهاتف"
            db_mapping["address"] = "العنوان"
            db_mapping["add_date"] = "تاريخ_الإضافة"
            db_mapping["notes"] = "ملاحظات"
        elif self.section_name == "الحسابات":
            db_mapping["expense_code"] = "التصنيف"
            db_mapping["description"] = "المصروف"
            db_mapping["amount"] = "المبلغ"
            db_mapping["expense_date"] = "تاريخ_المصروف"
            db_mapping["recipient"] = "المستلم"
            db_mapping["phone"] = "رقم_الهاتف"
            db_mapping["invoice_number"] = "رقم_الفاتورة"
            db_mapping["notes"] = "ملاحظات"
        elif self.section_name == "الموظفين":
            db_mapping["employee_code"] = "التصنيف"
            db_mapping["employee_name"] = "اسم_الموظف"
            db_mapping["phone"] = "الهاتف"
            db_mapping["address"] = "العنوان"
            db_mapping["job_title"] = "الوظيفة"
            db_mapping["salary"] = "المرتب"
            db_mapping["commission"] = "النسبة"
            db_mapping["start_date"] = "تاريخ_التوظيف"
            db_mapping["auto_salary_schedule"] = "جدولة_المرتب_تلقائية"
            db_mapping["attendance_system"] = "خاضع_لنظام_الحضور_والانصراف"
            db_mapping["notes"] = "ملاحظات"

        elif self.section_name == "التدريب":
            db_mapping["classification"] = "التصنيف"
            db_mapping["course_title"] = "عنوان_الدورة"
            db_mapping["cost"] = "التكلفة"
            db_mapping["start_date"] = "تاريخ_البدء"
            db_mapping["end_date"] = "تاريخ_الإنتهاء"
            db_mapping["status"] = "الحالة"
            db_mapping["notes"] = "ملاحظات"

        elif self.section_name == "الموردين":
            db_mapping["classification"] = "التصنيف"
            db_mapping["supplier_name"] = "اسم_المورد"
            db_mapping["phone"] = "رقم_الهاتف"
            db_mapping["address"] = "العنوان"
            db_mapping["email"] = "الإيميل"
            db_mapping["notes"] = "ملاحظات"
                        
        # تعبئة الحقول
        for field_key, widget in self.inputs.items():
            # تخطي الحقول المحسوبة مثل المدة
            if field_key == "duration" and self.section_name == "المشاريع":
                continue

            # جلب اسم العمود في قاعدة البيانات
            db_column = db_mapping.get(field_key, field_key)

            # جلب القيمة من entry_data
            value = None

            # معالجة خاصة لبيانات العميل
            if field_key == "phone" and self.section_name == "المشاريع" :
                value = self.entry_data.get("رقم_هاتف_العميل", "")
            elif field_key == "address" and self.section_name == "المشاريع":
                value = self.entry_data.get("عنوان_العميل", "")
            elif field_key == "client_code" and self.section_name == "المشاريع" :
                value = self.entry_data.get("كود_العميل", "")
            elif db_column in self.entry_data:
                value = self.entry_data[db_column]
            else:
                # محاولة البحث عن العمود بالاسم الأصلي
                value = self.entry_data.get(field_key, "")

            
            if value is None:
                value = ""

            try:
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value))
                elif isinstance(widget, QDateEdit):
                    date = None
                    if hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
                        # إذا كانت القيمة هي كائن تاريخ أو تاريخ ووقت
                        q_date = QDate(value.year, value.month, value.day)
                        widget.setDate(q_date)
                    elif isinstance(value, str) and value.strip():
                        # تجربة صيغ تواريخ متعددة
                        for fmt in [Qt.ISODate, "yyyy-MM-dd", "dd/MM/yyyy", "MM/dd/yyyy"]:
                            date = QDate.fromString(value, fmt)
                            if date.isValid():
                                break
                        if date and date.isValid():
                            widget.setDate(date)
                        else:
                            widget.setDate(QDate.currentDate())
                    else:
                        widget.setDate(QDate.currentDate())
                elif isinstance(widget, QComboBox):
                    # للكومبو بوكس، نبحث عن النص المطابق
                    if field_key == "client_name":
                        client_name = str(value)
                        # البحث عن النص في الكومبو بوكس
                        index = widget.findText(client_name)
                        if index >= 0:
                            widget.setCurrentIndex(index)
                        else:
                            # إذا لم يتم العثور على النص، نضيفه
                            widget.addItem(client_name)
                            widget.setCurrentText(client_name)
                    elif field_key == "responsible_engineer":
                        # معالجة خاصة للمهندس المسؤول
                        engineer_id = str(value)
                        if engineer_id == "المدير":
                            # البحث عن "المدير" مباشرة
                            index = widget.findText("المدير")
                            if index >= 0:
                                widget.setCurrentIndex(index)
                        else:
                            # البحث عن المهندس بالمعرف
                            found = False
                            for i in range(widget.count()):
                                item_data = widget.itemData(i)
                                if str(item_data) == engineer_id:
                                    widget.setCurrentIndex(i)
                                    found = True
                                    break

                            if not found:
                                # إذا لم يتم العثور على المهندس، نجلب اسمه من قاعدة البيانات
                                engineer_display_text = self.get_engineer_display_text(engineer_id)
                                if engineer_display_text:
                                    widget.addItem(engineer_display_text, engineer_id)
                                    widget.setCurrentIndex(widget.count() - 1)
                    else:
                        # للكومبو بوكسات الأخرى
                        widget.setCurrentText(str(value))
                elif isinstance(widget, QCheckBox):
                    # للتشك بوكسات، نحول القيمة إلى boolean
                    if isinstance(value, bool):
                        widget.setChecked(value)
                    elif isinstance(value, (int, str)):
                        # تحويل القيم المختلفة إلى boolean
                        if str(value).lower() in ['true', '1', 'نعم', 'yes']:
                            widget.setChecked(True)
                        else:
                            widget.setChecked(False)
                    else:
                        widget.setChecked(False)
            except Exception as e:
                print(f"خطأ في ملء الحقل {field_key}: {e}")
                if isinstance(widget, QLineEdit):
                    widget.setText("")
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText("")
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)

        # إعادة حساب المدة للمشاريع والمقاولات
        if self.section_name == "المشاريع" and "receive_date" in self.inputs and "delivery_date" in self.inputs:
            start = self.inputs["receive_date"].date()
            end = self.inputs["delivery_date"].date()
            days = start.daysTo(end)
            if "duration" in self.inputs:
                self.inputs["duration"].setText(str(days if days >= 0 else 0))

        # تحديث حالة تشك بوكس الراتب التلقائي للموظفين
        if self.section_name == "الموظفين" and "salary" in self.inputs and "auto_salary_schedule" in self.inputs:
            try:
                salary_value = float(self.inputs["salary"].text() or "0")
                self.inputs["auto_salary_schedule"].setEnabled(salary_value > 0)
            except ValueError:
                self.inputs["auto_salary_schedule"].setEnabled(False)

        # إعادة حساب إجمالي المبلغ للدورات التدريبية
        if self.section_name == "التدريب" and "cost" in self.inputs and "participants_count" in self.inputs and "total_amount" in self.inputs:
            try:
                cost = float(self.inputs["cost"].text() or "0")
                participants = int(self.inputs["participants_count"].text() or "0")
                total = cost * participants
                self.inputs["total_amount"].setText(str(total))
            except ValueError:
                pass
        
        elif self.section_name == "الموردين":
            if "classification" in self.inputs and "supplier_name" in self.inputs:
                classification = self.inputs["classification"].currentText()
                supplier_name = self.inputs["supplier_name"].text()
                if classification and supplier_name:
                    self.inputs["supplier_name"].setText(f"{classification} - {supplier_name}")


    # جلب اسم ووظيفة المهندس للعرض في الكومبو بوكس
    def get_engineer_display_text(self, engineer_id):
        try:
            if not engineer_id or engineer_id == "0":
                return None

            conn = self.main_window.get_db_connection()
            if not conn:
                return None

            cursor = conn.cursor()
            cursor.execute(
                "SELECT اسم_الموظف, الوظيفة FROM الموظفين WHERE id = %s",
                (engineer_id,)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                employee_name, job_title = result
                if job_title and job_title.strip():
                    return f"{employee_name} - {job_title}"
                else:
                    return employee_name
            else:
                return None

        except Exception as e:
            print(f"خطأ في جلب بيانات المهندس {engineer_id}: {e}")
            return None

    # تطبيق أنماط محددة لنافذة الحوار نفسها وتخطيطها.
    def apply_dialog_style(self):
        dialog_stylesheet = """
            QDialog {
                background-color: #f4f4f4; /* Light background for dialog */
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QDialog QLabel {
                color: white;
                min-width: 150px; /* Ensure labels have some minimum width */
                background-color: #3498db;
                font-size: 16px;
                font-weight: bold;
                font-family: "Janna LT";
            }
             QDialog QLineEdit, QDialog QDateEdit, QDialog QTextEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ffffff;
                color: #333;
                font-size: 16px;
                min-height: 25px; /* Adjust height */
            }
            QDialog QTextEdit {
                 min-height: 60px; /* Taller for notes */
            }
            QDialog QTextEdit {
                 min-height: 60px; /* Taller for notes */
            }
            QDialog QLineEdit:read-only {
                background-color: #e0e0e0; /* Grey background for read-only */
                color: #777;
            }
            QDialog QLineEdit:focus, QDialog QDateEdit:focus, QDialog QTextEdit:focus {
                border: 1px solid #0078D7;
                background-color: #E6F0FF;
            }

            QDialog QDateEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ffffff;
                color: #333;
                font-size: 10pt;
                min-height: 25px; /* Adjust height */
            }
            QDialog QDateEdit::calendar {
                background-color: #e6f2ff;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QDialog QCalendarWidget {
                background-color: #e6f2ff;
            }
            QDialog QCalendarWidget QWidget {
                background-color: #e6f2ff;
            }
            QDialog QCalendarWidget QToolButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 3px;
                padding: 5px;
            }
            QDialog QCalendarWidget QMenu {
                background-color: #e6f2ff;
            }
            QDialog QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QDialog QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: #333;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QDialog QCalendarWidget QAbstractItemView:disabled {
                color: #ccc;
            }

            QDialog QDateEdit::drop-down {
                /* Style the dropdown button */
                 subcontrol-origin: padding;
                 subcontrol-position: top left; /* Button on the left in RTL */
                 width: 20px;
                 border-right-width: 1px; /* Border on the right */
                 border-right-color: #bdc3c7;
                 border-left-width: 1px; /* Border on the right */
                 border-left-color: #bdc3c7;
                 border-right-style: solid;
                 border-top-left-radius: 3px;
                 border-bottom-left-radius: 3px;
            }
            QDialog QDateEdit::down-arrow {
                 image: none;
                 background-color: #bdc3c7;
                 border: none;
                 font-weight: bold;
                 text-align: center;
                 font-size: 16px;
             }
             QDialog QComboBox {
                 padding: 6px;
                 border: 1px solid #bdc3c7;
                 border-radius: 3px;
                 background-color: #ffffff;
                 color: #333;
                 font-size: 10pt;
                 min-height: 25px; /* Adjust height */
             }

             QDialog QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
                text-align: center;
                font-weight: normal;
                font-size: 10pt;
             }
             QDialog QPushButton:hover {
                 background-color: #2980b9;
             }
             QDialog QPushButton:pressed {
                 background-color: #2471a3;
             }
        """
        self.setStyleSheet(dialog_stylesheet)

    # تحميل المهندسين من جدول الموظفين إلى كومبو بوكس المهندس المسؤول
    def load_engineers_to_combo(self):
        if "responsible_engineer" not in self.inputs or not isinstance(self.inputs["responsible_engineer"], QComboBox):
            return

        combo_box = self.inputs["responsible_engineer"]
        combo_box.clear()
        combo_box.addItem("", "")  # خيار فارغ

        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات ")
                return

            cursor = conn.cursor()

            # استعلام لجلب المهندسين من جدول الموظفين
            cursor.execute("""
                SELECT id, اسم_الموظف, الوظيفة, التصنيف
                FROM الموظفين
                WHERE الوظيفة LIKE '%مهندس%' OR الوظيفة LIKE '%هندسي%' OR التصنيف LIKE '%مهندس%'
                ORDER BY اسم_الموظف
            """)
            engineers = cursor.fetchall()

            # إضافة المهندسين إلى الكومبو بوكس
            for engineer_id, engineer_name, job_title, classification in engineers:
                display_text = f"{engineer_name} - {job_title}"
                combo_box.addItem(display_text, engineer_id)

            # إضافة خيار "المدير" كافتراضي
            if combo_box.findText("المدير") == -1:
                combo_box.addItem("المدير", "المدير")

        except Exception as e:
            print(f"خطأ في تحميل المهندسين: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # تحميل أنواع العملاء المتاحة إلى كومبو بوكس نوع العميل
    def load_client_types_to_combo(self):
        if "client_code" not in self.inputs or not isinstance(self.inputs["client_code"], QComboBox):
            return

        combo_box = self.inputs["client_code"]
        combo_box.clear()
        combo_box.addItem("")  # إضافة عنصر فارغ في البداية

        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات للسنة")
                return

            cursor = conn.cursor()

            # استعلام لجلب أنواع العملاء الفريدة من جدول العملاء
            cursor.execute("SELECT DISTINCT `التصنيف` FROM `العملاء` WHERE `التصنيف` IS NOT NULL AND `التصنيف` != '' ORDER BY `التصنيف`")
            client_types = cursor.fetchall()

            # إضافة أنواع العملاء إلى الكومبو بوكس
            for (client_type,) in client_types:
                combo_box.addItem(client_type)

            # إضافة الأنواع الافتراضية إذا لم تكن موجودة
            default_types = [
                "مواطن",
                "مهندس",
                "شركة",
                "شركة هندسية",
                "مكتب هندسي",
                "مؤسسة حكومية",
                "مؤسسة خاصة"
            ]

            for default_type in default_types:
                if combo_box.findText(default_type) == -1:  # إذا لم يكن موجوداً
                    combo_box.addItem(default_type)

        except Exception as e:
            print(f"خطأ في تحميل أنواع العملاء: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # تحميل كود العميل التالي المتاح
    def load_next_available_client_code(self):
        if "client_code" not in self.inputs:
            return

        # لا نحتاج لتوليد كود تلقائي، فقط نترك الحقل فارغاً
        # المستخدم يمكنه اختيار نوع العميل من القائمة أو إدخال نوع جديد
        pass

    # تحميل بيانات العملاء من قاعدة البيانات وإضافتها إلى الكومبو بوكس
    def load_clients_to_combo(self):
        if "client_name" not in self.inputs or not isinstance(self.inputs["client_name"], QComboBox):
            return

        combo_box = self.inputs["client_name"]
        combo_box.clear()
        combo_box.addItem("")  # إضافة عنصر فارغ في البداية

        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات  ")
                return

            cursor = conn.cursor()

            # استعلام لجلب بيانات العملاء
            cursor.execute("SELECT id, اسم_العميل, رقم_الهاتف, التصنيف, العنوان FROM العملاء ORDER BY اسم_العميل")
            clients = cursor.fetchall()

            # إضافة العملاء إلى الكومبو بوكس
            for client_id, client_name, phone, code, address in clients:
                display_text = f"{client_name}"
                combo_box.addItem(display_text)
                # تخزين id العميل ورقم الهاتف والتصنيف والعنوان كبيانات إضافية
                combo_box.setItemData(combo_box.count() - 1, {
                    "id": client_id,
                    "phone": phone,
                    "code": code or "",
                    "التصنيف": code or "",  # إضافة المفتاح الصحيح للتصنيف
                    "address": address or ""
                })

            # إضافة خاصية الإكمال التلقائي
            client_names = [combo_box.itemText(i) for i in range(combo_box.count())]
            completer = QCompleter(client_names)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            combo_box.setCompleter(completer)

            # ربط حدث تغيير العميل بتحديث رقم الهاتف
            combo_box.currentIndexChanged.connect(self.update_phone_field)

        except Exception as e:
            print(f"خطأ في تحميل بيانات العملاء: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # جلب كود العميل من قاعدة البيانات
    def get_client_code(self, client_id):
        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات للسنة ")
                return ""

            cursor = conn.cursor()

            # تحديد اسم الجدول في قاعدة البيانات
            db_table_name = self.main_window.get_db_table_name("العملاء")

            # استعلام لجلب كود العميل
            cursor.execute(f"SELECT التصنيف FROM `{db_table_name}` WHERE id = %s", (client_id,))
            result = cursor.fetchone()

            if result:
                return result[0] or ""
            return ""

        except Exception as e:
            print(f"خطأ في جلب كود العميل: {e}")
            return ""
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # جلب عنوان العميل من قاعدة البيانات
    def get_client_address(self, client_id):
        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات للسنة")
                return ""

            cursor = conn.cursor()

            # تحديد اسم الجدول في قاعدة البيانات
            db_table_name = self.main_window.get_db_table_name("العملاء")

            # استعلام لجلب عنوان العميل
            cursor.execute(f"SELECT العنوان FROM `{db_table_name}` WHERE id = %s", (client_id,))
            result = cursor.fetchone()

            if result:
                return result[0] or ""
            return ""

        except Exception as e:
            print(f"خطأ في جلب عنوان العميل: {e}")
            return ""
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # تحديث بيانات العميل عند اختيار عميل من القائمة
    def update_phone_field(self):
        if "client_name" not in self.inputs:
            return

        combo_box = self.inputs["client_name"]
        current_index = combo_box.currentIndex()

        # تفريغ الحقول إذا لم يتم اختيار عميل
        if current_index <= 0:  # لا يوجد عميل محدد أو العنصر الفارغ
            if "phone" in self.inputs:
                self.inputs["phone"].setText("")
            if "client_code" in self.inputs:
                self.inputs["client_code"].setCurrentText("")
                # إذا كان في وضع إضافة مشروع جديد، نقوم بتحميل كود العميل التالي المتاح
                if not self.entry_data and self.section_name == "المشاريع":
                    self.load_next_available_client_code()
            if "address" in self.inputs:
                self.inputs["address"].setText("")
            return

        # استخراج بيانات العميل المخزنة
        client_data = combo_box.itemData(current_index)
        if client_data:
            # تحديث رقم الهاتف
            if "phone" in self.inputs and "phone" in client_data:
                self.inputs["phone"].setText(client_data["phone"] or "")

            # تحديث كود العميل
            if "client_code" in self.inputs:
                if "التصنيف" in client_data and client_data["التصنيف"]:
                    # استخدام التصنيف المخزن مباشرة من الكومبو بوكس
                    self.inputs["client_code"].setCurrentText(client_data["التصنيف"])
                elif "code" in client_data and client_data["code"]:
                    # استخدام التصنيف المخزن مباشرة من الكومبو بوكس (للتوافق مع النسخة القديمة)
                    self.inputs["client_code"].setCurrentText(client_data["code"])
                elif "id" in client_data:
                    # إذا لم يكن التصنيف متوفرًا، نجلبه من قاعدة البيانات
                    client_code = self.get_client_code(client_data["id"])
                    self.inputs["client_code"].setCurrentText(client_code or "")

            # تحديث عنوان العميل
            if "address" in self.inputs:
                if "address" in client_data and client_data["address"]:
                    # استخدام العنوان المخزن مباشرة من الكومبو بوكس
                    self.inputs["address"].setText(client_data["address"])
                elif "id" in client_data:
                    # إذا لم يكن العنوان متوفرًا، نجلبه من قاعدة البيانات
                    address = self.get_client_address(client_data["id"])
                    self.inputs["address"].setText(address or "")


    # تحميل أنواع المشاريع من قاعدة البيانات والأنواع المسبقة
    def load_project_types(self):
        if "project_type" not in self.inputs:
            return

        combo_box = self.inputs["project_type"]
        combo_box.clear()

        # الأنواع المسبقة الافتراضية
        default_types = [
            "تصميم معماري",
            "تصميم داخلي",
            "أعمال التنفيذ",
            "إشراف هندسي"
        ]

        # إضافة الأنواع المسبقة
        for project_type in default_types:
            combo_box.addItem(project_type)

        # تحميل الأنواع المخصصة من قاعدة البيانات
        try:
            conn = self.main_window.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            # التحقق من وجود جدول أنواع المشاريع وإنشاؤه إذا لم يكن موجوداً
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `أنواع_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_التصنيف` VARCHAR(255) UNIQUE NOT NULL,
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)

            # جلب الأنواع المخصصة
            cursor.execute("SELECT معرف_التصنيف FROM أنواع_المشاريع ORDER BY معرف_التصنيف")
            custom_types = cursor.fetchall()

            # إضافة الأنواع المخصصة للكومبو بوكس
            for (custom_type,) in custom_types:
                if custom_type not in default_types:  # تجنب التكرار
                    combo_box.addItem(custom_type)

        except Exception as e:
            print(f"خطأ في تحميل أنواع المشاريع: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # فتح نافذة إدارة أنواع المشاريع
    def open_project_types_manager(self):
        dialog = ProjectTypesManagerDialog(self.main_window, self.year, self)
        if dialog.exec() == QDialog.Accepted:
            # إعادة تحميل أنواع المشاريع بعد التعديل
            self.load_project_types()

    # حفظ نوع مشروع مخصص في قاعدة البيانات إذا لم يكن موجوداً
    def save_custom_project_type(self, project_type):
        if not project_type or project_type.strip() == "":
            return

        project_type = project_type.strip()

        # الأنواع المسبقة الافتراضية
        default_types = [
            "تصميم معماري",
            "تصميم داخلي",
            "أعمال التنفيذ",
            "إشراف هندسي"
        ]

        # إذا كان النوع من الأنواع المسبقة، لا نحتاج لحفظه
        if project_type in default_types:
            return

        try:
            conn = self.main_window.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            # التحقق من وجود النوع مسبقاً
            cursor.execute("SELECT COUNT(*) FROM أنواع_المشاريع WHERE معرف_التصنيف = %s", (project_type,))
            result = cursor.fetchone()

            if result and result[0] == 0:
                # إضافة النوع الجديد
                cursor.execute(
                    "INSERT INTO أنواع_المشاريع (معرف_التصنيف) VALUES (%s)",
                    (project_type,)
                )
                conn.commit()
                print(f"تم حفظ نوع المشروع المخصص: {project_type}")

        except Exception as e:
            print(f"خطأ في حفظ نوع المشروع المخصص: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    # جمع وحفظ البيانات
    def save_data(self):
        data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text().strip()
            elif isinstance(widget, QDateEdit):
                data[key] = widget.date().toString(Qt.ISODate)
            elif isinstance(widget, QTextEdit):
                data[key] = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText().strip()
                # إذا كان هذا هو كومبو بوكس العملاء، نحفظ id العميل أيضًا
                if key == "client_name" and widget.currentIndex() > 0:
                    client_data = widget.itemData(widget.currentIndex())
                    if client_data and "id" in client_data:
                        data["client_id"] = client_data["id"]
                # إذا كان هذا هو كومبو بوكس المهندس المسؤول، نحفظ id المهندس أيضًا
                elif key == "responsible_engineer" and widget.currentIndex() > 0:
                    engineer_id = widget.itemData(widget.currentIndex())
                    if engineer_id:
                        # إذا كان المهندس "المدير"، نحفظ النص كما هو
                        if engineer_id == "المدير":
                            data["responsible_engineer_id"] = "المدير"
                        else:
                            # إذا كان معرف المهندس رقمي، نحفظه
                            data["responsible_engineer_id"] = engineer_id
            elif isinstance(widget, QCheckBox):
                # حفظ قيمة التشك بوكس كـ boolean
                data[key] = widget.isChecked()

        # إضافة السنة والمستخدم تلقائياً
        data["user"] = settings.value("account_type", "admin")

        if not self.validate_data(data):
            return

        # إذا كان القسم هو المشاريع أو المقاولات، نتحقق من وجود العميل
        if (self.section_name == "المشاريع" or self.section_name == "المقاولات") and "client_name" in data:
            # إذا لم يتم اختيار عميل من الكومبو بوكس (لا يوجد client_id)
            if "client_id" not in data:
                client_name = data["client_name"]
                phone = data.get("phone", "")
                address = data.get("address", "")
                client_code = data.get("client_code", "")

                # التحقق من وجود العميل بنفس الاسم أو رقم الهاتف
                existing_client = self.check_client_exists(client_name, phone)

                if existing_client:
                    # إذا وجد عميل بنفس الاسم أو رقم الهاتف، نستخدم idه
                    data["client_id"] = existing_client["id"]

                    # إذا كان رقم الهاتف مختلف، نسأل المستخدم إذا كان يريد تحديثه
                    if phone and existing_client["phone"] != phone:
                        reply = QMessageBox.question(
                            self,
                            "تحديث رقم الهاتف",
                            f"تم العثور على عميل بنفس الاسم '{client_name}' ولكن برقم هاتف مختلف.\n"
                            f"الرقم الحالي: {existing_client['phone'] or 'غير محدد'}\n"
                            f"الرقم الجديد: {phone}\n\n"
                            f"هل تريد تحديث رقم الهاتف؟",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )

                        if reply == QMessageBox.Yes:
                            # تحديث رقم الهاتف في جدول العملاء
                            try:
                                self.update_client_phone(existing_client["id"], phone)
                            except Exception as e:
                                print(f"خطأ في تحديث رقم الهاتف: {e}")

                    # تحديث كود العميل في البيانات من قاعدة البيانات
                    if "client_code" in self.inputs:
                        client_code_from_db = self.get_client_code(existing_client["id"])
                        if client_code_from_db:
                            self.inputs["client_code"].setCurrentText(client_code_from_db)
                            data["client_code"] = client_code_from_db
                else:
                    # إذا لم يوجد عميل بنفس الاسم أو رقم الهاتف، نضيف عميل جديد
                    # استخدام كود العميل المدخل إذا كان موجودًا، وإلا توليد كود جديد
                    new_client = self.add_client_to_database(client_name, phone, address, client_code)
                    if new_client:
                        data["client_id"] = new_client["id"]
                        # تحديث كود العميل في البيانات وفي حقل الإدخال
                        if "client_code" in self.inputs and "code" in new_client:
                            self.inputs["client_code"].setCurrentText(new_client["code"])
                            data["client_code"] = new_client["code"]
                        QMessageBox.information(
                            self,
                            "إضافة عميل جديد",
                            f"تم إضافة العميل '{client_name}' إلى قاعدة البيانات."
                        )

        if self.entry_data and self.row_id:
            # استدعاء دالة التحديث في MainWindow (تمرر السنة داخلياً)
            self.main_window.update_entry(self.section_name, self.row_id, data)
        else:
            self.main_window.save_entry(self.section_name, data)
        self.accept()


    """تحديث رقم هاتف العميل في قاعدة البيانات"""
    # تحديث هاتف العميل
    def update_client_phone(self, client_id, new_phone=""):
        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات  ")
                return False

            cursor = conn.cursor()

            # تحديد اسم الجدول في قاعدة البيانات
            db_table_name = self.main_window.get_db_table_name("العملاء")

            # تحديث رقم الهاتف
            cursor.execute(f"UPDATE `{db_table_name}` SET `رقم_الهاتف` = %s WHERE `id` = %s", (new_phone, client_id))
            conn.commit()

            return True

        except Exception as e:
            print(f"خطأ في تحديث رقم هاتف العميل: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    
    #التحقق من وجود عميل بنفس الاسم أو رقم الهاتف
    # تحقق من العميل
    def check_client_exists(self, client_name, phone=""):

        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات للسنة ")
                return None

            cursor = conn.cursor()

            # تحديد اسم الجدول في قاعدة البيانات
            db_table_name = self.main_window.get_db_table_name("العملاء")

            # التحقق من وجود الجدول قبل الاستعلام
            cursor.execute(f"SHOW TABLES LIKE '{db_table_name}'")
            if not cursor.fetchone():
                return None

            # استعلام للتحقق من وجود عميل بنفس الاسم
            cursor.execute(f"SELECT id, اسم_العميل, رقم_الهاتف FROM `{db_table_name}` WHERE اسم_العميل = %s", (client_name,))
            result_by_name = cursor.fetchone()

            # إذا وجد عميل بنفس الاسم، نعيد idه
            if result_by_name:
                return {"id": result_by_name[0], "name": result_by_name[1], "phone": result_by_name[2]}

            # إذا تم توفير رقم هاتف، نتحقق من وجود عميل بنفس رقم الهاتف
            if phone:
                cursor.execute(f"SELECT id, اسم_العميل, رقم_الهاتف FROM `{db_table_name}` WHERE رقم_الهاتف = %s", (phone,))
                result_by_phone = cursor.fetchone()

                # إذا وجد عميل بنفس رقم الهاتف، نعيد idه
                if result_by_phone:
                    return {"id": result_by_phone[0], "name": result_by_phone[1], "phone": result_by_phone[2]}

            # لم يتم العثور على عميل بنفس الاسم أو رقم الهاتف
            return None

        except Exception as e:
            print(f"خطأ في التحقق من وجود العميل: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # إضافة عميل جديد إلى قاعدة البيانات
    def add_client_to_database(self, client_name, phone="", address="", client_code=""):
        try:
            # الاتصال بقاعدة البيانات
            conn = self.main_window.get_db_connection()
            if conn is None:
                print(f"تعذر الاتصال بقاعدة البيانات  ")
                return None

            cursor = conn.cursor()

            # تحديد اسم الجدول في قاعدة البيانات
            db_table_name = self.main_window.get_db_table_name("العملاء")

            # التحقق من وجود الجدول قبل الاستعلام
            cursor.execute(f"SHOW TABLES LIKE '{db_table_name}'")
            if not cursor.fetchone():
                print(f"جدول {db_table_name} غير موجود")
                return None

            # استخدام كود العميل المدخل إذا كان موجودًا، وإلا توليد كود جديد
            new_code = client_code
            if not new_code:
                # توليد كود جديد للعميل
                cursor.execute(f"SELECT التصنيف FROM `{db_table_name}` ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                last_code = result[0] if result else None
                new_code = self.main_window.increment_code(last_code if last_code else "CLT-000")

            # التحقق من أن التصنيف الجديد غير مستخدم بالفعل
            is_code_used = True
            max_attempts = 100  # تحديد عدد المحاولات القصوى لتجنب الحلقة اللانهائية
            attempts = 0

            while is_code_used and attempts < max_attempts:
                # التحقق من وجود التصنيف في قاعدة البيانات
                cursor.execute(f"SELECT COUNT(*) FROM `{db_table_name}` WHERE التصنيف = %s", (new_code,))
                result = cursor.fetchone()

                if result and result[0] > 0:
                    # التصنيف موجود بالفعل، نقوم بتوليد كود جديد
                    new_code = self.main_window.increment_code(new_code)
                    attempts += 1
                else:
                    # التصنيف غير موجود، يمكن استخدامه
                    is_code_used = False

            # إذا وصلنا للحد الأقصى من المحاولات ولم نجد كود غير مستخدم
            if attempts >= max_attempts:
                print("تعذر العثور على كود عميل غير مستخدم بعد عدة محاولات")
                # يمكن إضافة رقم عشوائي للكود لضمان عدم تكراره
                import random
                new_code = f"CLT-{random.randint(1000, 9999)}"

            # إضافة العميل الجديد
            current_date = QDate.currentDate().toString(Qt.ISODate)
            sql = f"""
                INSERT INTO `{db_table_name}`
                (`التصنيف`, `اسم_العميل`, `رقم_الهاتف`, `العنوان`, `تاريخ_الإضافة`)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (new_code, client_name, phone, address, current_date)
            cursor.execute(sql, values)
            conn.commit()

            # الحصول على id العميل الجديد
            cursor.execute(f"SELECT LAST_INSERT_id()")
            client_id = cursor.fetchone()[0]

            return {"id": client_id, "name": client_name, "phone": phone, "code": new_code, "address": address}

        except Exception as e:
            print(f"خطأ في إضافة العميل: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # التحقق من صحة البيانات
    def validate_data(self, data):
        if self.section_name == "المشاريع":
            # التحقق من وجود المفاتيح المطلوبة
            if "client_name" not in data or "project_name" not in data or "amount" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات غير مكتملة. تأكد من وجود اسم العميل واسم المشروع والمبلغ.")
                return False

            if not (data["client_name"] and data["project_name"] and data["amount"]):
                QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول المطلوبة (اسم العميل، اسم المشروع، المبلغ).")
                return False
            try:
                amount_value = float(data["amount"])
                if amount_value < 0:
                    QMessageBox.warning(self, "خطأ", "يجب أن يكون المبلغ قيمة موجبة.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح في حقل 'المبلغ'.")
                return False

            # التحقق من وجود التواريخ
            if "receive_date" not in data or "delivery_date" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات التواريخ غير مكتملة.")
                return False

            receive_date_qdate = QDate.fromString(data["receive_date"], Qt.ISODate)
            delivery_date_qdate = QDate.fromString(data["delivery_date"], Qt.ISODate)
            if delivery_date_qdate < receive_date_qdate:
                QMessageBox.warning(self, "خطأ في التواريخ", "تاريخ التسليم يجب أن يكون بعد تاريخ الاستلام.")
                return False

        elif self.section_name == "المقاولات":
            # التحقق من وجود المفاتيح المطلوبة للمقاولات (نفس المشاريع)
            if "client_name" not in data or "project_name" not in data or "amount" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات غير مكتملة. تأكد من وجود اسم العميل واسم المقاولات والمبلغ.")
                return False

            if not (data["client_name"] and data["project_name"] and data["amount"]):
                QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول المطلوبة (اسم العميل، اسم المقاولات، المبلغ).")
                return False
            try:
                amount_value = float(data["amount"])
                if amount_value < 0:
                    QMessageBox.warning(self, "خطأ", "يجب أن يكون المبلغ قيمة موجبة.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح في حقل 'المبلغ'.")
                return False

            # التحقق من وجود التواريخ
            if "receive_date" not in data or "delivery_date" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات التواريخ غير مكتملة.")
                return False

            receive_date_qdate = QDate.fromString(data["receive_date"], Qt.ISODate)
            delivery_date_qdate = QDate.fromString(data["delivery_date"], Qt.ISODate)
            if delivery_date_qdate < receive_date_qdate:
                QMessageBox.warning(self, "خطأ في التواريخ", "تاريخ التسليم يجب أن يكون بعد تاريخ الاستلام.")
                return False

        elif self.section_name == "العملاء":
            # التحقق من وجود اسم العميل
            if "client_name" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات غير مكتملة. تأكد من وجود اسم العميل.")
                return False

            if not data["client_name"]:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم العميل.")
                return False

            # التحقق من عدم تكرار اسم العميل أو رقم الهاتف
            client_name = data["client_name"]
            phone = data.get("phone", "")

            # لا نتحقق من التكرار في حالة التعديل
            if not self.entry_data:
                existing_client = self.check_client_exists(client_name, phone)

                if existing_client:
                    # إذا وجد عميل بنفس الاسم
                    if existing_client["name"] == client_name:
                        QMessageBox.warning(
                            self,
                            "خطأ",
                            f"يوجد عميل بنفس الاسم '{client_name}' في قاعدة البيانات."
                        )
                        return False

                    # إذا وجد عميل بنفس رقم الهاتف
                    if phone and existing_client["phone"] == phone:
                        QMessageBox.warning(
                            self,
                            "خطأ",
                            f"يوجد عميل برقم الهاتف '{phone}' في قاعدة البيانات."
                        )
                        return False

        elif self.section_name == "الحسابات":
            # التحقق من وجود المفاتيح المطلوبة
            if "description" not in data or "amount" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات غير مكتملة. تأكد من وجود وصف المصروف والمبلغ.")
                return False

            if not (data["description"] and data["amount"]):
                QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول المطلوبة (وصف المصروف، المبلغ).")
                return False
            try:
                amount_value = float(data["amount"])
                if amount_value <= 0:
                    QMessageBox.warning(self, "خطأ", "يجب أن يكون المبلغ قيمة موجبة وأكبر من الصفر.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح في حقل 'المبلغ'.")
                return False

        elif self.section_name == "الموظفين":
            # التحقق من وجود المفاتيح المطلوبة
            if "employee_name" not in data or "job_title" not in data:
                QMessageBox.warning(self, "خطأ", "بيانات غير مكتملة. تأكد من وجود اسم الموظف والوظيفة.")
                return False

            if not (data["employee_name"] and data["job_title"]):
                QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول المطلوبة (اسم الموظف، الوظيفة).")
                return False

            if "salary" in data:
                try:

                    salary_value = float(data["salary"])
                    if salary_value < 0:
                        QMessageBox.warning(self, "خطأ", "يجب أن يكون المرتب قيمة موجبة.")
                        return False
                except ValueError:
                    QMessageBox.warning(self, "خطأ", "يرجى إدخال مرتب صحيح في حقل 'المرتب'.")
                    return False


        return True


# افتح إضافة مربع حوار دخول
def open_add_entry_dialog(main_window, section_name):
     dialog = AddEntryDialog(main_window, section_name, parent=main_window)
     if dialog.exec() == QDialog.Accepted:
          pass #


# استخراج معرف المهندس من النص المعروض في الكومبو بوكس
def get_engineer_id_from_display_text(self, display_text):
    if not display_text or display_text.strip() == "":
        return None

    # إذا كان النص "المدير" فقط، نعيده كما هو
    if display_text.strip() == "المدير":
        return "المدير"

    try:
        # الاتصال بقاعدة البيانات
        conn = self.get_db_connection()
        if conn is None:
            print(f"تعذر الاتصال بقاعدة البيانات  ")
            return None

        cursor = conn.cursor()

        # استخراج اسم المهندس من النص المعروض
        # النص بالشكل: "اسم المهندس - الوظيفة"
        if " - " in display_text:
            engineer_name = display_text.split(" - ")[0].strip()
        else:
            engineer_name = display_text.strip()

        # البحث عن معرف المهندس في قاعدة البيانات
        cursor.execute("SELECT id FROM الموظفين WHERE اسم_الموظف = %s", (engineer_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            print(f"لم يتم العثور على المهندس: {engineer_name}")
            return None

    except Exception as e:
        print(f"خطأ في استخراج معرف المهندس: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#حفظ الاضافة
# حفظ الدخول
def save_entry(self, section_name, data):
    conn = self.get_db_connection()
    if conn is None:
        QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بقاعدة البيانات للسنة")
        return
    cursor = conn.cursor()
    try:
        db_table_name = self.get_db_table_name(section_name)
        if section_name == "المشاريع" or section_name == "المقاولات":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            # تحديد نوع المشروع تلقائياً حسب القسم
            if section_name == "المشاريع":
                project_type = "المشاريع"
            elif section_name == "المقاولات":
                project_type = "المقاولات"
            else:
                project_type = "المشاريع"  # افتراضي

            # تحويل التواريخ من نصوص إلى QDate
            delivery_date_qdate = QDate.fromString(data["delivery_date"], Qt.ISODate)

            # حساب الوقت المتبقي (من التاريخ الحالي إلى تاريخ التسليم)
            current_date = QDate.currentDate()
            remaining_days = current_date.daysTo(delivery_date_qdate) if delivery_date_qdate.isValid() else 0
            remaining_time = f"{remaining_days} يوم" if remaining_days >= 0 else "منتهي"

            # تحديد الحالة الافتراضية
            initial_status = "قيد الإنجاز"  # Default status for new projects

            # الحصول على المهندس المسؤول وتحويله إلى معرف
            # أولاً، نتحقق من وجود معرف المهندس مباشرة من الكومبو بوكس
            if "responsible_engineer_id" in data and data["responsible_engineer_id"]:
                responsible_engineer_id = data["responsible_engineer_id"]
            else:
                # إذا لم يكن معرف المهندس متوفراً، نستخرجه من النص المعروض
                responsible_engineer_text = data.get("responsible_engineer", "المدير")

                # تحويل نص المهندس إلى معرف إذا لم يكن "المدير"
                if responsible_engineer_text == "المدير":
                    responsible_engineer_id = "المدير"
                else:
                    # استخراج معرف المهندس من النص المعروض
                    responsible_engineer_id = get_engineer_id_from_display_text(responsible_engineer_text)
                    if responsible_engineer_id is None:
                        responsible_engineer_id = "المدير"  # افتراضي في حالة عدم العثور على المهندس

            # جملة SQL مع الأعمدة المتطابقة مع تعريف الجدول (إضافة المهندس المسؤول)
            sql = f"""
                INSERT INTO `{db_table_name}`
                (`اسم_القسم`, `معرف_العميل`, `التصنيف`, `اسم_المشروع`, `وصف_المشروع`,
                `المبلغ`, `المدفوع`, `تاريخ_الإستلام`, `تاريخ_التسليم`, `معرف_المهندس`,
                `الحالة`, `ملاحظات`, `المستخدم`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # تعيين القيم مع الأخذ في الاعتبار الأعمدة المطلوبة
            client_id = data.get("client_id", None)  # يجب أن يتم تمريره من الواجهة أو جلب من قاعدة البيانات
            paid_amount = data.get("paid_amount", 0.0)  # افتراضي 0 إذا لم يتم دفع شيء
            values = (
                project_type,                  # اسم_القسم
                client_id,                     # معرف_العميل
                classification,                # التصنيف
                data.get("project_name", ""),  # اسم_المشروع
                data.get("description", ""),   # وصف_المشروع
                float(data["amount"]),         # المبلغ
                float(paid_amount),            # المدفوع
                data["receive_date"],          # تاريخ_الإستلام
                data["delivery_date"],         # تاريخ_التسليم
                responsible_engineer_id,       # معرف_المهندس
                initial_status,                # الحالة
                data.get("notes", ""),         # ملاحظات
                data.get("user", "")           # المستخدم
            )
            cursor.execute(sql, values)

        elif section_name == "العملاء":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            sql = f"""
                INSERT INTO `{db_table_name}`
                (`التصنيف`, `اسم_العميل`, `رقم_الهاتف`, `العنوان`, `تاريخ_الإضافة`, `ملاحظات`,  `المستخدم`)
                VALUES (%s, %s, %s,  %s, %s, %s, %s)
            """
            values = (
                classification, data["client_name"], data.get("phone", ""),
                data.get("address", ""), data["add_date"], data.get("notes", ""), data.get("user", "")
            )
            cursor.execute(sql, values)

        elif section_name == "الحسابات":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            sql = f"""
                INSERT INTO `{db_table_name}`
                (`التصنيف`, `المصروف`, `المبلغ`, `تاريخ_المصروف`, `المستلم`, `رقم_الهاتف`, `رقم_الفاتورة`, `ملاحظات`,  `المستخدم`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                classification, data["description"], float(data["amount"]),
                data["expense_date"], data.get("recipient", ""),
                data.get("phone", ""), data.get("invoice_number", ""), data.get("notes", ""),
                data.get("user", "")
            )
            cursor.execute(sql, values)

        elif section_name == "الموظفين":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            sql = f"""
                INSERT INTO `{db_table_name}`
                (`التصنيف`, `اسم_الموظف`, `الوظيفة`, `العنوان`, `تاريخ_التوظيف`, `المرتب`, `النسبة`, `الهاتف`, `جدولة_المرتب_تلقائية`, `خاضع_لنظام_الحضور_والانصراف`, `ملاحظات`, `المستخدم`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Ensure commission is stored as INT or float depending on schema
            commission_value = data.get("commission", "").strip()
            try:
                    commission_value = int(commission_value) if commission_value else 0 # Or float()
            except ValueError:
                    commission_value = 0 # Default to 0 if invalid

            # تحويل قيم التشك بوكسات إلى boolean
            auto_salary_schedule = data.get("auto_salary_schedule", False)
            attendance_system = data.get("attendance_system", True)

            values = (
                classification, data["employee_name"], data["job_title"],
                data.get("address", ""), data["start_date"], float(data["salary"]), commission_value,
                data.get("phone", ""), auto_salary_schedule, attendance_system, data.get("notes", ""),
                data.get("user", "")
            )
            cursor.execute(sql, values)

        elif section_name == "الموردين":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            sql = f"""
                INSERT INTO `{db_table_name}`
                (`التصنيف`, `اسم_المورد`, `رقم_الهاتف`, `العنوان`, `تاريخ_الإضافة`, `ملاحظات`, `المستخدم`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                classification, data["supplier_name"], data.get("phone", ""),
                data.get("address", ""), data["add_date"], data.get("notes", ""), data.get("user", "")
            )
            cursor.execute(sql, values)



        elif section_name == "التدريب":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            # تحديد الحالة الأولية
            initial_status = data.get("status", "قيد التسجيل")  # Default status

            sql = f"""
                INSERT INTO `{db_table_name}`
                (`التصنيف`, `عنوان_الدورة`, `التكلفة`, `تاريخ_البدء`, `تاريخ_الإنتهاء`,
                `الحالة`, `ملاحظات`, `المستخدم`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            # تحويل التكلفة إلى رقم
            cost = float(data["cost"]) if data.get("cost") else 0.0

            values = (
                classification, data["course_title"], cost,
                data["start_date"], data["end_date"],
                initial_status, data.get("notes", ""), data.get("user", "admin")
            )
            cursor.execute(sql, values)

        conn.commit()
        QMessageBox.information(self, "نجاح", f"تم إضافة {section_name} بنجاح.")

        # After successful save, refresh the data display for the current section
        self.show_section(section_name)

        # تحديث عرض البطاقات إذا كان نشطاً
        if hasattr(self, 'update_cards_view'):
            self.update_cards_view(section_name)

    except mysql.connector.Error as err:
        conn.rollback() # Rollback changes on error
        print(f"Error adding data to {db_table_name}: {err}")
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إضافة البيانات إلى {section_name}: {err}")
    except Exception as e:
        conn.rollback()
        print(f"Unexpected Error saving data: {e}")
        QMessageBox.critical(self, "خطأ غير متوقع",
                                f"حدث خطأ غير متوقع أثناء حفظ البيانات:\n{e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#تعديل البيانات
# تحديث بيانات موجودة في قاعدة البيانات
def update_entry(self, section_name, year, row_id, data):
    conn = self.get_db_connection()
    if conn is None:
        QMessageBox.critical(self, "خطأ", f"تعذر الاتصال بقاعدة البيانات ")
        return
    cursor = conn.cursor()
    try:
        db_table_name = self.get_db_table_name(section_name)

        # بناء جملة SQL للتحديث بناءً على القسم
        if section_name == "المشاريع" or section_name == "المقاولات":
            # التحقق من وجود id العميل والتصنيف والمهندس المسؤول
            client_id = data.get("client_id", None)
            classification = data.get("classification", "")

            # الحصول على المهندس المسؤول وتحويله إلى معرف
            # أولاً، نتحقق من وجود معرف المهندس مباشرة من الكومبو بوكس
            if "responsible_engineer_id" in data and data["responsible_engineer_id"]:
                responsible_engineer_id = data["responsible_engineer_id"]
            else:
                # إذا لم يكن معرف المهندس متوفراً، نستخرجه من النص المعروض
                responsible_engineer_text = data.get("responsible_engineer", "المدير")

                # تحويل نص المهندس إلى معرف إذا لم يكن "المدير"
                if responsible_engineer_text == "المدير":
                    responsible_engineer_id = "المدير"
                else:
                    # استخراج معرف المهندس من النص المعروض
                    responsible_engineer_id = get_engineer_id_from_display_text(responsible_engineer_text, year)
                    if responsible_engineer_id is None:
                        responsible_engineer_id = "المدير"  # افتراضي في حالة عدم العثور على المهندس

            if client_id:
                # إذا كان id العميل موجودًا، نستخدمه في التحديث
                sql = f"""
                    UPDATE `{db_table_name}`
                    SET `معرف_العميل` = %s, `التصنيف` = %s, `اسم_المشروع` = %s, `وصف_المشروع` = %s, `المبلغ` = %s,
                        `تاريخ_الإستلام` = %s, `تاريخ_التسليم` = %s, `معرف_المهندس` = %s, `ملاحظات` = %s
                    WHERE `id` = %s
                """
                values = (
                    client_id, classification, data.get("project_name", ""), data.get("description", ""), float(data["amount"]),
                    data["receive_date"], data["delivery_date"], responsible_engineer_id, data.get("notes", ""),
                    row_id
                )
            else:
                # إذا لم يكن id العميل موجودًا، نستخدم اسم العميل
                sql = f"""
                    UPDATE `{db_table_name}`
                    SET `التصنيف` = %s, `اسم_المشروع` = %s, `وصف_المشروع` = %s, `المبلغ` = %s,
                        `تاريخ_الإستلام` = %s, `تاريخ_التسليم` = %s, `معرف_المهندس` = %s, `ملاحظات` = %s
                    WHERE `id` = %s
                """
                values = (
                    classification, data.get("project_name", ""), data.get("description", ""), float(data["amount"]),
                    data["receive_date"], data["delivery_date"], responsible_engineer_id, data.get("notes", ""),
                    row_id
                )

        elif section_name == "العملاء":
            classification = data.get("classification", "")
            sql = f"""
                UPDATE `{db_table_name}`
                SET `التصنيف` = %s, `اسم_العميل` = %s, `رقم_الهاتف` = %s, `العنوان` = %s, `تاريخ_الإضافة` = %s, `ملاحظات` = %s
                WHERE `id` = %s
            """
            values = (
                classification, data["client_name"], data.get("phone", ""), data.get("address", ""),
                data["add_date"], data.get("notes", ""),
                row_id
            )

        elif section_name == "الحسابات":
            classification = data.get("classification", "")
            sql = f"""
                UPDATE `{db_table_name}`
                SET `التصنيف` = %s, `المصروف` = %s, `المبلغ` = %s, `تاريخ_المصروف` = %s, `المستلم` = %s,
                    `رقم_الهاتف` = %s, `رقم_الفاتورة` = %s, `ملاحظات` = %s
                WHERE `id` = %s
            """
            values = (
                classification, data["description"], float(data["amount"]), data["expense_date"],
                data.get("recipient", ""), data.get("phone", ""), data.get("invoice_number", ""),
                data.get("notes", ""), row_id
            )

        elif section_name == "الموظفين":
            classification = data.get("classification", "")
            sql = f"""
                UPDATE `{db_table_name}`
                SET `التصنيف` = %s, `اسم_الموظف` = %s, `الوظيفة` = %s, `العنوان` = %s,
                    `المرتب` = %s, `تاريخ_التوظيف` = %s, `النسبة` = %s, `الهاتف` = %s,
                    `جدولة_المرتب_تلقائية` = %s, `خاضع_لنظام_الحضور_والانصراف` = %s, `ملاحظات` = %s
                WHERE `id` = %s
            """
            # تحويل النسبة إلى رقم
            commission_value = data.get("commission", "").strip()
            try:
                commission_value = int(commission_value) if commission_value else 0
            except ValueError:
                commission_value = 0

            # تحويل قيم التشك بوكسات إلى boolean
            auto_salary_schedule = data.get("auto_salary_schedule", False)
            attendance_system = data.get("attendance_system", True)

            values = (
                classification, data["employee_name"], data["job_title"],
                data.get("address", ""), float(data["salary"]), data["start_date"],
                commission_value, data.get("phone", ""), auto_salary_schedule, attendance_system,
                data.get("notes", ""), row_id
            )

        elif section_name == "الموردين":
            classification = data.get("classification", "")
            sql = f"""
                UPDATE `{db_table_name}`
                SET `التصنيف` = %s, `اسم_المورد` = %s, `رقم_الهاتف` = %s, `العنوان` = %s,
                    `الايميل` = %s, `الحالة` = %s, `ملاحظات` = %s
                WHERE `id` = %s
            """
            values = (
                classification, data["supplier_name"], data.get("phone", ""),
                data.get("address", ""), data.get("email", ""),
                data.get("status", "نشط"), data.get("notes", ""),
                row_id
            )


        elif section_name == "التدريب":
            # استخدام التصنيف من حقل الإدخال الجديد
            classification = data.get("classification", "")

            # تحويل التكلفة إلى رقم
            cost = float(data["cost"]) if data.get("cost") else 0.0

            sql = f"""
                UPDATE `{db_table_name}`
                SET `التصنيف` = %s, `عنوان_الدورة` = %s, `التكلفة` = %s,
                    `تاريخ_البدء` = %s, `تاريخ_الإنتهاء` = %s, `الحالة` = %s, `ملاحظات` = %s
                WHERE `id` = %s
            """
            values = (
                classification, data["course_title"], cost,
                data["start_date"], data["end_date"],
                data.get("status", "قيد التسجيل"), data.get("notes", ""),
                row_id
            )

        else:
            QMessageBox.warning(self, "تحذير", f"لم يتم تنفيذ تحديث البيانات للقسم {section_name}")
            return

        cursor.execute(sql, values)
        conn.commit()

        # إعادة حساب المدة للمشاريع - فقط إذا كانت الحالة "قيد الإنجاز"
        if section_name == "المشاريع":
            # التحقق من حالة المشروع أولاً
            cursor.execute(f"SELECT `الحالة` FROM `{db_table_name}` WHERE `id` = %s", (row_id,))
            status_result = cursor.fetchone()
            current_status = status_result[0] if status_result else ""

            # تحديث الوقت المتبقي فقط للمشاريع قيد الإنجاز
            if current_status == "قيد الإنجاز":
                receive_date = QDate.fromString(data["receive_date"], Qt.ISODate)
                delivery_date = QDate.fromString(data["delivery_date"], Qt.ISODate)
                days = receive_date.daysTo(delivery_date)

                # تحديث مدة الإنجاز
                cursor.execute(f"UPDATE `{db_table_name}` SET `الوقت_المتبقي` = %s WHERE `id` = %s", (days if days >= 0 else 0, row_id))
                conn.commit()

        QMessageBox.information(self, "نجاح", f"تم تحديث {section_name} بنجاح.")

        # بعد التحديث الناجح، قم بتحديث عرض البيانات للقسم الحالي
        self.show_section(section_name)

        # تحديث عرض البطاقات إذا كان نشطاً
        if hasattr(self, 'update_cards_view'):
            self.update_cards_view(section_name, year)

    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث البيانات: {e}")
        print(f"Error updating entry: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# تم نقل دالة min_open_edit_dialog إلى فئة MainWindow في ملف منظومة_المهندس.py


# يحذف الصفوف المحددة من قاعدة البيانات والجدول.
def delete_selected_rows(self, table, section_name, year, selected_rows):
    db_table_name = self.get_db_table_name(section_name)
    conn = None
    cursor = None
    try:
        conn = self.get_db_connection()
        if conn is None:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"تعذر الاتصال بقاعدة البيانات للسنة {year} للحذف.")
            return

        cursor = conn.cursor()

        deleted_count = 0
        # Iterate through selected rows in reverse order to avoid index issues after deletion
        # We need the ids *before* removing rows from the table widget
        ids_to_delete = []
        for row_index in selected_rows:
            # Get the id from the hidden first column
            معرف_item = table.item(row_index, 0)
            if معرف_item is None:
                print(f"Warning: No id item found for row {row_index}")
                continue
            # Get the original value (int) from UserRole
            row_id = معرف_item.data(Qt.UserRole)
            if row_id is None:
                    print(f"Warning: Invalid id value ({معرف_item.data(Qt.DisplayRole)}) for row {row_index}")
                    continue
            ids_to_delete.append(row_id)

        if not ids_to_delete:
            QMessageBox.warning(self, "لا يوجد معرّفات صالحة", "لم يتم العثور على معرّفات صالحة للصفوف المختارة للحذف.")
            return

        # Perform deletion in DB using collected ids
        sql = f"DELETE FROM `{db_table_name}` WHERE `id` IN ({','.join(['%s'] * len(ids_to_delete))})"
        try:
            cursor.execute(sql, tuple(ids_to_delete))
            conn.commit()
            deleted_count = cursor.rowcount # Number of rows actually deleted in DB
            print(f"Deleted {deleted_count} rows with ids {ids_to_delete} from {db_table_name}")

            # Remove rows from the QTableWidget (in reverse order after DB deletion)
            for row_index in reversed(selected_rows):
                    # Check if the id of this row was actually in the deleted_ids list
                    # This check is important if the user selected rows that didn't have valid ids
                    # Or if some DB deletion failed silently per row (less likely with batch delete)
                    معرف_item = table.item(row_index, 0)
                    if معرف_item and معرف_item.data(Qt.UserRole) in ids_to_delete:
                        table.removeRow(row_index)

            if deleted_count > 0:
                    QMessageBox.information(self, "نجاح", f"تم حذف {deleted_count} صفوف بنجاح من {section_name}.")
                    # Reload stats after deletion if necessary (e.g., for sections with counts)
                    self._update_stats(self.sections[section_name]["stats"], section_name, year)
            elif len(selected_rows) > 0:
                    # This case happens if selected_rows had items, but none had valid ids,
                    # or if the DB deletion didn't affect any rows.
                    QMessageBox.warning(self, "لم يتم الحذف", "لم يتم حذف أي صفوف من قاعدة البيانات. قد تكون الصفوف المختارة غير موجودة أو تحتوي على بيانات غير صالحة.")


        except mysql.connector.Error as err:
            conn.rollback() # Rollback changes if deletion fails
            print(f"Error deleting rows from {db_table_name} with ids {ids_to_delete}: {err}")
            QMessageBox.warning(self, "خطأ في الحذف", f"حدث خطأ أثناء حذف الصفوف من {section_name}:\n{err}")
        except Exception as e:
            conn.rollback()
            print(f"Unexpected error deleting rows: {e}")
            QMessageBox.critical(self, "خطأ غير متوقع", f"حدث خطأ غير متوقع أثناء حذف الصفوف:\n{e}")


    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# معالجة حدث تغيير نص البحث وتطبيق فلتر على الجدول والبطاقات في الصفحة المحددة
def search_data(self, text, section_name):
    search_text = text.strip()

    section_info = self.sections.get(section_name)
    if not section_info:
        print(f"Section info not found for {section_name} during search")
        return

    current_view = section_info.get("current_view", "table")

    # تطبيق البحث على الجدول (دائماً للحفاظ على البيانات)
    _apply_search_to_table(self, search_text, section_name, section_info)

    # تطبيق البحث على البطاقات إذا كانت نشطة
    if current_view == "cards":
        _apply_search_to_cards(self, search_text, section_name, section_info)

# تطبيق البحث على عرض الجدول
def _apply_search_to_table(self, search_text, section_name, section_info):
    current_table = section_info["table"]

    # معالجة خاصة للأقسام التي لا تستخدم جدول تقليدي (مثل التقارير المالية)
    if current_table is None:
        print(f"⚠️ القسم '{section_name}' لا يستخدم جدول تقليدي - تخطي البحث في الجدول")

        # معالجة خاصة لقسم التقارير المالية
        if section_name == "التقارير":
            try:
                # البحث عن ويدجت التقارير المالية وتطبيق البحث عليه
                if "page" in section_info:
                    page = section_info["page"]
                    for child in page.findChildren(QWidget):
                        if hasattr(child, 'apply_search'):
                            child.apply_search(search_text)
                            print(f"✅ تم تطبيق البحث على ويدجت التقارير المالية: '{search_text}'")
                            break
                        elif hasattr(child, 'search_in_widget'):
                            child.search_in_widget(search_text)
                            print(f"✅ تم تطبيق البحث على ويدجت التقارير المالية: '{search_text}'")
                            break

            except Exception as e:
                print(f"⚠️ خطأ في تطبيق البحث على التقارير المالية: {e}")

        return  # الخروج من الدالة للأقسام التي لا تستخدم جدول

    # للأقسام التي تستخدم جدول تقليدي
    # Disable sorting while filtering
    is_sorting_enabled = current_table.isSortingEnabled()
    current_table.setSortingEnabled(False)

    for row_index in range(current_table.rowCount()):
        row_hidden = True
        # Only hide/show if the empty state widget is not visible
        if section_info.get("empty_state_widget") and section_info["empty_state_widget"].isVisible():
            row_hidden = True # Always hide table rows if empty state is visible
        else:
            for col_index in range(current_table.columnCount()):
                # Skip hidden id column from search
                if current_table.isColumnHidden(col_index):
                    continue

                item = current_table.item(row_index, col_index)
                if item:
                    # Get the display text of the item
                    item_text = item.data(Qt.DisplayRole)
                    if item_text is not None:
                        # Convert to string and search case-insensitively
                        if search_text.lower() in str(item_text).lower():
                            row_hidden = False
                            break
        current_table.setRowHidden(row_index, row_hidden)

    # Re-enable sorting
    current_table.setSortingEnabled(is_sorting_enabled)

# تطبيق البحث على عرض البطاقات
def _apply_search_to_cards(self, search_text, section_name, section_info):
    try:
        view_stack = section_info.get("view_stack")
        if not view_stack or view_stack.count() <= 1:
            return

        cards_view = view_stack.widget(1)
        if not hasattr(cards_view, 'search_input'):
            return

        # تحديث نص البحث في البطاقات
        cards_view.search_input.setText(search_text)

        # تطبيق الفلتر على البطاقات
        if hasattr(cards_view, 'filter_cards'):
            cards_view.filter_cards()

    except Exception as e:
        print(f"خطأ في تطبيق البحث على البطاقات: {e}")


# نافذة إدارة أنواع المشاريع المخصصة
class ProjectTypesManagerDialog(QDialog):

    # init
    def __init__(self, main_window, year, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.year = year
        self.setWindowTitle("إدارة أنواع المشاريع")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(400, 300)

        self.setup_ui()
        self.load_custom_types()

    # إعداد واجهة النافذة
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # عنوان النافذة
        title_label = QLabel("إدارة أنواع المشاريع المخصصة")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # قائمة الأنواع المخصصة
        self.types_list = QListWidget()
        layout.addWidget(self.types_list)

        # حقل إضافة نوع جديد
        add_layout = QHBoxLayout()
        self.new_type_edit = QLineEdit()
        self.new_type_edit.setPlaceholderText("أدخل نوع مشروع جديد...")
        add_layout.addWidget(self.new_type_edit)

        add_btn = QPushButton("إضافة")
        add_btn.clicked.connect(self.add_custom_type)
        add_layout.addWidget(add_btn)

        layout.addLayout(add_layout)

        # أزرار الحذف والإغلاق
        buttons_layout = QHBoxLayout()

        delete_btn = QPushButton("حذف المحدد")
        delete_btn.clicked.connect(self.delete_selected_type)
        buttons_layout.addWidget(delete_btn)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        # ربط Enter بإضافة نوع جديد
        self.new_type_edit.returnPressed.connect(self.add_custom_type)

    # تحميل الأنواع المخصصة من قاعدة البيانات
    def load_custom_types(self):
        self.types_list.clear()

        try:
            conn = self.main_window.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            # التحقق من وجود الجدول وإنشاؤه إذا لم يكن موجوداً
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `أنواع_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_التصنيف` VARCHAR(255) UNIQUE NOT NULL,
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)

            # جلب الأنواع المخصصة
            cursor.execute("SELECT id, معرف_التصنيف FROM أنواع_المشاريع ORDER BY معرف_التصنيف")
            custom_types = cursor.fetchall()

            # إضافة الأنواع للقائمة
            for type_id, type_name in custom_types:
                item = QListWidgetItem(type_name)
                item.setData(Qt.UserRole, type_id)  # حفظ الid
                self.types_list.addItem(item)

        except Exception as e:
            print(f"خطأ في تحميل الأنواع المخصصة: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل الأنواع المخصصة:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # إضافة نوع مشروع مخصص جديد
    def add_custom_type(self):
        new_type = self.new_type_edit.text().strip()

        if not new_type:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال نوع المشروع.")
            return

        # التحقق من عدم تكرار النوع
        for i in range(self.types_list.count()):
            if self.types_list.item(i).text() == new_type:
                QMessageBox.warning(self, "تحذير", "هذا النوع موجود بالفعل.")
                return

        # الأنواع المسبقة الافتراضية
        default_types = [
            "تصميم معماري",
            "تصميم داخلي",
            "أعمال التنفيذ",
            "إشراف هندسي"
        ]

        if new_type in default_types:
            QMessageBox.warning(self, "تحذير", "هذا النوع من الأنواع المسبقة ولا يمكن إضافته كنوع مخصص.")
            return

        try:
            conn = self.main_window.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            # إضافة النوع الجديد
            cursor.execute(
                "INSERT INTO أنواع_المشاريع (معرف_التصنيف) VALUES (%s)",
                (new_type,)
            )
            conn.commit()

            # إضافة النوع للقائمة
            item = QListWidgetItem(new_type)
            item.setData(Qt.UserRole, cursor.lastrowid)
            self.types_list.addItem(item)

            # تفريغ حقل الإدخال
            self.new_type_edit.clear()

            QMessageBox.information(self, "نجح", f"تم إضافة نوع المشروع '{new_type}' بنجاح.")

        except Exception as e:
            print(f"خطأ في إضافة النوع المخصص: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إضافة النوع المخصص:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # حذف النوع المحدد
    def delete_selected_type(self):
        current_item = self.types_list.currentItem()

        if not current_item:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار نوع لحذفه.")
            return

        type_name = current_item.text()
        type_id = current_item.data(Qt.UserRole)

        # تأكيد الحذف
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف نوع المشروع '{type_name}'؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            conn = self.main_window.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            # حذف النوع من قاعدة البيانات
            cursor.execute("DELETE FROM أنواع_المشاريع WHERE id = %s", (type_id,))
            conn.commit()

            # حذف النوع من القائمة
            row = self.types_list.row(current_item)
            self.types_list.takeItem(row)

            QMessageBox.information(self, "نجح", f"تم حذف نوع المشروع '{type_name}' بنجاح.")

        except Exception as e:
            print(f"خطأ في حذف النوع المخصص: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف النوع المخصص:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()