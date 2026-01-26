from الإعدادات_العامة import *
from ستايل_نوافذ_الإدارة import (
    apply_to_project_management, setup_table_style, create_stat_card,
    get_status_color, format_currency, format_date, apply_management_style
)
from أزرار_الواجهة import *
from DB import *
import qtawesome as qta
from datetime import datetime
import mysql.connector
from PySide6.QtWidgets import QInputDialog, QCheckBox
from قائمة_الجداول import setup_table_context_menu
from مساعد_أزرار_الطباعة import quick_add_print_button


# نافذة شاملة لإدارة مراحل المشروع
# ProjectPhaseswindow
class ProjectPhasesWindow(QDialog):
    
    # دالة الإنشاء
    # init
    def __init__(self, parent=None, project_data=None, project_type="المشاريع"):
        super().__init__(parent)
        self.parent = parent
        self.project_data = project_data or {}
        self.project_type = project_type
        self.project_id = self.project_data.get('id', None)
        self.client_id = self.project_data.get('معرف_العميل', None)

        # تهيئة متغيرات الجداول
        self.phases_table = None
        self.timeline_table = None
        self.attachments_table = None

        # إعداد النافذة الأساسية
        self.setup_window()

        # تطبيق الستايل الموحد
        apply_to_project_management(self)

        # إنشاء التابات
        self.create_tabs()

        # تحميل البيانات
        self.load_project_info()



        # إضافة أزرار الطباعة لجميع التابات
        self.add_print_buttons()

    # دالة إضافة أرقام تلقائية لجدول
    # أضف أرقام السيارات إلى الجدول
    def add_auto_numbers_to_table(self, table):
        # التحقق من وجود الجدول
        if table is None:
            return

        for row in range(table.rowCount()):
            auto_number_item = QTableWidgetItem(str(row + 1))
            auto_number_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, auto_number_item)  # العمود الثاني (index 1) هو عمود الرقم

    # دالة تطبيق تنسيق الألوان لحالة المبلغ
    # تطبيق لون حالة المبلغ
    def apply_amount_status_color(self, item, status_text):
        try:
            if status_text == "غير مدرج":
                # تطبيق اللون الأحمر للنص
                item.setForeground(QBrush(QColor(231, 76, 60)))
                # تطبيق الخط العريض
                font = QFont()
                font.setBold(True)
                item.setFont(font)
            elif status_text == "تم الإدراج":
                # تطبيق اللون الأخضر للنص
                item.setForeground(QBrush(QColor(46, 125, 50)))
                # تطبيق الخط العريض
                font = QFont()
                font.setBold(True)
                item.setFont(font)
            else:
                # إزالة أي تنسيق للحالات الأخرى
                item.setForeground(QBrush())
                font = QFont()
                font.setBold(False)
                item.setFont(font)
        except Exception as e:
            print(f"خطأ في تطبيق تنسيق الألوان: {e}")
        
    # دالة إعداد النافذة
    # نافذة الإعداد
    def setup_window(self):
        project_name = self.project_data.get('اسم_المشروع', 'مشروع جديد')
        self.setWindowTitle(f"إدارة المشروع - {project_name}")
        self.setGeometry(100, 100, 1600, 900)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # العنوان الرئيسي
        self.title_label = QLabel()
        self.title_label.setObjectName("main_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # إنشاء التابات
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
    # دالة تحديث العنوان
    # تحديث العنوان
    def update_title(self):
        try:
            project_name = self.project_data.get('اسم_المشروع', 'مشروع جديد')
            current_tab_index = self.tab_widget.currentIndex()
            
            if current_tab_index >= 0:
                tab_text = self.tab_widget.tabText(current_tab_index)
                # إزالة أيقونات HTML من نص التاب إذا كانت موجودة
                import re
                clean_tab_text = re.sub(r'<[^>]+>', '', tab_text)
                title_text = f"إدارة مشروع {project_name} - {clean_tab_text}"
            else:
                title_text = f"إدارة مشروع {project_name}"
            
            self.title_label.setText(title_text)
            
        except Exception as e:
            print(f"خطأ في تحديث العنوان: {e}")
            self.title_label.setText(f"إدارة مشروع {self.project_data.get('اسم_المشروع', 'مشروع جديد')}")
        
    # دالة إنشاء التابات
    # إنشاء علامات تبويب
    def create_tabs(self):
        # تاب معلومات المشروع (افتراضي)
        self.create_project_info_tab()
        
        # تاب دفعات المشروع الجديد
        self.create_payments_tab()
        
        # تاب مراحل المشروع
        self.create_project_phases_tab()
        
        # تاب فريق العمل
        self.create_engineers_tasks_tab()
        
        # تاب الجدول الزمني
        self.create_timeline_tab()
        
        # إضافة تابات خاصة بالمقاولات
        if self.project_type == "المقاولات":
            self.create_integrated_custody_tabs()
            # حذف تابات المقاولين والعمال - دمجهم في تاب فريق العمل
            # self.create_contractors_tab()
            # self.create_workers_tab()
            self.create_losses_tab()
            self.create_returns_tab()
        
        # تاب الملفات والمرفقات (متاح لجميع أنواع المشاريع)
        self.create_attachments_tab()
        # تاب التقارير الشاملة
        self.create_reports_tab()

        # ربط إشارة تغيير التاب بدالة التحديث التلقائي
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # تحديث العنوان الأولي
        self.update_title()

    # دالة إنشاء تاب معلومات المشروع
    # إنشاء علامة تبويب معلومات المشروع
    def create_project_info_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # إنشاء scroll area للمحتوى
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # أ. حاوية الإحصائيات المالية (في الأعلى)
        self.create_statistics_container(content_layout)

        # تخطيط أفقي للحاويات الثلاث الأساسية
        top_containers_layout = QHBoxLayout()
        top_containers_layout.setSpacing(15)

        # إنشاء حاويات فرعية للحاويات الثلاث الأساسية
        basic_info_widget = QWidget()
        basic_info_layout = QVBoxLayout(basic_info_widget)
        basic_info_layout.setContentsMargins(0, 0, 0, 0)
        self.create_basic_info_container(basic_info_layout)

        financial_info_widget = QWidget()
        financial_info_layout = QVBoxLayout(financial_info_widget)
        financial_info_layout.setContentsMargins(0, 0, 0, 0)
        self.create_financial_info_container(financial_info_layout)

        timing_status_widget = QWidget()
        timing_status_layout = QVBoxLayout(timing_status_widget)
        timing_status_layout.setContentsMargins(0, 0, 0, 0)
        self.create_timing_status_container(timing_status_layout)

        # إضافة الحاويات الثلاث إلى التخطيط الأفقي
        top_containers_layout.addWidget(basic_info_widget)
        top_containers_layout.addWidget(financial_info_widget)
        top_containers_layout.addWidget(timing_status_widget)

        # إضافة التخطيط الأفقي إلى التخطيط الرئيسي
        content_layout.addLayout(top_containers_layout)

        # ب. حاوية الوصف والملاحظات
        self.create_description_container(content_layout)

        # ج. حاوية المعلومات الإضافية الجديدة
        self.create_additional_info_container(content_layout)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab, qta.icon('fa5s.info-circle', color='#3498db'), "معلومات المشروع")

    # دالة إنشاء تاب الدفعات
    # إنشاء علامة تبويب المدفوعات
    def create_payments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_payment_btn = QPushButton("إضافة دفعة")
        add_payment_btn.setIcon(qta.icon('fa5s.plus'))
        add_payment_btn.clicked.connect(self.add_payment)
        buttons_layout.addWidget(add_payment_btn)

        edit_payment_btn = QPushButton("تعديل")
        edit_payment_btn.setIcon(qta.icon('fa5s.edit'))
        edit_payment_btn.clicked.connect(self.edit_payment)
        buttons_layout.addWidget(edit_payment_btn)

        delete_payment_btn = QPushButton("حذف")
        delete_payment_btn.setIcon(qta.icon('fa5s.trash'))
        delete_payment_btn.clicked.connect(self.delete_payment)
        buttons_layout.addWidget(delete_payment_btn)

        # زر طباعة إيصال
        print_receipt_btn = QPushButton("طباعة إيصال")
        print_receipt_btn.setIcon(qta.icon('fa5s.print'))
        print_receipt_btn.clicked.connect(self.print_payment_receipt)
        buttons_layout.addWidget(print_receipt_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # الفلاتر (في الجانب الأيسر)
        filter_layout = QHBoxLayout()
        
        # فلتر حسب طريقة الدفع
        filter_layout.addWidget(QLabel("طريقة الدفع:"))
        self.payment_method_filter_combo = QComboBox()
        self.payment_method_filter_combo.addItems(["جميع الطرق", "نقدي", "بطاقة", "أجل/دين", "شيك", "تحويل بنكي"])
        self.payment_method_filter_combo.currentTextChanged.connect(self.filter_payments_combined)
        filter_layout.addWidget(self.payment_method_filter_combo)

        # فلتر حسب السنة
        filter_layout.addWidget(QLabel("السنة:"))
        self.payment_year_filter_combo = QComboBox()
        self.payment_year_filter_combo.addItem("جميع السنوات")
        self.load_payment_years()
        self.payment_year_filter_combo.currentTextChanged.connect(self.filter_payments_combined)
        filter_layout.addWidget(self.payment_year_filter_combo)

        # شريط البحث
        filter_layout.addWidget(QLabel("البحث:"))
        self.payments_search = QLineEdit()
        self.payments_search.setPlaceholderText("ابحث في الدفعات...")
        self.payments_search.textChanged.connect(self.filter_payments_combined)
        filter_layout.addWidget(self.payments_search)

        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # البطاقات الإحصائية للدفعات
        self.create_payments_statistics_cards(layout)

        # جدول الدفعات
        self.payments_table = QTableWidget()
        self.setup_payments_table()
        layout.addWidget(self.payments_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.money-bill-wave', color='#27ae60'), "دفعات المشروع")

    # دالة إعداد جدول الدفعات
    # جدول مدفوعات الإعداد
    def setup_payments_table(self):
        headers = ["ID", "الرقم", "المبلغ المدفوع", "تاريخ الدفع", "وصف المدفوع", "طريقة الدفع", "الخصم", "المستلم"]
        self.payments_table.setColumnCount(len(headers))
        self.payments_table.setHorizontalHeaderLabels(headers)
        self.payments_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول الموحدة
        setup_table_style(self.payments_table)

        # تمكين التحديد المتعدد للصفوف
        self.payments_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.payments_table, self, "دفعات المشروع", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.payments_table.itemDoubleClicked.connect(self.on_payments_table_double_click)

    # دالة إنشاء payments_statistics_cards
    # إنشاء بطاقات إحصائيات المدفوعات
    def create_payments_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("payments_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات الإحصائية
        self.total_payments_count_label = QLabel("0")
        self.total_payments_amount_label = QLabel("0")
        self.this_month_payments_label = QLabel("0")
        self.this_year_payments_label = QLabel("0")
        self.average_payment_label = QLabel("0")

        # إنشاء البطاقات
        stats = [
            ("عدد الدفعات", self.total_payments_count_label, "#3498db"),
            ("إجمالي المبلغ", self.total_payments_amount_label, "#27ae60"),
            ("دفعات هذا الشهر", self.this_month_payments_label, "#f39c12"),
            ("دفعات هذا العام", self.this_year_payments_label, "#9b59b6"),
            ("متوسط الدفعة", self.average_payment_label, "#e74c3c"),
        ]

        # إنشاء البطاقات
        for title, label, color in stats:
            card = create_stat_card(title, label.text(), color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

        # تحميل الإحصائيات الأولية
        self.update_payments_statistics()
        
    # دالة إنشاء حاوية المعلومات الأساسية
    # إنشاء حاوية المعلومات الأساسية
    def create_basic_info_container(self, parent_layout):
        group = QGroupBox("المعلومات الأساسية")
        
        layout = QGridLayout(group)
        layout.setSpacing(15)
        
        # اسم المشروع
        layout.addWidget(QLabel("اسم المشروع:"), 0, 0)
        self.project_name_label = QLabel()
        layout.addWidget(self.project_name_label, 0, 1)

        # اسم المالك/العميل
        layout.addWidget(QLabel("اسم المالك/العميل:"), 1, 0)
        self.client_name_label = QLabel()
        layout.addWidget(self.client_name_label, 1, 1)

        # عضو فريق العمل المسؤول
        layout.addWidget(QLabel("المهندس المسؤول:"), 2, 0)
        self.engineer_name_label = QLabel()
        layout.addWidget(self.engineer_name_label, 2, 1)

        #
        view_payments_btn = QPushButton("تعديل البيانات")
        view_payments_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        view_payments_btn.clicked.connect(self.edit_project_data)
        layout.addWidget(view_payments_btn, 3, 0,2,2)
        
        parent_layout.addWidget(group)
        
    # دالة إنشاء حاوية المعلومات المالية
    # إنشاء حاوية معلومات مالية
    def create_financial_info_container(self, parent_layout):
        group = QGroupBox("المعلومات المالية")
        
        layout = QGridLayout(group)
        layout.setSpacing(15)
        
        # إجمالي قيمة المشروع
        layout.addWidget(QLabel("إجمالي قيمة المشروع:"), 0, 0)
        self.info_total_amount_label = QLabel()
        layout.addWidget(self.info_total_amount_label, 0, 1)

        # إجمالي المبلغ المدفوع
        layout.addWidget(QLabel("إجمالي المبلغ المدفوع:"), 1, 0)
        self.info_paid_amount_label = QLabel()
        layout.addWidget(self.info_paid_amount_label, 1, 1)

        # إجمالي المبلغ المتبقي
        layout.addWidget(QLabel("إجمالي المبلغ المتبقي:"), 2, 0)
        self.remaining_amount_label = QLabel()
        layout.addWidget(self.remaining_amount_label, 2, 1)
        
        # أزرار العمليات المالية
        buttons_layout = QHBoxLayout()
        
        # زر إضافة دفعة جديدة
        add_payment_btn = QPushButton("إضافة دفعة")
        add_payment_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_payment_btn.clicked.connect(self.add_payment)
        buttons_layout.addWidget(add_payment_btn)
        
        
        
        #buttons_layout.addStretch()
        layout.addLayout(buttons_layout, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)
        
    # دالة تحميل معلومات المشروع
    # تحميل معلومات المشروع
    def load_project_info(self):
        if not self.project_data:
            return
        # تحميل المعلومات الأساسية
        self.project_name_label.setText(self.project_data.get('اسم_المشروع', 'غير محدد'))

        # جلب اسم العميل من قاعدة البيانات
        client_name = self.get_client_name()
        self.client_name_label.setText(client_name)

        # جلب اسم عضو فريق العمل من قاعدة البيانات
        engineer_name = self.get_engineer_name()
        self.engineer_name_label.setText(engineer_name)

        # تحميل المعلومات المالية مباشرة من البيانات المرسلة
        self.load_financial_info_from_data()

        # تحميل معلومات التوقيت والحالة
        self.load_timing_status_info()

        # تحميل الوصف والملاحظات
        self.load_description_notes()

        # تحميل الإحصائيات
        self.load_statistics()

        # تحميل المعلومات الإضافية الجديدة
        self.load_additional_info()

        # تحميل بيانات الجداول
        self.load_all_tables_data()

        # تحميل بيانات الفلاتر
        self.load_filter_data()

        

    # دالة تحميل financial_info_from_data
    # تحميل المعلومات المالية من البيانات
    def load_financial_info_from_data(self):
        try:
            # استخراج المبالغ من البيانات المرسلة
            total_amount = self.project_data.get('المبلغ', 0)
            paid_amount = self.project_data.get('المدفوع', 0)
            remaining_amount = self.project_data.get('الباقي', 0)

            # # التحقق من وجود التسميات
            # if not hasattr(self, 'total_amount_label') or not hasattr(self, 'paid_amount_label') or not hasattr(self, 'remaining_amount_label'):
            #     return

            # تنسيق وعرض المبالغ مع التلوين
            # إجمالي قيمة المشروع - أزرق إذا كان أكبر من 0، "مبلغ غير محدد" إذا كان 0
            if total_amount and total_amount > 0:
                self.info_total_amount_label.setText(f"{total_amount:,.0f} {Currency_type}")
                self.info_total_amount_label.setObjectName("info_label")
            else:
                self.info_total_amount_label.setText("مبلغ غير محدد")
                self.info_total_amount_label.setObjectName("warning_label")

            # المبلغ المدفوع - برتقالي إذا كان 0 مع نص "لاشيء"
            if paid_amount is not None and paid_amount > 0:
                self.info_paid_amount_label.setText(f"{paid_amount:,.0f} {Currency_type}")
                self.info_paid_amount_label.setObjectName("value_label")
            else:
                self.info_paid_amount_label.setText("لاشيء")
                self.info_paid_amount_label.setObjectName("warning_label")

            # المبلغ المتبقي - أخضر إذا كان 0 مع نص "خالص"
            if remaining_amount is not None and remaining_amount > 0:
                self.remaining_amount_label.setText(f"{remaining_amount:,.0f} {Currency_type}")
                self.remaining_amount_label.setObjectName("value_label")
            elif remaining_amount == 0:
                self.remaining_amount_label.setText("خالص")
                self.remaining_amount_label.setObjectName("success_label")
            else:
                self.remaining_amount_label.setText(f"0 {Currency_type}")
                self.remaining_amount_label.setObjectName("value_label")

            # إجبار تحديث الواجهة
            if hasattr(self, 'info_total_amount_label'):
                self.info_total_amount_label.repaint()
            if hasattr(self, 'info_paid_amount_label'):
                self.info_paid_amount_label.repaint()
            if hasattr(self, 'remaining_amount_label'):
                self.remaining_amount_label.repaint()

        except Exception as e:
            print(f"خطأ في تحميل المعلومات المالية: {e}")

    # دالة تحديث بيانات المشروع
    # تحديث بيانات المشروع
    def refresh_project_data(self):
        if not self.project_id:
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب البيانات المحدثة للمشروع
            cursor.execute("""
                SELECT اسم_المشروع, المبلغ, المدفوع, الباقي, تاريخ_الإستلام,
                       تاريخ_التسليم, الحالة, وصف_المشروع, ملاحظات, معرف_العميل
                FROM المشاريع
                WHERE id = %s
            """, (self.project_id,))

            result = cursor.fetchone()
            if result:
                # تحديث بيانات المشروع
                self.project_data.update({
                    'اسم_المشروع': result[0],
                    'المبلغ': result[1],
                    'المدفوع': result[2],
                    'الباقي': result[3],
                    'تاريخ_الإستلام': result[4],
                    'تاريخ_التسليم': result[5],
                    'الحالة': result[6],
                    'وصف_المشروع': result[7],
                    'ملاحظات': result[8],
                    'معرف_العميل': result[9]
                })

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث بيانات المشروع: {e}")

    
    # دالة تحميل timing_status_info
    # تحميل معلومات حالة التوقيت
    def load_timing_status_info(self):
        start_date = self.project_data.get('تاريخ_الإستلام', '')
        end_date = self.project_data.get('تاريخ_التسليم', '')
        status = self.project_data.get('الحالة', 'غير محدد')

        self.start_date_label.setText(str(start_date) if start_date else 'غير محدد')
        self.end_date_label.setText(str(end_date) if end_date else 'غير محدد')

        # تحديث عرض الحالة حسب المتطلبات الجديدة
        status_display = self.get_project_status_display(status, start_date, end_date)
        self.project_status_label.setText(status_display['text'])
        # سيتم تطبيق النمط من خلال الدالة المركزية
                # تطبيق الستايل الموحد
        self.project_status_label.setObjectName("status_label")

    # دالة الحصول على project_status_display
    # احصل على عرض حالة المشروع
    def get_project_status_display(self, status, start_date, end_date):
        try:
            from datetime import datetime

            # إذا كانت الحالة "قيد الإنجاز"
            if status == 'قيد الإنجاز':
                if end_date:
                    try:
                        end_date_obj = datetime.strptime(str(end_date), '%Y-%m-%d')
                        today = datetime.now()
                        remaining_days = (end_date_obj - today).days

                        # حساب نسبة الإنجاز
                        completion_percentage = self.calculate_completion_percentage()

                        if remaining_days > 0:
                            return {
                                'text': f"قيد الإنجاز - {remaining_days} يوم متبقي - نسبة الإنجاز {completion_percentage}%",
                                'color': '#f39c12'  # برتقالي
                            }
                        elif remaining_days == 0:
                            return {
                                'text': f"قيد الإنجاز - ينتهي اليوم - نسبة الإنجاز {completion_percentage}%",
                                'color': '#e67e22'  # برتقالي داكن
                            }
                        else:
                            return {
                                'text': f"قيد الإنجاز - متأخر {abs(remaining_days)} يوم - نسبة الإنجاز {completion_percentage}%",
                                'color': '#e74c3c'  # أحمر
                            }
                    except:
                        return {
                            'text': f"{status} - غير محدد",
                            'color': '#7f8c8d'  # رمادي
                        }
                else:
                    completion_percentage = self.calculate_completion_percentage()
                    return {
                        'text': f"قيد الإنجاز - نسبة الإنجاز {completion_percentage}%",
                        'color': '#3498db'  # أزرق
                    }

            # لباقي الحالات - عرض الحالة + فرق الأيام بين تاريخ التسليم والاستلام
            else:
                if start_date and end_date:
                    try:
                        start_date_obj = datetime.strptime(str(start_date), '%Y-%m-%d')
                        end_date_obj = datetime.strptime(str(end_date), '%Y-%m-%d')
                        duration_days = (end_date_obj - start_date_obj).days

                        # تحديد اللون حسب الحالة
                        color = self.get_status_color_by_name(status)

                        return {
                            'text': f"{status} - مدة المشروع {duration_days} يوم",
                            'color': color
                        }
                    except:
                        return {
                            'text': f"{status}",
                            'color': self.get_status_color_by_name(status)
                        }
                else:
                    return {
                        'text': f"{status}",
                        'color': self.get_status_color_by_name(status)
                    }

        except Exception as e:
            print(f"خطأ في حساب عرض الحالة: {e}")
            return {
                'text': f"{status}",
                'color': '#7f8c8d'
            }

    # دالة الحصول على status_color_by_name
    # احصل على لون الحالة بالاسم
    def get_status_color_by_name(self, status):
        status_colors = {
            'تم التسليم': '#27ae60',      # أخضر
            'تأكيد التسليم': '#2ecc71',   # أخضر فاتح
            'منتهي': '#27ae60',           # أخضر
            'معلق': '#3498db',            # أزرق
            'متوقف': '#e74c3c',           # أحمر
            'قيد الإنجاز': '#f39c12',     # برتقالي
        }
        return status_colors.get(status, '#7f8c8d')  # رمادي افتراضي


    # دالة تحميل description_notes
    # تحميل الوصف ملاحظات
    def load_description_notes(self):
        description = self.project_data.get('وصف_المشروع', '')
        notes = self.project_data.get('ملاحظات', '')

        self.project_description.setPlainText(description)
        self.project_notes.setPlainText(notes)

    # دالة تحميل statistics
    # إحصائيات تحميل
    def load_statistics(self):
        try:
            # حساب إجمالي مبلغ المراحل
            total_phases_amount = self.get_total_phases_amount()
            self.total_phases_amount_label.setText(f"{total_phases_amount:,.0f} {Currency_type}")

            # حساب إجمالي حسابات فريق العمل
            total_engineers_amount = self.get_total_engineers_amount()
            self.total_engineers_amount_label.setText(f"{total_engineers_amount:,.0f} {Currency_type}")

            # حساب صافي ربح الشركة (إجمالي مبلغ المراحل - إجمالي حسابات فريق العمل)
            net_profit = total_phases_amount - total_engineers_amount
            self.net_profit_label.setText(f"{net_profit:,.0f} {Currency_type}")

            # حساب عدد المراحل المكتملة
            completed_phases = self.get_completed_phases_count()
            self.completed_phases_label.setText(f"{completed_phases} مرحلة")

            # حساب عدد المراحل المتأخرة
            overdue_phases = self.get_overdue_phases_count()
            self.overdue_phases_label.setText(f"{overdue_phases} مرحلة")

            # حساب عدد المراحل قيد التنفيذ
            in_progress_phases = self.get_in_progress_phases_count()
            self.in_progress_phases_label.setText(f"{in_progress_phases} مرحلة")

        except Exception as e:
            print(f"خطأ في تحميل الإحصائيات: {e}")

    # دالة تحميل additional_info
    # تحميل معلومات إضافية
    def load_additional_info(self):
        try:
            # تحميل آخر دفعة مضافة
            self.load_last_payment_info()

            # تحميل عدد المراحل غير المدرجة
            self.load_unposted_phases_count()

            # تحميل عدد الموظفين غير المدرجين
            self.load_unposted_employees_count()

            # تحميل عدد المهام المتأخرة
            self.load_overdue_tasks_count()

        except Exception as e:
            print(f"خطأ في تحميل المعلومات الإضافية: {e}")

    # دالة تحميل last_payment_info
    # تحميل معلومات الدفع الأخيرة
    def load_last_payment_info(self):
        try:
            if not self.project_id:
                self.last_payment_label.setText("لا توجد دفعات")
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT المبلغ_المدفوع, تاريخ_الدفع, وصف_المدفوع
                FROM المشاريع_المدفوعات
                WHERE معرف_المشروع = %s
                ORDER BY تاريخ_الدفع DESC, id DESC
                LIMIT 1
            """, (self.project_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                amount, date, description = result
                date_str = str(date) if date else "غير محدد"
                desc_str = description if description else "دفعة"
                self.last_payment_label.setText(f"{amount:,.0f} {Currency_type} | {date_str} | {desc_str}")
            else:
                self.last_payment_label.setText("لا توجد دفعات")

        except Exception as e:
            print(f"خطأ في جلب آخر دفعة: {e}")
            self.last_payment_label.setText("خطأ في التحميل")

    # دالة تحميل unposted_phases_count
    # تحميل المراحل غير المعقولة
    def load_unposted_phases_count(self):
        try:
            if not self.project_id:
                self.unposted_phases_label.setText("0 مرحلة")
                if hasattr(self, 'insert_phases_btn'):
                    self.insert_phases_btn.setVisible(False)
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(الإجمالي), 0)
                FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s AND حالة_المبلغ = 'غير مدرج'
            """, (self.project_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                count, total_amount = result
                if count > 0:
                    self.unposted_phases_label.setText(f"{count} مرحلة | {total_amount:,.0f} {Currency_type}")
                    if hasattr(self, 'insert_phases_btn'):
                        self.insert_phases_btn.setVisible(True)
                        self.insert_phases_btn.setEnabled(True)
                else:
                    self.unposted_phases_label.setText("جميع المراحل مدرجة ✓")
                    # سيتم تطبيق النمط من خلال الدالة المركزية
                    if hasattr(self, 'insert_phases_btn'):
                        self.insert_phases_btn.setVisible(False)
            else:
                self.unposted_phases_label.setText("0 مرحلة")
                if hasattr(self, 'insert_phases_btn'):
                    self.insert_phases_btn.setVisible(False)

        except Exception as e:
            print(f"خطأ في جلب المراحل غير المدرجة: {e}")
            self.unposted_phases_label.setText("خطأ في التحميل")

    # دالة تحميل unposted_employees_count
    # تحميل عدد الموظفين غير المعتمدين
    def load_unposted_employees_count(self):
        try:
            if not self.project_id:
                self.unposted_employees_label.setText("0 موظف")
                if hasattr(self, 'insert_employees_btn'):
                    self.insert_employees_btn.setVisible(False)
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_الموظف), COALESCE(SUM(مبلغ_الموظف), 0)
                FROM المشاريع_مهام_الفريق
                WHERE معرف_القسم = %s AND حالة_مبلغ_الموظف = 'غير مدرج'
            """, (self.project_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                count, total_amount = result
                if count > 0:
                    self.unposted_employees_label.setText(f"{count} موظف | {total_amount:,.0f} {Currency_type}")
                    if hasattr(self, 'insert_employees_btn'):
                        self.insert_employees_btn.setVisible(True)
                        self.insert_employees_btn.setEnabled(True)
                else:
                    self.unposted_employees_label.setText("جميع الأرصدة مدرجة ✓")
                    # سيتم تطبيق النمط من خلال الدالة المركزية
                    if hasattr(self, 'insert_employees_btn'):
                        self.insert_employees_btn.setVisible(False)
            else:
                self.unposted_employees_label.setText("0 موظف")
                if hasattr(self, 'insert_employees_btn'):
                    self.insert_employees_btn.setVisible(False)

        except Exception as e:
            print(f"خطأ في جلب الموظفين غير المدرجين: {e}")
            self.unposted_employees_label.setText("خطأ في التحميل")

    # دالة تحميل overdue_tasks_count
    # تحميل المهام المتأخرة
    def load_overdue_tasks_count(self):
        try:
            if not self.project_id:
                self.overdue_tasks_label.setText("0 مهمة")
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            from datetime import datetime
            today = datetime.now().date()

            cursor.execute("""
                SELECT COUNT(*)
                FROM المشاريع_مهام_الفريق
                WHERE معرف_القسم = %s
                AND تاريخ_الانتهاء < %s
                AND الحالة NOT IN ('منتهي', 'متوقف')
            """, (self.project_id, today))

            result = cursor.fetchone()
            conn.close()

            if result:
                count = result[0]
                if count > 0:
                    self.overdue_tasks_label.setText(f"{count} مهمة متأخرة")
                    self.overdue_tasks_label.setObjectName("danger_label")
                else:
                    self.overdue_tasks_label.setText("لا توجد مهام متأخرة")
                    self.overdue_tasks_label.setObjectName("success_label")
            else:
                self.overdue_tasks_label.setText("0 مهمة")

        except Exception as e:
            print(f"خطأ في جلب المهام المتأخرة: {e}")
            self.overdue_tasks_label.setText("خطأ في التحميل")

    # دالة حساب completion_percentage
    # حساب نسبة الانتهاء
    def calculate_completion_percentage(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # حساب إجمالي المراحل
            cursor.execute("""
                SELECT COUNT(*) FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة IN (
                    SELECT id FROM المشاريع_المراحل WHERE معرف_القسم = %s
                )
            """, (self.project_id,))
            total_phases = cursor.fetchone()[0]

            if total_phases == 0:
                return 0

            # حساب المراحل المكتملة
            cursor.execute("""
                SELECT COUNT(*) FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة IN (
                    SELECT id FROM المشاريع_المراحل WHERE معرف_المشروع = %s
                ) AND الحالة = 'منتهي'
            """, (self.project_id,))
            completed_phases = cursor.fetchone()[0]

            conn.close()

            return round((completed_phases / total_phases) * 100, 1)

        except Exception as e:
            print(f"خطأ في حساب نسبة الإنجاز: {e}")
            return 0

    # دالة الحصول على total_phases_count
    # احصل على إجمالي عدد المراحل
    def get_total_phases_count(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM المشاريع_المراحل WHERE معرف_المشروع = %s", (self.project_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result else 0

        except Exception as e:
            print(f"خطأ في جلب عدد المراحل: {e}")
            return 0

    # دالة الحصول على total_engineers_amount
    # احصل على إجمالي مبلغ المهندسين
    def get_total_engineers_amount(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(مبلغ_الموظف) FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة IN (
                    SELECT id FROM المشاريع_المراحل WHERE معرف_المشروع = %s
                )
            """, (self.project_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result and result[0] else 0

        except Exception as e:
            print(f"خطأ في جلب مبالغ فريق العمل: {e}")
            return 0

    # دالة الحصول على total_phases_amount
    # احصل على إجمالي مراحل المبلغ
    def get_total_phases_amount(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(الإجمالي) FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s
            """, (self.project_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result and result[0] else 0

        except Exception as e:
            print(f"خطأ في جلب إجمالي مبلغ المراحل: {e}")
            return 0

    # دالة الحصول على completed_phases_count
    # احصل على عدد المراحل المكتملة
    def get_completed_phases_count(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_المرحلة) FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة IN (
                    SELECT id FROM المشاريع_المراحل WHERE معرف_المشروع = %s
                ) AND الحالة = 'منتهي'
            """, (self.project_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result and result[0] else 0

        except Exception as e:
            print(f"خطأ في جلب عدد المراحل المكتملة: {e}")
            return 0

    # دالة الحصول على overdue_phases_count
    # الحصول على مراحل المراحل المتأخرة
    def get_overdue_phases_count(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # المراحل المتأخرة: التي تجاوزت تاريخ الانتهاء وليست مكتملة
            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_المرحلة) FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة IN (
                    SELECT id FROM المشاريع_المراحل WHERE معرف_المشروع = %s
                ) AND تاريخ_الانتهاء < CURDATE()
                AND الحالة NOT IN ('منتهي')
            """, (self.project_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result and result[0] else 0

        except Exception as e:
            print(f"خطأ في جلب عدد المراحل المتأخرة: {e}")
            return 0

    # دالة الحصول على in_progress_phases_count
    # احصل على مراحل التقدم
    def get_in_progress_phases_count(self):
        try:
            if not self.project_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(DISTINCT معرف_المرحلة) FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة IN (
                    SELECT id FROM المشاريع_المراحل WHERE معرف_المشروع = %s
                ) AND الحالة = 'قيد التنفيذ'
            """, (self.project_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result and result[0] else 0

        except Exception as e:
            print(f"خطأ في جلب عدد المراحل قيد التنفيذ: {e}")
            return 0



    # دالة تحميل all_tables_data
    # تحميل جميع بيانات الجداول
    def load_all_tables_data(self):
        try:
            self.load_phases_data()
            self.load_payments_data()
            self.load_engineers_tasks_data()
            self.load_timeline_data()

            # تحميل بيانات الملفات والمرفقات (لجميع أنواع المشاريع)
            self.load_attachments_data()

            if self.project_type == "المقاولات":
                self.load_expenses_data()
                self.load_custody_data()
                self.load_custody_payments_data()
                self.load_contractors_data()
                self.load_workers_data()
                self.load_losses_data()
                self.load_returns_data()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الجداول: {e}")

    # دالة تحميل بيانات المراحل
    # تحميل بيانات المراحل
    def load_phases_data(self):
        try:
            if not self.project_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_المرحلة, وصف_المرحلة, الوحدة, الكمية, السعر, الإجمالي, ملاحظات, حالة_المبلغ
                FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s
                ORDER BY id
            """, (self.project_id,))

            rows = cursor.fetchall()
            self.phases_table.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                # إضافة باقي البيانات مع تعديل الفهارس
                for col_idx, data in enumerate(row_data):
                    if col_idx == 0:  # عمود ID (مخفي)
                        item = QTableWidgetItem(str(data) if data is not None else "")
                        self.phases_table.setItem(row_idx, 0, item)
                    else:  # باقي الأعمدة مع إزاحة بسبب عمود الرقم التلقائي
                        item = QTableWidgetItem(str(data) if data is not None else "")
                        # تطبيق تنسيق الألوان لعمود حالة المبلغ
                        if col_idx == 8:  # عمود حالة المبلغ (الفهرس الأصلي 8)
                            self.apply_amount_status_color(item, str(data) if data is not None else "")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        self.phases_table.setItem(row_idx, col_idx + 1, item)

                # إضافة أزرار الإجراءات
                #self.add_phase_action_buttons(row_idx)

            # إضافة الأرقام التلقائية
            self.add_auto_numbers_to_table(self.phases_table)

            # تحديث قائمة الفلترة
            self.update_phases_filter_combo()

            # تحديث إحصائيات المراحل
            self.update_phases_statistics()

            # تحديث الأنماط للعناصر الجديدة
            self.refresh_styles()

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات المراحل: {e}")

    # دالة تعديل phase_from_button
    # تحرير المرحلة من الزر
    def edit_phase_from_button(self, row):
        # الحصول على معرف المرحلة من العمود المخفي
        phase_id_item = self.phases_table.item(row, 0)
        if not phase_id_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المرحلة")
            return

        phase_id = int(phase_id_item.text())
        dialog = PhaseDialog(self, project_id=self.project_id, phase_id=phase_id, project_type=self.project_type)
        if dialog.exec() == QDialog.Accepted:
            self.load_phases_data()
            self.update_phases_statistics()

    # دالة حذف phase_from_button
    # حذف المرحلة من الزر
    def delete_phase_from_button(self, row):
        # الحصول على معرف المرحلة واسمها
        phase_id_item = self.phases_table.item(row, 0)
        phase_name_item = self.phases_table.item(row, 2)

        if not phase_id_item or not phase_name_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات المرحلة")
            return

        phase_id = int(phase_id_item.text())
        phase_name = phase_name_item.text()

        # تأكيد الحذف
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف المرحلة '{phase_name}'؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # حذف المرحلة
                cursor.execute("DELETE FROM المشاريع_المراحل WHERE id = %s", (phase_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم حذف المرحلة '{phase_name}' بنجاح")
                self.load_phases_data()
                self.update_phases_statistics()

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المرحلة: {str(e)}")

    # دالة تصفية phases_by_name
    # مراحل التصفية بالاسم
    def filter_phases_by_name(self):
        self.filter_phases_combined()

    # دالة تحديث phases_filter_combo
    # تحديث مراحل تصفية التحرير والسرد
    def update_phases_filter_combo(self):
        try:
            if not hasattr(self, 'phases_filter_combo'):
                return

            # التحقق من وجود الجدول
            if not hasattr(self, 'phases_table') or self.phases_table is None:
                return

            # حفظ الاختيار الحالي
            current_selection = self.phases_filter_combo.currentText()

            # مسح القائمة وإضافة الخيار الافتراضي
            self.phases_filter_combo.clear()
            self.phases_filter_combo.addItem("جميع المراحل")

            # جمع أسماء المراحل الفريدة من الجدول
            phase_names = set()
            for row in range(self.phases_table.rowCount()):
                phase_name_item = self.phases_table.item(row, 2)  # عمود اسم المرحلة
                if phase_name_item and phase_name_item.text().strip():
                    phase_names.add(phase_name_item.text().strip())

            # إضافة أسماء المراحل مرتبة
            for phase_name in sorted(phase_names):
                self.phases_filter_combo.addItem(phase_name)

            # استعادة الاختيار السابق إن أمكن
            index = self.phases_filter_combo.findText(current_selection)
            if index >= 0:
                self.phases_filter_combo.setCurrentIndex(index)

        except Exception as e:
            print(f"خطأ في تحديث قائمة فلترة المراحل: {e}")

    # دالة تحميل بيانات مهام المهندسين
    # تحميل بيانات مهام المهندسين
    def load_engineers_tasks_data(self):
        try:
            if not self.project_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # استعلام محدث للجدول الموحد مع الفلترة المباشرة بمعرف المشروع
            cursor.execute("""
                SELECT
                    مم.id,
                    م.اسم_الموظف,
                    COALESCE(م.التصنيف, 'موظف') as نوع_العضو,
                    CASE
                        WHEN COALESCE(مم.نوع_دور_المهمة, 'دور_عام') = 'ربط_بمرحلة'
                        THEN COALESCE(مر.اسم_المرحلة, مم.عنوان_المهمة, 'غير محدد')
                        ELSE COALESCE(مم.عنوان_المهمة, 'دور عام')
                    END as اسم_المهمة,
                    CASE
                        WHEN COALESCE(مم.نوع_دور_المهمة, 'دور_عام') = 'ربط_بمرحلة'
                        THEN COALESCE(مر.وصف_المرحلة, مم.وصف_المهمة, '')
                        ELSE COALESCE(مم.وصف_المهمة, '')
                    END as وصف_المهمة,
                    مم.نسبة_الموظف,
                    مم.مبلغ_الموظف,
                    مم.حالة_مبلغ_الموظف
                FROM المشاريع_مهام_الفريق مم
                JOIN الموظفين م ON مم.معرف_الموظف = م.id
                LEFT JOIN المشاريع_المراحل مر ON مم.معرف_المرحلة = مر.id
                WHERE مم.معرف_المشروع = %s
                AND مم.نوع_المهمة IN ('مهمة مشروع', 'مهمة مقاولات')
                ORDER BY مم.id
            """, (self.project_id,))

            rows = cursor.fetchall()
            self.engineers_tasks_table.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data):
                    if col_idx == 0:  # عمود ID (مخفي)
                        item = QTableWidgetItem(str(data) if data is not None else "")
                        self.engineers_tasks_table.setItem(row_idx, 0, item)
                    else:  # باقي الأعمدة مع إزاحة بسبب عمود الرقم التلقائي
                        item = QTableWidgetItem(str(data) if data is not None else "")

                        # محاذاة الأرقام في المنتصف
                        if col_idx in [5, 6]:  # أعمدة الأرقام (النسبة، المبلغ)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        # تطبيق تنسيق الألوان لعمود حالة المبلغ
                        if col_idx == 7:  # عمود حالة مبلغ الموظف
                            self.apply_amount_status_color(item, str(data) if data is not None else "")

                        self.engineers_tasks_table.setItem(row_idx, col_idx + 1, item)

            # إضافة الأرقام التلقائية
            self.add_auto_numbers_to_table(self.engineers_tasks_table)

            # تحديث فلاتر أعضاء فريق العمل
            self.update_engineers_filters()

            # تحديث الإحصائيات
            self.update_team_statistics()

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات فريق العمل: {e}")

    # دالة تحميل بيانات الجدول الزمني
    # تحميل بيانات الجدول الزمني
    def load_timeline_data(self):
        try:
            if not self.project_id or not hasattr(self, 'timeline_table'):
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    مم.id,
                    CONCAT(م.اسم_الموظف,
                           CASE
                               WHEN م.الوظيفة IS NOT NULL AND م.الوظيفة != ''
                               THEN CONCAT(' - ', م.الوظيفة)
                               ELSE ''
                           END) as المهندس_الكامل,
                    CASE
                        WHEN COALESCE(مم.نوع_دور_المهمة, 'دور_عام') = 'ربط_بمرحلة'
                        THEN COALESCE(مر.اسم_المرحلة, مم.عنوان_المهمة, 'غير محدد')
                        ELSE COALESCE(مم.عنوان_المهمة, 'دور عام')
                    END as اسم_المهمة,
                    CASE
                        WHEN COALESCE(مم.نوع_دور_المهمة, 'دور_عام') = 'ربط_بمرحلة'
                        THEN COALESCE(مر.وصف_المرحلة, مم.وصف_المهمة, '')
                        ELSE COALESCE(مم.وصف_المهمة, '')
                    END as وصف_المهمة,
                    مم.تاريخ_البدء,
                    CASE
                        WHEN مم.تاريخ_البدء = مم.تاريخ_الانتهاء THEN 'غير محدد'
                        ELSE مم.تاريخ_الانتهاء
                    END as تاريخ_الإنتهاء_معدل,
                    CASE
                        WHEN مم.الحالة = 'قيد التنفيذ' AND مم.تاريخ_الانتهاء != مم.تاريخ_البدء THEN
                            CASE
                                WHEN DATEDIFF(مم.تاريخ_الانتهاء, CURDATE()) >= 0
                                THEN CONCAT(DATEDIFF(مم.تاريخ_الانتهاء, CURDATE()), ' يوم متبقي')
                                ELSE CONCAT(ABS(DATEDIFF(مم.تاريخ_الانتهاء, CURDATE())), ' يوم تأخير')
                            END
                        ELSE مم.الحالة
                    END as حالة_معدلة
                FROM المشاريع_مهام_الفريق مم
                JOIN الموظفين م ON مم.معرف_الموظف = م.id
                LEFT JOIN المشاريع_المراحل مر ON مم.معرف_المرحلة = مر.id
                WHERE مم.معرف_المشروع = %s
                ORDER BY مم.id
            """, (self.project_id,))

            rows = cursor.fetchall()
            self.timeline_table.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data):
                    if col_idx == 0:  # عمود ID (مخفي)
                        item = QTableWidgetItem(str(data) if data is not None else "")
                        self.timeline_table.setItem(row_idx, 0, item)
                    else:  # باقي الأعمدة مع إزاحة بسبب عمود الرقم التلقائي
                        # تنسيق خاص للتواريخ
                        if col_idx in [4, 5] and data:  # أعمدة التواريخ (تحديث الفهارس)
                            formatted_date = str(data) if data else ""
                            item = QTableWidgetItem(formatted_date)
                        else:
                            item = QTableWidgetItem(str(data) if data is not None else "")

                        # محاذاة التواريخ في المنتصف
                        if col_idx in [4, 5]:  # أعمدة التواريخ (تحديث الفهارس)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        # تلوين حالة المهمة المعدلة
                        if col_idx == 6:  # عمود حالة المهمة المعدلة (تحديث الفهرس)
                            if "مكتملة" in str(data):
                                item.setForeground(QColor(46, 204, 113, 50))  # أخضر فاتح
                            elif "قيد التنفيذ" in str(data) or "متبقي" in str(data):
                                item.setForeground(QColor(52, 152, 219, 50))  # أزرق فاتح
                            elif "تأخير" in str(data):
                                item.setForeground(QColor(231, 76, 60, 50))   # أحمر فاتح للتأخير
                            elif "متوقف" in str(data):
                                item.setForeground(QColor(230, 126, 34, 50))  # برتقالي للمتوقف
                            elif "لم يبدأ" in str(data):
                                item.setForeground(QColor(149, 165, 166, 50)) # رمادي فاتح

                        self.timeline_table.setItem(row_idx, col_idx + 1, item)

            # إضافة الأرقام التلقائية
            self.add_auto_numbers_to_table(self.timeline_table)

            # تحديث فلتر أعضاء الفريق
            self.update_timeline_member_filter()

            # تحديث إحصائيات الجدول الزمني
            self.update_timeline_statistics()

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الجدول الزمني: {e}")

    # دالة معالجة تغيير التاب
    # في علامة التبويب تغيرت
    def on_tab_changed(self, index):
        try:
            # تحديث العنوان الرئيسي
            self.update_title()
            
            # الحصول على اسم التاب الحالي
            tab_text = self.tab_widget.tabText(index)

            # تحديث البيانات حسب التاب المحدد
            if "معلومات المشروع" in tab_text:
                self.load_project_info()
                self.load_additional_info()  # تحديث المعلومات الإضافية
            elif "دفعات المشروع" in tab_text:
                self.load_payments_data()
                self.update_payments_statistics()
            elif "مراحل المشروع" in tab_text:
                self.load_phases_data()
                self.update_phases_statistics()
            elif "فريق العمل" in tab_text:
                self.load_engineers_tasks_data()
            elif "الجدول الزمني" in tab_text:
                self.load_timeline_data()
                self.update_timeline_statistics()
            elif "الملفات والمرفقات" in tab_text:
                self.load_attachments_data()
                self.update_attachments_statistics()
            elif "المصروفات" in tab_text:
                self.load_expenses_data()
            elif "العهد المالية" in tab_text:
                self.load_custody_data()
            elif "دفعات العهد" in tab_text:
                self.load_custody_payments_data()
            elif "المقاولين" in tab_text:
                self.load_contractors_data()
            elif "العمال" in tab_text:
                self.load_workers_data()
            elif "الخسائر" in tab_text:
                self.load_losses_data()
            elif "المردودات" in tab_text:
                self.load_returns_data()

            # تحديث الإحصائيات عند تغيير أي تاب
            self.load_statistics()

            # تمديد أعمدة الجداول بعرض النافذة
            self.extend_table_columns()

        except Exception as e:
            print(f"خطأ في تحديث بيانات التاب: {e}")

    # دالة تمديد table_columns
    # تمديد أعمدة الجدول
    def extend_table_columns(self):
        try:
            # قائمة الجداول المراد تمديد أعمدتها
            tables = [
                self.phases_table,
                self.payments_table,
                self.engineers_tasks_table,
                self.timeline_table,
                self.attachments_table
            ]

            # إضافة جداول المقاولات إذا كانت موجودة
            if hasattr(self, 'expenses_table'):
                tables.append(self.expenses_table)
            if hasattr(self, 'custody_table'):
                tables.append(self.custody_table)
            if hasattr(self, 'custody_payments_table'):
                tables.append(self.custody_payments_table)
            if hasattr(self, 'contractors_table'):
                tables.append(self.contractors_table)
            if hasattr(self, 'workers_table'):
                tables.append(self.workers_table)
            if hasattr(self, 'losses_table'):
                tables.append(self.losses_table)
            if hasattr(self, 'returns_table'):
                tables.append(self.returns_table)

            for table in tables:
                if table and hasattr(table, 'horizontalHeader'):
                    # تمديد الأعمدة لتملأ عرض الجدول
                    header = table.horizontalHeader()
                    header.setStretchLastSection(True)
                    header.setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
            print(f"خطأ في تمديد أعمدة الجداول: {e}")

    # دالة تحميل expenses_data
    # تحميل بيانات النفقات
    def load_expenses_data(self):
        try:
            if not self.project_id or not hasattr(self, 'expenses_table'):
                return
            # تنفيذ أساسي - يمكن تطويره لاحقاً
            self.expenses_table.setRowCount(0)
        except Exception as e:
            print(f"خطأ في تحميل بيانات المصروفات: {e}")

    # دالة تحميل custody_data
    # تحميل بيانات الحضانة
    def load_custody_data(self):
        try:
            if not self.project_id or not hasattr(self, 'custody_table'):
                return
            # تنفيذ أساسي - يمكن تطويره لاحقاً
            self.custody_table.setRowCount(0)
        except Exception as e:
            print(f"خطأ في تحميل بيانات العهد المالية: {e}")

    # دالة تحميل custody_payments_data
    # تحميل بيانات مدفوعات الحضانة
    def load_custody_payments_data(self):
        try:
            if not self.project_id or not hasattr(self, 'custody_payments_table'):
                return
            # تنفيذ أساسي - يمكن تطويره لاحقاً
            self.custody_payments_table.setRowCount(0)
        except Exception as e:
            print(f"خطأ في تحميل بيانات دفعات العهد: {e}")

    # دالة تحميل contractors_data
    # تحميل بيانات المقاولين
    def load_contractors_data(self):
        try:
            if not self.project_id or not hasattr(self, 'contractors_table'):
                return
            # تنفيذ أساسي - يمكن تطويره لاحقاً
            self.contractors_table.setRowCount(0)
        except Exception as e:
            print(f"خطأ في تحميل بيانات المقاولين: {e}")

    # دالة تحميل workers_data
    # تحميل بيانات العمال
    def load_workers_data(self):
        try:
            if not self.project_id or not hasattr(self, 'workers_table'):
                return
            # تنفيذ أساسي - يمكن تطويره لاحقاً
            self.workers_table.setRowCount(0)
        except Exception as e:
            print(f"خطأ في تحميل بيانات العمال: {e}")

    # دالة تحميل losses_data
    # تحميل بيانات الخسائر
    def load_losses_data(self):
        try:
            if not self.project_id or not hasattr(self, 'losses_table'):
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب بيانات الخسائر
            cursor.execute("""
                SELECT id, وصف_المصروف, المبلغ, تاريخ_المصروف, المسؤول,
                       متحمل_الخسائر, طريقة_الدفع, ملاحظات
                FROM المقاولات_مصروفات_العهد
                WHERE معرف_المشروع = %s AND نوع_المصروف = 'خسائر'
                ORDER BY تاريخ_المصروف DESC
            """, (self.project_id,))

            losses = cursor.fetchall()
            self.losses_table.setRowCount(len(losses))

            for row, loss in enumerate(losses):
                for col, value in enumerate(loss):
                    if value is not None:
                        if col == 2:  # عمود المبلغ
                            item = QTableWidgetItem(f"{value:,.2f}")
                        elif col == 3:  # عمود التاريخ
                            item = QTableWidgetItem(str(value))
                        else:
                            item = QTableWidgetItem(str(value))
                        self.losses_table.setItem(row, col, item)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الخسائر: {e}")

    # دالة تحميل returns_data
    # تحميل البيانات إرجاع البيانات
    def load_returns_data(self):
        try:
            if not self.project_id or not hasattr(self, 'returns_table'):
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب بيانات المردودات
            cursor.execute("""
                SELECT مع.id, مع.وصف_المصروف, مع.المبلغ, مع.تاريخ_المصروف,
                       مع.المسؤول, ع.وصف_العهدة, مع.طريقة_الدفع, مع.ملاحظات
                FROM المقاولات_مصروفات_العهد مع
                LEFT JOIN المقاولات_العهد ع ON مع.معرف_العهدة_المردودة = ع.id
                WHERE مع.معرف_المشروع = %s AND مع.نوع_المصروف = 'مردودات'
                ORDER BY مع.تاريخ_المصروف DESC
            """, (self.project_id,))

            returns = cursor.fetchall()
            self.returns_table.setRowCount(len(returns))

            for row, return_item in enumerate(returns):
                for col, value in enumerate(return_item):
                    if value is not None:
                        if col == 2:  # عمود المبلغ
                            item = QTableWidgetItem(f"{value:,.2f}")
                        elif col == 3:  # عمود التاريخ
                            item = QTableWidgetItem(str(value))
                        else:
                            item = QTableWidgetItem(str(value))
                        self.returns_table.setItem(row, col, item)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات المردودات: {e}")

    # دالة تحميل بيانات المرفقات
    # تحميل بيانات المرفقات
    def load_attachments_data(self):
        try:
            import os

            if not self.project_id:
                return

            # مسار مجلد المرفقات
            attachments_dir = os.path.join(os.getcwd(), "attachments", f"project_{self.project_id}")

            if not os.path.exists(attachments_dir):
                return

            # مسح الجدول
            self.attachments_table.setRowCount(0)

            # قراءة الملفات من المجلد
            for file_name in os.listdir(attachments_dir):
                file_path = os.path.join(attachments_dir, file_name)

                if os.path.isfile(file_path):
                    # الحصول على معلومات الملف
                    file_size = os.path.getsize(file_path)
                    file_extension = os.path.splitext(file_name)[1].lower()
                    file_type = self.get_file_type(file_extension)

                    # إضافة الملف إلى الجدول
                    self.add_attachment_to_table(
                        file_name,
                        file_type,
                        f"ملف {file_type}",  # وصف افتراضي
                        file_path,
                        file_size
                    )

            # تحديث فلتر أنواع الملفات
            self.update_attachments_type_filter()

            # تحديث إحصائيات الملفات
            self.update_attachments_statistics()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الملفات: {e}")
        
    # دالة الحصول على client_name
    # احصل على اسم العميل
    def get_client_name(self):
        try:
            if not self.client_id:
                return "غير محدد"
                
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r, 
                database="project_manager_V2"
            )
            cursor = conn.cursor()
            
            cursor.execute("SELECT اسم_العميل FROM العملاء WHERE id = %s", (self.client_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else "غير محدد"
            
        except Exception as e:
            print(f"خطأ في جلب اسم العميل: {e}")
            return "غير محدد"
            
    # دالة الحصول على engineer_name
    # احصل على اسم المهندس
    def get_engineer_name(self):
        try:
            engineer_id = self.project_data.get('معرف_الموظف')
            if not engineer_id:
                return "غير محدد"

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب اسم الموظف والوظيفة معاً
            cursor.execute("SELECT اسم_الموظف, الوظيفة FROM الموظفين WHERE id = %s", (engineer_id,))
            result = cursor.fetchone()

            conn.close()

            if result:
                employee_name, job_title = result
                # تنسيق العرض: اسم الموظف - الوظيفة
                if job_title and job_title.strip():
                    return f"{employee_name} - {job_title}"
                else:
                    return employee_name
            else:
                return "غير محدد"

        except Exception as e:
            print(f"خطأ في جلب اسم عضو فريق العمل: {e}")
            return "غير محدد"
            
    # دالة إنشاء حاوية حالة التوقيت
    # إنشاء حاوية حالة توقيت
    def create_timing_status_container(self, parent_layout):
        group = QGroupBox("معلومات التوقيت والحالة")

        layout = QGridLayout(group)
        layout.setSpacing(15)

        # تاريخ الاستلام
        layout.addWidget(QLabel("تاريخ الاستلام:"), 0, 0)
        self.start_date_label = QLabel()
        layout.addWidget(self.start_date_label, 0, 1)

        # تاريخ التسليم المتوقع
        layout.addWidget(QLabel("تاريخ التسليم المتوقع:"), 1, 0)
        self.end_date_label = QLabel()
        layout.addWidget(self.end_date_label, 1, 1)

        # # الوقت المتبقي
        # layout.addWidget(QLabel("الوقت المتبقي:"), 2, 0)
        # self.remaining_time_label = QLabel()

        # layout.addWidget(self.remaining_time_label, 2, 1)

        # # نسبة الإنجاز
        # layout.addWidget(QLabel("نسبة الإنجاز:"), 0, 2)
        # self.completion_percentage_label = QLabel()

        # layout.addWidget(self.completion_percentage_label, 0, 3)

        # حالة المشروع الحالية
        layout.addWidget(QLabel("حالة المشروع:"), 2, 0)
        self.project_status_label = QLabel()
        layout.addWidget(self.project_status_label, 2, 1)

        # زر تحرير حالة المشروع
        edit_status_btn = QPushButton("تحرير حالة المشروع")
        edit_status_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        edit_status_btn.clicked.connect(self.edit_project_status)
        layout.addWidget(edit_status_btn, 3, 0, 2, 2)

        parent_layout.addWidget(group)

    # دالة إنشاء حاوية الوصف
    # إنشاء الوصف حاوية
    def create_description_container(self, parent_layout):
        group = QGroupBox("الوصف والملاحظات")

        layout = QHBoxLayout(group)
        #layout.setSpacing(5)

        # وصف المشروع
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("وصف المشروع:"))
        self.project_description = QTextEdit()
        #self.project_description.setMaximumHeight(100)
        desc_layout.addWidget(self.project_description)
        layout.addLayout(desc_layout)

        # ملاحظات
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("الملاحظات:"))
        self.project_notes = QTextEdit()
        #self.project_notes.setMaximumHeight(100)
        notes_layout.addWidget(self.project_notes)
        layout.addLayout(notes_layout)

        parent_layout.addWidget(group)

    # دالة إنشاء حاوية المعلومات الإضافية
    # إنشاء حاوية معلومات إضافية
    def create_additional_info_container(self, parent_layout):
        group = QGroupBox("معلومات إضافية")

        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 25, 20, 20)

        # صف آخر دفعة مضافة
        self.create_info_row(
            layout,
            "آخر دفعة مضافة",
            "last_payment_label",
            "لا توجد دفعات",
            "#e8f5e8",  # خلفية خضراء فاتحة
            "#27ae60"   # نص أخضر
        )

        # صف المراحل غير المدرجة
        self.create_info_row_with_button(
            layout,
            "المراحل غير المدرجة",
            "unposted_phases_label",
            "0 مرحلة",
            "#fdf2e9",  # خلفية برتقالية فاتحة
            "#e67e22",  # نص برتقالي
            "insert_phases_btn",
            "إدراج جميع المراحل",
            'fa5s.coins',
            "#8e44ad",
            self.insert_all_phase_amounts
        )

        # صف الموظفين غير المدرجين
        self.create_info_row_with_button(
            layout,
            "الموظفين غير المدرجين",
            "unposted_employees_label",
            "0 موظف",
            "#e3f2fd",  # خلفية زرقاء فاتحة
            "#2196f3",  # نص أزرق
            "insert_employees_btn",
            "إدراج جميع الأرصدة",
            'fa5s.user-check',
            "#3498db",
            self.insert_all_employee_transactions
        )

        # صف المهام المتأخرة
        self.create_info_row(
            layout,
            "المهام المتأخرة",
            "overdue_tasks_label",
            "0 مهمة",
            "#ffebee",  # خلفية حمراء فاتحة
            "#e74c3c"   # نص أحمر
        )

        parent_layout.addWidget(group)

    # دالة إنشاء info_row
    # إنشاء صف المعلومات
    def create_info_row(self, parent_layout, title, label_attr, default_text, bg_color, text_color):
        # إنشاء حاوية للصف
        row_widget = QWidget()
        row_widget.setObjectName("info_card")

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(15, 10, 15, 10)

        # عنوان الصف
        title_label = QLabel(f"{title}:")
        title_label.setObjectName("title")
        row_layout.addWidget(title_label)

        # فاصل بصري
        separator = QLabel("|")
        separator.setObjectName("separator_label")
        row_layout.addWidget(separator)

        # تسمية المعلومات
        info_label = QLabel(default_text)
        info_label.setObjectName("value_label")
        setattr(self, label_attr, info_label)
        row_layout.addWidget(info_label)

        row_layout.addStretch()
        parent_layout.addWidget(row_widget)

    # إنشاء صف معلومات مع الزر
    def create_info_row_with_button(self, parent_layout, title, label_attr, default_text,
                                   bg_color, text_color, btn_attr, btn_text, btn_icon,
                                   btn_color, btn_callback):
        """إنشاء صف معلومات مع زر إجراء"""
        # إنشاء حاوية للصف
        row_widget = QWidget()
        row_widget.setObjectName("info_card")

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(15, 10, 15, 10)

        # عنوان الصف
        title_label = QLabel(f"{title}:")
        title_label.setObjectName("title")
        row_layout.addWidget(title_label)

        # فاصل بصري
        separator = QLabel("|")
        separator.setObjectName("separator_label")
        row_layout.addWidget(separator)

        # تسمية المعلومات
        info_label = QLabel(default_text)
        info_label.setObjectName("value_label")
        setattr(self, label_attr, info_label)
        row_layout.addWidget(info_label)

        row_layout.addStretch()

        # زر الإجراء
        action_btn = QPushButton(btn_text)
        action_btn.setIcon(qta.icon(btn_icon, color='white'))
        action_btn.setObjectName("edit_button")
        action_btn.clicked.connect(btn_callback)
        setattr(self, btn_attr, action_btn)
        row_layout.addWidget(action_btn)

        parent_layout.addWidget(row_widget)



    # دالة إنشاء حاوية الإحصائيات
    # إنشاء حاوية إحصائيات
    def create_statistics_container(self, parent_layout):
        group = QGroupBox("الإحصائيات المالية")

        # تخطيط أفقي للبطاقات الستة
        layout = QHBoxLayout(group)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 20, 15, 15)

        # إنشاء labels للإحصائيات
        self.total_phases_amount_label = QLabel("0.00")
        self.total_engineers_amount_label = QLabel("0.00")
        self.net_profit_label = QLabel("0.00")
        self.total_phases_label = QLabel("0")
        self.completed_phases_label = QLabel("0")
        self.overdue_phases_label = QLabel("0")
        self.in_progress_phases_label = QLabel("0")

        # إنشاء البطاقات الملونة
        stats = [
            ("إجمالي مبلغ المراحل", self.total_phases_amount_label, "#8e44ad"),  # بنفسجي للمبالغ المالية
            ("إجمالي فريق العمل", self.total_engineers_amount_label, "#3498db"),   # أزرق لفريق العمل
            ("صافي الشركة", self.net_profit_label, "#27ae60"),                    # أخضر للأرباح
            ("عدد المراحل المكتملة", self.completed_phases_label, "#2ecc71"),     # أخضر فاتح للمكتمل
            ("عدد المراحل المتأخرة", self.overdue_phases_label, "#e74c3c"),       # أحمر للمتأخر
            ("عدد المراحل قيد التنفيذ", self.in_progress_phases_label, "#f39c12"), # برتقالي لقيد التنفيذ
        ]

        # إضافة البطاقات إلى التخطيط
        for title, label, color in stats:
            card = create_stat_card(title, label.text(), color)
            layout.addWidget(card)

        parent_layout.addWidget(group)

    # دالة إنشاء تاب مراحل المشروع
    # إنشاء علامة تبويب مراحل المشروع
    def create_project_phases_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_phase_btn = QPushButton("إضافة")
        add_phase_btn.setIcon(qta.icon('fa5s.plus'))
        add_phase_btn.clicked.connect(self.add_phase)
        buttons_layout.addWidget(add_phase_btn)



        # إضافة الأزرار الجديدة لتاب مراحل المشروع
        insert_amount_btn = QPushButton("إدراج المبلغ")
        insert_amount_btn.setIcon(qta.icon('fa5s.money-bill'))
        insert_amount_btn.clicked.connect(self.insert_phase_amount)
        buttons_layout.addWidget(insert_amount_btn)

        cancel_amount_btn = QPushButton("إلغاء الإدراج")
        cancel_amount_btn.setIcon(qta.icon('fa5s.times-circle'))
        cancel_amount_btn.clicked.connect(self.cancel_phase_amount)
        buttons_layout.addWidget(cancel_amount_btn)

        insert_all_amounts_btn = QPushButton("إدراج جميع المبالغ")
        insert_all_amounts_btn.setIcon(qta.icon('fa5s.coins'))
        insert_all_amounts_btn.clicked.connect(self.insert_all_phase_amounts)
        buttons_layout.addWidget(insert_all_amounts_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # ComboBox للفلترة حسب اسم المرحلة
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("فلترة حسب المرحلة:"))
        self.phases_filter_combo = QComboBox()
        self.phases_filter_combo.addItem("جميع المراحل")
        self.phases_filter_combo.currentTextChanged.connect(self.filter_phases_combined)
        filter_layout.addWidget(self.phases_filter_combo)

        # ComboBox للفلترة حسب حالة المبلغ
        filter_layout.addWidget(QLabel("حالة المبلغ:"))
        self.phases_amount_status_filter_combo = QComboBox()
        self.phases_amount_status_filter_combo.addItems(["جميع الحالات", "غير مدرج", "تم الإدراج"])
        self.phases_amount_status_filter_combo.currentTextChanged.connect(self.filter_phases_combined)
        filter_layout.addWidget(self.phases_amount_status_filter_combo)

        # شريط البحث (في الجانب الأيسر)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.phases_search = QLineEdit()
        self.phases_search.setPlaceholderText("ابحث في مراحل المشروع...")
        self.phases_search.textChanged.connect(self.filter_phases_combined)
        search_layout.addWidget(self.phases_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للمراحل (في صف منفصل)
        self.create_phases_statistics_cards(layout)

        # جدول المراحل
        self.phases_table = QTableWidget()
        self.setup_phases_table()
        layout.addWidget(self.phases_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.tasks', color='#9b59b6'), "مراحل المشروع")

    # دالة إعداد جدول المراحل
    # جدول مراحل الإعداد
    def setup_phases_table(self):
        headers = ["ID", "الرقم", "اسم المرحلة", "وصف المرحلة", "الوحدة", "الكمية", "السعر", "الإجمالي", "ملاحظات", "حالة المبلغ"]
        self.phases_table.setColumnCount(len(headers))
        self.phases_table.setHorizontalHeaderLabels(headers)
        self.phases_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول الموحدة
        setup_table_style(self.phases_table)

        # تمكين التحديد المتعدد للصفوف
        self.phases_table.setSelectionMode(QAbstractItemView.MultiSelection)

        # إضافة قائمة السياق للجدول (جدول فرعي - بدون خيار عرض)
        setup_table_context_menu(self.phases_table, self, "مراحل المشروع", is_main_table=False)

        # تعيين عرض عمود الإجراءات
        self.phases_table.setColumnWidth(10, 150)  # عمود الإجراءات

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.phases_table.itemDoubleClicked.connect(self.on_phases_table_double_click)

    # دالة عرض payments
    # عرض المدفوعات
    def view_payments(self):
        try:
            from إدارة_دفعات_المشروع import open_project_payments_window
            self.payments_window = open_project_payments_window(self, self.project_data)

            # ربط إشارة إغلاق النافذة بتحديث البيانات
            if hasattr(self.payments_window, 'finished'):
                self.payments_window.finished.connect(self.on_payments_window_closed)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة الدفعات: {str(e)}")

    # دالة معالجة payments_window_closed
    # على نافذة المدفوعات مغلقة
    def on_payments_window_closed(self):
        try:
            # تحديث البيانات المالية
            self.refresh_project_data()
            self.load_project_info()
            self.load_statistics()
            self.load_additional_info()

            # تحديث النافذة الرئيسية
            self.update_main_window()

        except Exception as e:
            print(f"خطأ في تحديث البيانات بعد إغلاق نافذة الدفعات: {e}")

    # دالة تعديل project_status
    # تحرير حالة المشروع
    def edit_project_status(self):
        try:
            # التحقق من وجود بيانات المشروع
            if not self.project_data or not self.project_data.get('id'):
                QMessageBox.warning(self, "خطأ", "لا يمكن العثور على بيانات المشروع")
                return

            # فتح نافذة حوار تحرير حالة المشروع
            dialog = ProjectStatusEditDialog(self, self.project_data)
            if dialog.exec() == QDialog.Accepted:
                # تحديث جميع البيانات (سيتم التحديث من داخل ProjectStatusEditDialog)
                pass

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة تحرير حالة المشروع: {str(e)}")
            print(f"خطأ في edit_project_status: {e}")

    # دالة تحديث بيانات المشروع
    # تحديث بيانات المشروع
    def refresh_project_data(self):
        try:
            if not self.project_data or not self.project_data.get('id'):
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor(dictionary=True)

            # جلب بيانات المشروع المحدثة
            project_id = self.project_data['id']
            cursor.execute("""
                SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                FROM المشاريع p
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                WHERE p.id = %s
            """, (project_id,))

            result = cursor.fetchone()
            if result:
                # تحديث بيانات المشروع المحلية
                self.project_data.update(result)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث بيانات المشروع: {e}")

    # دالة تعديل project_data
    # تحرير بيانات المشروع
    def edit_project_data(self):
        try:
            if not self.project_id:
                QMessageBox.warning(self, "تحذير", "لا يوجد مشروع محدد للتعديل")
                return

            # البحث عن MainWindow في التسلسل الهرمي للنوافذ
            main_window = self.find_main_window()

            # إذا لم نجد MainWindow، نحاول استخدام طريقة بديلة
            if not main_window:
                print("⚠️ لم يتم العثور على MainWindow، محاولة استخدام طريقة بديلة...")
                # محاولة تحديث البيانات مباشرة
                success = self.update_project_data_directly()
                if success:
                    return
                else:
                    QMessageBox.critical(self, "خطأ", "لا يمكن العثور على النافذة الرئيسية ولا يمكن تحديث البيانات مباشرة")
                    return

            # استيراد نافذة التعديل
            from الأدوات import AddEntryDialog

            # إعداد بيانات المشروع للتعديل
            dialog = AddEntryDialog(
                main_window=main_window,
                section_name=self.project_type,  # استخدام نوع المشروع (المشاريع أو المقاولات)
                parent=self,
                entry_data=self.project_data,
                row_id=self.project_id
            )

            if dialog.exec() == QDialog.Accepted:
                # تحديث بيانات المشروع المحلية
                self.refresh_project_data()
                # تحديث واجهة المستخدم
                self.load_project_info()
                self.load_timing_status_info()
                self.load_additional_info()
                self.load_statistics()

                # تحديث النافذة الرئيسية إذا كانت متاحة
                if main_window and hasattr(main_window, 'show_section'):
                    section_name = self.project_data.get('اسم_القسم', 'المشاريع')
                    main_window.show_section(section_name)
                    # تحديث عرض البطاقات إذا كان متاحاً
                    if hasattr(main_window, 'update_cards_view'):
                        year = str(QDate.currentDate().year())
                        main_window.update_cards_view(section_name, year)

                QMessageBox.information(self, "نجح", "تم تحديث بيانات المشروع بنجاح")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة تعديل المشروع: {str(e)}")

    # دالة العثور على النافذة الرئيسية
    # ابحث عن النافذة الرئيسية
    def find_main_window(self):
        try:
            print("🔍 بدء البحث عن النافذة الرئيسية...")
            print(f"  📱 النافذة الحالية: {type(self).__name__}")
            print(f"  📱 النافذة الأب: {type(self.parent).__name__ if self.parent else 'None'}")

            # فحص مباشر للنافذة الأب
            if self.parent:
                print(f"  🔍 فحص النافذة الأب مباشرة: {type(self.parent).__name__}")

                # التحقق من الدوال المطلوبة
                has_get_db = hasattr(self.parent, 'get_db_connection')
                has_update = hasattr(self.parent, 'update_entry')
                print(f"    - لديه get_db_connection: {has_get_db}")
                print(f"    - لديه update_entry: {has_update}")

                if has_get_db and has_update:
                    print("  ✅ النافذة الأب هي MainWindow!")
                    return self.parent

                # التحقق من اسم الفئة
                if type(self.parent).__name__ == 'MainWindow':
                    print("  ✅ النافذة الأب هي MainWindow بالاسم!")
                    return self.parent

            # الطريقة 1: البحث في التسلسل الهرمي
            current = self.parent
            level = 0
            while current and level < 10:  # تجنب الحلقة اللانهائية
                print(f"  📍 المستوى {level}: فحص {type(current).__name__}")

                # التحقق من أن النافذة هي MainWindow
                if hasattr(current, 'get_db_connection') and hasattr(current, 'update_entry'):
                    print(f"  ✅ تم العثور على MainWindow في المستوى {level}")
                    return current

                # التحقق من اسم الفئة
                if type(current).__name__ == 'MainWindow':
                    print(f"  ✅ تم العثور على MainWindow بالاسم في المستوى {level}")
                    return current

                # الانتقال إلى النافذة الأب
                next_parent = None
                if hasattr(current, 'parent') and callable(getattr(current, 'parent')):
                    next_parent = current.parent()
                elif hasattr(current, 'parent') and not callable(getattr(current, 'parent')):
                    next_parent = current.parent
                elif hasattr(current, 'parentWidget') and callable(getattr(current, 'parentWidget')):
                    next_parent = current.parentWidget()

                current = next_parent
                level += 1

            # الطريقة 2: البحث في جميع النوافذ المفتوحة
            print("  🔍 البحث في جميع النوافذ المفتوحة...")
            from PySide6.QtWidgets import QApplication
            for widget in QApplication.topLevelWidgets():
                widget_name = type(widget).__name__
                print(f"    📱 فحص النافذة: {widget_name}")

                if hasattr(widget, 'get_db_connection') and hasattr(widget, 'update_entry'):
                    print(f"    ✅ تم العثور على MainWindow: {widget_name}")
                    return widget

                if widget_name == 'MainWindow':
                    print(f"    ✅ تم العثور على MainWindow بالاسم: {widget_name}")
                    return widget

            # الطريقة 3: البحث باستخدام QApplication.activeWindow
            print("  🔍 البحث في النافذة النشطة...")
            active_window = QApplication.activeWindow()
            if active_window:
                print(f"    📱 النافذة النشطة: {type(active_window).__name__}")
                if hasattr(active_window, 'get_db_connection') and hasattr(active_window, 'update_entry'):
                    print("    ✅ النافذة النشطة هي MainWindow")
                    return active_window

            print("  ❌ لم يتم العثور على MainWindow")
            return None

        except Exception as e:
            print(f"❌ خطأ في البحث عن النافذة الرئيسية: {e}")
            return None

    # دالة تحديث project_data_directly
    # تحديث بيانات المشروع مباشرة
    def update_project_data_directly(self):
        try:
            print("🔧 محاولة تحديث البيانات مباشرة...")

            # استيراد نافذة التعديل مع self كـ main_window
            from الأدوات import AddEntryDialog

            # إنشاء كائس وهمي يحتوي على الدوال المطلوبة
            # كلاس وهمي للنافذة الرئيسية
            # Dummymainwindow
            class DummyMainWindow:
                # دالة الإنشاء
                # init
                def __init__(self, project_window):
                    self.project_window = project_window

                # دالة الحصول على اتصال قاعدة البيانات
                # احصل على اتصال DB
                def get_db_connection(self):
                    import mysql.connector
                    from DB import host, user_r, password_r
                    try:
                        conn = mysql.connector.connect(
                            host=host,
                            user=user_r,
                            password=password_r,
                            database="project_manager_V2"
                        )
                        return conn
                    except Exception as e:
                        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
                        return None

                # دالة تحديث الإدخال
                # تحديث الإدخال
                def update_entry(self, section_name, row_id, data):
                    from PySide6.QtCore import QDate
                    from الأدوات import update_entry
                    current_year = str(QDate.currentDate().year())
                    update_entry(self, section_name, current_year, row_id, data)

                # دالة إظهار القسم
                # عرض قسم
                def show_section(self, section_name):
                    print(f"تحديث القسم: {section_name}")

                # دالة تحديث عرض البطاقات
                # عرض بطاقات التحديث
                def update_cards_view(self, section_name, year):
                    print(f"تحديث عرض البطاقات: {section_name}, {year}")

            # إنشاء الكائن الوهمي
            dummy_main_window = DummyMainWindow(self)

            # إعداد بيانات المشروع للتعديل
            dialog = AddEntryDialog(
                main_window=dummy_main_window,
                section_name=self.project_type,
                parent=self,
                entry_data=self.project_data,
                row_id=self.project_id
            )

            if dialog.exec() == QDialog.Accepted:
                # تحديث بيانات المشروع المحلية
                self.refresh_project_data()
                # تحديث واجهة المستخدم
                self.load_project_info()
                self.load_timing_status_info()
                self.load_additional_info()
                self.load_statistics()

                QMessageBox.information(self, "نجح", "تم تحديث بيانات المشروع بنجاح")
                return True

            return False

        except Exception as e:
            print(f"❌ خطأ في التحديث المباشر: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث البيانات: {str(e)}")
            return False

    # دالة تصفية المراحل
    # مراحل المرشح
    def filter_phases(self):
        self.filter_phases_combined()

    # دالة إضافة مرحلة جديدة
    # أضف المرحلة
    def add_phase(self):
        dialog = PhaseDialog(self, project_id=self.project_id, project_type=self.project_type)
        if dialog.exec() == QDialog.Accepted:
            self.load_phases_data()
            self.load_statistics()
            self.update_phases_statistics()

    # دالة تعديل مرحلة
    # تحرير المرحلة
    def edit_phase(self):
        current_row = self.phases_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مرحلة للتعديل")
            return

        # الحصول على معرف المرحلة من العمود المخفي
        phase_id_item = self.phases_table.item(current_row, 0)
        if not phase_id_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المرحلة")
            return

        phase_id = int(phase_id_item.text())
        dialog = PhaseDialog(self, project_id=self.project_id, phase_id=phase_id, project_type=self.project_type)
        if dialog.exec() == QDialog.Accepted:
            self.load_phases_data()
            self.load_statistics()
            self.update_phases_statistics()

    # دالة حذف مرحلة
    # حذف المرحلة
    def delete_phase(self):
        current_row = self.phases_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مرحلة للحذف")
            return

        # الحصول على معرف المرحلة واسمها
        phase_id_item = self.phases_table.item(current_row, 0)
        phase_name_item = self.phases_table.item(current_row, 2)

        if not phase_id_item or not phase_name_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات المرحلة")
            return

        phase_id = int(phase_id_item.text())
        phase_name = phase_name_item.text()

        # تأكيد الحذف
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف المرحلة '{phase_name}'؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # حذف المرحلة
                cursor.execute("DELETE FROM المشاريع_المراحل WHERE id = %s", (phase_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم حذف المرحلة '{phase_name}' بنجاح")
                self.load_phases_data()
                self.load_statistics()
                self.update_phases_statistics()

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المرحلة: {str(e)}")

    # دالة إنشاء تاب مهام المهندسين
    # إنشاء علامة تبويب مهام المهندسين
    def create_engineers_tasks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_task_btn = QPushButton("إضافة")
        add_task_btn.setIcon(qta.icon('fa5s.plus'))
        add_task_btn.clicked.connect(self.add_engineer_task)
        buttons_layout.addWidget(add_task_btn)

        
        # إضافة الأزرار الجديدة لتاب فريق العمل
        insert_balance_btn = QPushButton("إدراج الرصيد")
        insert_balance_btn.setIcon(qta.icon('fa5s.user-plus'))
        insert_balance_btn.clicked.connect(self.insert_engineer_balance)
        buttons_layout.addWidget(insert_balance_btn)

        insert_all_balances_btn = QPushButton("إدراج جميع الأرصدة")
        insert_all_balances_btn.setIcon(qta.icon('fa5s.users-cog'))
        insert_all_balances_btn.clicked.connect(self.insert_all_engineer_balances)
        buttons_layout.addWidget(insert_all_balances_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # الصف الأول: الفلاتر
        filter_layout = QHBoxLayout()

        # فلتر حسب نوع العضو
        self.member_type_filter_combo = QComboBox()
        self.member_type_filter_combo.addItems(["جميع الأنواع", "مهندس", "مقاول", "عامل", "موظف"])
        self.member_type_filter_combo.currentTextChanged.connect(self.filter_engineers_tasks)
        filter_layout.addWidget(self.member_type_filter_combo)

        # فلتر حسب اسم عضو فريق العمل
        self.engineers_filter_combo = QComboBox()
        self.engineers_filter_combo.addItem("جميع أعضاء الفريق")
        self.engineers_filter_combo.currentTextChanged.connect(self.filter_engineers_tasks)
        filter_layout.addWidget(self.engineers_filter_combo)

        # فلتر حسب حالة المبلغ
        
        self.amount_status_filter_combo = QComboBox()
        self.amount_status_filter_combo.addItems(["جميع الحالات", "غير مدرج", "تم الإدراج"])
        self.amount_status_filter_combo.currentTextChanged.connect(self.filter_engineers_tasks)
        filter_layout.addWidget(self.amount_status_filter_combo)

        # شريط البحث
        filter_layout.addWidget(QLabel("البحث:"))
        self.engineers_search = QLineEdit()
        self.engineers_search.setPlaceholderText("ابحث في فريق العمل...")
        self.engineers_search.textChanged.connect(self.filter_engineers_tasks)
        filter_layout.addWidget(self.engineers_search)

        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية (في صف منفصل)
        self.create_team_statistics_cards(layout)

        # جدول فريق العمل
        self.engineers_tasks_table = QTableWidget()
        self.setup_engineers_tasks_table()
        layout.addWidget(self.engineers_tasks_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.users', color='#16a085'), "فريق العمل")

    # دالة إنشاء team_statistics_cards
    # إنشاء بطاقات إحصائيات الفريق
    def create_team_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("team_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات الإحصائية
        self.total_members_label = QLabel("0")
        self.engineers_count_label = QLabel("0")
        self.contractors_count_label = QLabel("0")
        self.workers_count_label = QLabel("0")
        self.employees_count_label = QLabel("0")

        # استخدام عملة افتراضية إذا لم تكن معرفة
        currency = f"{Currency_type}"
        try:
            currency = Currency_type
        except:
            pass

        self.total_amount_label = QLabel(f"0 {currency}")
        self.paid_amount_label = QLabel(f"0 {currency}")
        self.unpaid_amount_label = QLabel(f"0 {currency}")

        # تعريف البطاقات
        stats = [
            ("إجمالي المبالغ", self.total_amount_label, "#3498db"),
            ("المبالغ المدرجة", self.paid_amount_label, "#27ae60"),
            ("المبالغ غير المدرجة", self.unpaid_amount_label, "#e74c3c"),
        ]

        # إنشاء البطاقات
        for title, label, color in stats:
            card = create_stat_card(title, label.text(), color)
            stats_layout.addWidget(card)
            
        parent_layout.addWidget(stats_container)

        # تحميل الإحصائيات الأولية
        self.update_team_statistics()

    # دالة إنشاء phases_statistics_cards
    # إنشاء بطاقات إحصائيات المراحل
    def create_phases_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("phases_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات الإحصائية
        self.phases_total_amount_label = QLabel("0")
        self.phases_posted_amount_label = QLabel("0")
        self.phases_unposted_amount_label = QLabel("0")

        # إنشاء البطاقات
        stats = [
            ("إجمالي المبالغ", self.phases_total_amount_label, "#8e44ad"),      # بنفسجي للإجمالي
            ("المبالغ المدرجة", self.phases_posted_amount_label, "#27ae60"),     # أخضر للمدرجة
            ("المبالغ غير المدرجة", self.phases_unposted_amount_label, "#e74c3c"), # أحمر لغير المدرجة
        ]

        # إنشاء البطاقات
        for title, label, color in stats:
            card = create_stat_card(title, label.text(), color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

        # تحميل الإحصائيات الأولية
        self.update_phases_statistics()



    # دالة إعداد جدول مهام المهندسين
    # طاولة مهندسي المهندسين الإعداد
    def setup_engineers_tasks_table(self):
        headers = ["ID", "الرقم", "عضو فريق العمل", "نوع العضو", "اسم المهمة", "وصف المهمة", "% النسبة", "مبلغ عضو فريق العمل", "حالة المبلغ"]
        self.engineers_tasks_table.setColumnCount(len(headers))
        self.engineers_tasks_table.setHorizontalHeaderLabels(headers)
        self.engineers_tasks_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول الموحدة
        setup_table_style(self.engineers_tasks_table)

        # إضافة قائمة السياق للجدول (جدول فرعي - بدون خيار عرض)
        setup_table_context_menu(self.engineers_tasks_table, self, "فريق العمل", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.engineers_tasks_table.itemDoubleClicked.connect(self.on_engineers_tasks_table_double_click)

    # دالة تحديث team_statistics
    # تحديث إحصائيات الفريق
    def update_team_statistics(self):
        try:
            
            # التحقق من وجود البطاقات
            if not hasattr(self, 'total_members_label'):
                print("❌ البطاقات الإحصائية غير موجودة")
                return

            if not self.project_id:
                print("⚠️ لا يوجد معرف مشروع - تعيين قيم افتراضية")
                # تعيين قيم افتراضية عند عدم وجود مشروع
                self.total_members_label.setText("0")
                self.engineers_count_label.setText("0")
                self.contractors_count_label.setText("0")
                self.workers_count_label.setText("0")
                self.employees_count_label.setText("0")
                self.total_amount_label.setText(f"0 {Currency_type}")
                self.paid_amount_label.setText(f"0 {Currency_type}")
                self.unpaid_amount_label.setText(f"0 {Currency_type}")
                
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # استعلام محدث لإحصائيات عدد الأعضاء باستخدام JOIN مع جدول الموظفين
            cursor.execute("""
                SELECT
                    COUNT(*) as total_members,
                    SUM(CASE WHEN COALESCE(م.التصنيف, 'موظف') = 'مهندس' THEN 1 ELSE 0 END) as engineers,
                    SUM(CASE WHEN COALESCE(م.التصنيف, 'موظف') = 'مقاول' THEN 1 ELSE 0 END) as contractors,
                    SUM(CASE WHEN COALESCE(م.التصنيف, 'موظف') = 'عامل' THEN 1 ELSE 0 END) as workers,
                    SUM(CASE WHEN COALESCE(م.التصنيف, 'موظف') = 'موظف' THEN 1 ELSE 0 END) as employees
                FROM المشاريع_مهام_الفريق مم
                JOIN الموظفين م ON مم.معرف_الموظف = م.id
                WHERE مم.معرف_المشروع = %s
                AND مم.نوع_المهمة IN ('مهمة مشروع', 'مهمة مقاولات')
            """, (self.project_id,))

            counts = cursor.fetchone()
            if counts:
                total_members, engineers, contractors, workers, employees = counts
                

                self.total_members_label.setText(str(total_members or 0))
                self.engineers_count_label.setText(str(engineers or 0))
                self.contractors_count_label.setText(str(contractors or 0))
                self.workers_count_label.setText(str(workers or 0))
                self.employees_count_label.setText(str(employees or 0))

                
            else:
                # قيم افتراضية إذا لم يتم العثور على بيانات
                self.total_members_label.setText("0")
                self.engineers_count_label.setText("0")
                self.contractors_count_label.setText("0")
                self.workers_count_label.setText("0")
                self.employees_count_label.setText("0")

            # استعلام مبسط للإحصائيات المالية
            cursor.execute("""
                SELECT
                    COALESCE(SUM(COALESCE(مبلغ_الموظف, 0)), 0) as total_amount,
                    COALESCE(SUM(CASE WHEN حالة_مبلغ_الموظف = 'تم الإدراج' THEN COALESCE(مبلغ_الموظف, 0) ELSE 0 END), 0) as paid_amount,
                    COALESCE(SUM(CASE WHEN COALESCE(حالة_مبلغ_الموظف, 'غير مدرج') = 'غير مدرج' THEN COALESCE(مبلغ_الموظف, 0) ELSE 0 END), 0) as unpaid_amount
                FROM المشاريع_مهام_الفريق مم
                WHERE مم.معرف_القسم = %s
                AND مم.نوع_المهمة IN ('مهمة مشروع', 'مهمة مقاولات')
            """, (self.project_id,))

            amounts = cursor.fetchone()
            if amounts:
                total_amount, paid_amount, unpaid_amount = amounts
                

                # استخدام عملة افتراضية إذا لم تكن معرفة
                currency = f"{Currency_type}"
                try:
                    currency = Currency_type
                except:
                    pass

                self.total_amount_label.setText(f"{total_amount:,.0f} {currency}")
                self.paid_amount_label.setText(f"{paid_amount:,.0f} {currency}")
                self.unpaid_amount_label.setText(f"{unpaid_amount:,.0f} {currency}")

                
            else:
                print("⚠️ لم يتم العثور على بيانات المبالغ - تعيين قيم افتراضية")
                # قيم افتراضية للمبالغ
                currency = f"{Currency_type}"
                try:
                    currency = Currency_type
                except:
                    pass
                self.total_amount_label.setText(f"0 {currency}")
                self.paid_amount_label.setText(f"0 {currency}")
                self.unpaid_amount_label.setText(f"0 {currency}")

            conn.close()
            

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات فريق العمل: {e}")
            # تعيين قيم افتراضية في حالة الخطأ
            try:
                self.total_members_label.setText("0")
                self.engineers_count_label.setText("0")
                self.contractors_count_label.setText("0")
                self.workers_count_label.setText("0")
                self.employees_count_label.setText("0")
                self.total_amount_label.setText(f"0 {Currency_type}")
                self.paid_amount_label.setText(f"0 {Currency_type}")
                self.unpaid_amount_label.setText(f"0 {Currency_type}")
            except:
                pass

    # دالة تحديث engineers_filters
    # تحديث مرشحات المهندسين
    def update_engineers_filters(self):
        try:
            # التحقق من وجود الجدول
            if not hasattr(self, 'engineers_tasks_table') or self.engineers_tasks_table is None:
                return

            # حفظ الاختيار الحالي
            current_engineer = self.engineers_filter_combo.currentText()

            # مسح القائمة وإعادة تعبئتها
            self.engineers_filter_combo.clear()
            self.engineers_filter_combo.addItem("جميع أعضاء فريق العمل")

            # جمع أسماء الأعضاء من الجدول
            engineers_set = set()
            for row in range(self.engineers_tasks_table.rowCount()):
                engineer_item = self.engineers_tasks_table.item(row, 2)  # عمود عضو فريق العمل
                if engineer_item:
                    engineer_name = engineer_item.text()
                    if engineer_name and engineer_name not in engineers_set:
                        engineers_set.add(engineer_name)
                        self.engineers_filter_combo.addItem(engineer_name)

            # استعادة الاختيار السابق إن أمكن
            index = self.engineers_filter_combo.findText(current_engineer)
            if index >= 0:
                self.engineers_filter_combo.setCurrentIndex(index)

        except Exception as e:
            print(f"خطأ في تحديث فلاتر أعضاء فريق العمل: {e}")

    # دالة إنشاء تاب الجدول الزمني
    # إنشاء علامة تبويب الجدول الزمني
    def create_timeline_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_timeline_btn = QPushButton("إضافة")
        add_timeline_btn.setIcon(qta.icon('fa5s.plus'))
        add_timeline_btn.clicked.connect(self.add_timeline_entry)
        buttons_layout.addWidget(add_timeline_btn)

        edit_timeline_btn = QPushButton("تعديل")
        edit_timeline_btn.setIcon(qta.icon('fa5s.edit'))
        edit_timeline_btn.clicked.connect(self.edit_timeline_entry)
        buttons_layout.addWidget(edit_timeline_btn)

        delete_timeline_btn = QPushButton("حذف")
        delete_timeline_btn.setIcon(qta.icon('fa5s.trash'))
        delete_timeline_btn.clicked.connect(self.delete_timeline_entry)
        buttons_layout.addWidget(delete_timeline_btn)

        # إضافة زر الحالة لتاب الجدول الزمني
        status_btn = QPushButton("الحالة")
        status_btn.setIcon(qta.icon('fa5s.tasks'))
        status_btn.clicked.connect(self.manage_timeline_status)
        buttons_layout.addWidget(status_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # الفلاتر (في الجانب الأيسر)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("الحالة:"))
        self.timeline_status_filter_combo = QComboBox()
        self.timeline_status_filter_combo.addItems(["جميع الحالات", "لم يبدأ", "قيد التنفيذ", "منتهي", "متوقف"])
        self.timeline_status_filter_combo.currentTextChanged.connect(self.filter_timeline_combined)
        filter_layout.addWidget(self.timeline_status_filter_combo)

        filter_layout.addWidget(QLabel("عضو الفريق:"))
        self.timeline_member_filter_combo = QComboBox()
        self.timeline_member_filter_combo.addItem("جميع الأعضاء")
        self.timeline_member_filter_combo.currentTextChanged.connect(self.filter_timeline_combined)
        filter_layout.addWidget(self.timeline_member_filter_combo)

        # شريط البحث
        filter_layout.addWidget(QLabel("البحث:"))
        self.timeline_search = QLineEdit()
        self.timeline_search.setPlaceholderText("ابحث في الجدول الزمني...")
        self.timeline_search.textChanged.connect(self.filter_timeline_combined)
        filter_layout.addWidget(self.timeline_search)

        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية (في صف منفصل)
        self.create_timeline_statistics_cards(layout)

        # جدول الجدول الزمني
        self.timeline_table = QTableWidget()
        self.setup_timeline_table()
        layout.addWidget(self.timeline_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.calendar', color='#f39c12'), "الجدول الزمني")

    # دالة إعداد جدول الجدول الزمني
    # جدول الإعداد الجدول الزمني
    def setup_timeline_table(self):
        headers = ["ID", "الرقم", "عضو فريق العمل", "اسم المهمة", "وصف المهمة", "تاريخ البدء", "تاريخ الانتهاء", "حالة المهمة"]
        self.timeline_table.setColumnCount(len(headers))
        self.timeline_table.setHorizontalHeaderLabels(headers)
        self.timeline_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول الموحدة
        setup_table_style(self.timeline_table)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.timeline_table.itemDoubleClicked.connect(self.on_timeline_table_double_click)

    # دالة إنشاء timeline_statistics_cards
    # إنشاء بطاقات إحصائيات الجدول الزمني
    def create_timeline_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات الإحصائية
        self.timeline_total_tasks_label = QLabel("0")
        self.timeline_completed_tasks_label = QLabel("0")
        self.timeline_in_progress_tasks_label = QLabel("0")
        self.timeline_delayed_tasks_label = QLabel("0")
        self.timeline_not_started_tasks_label = QLabel("0")

        # إنشاء البطاقات
        stats = [
            ("إجمالي المهام", self.timeline_total_tasks_label, "#3498db"),           # أزرق للإجمالي
            ("المنتهية", self.timeline_completed_tasks_label, "#27ae60"),            # أخضر للمنتهية
            ("قيد التنفيذ", self.timeline_in_progress_tasks_label, "#f39c12"),       # برتقالي لقيد التنفيذ
            ("متأخرة", self.timeline_delayed_tasks_label, "#e74c3c"),               # أحمر للمتأخرة
            ("لم تبدأ", self.timeline_not_started_tasks_label, "#95a5a6"),          # رمادي لغير المبدوءة
        ]

        # إنشاء البطاقات
        for title, label, color in stats:
            card = create_stat_card(title, label.text(), color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

        # تحميل الإحصائيات الأولية
        self.update_timeline_statistics()



    # دالة تصفية timeline_combined
    # مرشح الجدول الزمني مجتمعة
    def filter_timeline_combined(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'timeline_table') or self.timeline_table is None:
            return

        selected_status = self.timeline_status_filter_combo.currentText()
        selected_member = self.timeline_member_filter_combo.currentText()
        search_text = self.timeline_search.text().lower()

        for row in range(self.timeline_table.rowCount()):
            show_row = True

            # فلترة حسب الحالة
            if selected_status != "جميع الحالات":
                status_item = self.timeline_table.item(row, 6)  # عمود حالة المهمة
                if status_item:
                    status_text = status_item.text()
                    # التحقق من الحالة مع مراعاة النصوص المعدلة (مثل "تأخير" و "متبقي")
                    if selected_status == "منتهي" and "منتهي" not in status_text:
                        show_row = False
                    elif selected_status == "قيد التنفيذ" and ("قيد التنفيذ" not in status_text and "متبقي" not in status_text):
                        show_row = False
                    elif selected_status == "متوقف" and "متوقف" not in status_text:
                        show_row = False
                    elif selected_status == "لم يبدأ" and "لم يبدأ" not in status_text:
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب عضو الفريق
            if show_row and selected_member != "جميع الأعضاء":
                member_item = self.timeline_table.item(row, 2)  # عمود عضو فريق العمل
                if member_item:
                    if selected_member not in member_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب البحث
            if show_row and search_text:
                row_match = False
                for col in range(self.timeline_table.columnCount()):
                    item = self.timeline_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_match = True
                        break
                if not row_match:
                    show_row = False

            self.timeline_table.setRowHidden(row, not show_row)

        # تحديث إحصائيات الجدول الزمني بعد الفلترة
        self.update_timeline_statistics()

    # دالة تحديث timeline_statistics
    # تحديث إحصائيات الجدول الزمني
    def update_timeline_statistics(self):
        try:
            # التحقق من وجود البطاقات
            if not hasattr(self, 'timeline_total_tasks_label'):
                return

            # التحقق من وجود الجدول
            if not hasattr(self, 'timeline_table') or self.timeline_table is None:
                return

            total_tasks = 0
            completed_tasks = 0
            in_progress_tasks = 0
            delayed_tasks = 0
            not_started_tasks = 0

            # حساب الإحصائيات من الصفوف المرئية في الجدول
            for row in range(self.timeline_table.rowCount()):
                if not self.timeline_table.isRowHidden(row):
                    total_tasks += 1

                    # الحصول على حالة المهمة
                    status_item = self.timeline_table.item(row, 6)  # عمود حالة المهمة

                    if status_item and status_item.text():
                        status_text = status_item.text()

                        # تصنيف المهام حسب الحالة
                        if "منتهي" in status_text:
                            completed_tasks += 1
                        elif "قيد التنفيذ" in status_text or "متبقي" in status_text:
                            in_progress_tasks += 1
                        elif "تأخير" in status_text:
                            delayed_tasks += 1
                        elif "متوقف" in status_text:
                            # يمكن إضافة عداد منفصل للمتوقفة أو دمجها مع المتأخرة
                            delayed_tasks += 1
                        elif "لم يبدأ" in status_text:
                            not_started_tasks += 1

            # تحديث البطاقات
            self.timeline_total_tasks_label.setText(f"{total_tasks} مهمة")
            self.timeline_completed_tasks_label.setText(f"{completed_tasks} مهمة")
            self.timeline_in_progress_tasks_label.setText(f"{in_progress_tasks} مهمة")
            self.timeline_delayed_tasks_label.setText(f"{delayed_tasks} مهمة")
            self.timeline_not_started_tasks_label.setText(f"{not_started_tasks} مهمة")

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الجدول الزمني: {e}")

    # دالة تحديث timeline_member_filter
    # تحديث مرشح عضو الجدول الزمني
    def update_timeline_member_filter(self):
        try:
            # التحقق من وجود الجدول
            if not hasattr(self, 'timeline_table') or self.timeline_table is None:
                return

            # جمع أسماء أعضاء الفريق من الجدول
            members = set()
            for row in range(self.timeline_table.rowCount()):
                member_item = self.timeline_table.item(row, 2)  # عمود عضو فريق العمل
                if member_item and member_item.text():
                    members.add(member_item.text())

            # تحديث ComboBox
            current_text = self.timeline_member_filter_combo.currentText()
            self.timeline_member_filter_combo.clear()
            self.timeline_member_filter_combo.addItem("جميع الأعضاء")

            for member in sorted(members):
                self.timeline_member_filter_combo.addItem(member)

            # استعادة الاختيار السابق إن أمكن
            index = self.timeline_member_filter_combo.findText(current_text)
            if index >= 0:
                self.timeline_member_filter_combo.setCurrentIndex(index)

        except Exception as e:
            print(f"خطأ في تحديث فلتر أعضاء الفريق: {e}")

    # دالة إنشاء تاب التقارير
    # إنشاء تبويب تقارير
    def create_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # عنوان التقارير
        title_label = QLabel("التقارير الشاملة")
        title_label.setObjectName("reports_title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # أزرار التقارير
        reports_layout = QGridLayout()

        # تقرير المراحل
        phases_report_btn = QPushButton("تقرير المراحل")
        phases_report_btn.setIcon(qta.icon('fa5s.file-alt'))
        phases_report_btn.clicked.connect(self.generate_phases_report)
        reports_layout.addWidget(phases_report_btn, 0, 0)

        # تقرير فريق العمل
        engineers_report_btn = QPushButton("تقرير فريق العمل")
        engineers_report_btn.setIcon(qta.icon('fa5s.users'))
        engineers_report_btn.clicked.connect(self.generate_engineers_report)
        reports_layout.addWidget(engineers_report_btn, 0, 1)

        # تقرير الجدول الزمني
        timeline_report_btn = QPushButton("تقرير الجدول الزمني")
        timeline_report_btn.setIcon(qta.icon('fa5s.calendar'))
        timeline_report_btn.clicked.connect(self.generate_timeline_report)
        reports_layout.addWidget(timeline_report_btn, 1, 0)

        # تقرير مالي شامل
        financial_report_btn = QPushButton("تقرير مالي شامل")
        financial_report_btn.setIcon(qta.icon('fa5s.chart-line'))
        financial_report_btn.clicked.connect(self.generate_financial_report)
        reports_layout.addWidget(financial_report_btn, 1, 1)

        layout.addLayout(reports_layout)
        layout.addStretch()

        self.tab_widget.addTab(tab, qta.icon('fa5s.chart-bar', color='#e74c3c'), "تقارير شاملة")

    # دالة إنشاء تاب المرفقات
    # إنشاء علامة تبويب المرفقات
    def create_attachments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_file_btn = QPushButton("إضافة")
        add_file_btn.setIcon(qta.icon('fa5s.plus'))
        add_file_btn.clicked.connect(self.add_attachment)
        buttons_layout.addWidget(add_file_btn)

        view_file_btn = QPushButton("عرض")
        view_file_btn.setIcon(qta.icon('fa5s.eye'))
        view_file_btn.clicked.connect(self.view_attachment)
        buttons_layout.addWidget(view_file_btn)

        download_file_btn = QPushButton("تنزيل")
        download_file_btn.setIcon(qta.icon('fa5s.download'))
        download_file_btn.clicked.connect(self.download_attachment)
        buttons_layout.addWidget(download_file_btn)

        delete_file_btn = QPushButton("حذف")
        delete_file_btn.setIcon(qta.icon('fa5s.trash'))
        delete_file_btn.clicked.connect(self.delete_attachment)
        buttons_layout.addWidget(delete_file_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # الفلاتر (في الجانب الأيسر)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("نوع الملف:"))
        self.attachments_type_filter_combo = QComboBox()
        self.attachments_type_filter_combo.addItem("جميع الأنواع")
        self.attachments_type_filter_combo.currentTextChanged.connect(self.filter_attachments_combined)
        filter_layout.addWidget(self.attachments_type_filter_combo)

        # شريط البحث
        filter_layout.addWidget(QLabel("البحث:"))
        self.attachments_search = QLineEdit()
        self.attachments_search.setPlaceholderText("ابحث في الملفات والمرفقات...")
        self.attachments_search.textChanged.connect(self.filter_attachments_combined)
        filter_layout.addWidget(self.attachments_search)

        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية (في صف منفصل)
        self.create_attachments_statistics_cards(layout)

        # جدول الملفات والمرفقات
        self.attachments_table = QTableWidget()
        self.setup_attachments_table()
        layout.addWidget(self.attachments_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.paperclip', color='#95a5a6'), "الملفات والمرفقات")

    # دالة إعداد جدول المرفقات
    # جدول مرفقات الإعداد
    def setup_attachments_table(self):
        headers = ["ID", "الرقم", "اسم الملف", "نوع الملف", "الوصف", "المسار", "تاريخ الإضافة", "حجم الملف"]
        self.attachments_table.setColumnCount(len(headers))
        self.attachments_table.setHorizontalHeaderLabels(headers)
        self.attachments_table.hideColumn(0)  # إخفاء عمود ID
        self.attachments_table.hideColumn(5)  # إخفاء عمود المسار للأمان

        # تطبيق إعدادات الجدول الموحدة
        setup_table_style(self.attachments_table)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.attachments_table.itemDoubleClicked.connect(self.on_attachments_table_double_click)

        # تعديل عرض الأعمدة لتحسين العرض
        self.attachments_table.setColumnWidth(1, 50)   # الرقم
        self.attachments_table.setColumnWidth(2, 250)  # اسم الملف
        self.attachments_table.setColumnWidth(3, 80)   # نوع الملف
        self.attachments_table.setColumnWidth(4, 300)  # الوصف
        self.attachments_table.setColumnWidth(6, 150)  # تاريخ الإضافة
        self.attachments_table.setColumnWidth(7, 100)  # حجم الملف
        self.attachments_table.setColumnWidth(5, 150)  # تاريخ الإضافة
        self.attachments_table.setColumnWidth(6, 100)  # حجم الملف

    # دالة إنشاء attachments_statistics_cards
    # إنشاء بطاقات إحصائيات مرفقات
    def create_attachments_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات الإحصائية
        self.attachments_total_files_label = QLabel("0")
        self.attachments_total_size_label = QLabel("0")
        self.attachments_documents_count_label = QLabel("0")
        self.attachments_images_count_label = QLabel("0")
        self.attachments_others_count_label = QLabel("0")

        # إنشاء البطاقات
        stats = [
            ("إجمالي الملفات", self.attachments_total_files_label, "#3498db"),        # أزرق للإجمالي
            ("الحجم الكلي", self.attachments_total_size_label, "#8e44ad"),            # بنفسجي للحجم
            ("المستندات", self.attachments_documents_count_label, "#27ae60"),         # أخضر للمستندات
            ("الصور", self.attachments_images_count_label, "#f39c12"),               # برتقالي للصور
            ("أخرى", self.attachments_others_count_label, "#95a5a6"),                # رمادي للأخرى
        ]

        # إنشاء البطاقات
        for title, label, color in stats:
            card = create_stat_card(title, label.text(), color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

        # تحميل الإحصائيات الأولية
        self.update_attachments_statistics()



    # دالة تصفية attachments_combined
    # مرفقات التصفية مجتمعة
    def filter_attachments_combined(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'attachments_table') or self.attachments_table is None:
            return

        selected_type = self.attachments_type_filter_combo.currentText()
        search_text = self.attachments_search.text().lower()

        for row in range(self.attachments_table.rowCount()):
            show_row = True

            # فلترة حسب نوع الملف
            if selected_type != "جميع الأنواع":
                type_item = self.attachments_table.item(row, 3)  # عمود نوع الملف
                if type_item:
                    if selected_type != type_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب البحث
            if show_row and search_text:
                row_match = False
                for col in range(self.attachments_table.columnCount()):
                    item = self.attachments_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_match = True
                        break
                if not row_match:
                    show_row = False

            self.attachments_table.setRowHidden(row, not show_row)

        # تحديث إحصائيات الملفات بعد الفلترة
        self.update_attachments_statistics()

    # دالة تحديث attachments_statistics
    # تحديث إحصائيات المرفقات
    def update_attachments_statistics(self):
        try:
            # التحقق من وجود البطاقات
            if not hasattr(self, 'attachments_total_files_label'):
                return

            # التحقق من وجود الجدول
            if not hasattr(self, 'attachments_table') or self.attachments_table is None:
                return

            total_files = 0
            total_size = 0
            documents_count = 0
            images_count = 0
            others_count = 0

            # أنواع الملفات
            document_types = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
            image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff']

            # حساب الإحصائيات من الصفوف المرئية في الجدول
            for row in range(self.attachments_table.rowCount()):
                if not self.attachments_table.isRowHidden(row):
                    total_files += 1

                    # الحصول على نوع الملف والحجم
                    type_item = self.attachments_table.item(row, 3)  # عمود نوع الملف
                    size_item = self.attachments_table.item(row, 7)  # عمود حجم الملف

                    # حساب الحجم
                    if size_item and size_item.text():
                        try:
                            # استخراج الرقم من النص (مثل "1.5 MB")
                            size_text = size_item.text().replace(',', '')
                            if 'KB' in size_text:
                                size_value = float(size_text.replace('KB', '').strip()) / 1024
                            elif 'MB' in size_text:
                                size_value = float(size_text.replace('MB', '').strip())
                            elif 'GB' in size_text:
                                size_value = float(size_text.replace('GB', '').strip()) * 1024
                            else:
                                size_value = float(size_text.replace('B', '').strip()) / (1024 * 1024)
                            total_size += size_value
                        except ValueError:
                            continue

                    # تصنيف الملفات حسب النوع
                    if type_item and type_item.text():
                        file_type = type_item.text().lower()
                        if any(doc_type in file_type for doc_type in document_types):
                            documents_count += 1
                        elif any(img_type in file_type for img_type in image_types):
                            images_count += 1
                        else:
                            others_count += 1

            # تحديث البطاقات
            self.attachments_total_files_label.setText(f"{total_files} ملف")

            # تنسيق الحجم
            if total_size >= 1024:
                self.attachments_total_size_label.setText(f"{total_size/1024:.1f} GB")
            else:
                self.attachments_total_size_label.setText(f"{total_size:.1f} MB")

            self.attachments_documents_count_label.setText(f"{documents_count} ملف")
            self.attachments_images_count_label.setText(f"{images_count} ملف")
            self.attachments_others_count_label.setText(f"{others_count} ملف")

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الملفات: {e}")

    # دالة تحديث attachments_type_filter
    # تحديث مرشح مرفقات مرفقات
    def update_attachments_type_filter(self):
        try:
            # التحقق من وجود الجدول
            if not hasattr(self, 'attachments_table') or self.attachments_table is None:
                return

            # جمع أنواع الملفات من الجدول
            file_types = set()
            for row in range(self.attachments_table.rowCount()):
                type_item = self.attachments_table.item(row, 3)  # عمود نوع الملف
                if type_item and type_item.text():
                    file_types.add(type_item.text())

            # تحديث ComboBox
            current_text = self.attachments_type_filter_combo.currentText()
            self.attachments_type_filter_combo.clear()
            self.attachments_type_filter_combo.addItem("جميع الأنواع")

            for file_type in sorted(file_types):
                self.attachments_type_filter_combo.addItem(file_type)

            # استعادة الاختيار السابق إن أمكن
            index = self.attachments_type_filter_combo.findText(current_text)
            if index >= 0:
                self.attachments_type_filter_combo.setCurrentIndex(index)

        except Exception as e:
            print(f"خطأ في تحديث فلتر أنواع الملفات: {e}")

    # دوال معالجة الأحداث للتابات الجديدة
    # دالة تصفية مهام المهندسين
    # مهام مهندسي التصفية
    def filter_engineers_tasks(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'engineers_tasks_table') or self.engineers_tasks_table is None:
            return

        search_text = self.engineers_search.text().lower()
        for row in range(self.engineers_tasks_table.rowCount()):
            show_row = False
            for col in range(self.engineers_tasks_table.columnCount()):
                item = self.engineers_tasks_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.engineers_tasks_table.setRowHidden(row, not show_row)

    # دالة تصفية الجدول الزمني
    # مرشح الجدول الزمني
    def filter_timeline(self):
        self.filter_timeline_combined()

    # دالة تصفية timeline_by_status
    # تصفية الجدول الزمني حسب الحالة
    def filter_timeline_by_status(self):
        self.filter_timeline_combined()

    # دالة إضافة مهمة مهندس
    # إضافة مهمة المهندس
    def add_engineer_task(self):
        if not self.project_id:
            QMessageBox.warning(self, "تحذير", "لا يوجد مشروع محدد")
            return

        from إدارة_الموظفين import UnifiedTaskDialog
        dialog = UnifiedTaskDialog(self, project_id=self.project_id, context="project")
        dialog.project_type = self.project_type  # تمرير نوع المشروع
        if dialog.exec() == QDialog.Accepted:
            self.load_engineers_tasks_data()
            # تحديث الإحصائيات
            self.load_statistics()

    # دالة تعديل مهمة مهندس
    # تحرير المهندس مهمة
    def edit_engineer_task(self):
        current_row = self.engineers_tasks_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مهمة للتعديل")
            return

        # الحصول على معرف المهمة من العمود المخفي
        task_id_item = self.engineers_tasks_table.item(current_row, 0)
        if not task_id_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المهمة")
            return

        task_id = int(task_id_item.text())
        from إدارة_الموظفين import UnifiedTaskDialog
        dialog = UnifiedTaskDialog(self, project_id=self.project_id, task_id=task_id, context="project")
        dialog.project_type = self.project_type  # تمرير نوع المشروع
        if dialog.exec() == QDialog.Accepted:
            self.load_engineers_tasks_data()
            # تحديث الإحصائيات
            self.load_statistics()

    # دالة حذف مهمة مهندس
    # حذف مهمة المهندس
    def delete_engineer_task(self):
        current_row = self.engineers_tasks_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مهمة للحذف")
            return

        # الحصول على معرف المهمة واسم عضو فريق العمل
        task_id_item = self.engineers_tasks_table.item(current_row, 0)
        engineer_name_item = self.engineers_tasks_table.item(current_row, 2)

        if not task_id_item or not engineer_name_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات المهمة")
            return

        task_id = int(task_id_item.text())
        engineer_name = engineer_name_item.text()

        # تأكيد الحذف
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف عضو فريق العمل '{engineer_name}'؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # حذف المهمة
                cursor.execute("DELETE FROM المشاريع_مهام_الفريق WHERE id = %s", (task_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم حذف عضو فريق العمل '{engineer_name}' بنجاح")
                self.load_engineers_tasks_data()
                # تحديث الإحصائيات
                self.load_statistics()

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المهمة: {str(e)}")

    # دالة إضافة إدخال جدول زمني
    # أضف إدخال الجدول الزمني
    def add_timeline_entry(self):
        if not self.project_id:
            QMessageBox.warning(self, "تحذير", "لا يوجد مشروع محدد")
            return

        dialog = TimelineEntryDialog(self, project_id=self.project_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_timeline_data()
            self.update_timeline_statistics()

    # دالة تعديل إدخال جدول زمني
    # تحرير إدخال الجدول الزمني
    def edit_timeline_entry(self):
        current_row = self.timeline_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد جدولة للتعديل")
            return

        # الحصول على معرف الجدولة من العمود المخفي
        entry_id_item = self.timeline_table.item(current_row, 0)
        if not entry_id_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف الجدولة")
            return

        entry_id = int(entry_id_item.text())
        dialog = TimelineEntryDialog(self, project_id=self.project_id, entry_id=entry_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_timeline_data()
            self.update_timeline_statistics()

    # دالة حذف إدخال جدول زمني
    # حذف إدخال الجدول الزمني
    def delete_timeline_entry(self):
        current_row = self.timeline_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد جدولة للحذف")
            return

        # الحصول على معرف الجدولة واسم عضو فريق العمل
        entry_id_item = self.timeline_table.item(current_row, 0)
        engineer_name_item = self.timeline_table.item(current_row, 2)

        if not entry_id_item or not engineer_name_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات الجدولة")
            return

        entry_id = int(entry_id_item.text())
        engineer_name = engineer_name_item.text()

        # تأكيد الحذف
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف الجدولة الزمنية لعضو فريق العمل '{engineer_name}'؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # حذف الجدولة
                cursor.execute("DELETE FROM المشاريع_مهام_الفريق WHERE id = %s", (entry_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم حذف الجدولة الزمنية لعضو فريق العمل '{engineer_name}' بنجاح")
                self.load_timeline_data()
                self.update_timeline_statistics()

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف الجدولة: {str(e)}")

    # ==================== دوال النقر المزدوج للجداول ====================

    # دالة معالجة phases_table_double_click
    # على جدول المراحل انقر نقرًا مزدوجًا
    def on_phases_table_double_click(self, item):
        if item is not None:
            self.edit_phase()

    # دالة معالجة engineers_tasks_table_double_click
    # في مهام المهندسين جدول انقر نقرًا مزدوجًا
    def on_engineers_tasks_table_double_click(self, item):
        if item is not None:
            self.edit_engineer_task()

    # دالة معالجة timeline_table_double_click
    # على جدول الجدول الزمني انقر نقرًا مزدوجًا
    def on_timeline_table_double_click(self, item):
        if item is not None:
            self.edit_timeline_entry()

    # دالة معالجة expenses_table_double_click
    # على جدول النفقات انقر نقرًا مزدوجًا
    def on_expenses_table_double_click(self, item):
        if item is not None:
            self.edit_expense()

    # دالة معالجة custody_table_double_click
    # على جدول الحضانة انقر نقرًا مزدوجًا
    def on_custody_table_double_click(self, item):
        if item is not None:
            self.edit_custody()

    # دالة معالجة custody_payments_table_double_click
    # على جدول مدفوعات الحضانة انقر نقرًا مزدوجًا
    def on_custody_payments_table_double_click(self, item):
        if item is not None:
            self.edit_custody_payment()

    # دالة معالجة contractors_table_double_click
    # على جدول المقاولين انقر نقرًا مزدوجًا
    def on_contractors_table_double_click(self, item):
        if item is not None:
            self.edit_contractor()

    # دالة معالجة workers_table_double_click
    # على طاولة العمال انقر نقرًا مزدوجًا
    def on_workers_table_double_click(self, item):
        if item is not None:
            self.edit_worker()

    # دالة معالجة losses_table_double_click
    # على جدول الخسائر انقر نقرًا مزدوجًا
    def on_losses_table_double_click(self, item):
        if item is not None:
            self.edit_loss()

    # دالة معالجة returns_table_double_click
    # على جدول الإرجاع انقر نقرًا مزدوجًا
    def on_returns_table_double_click(self, item):
        if item is not None:
            self.edit_return()

    # دالة معالجة attachments_table_double_click
    # على جدول المرفقات انقر نقرًا مزدوجًا
    def on_attachments_table_double_click(self, item):
        if item is not None:
            self.view_attachment()

    # دالة إنشاء تقرير المراحل
    # توليد تقرير المراحل
    def generate_phases_report(self):
        QMessageBox.information(self, "تقرير المراحل", "سيتم إنتاج تقرير شامل للمراحل")

    # دالة إنشاء تقرير المهندسين
    # توليد تقرير المهندسين
    def generate_engineers_report(self):
        QMessageBox.information(self, "تقرير فريق العمل", "سيتم إنتاج تقرير شامل لفريق العمل")

    # دالة إنشاء تقرير الجدول الزمني
    # إنشاء تقرير الجدول الزمني
    def generate_timeline_report(self):
        QMessageBox.information(self, "تقرير الجدول الزمني", "سيتم إنتاج تقرير شامل للجدول الزمني")

    # دالة إنشاء تقرير مالي
    # توليد تقرير مالي
    def generate_financial_report(self):
        QMessageBox.information(self, "تقرير مالي", "سيتم إنتاج تقرير مالي شامل للمشروع")

    # ==================== دوال معالجة تاب الملفات والمرفقات ====================

    # دالة تصفية المرفقات
    # مرفقات التصفية
    def filter_attachments(self):
        self.filter_attachments_combined()

    # دالة إضافة مرفق
    # إضافة المرفق
    def add_attachment(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            import os
            import shutil

            # فتح نافذة اختيار الملف
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "اختيار ملف للإرفاق",
                "",
                "جميع الملفات (*.*)"
            )

            if file_path:
                # الحصول على معلومات الملف
                file_name = os.path.basename(file_path)
                file_extension = os.path.splitext(file_name)[1].lower()
                file_size = os.path.getsize(file_path)

                # تحديد نوع الملف
                file_type = self.get_file_type(file_extension)

                # فتح حوار إضافة المرفق
                dialog = AttachmentDialog(self, file_name, file_extension, file_type)
                if dialog.exec_() == QDialog.Accepted:
                    description = dialog.get_description()
                    # إنشاء مجلد المرفقات إذا لم يكن موجوداً
                    attachments_dir = os.path.join(os.getcwd(), "attachments", f"project_{self.project_id}")
                    os.makedirs(attachments_dir, exist_ok=True)

                    # نسخ الملف إلى مجلد المرفقات
                    destination_path = os.path.join(attachments_dir, file_name)

                    # التأكد من عدم وجود ملف بنفس الاسم
                    counter = 1
                    original_destination = destination_path
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(original_destination)
                        destination_path = f"{name}_{counter}{ext}"
                        counter += 1

                    shutil.copy2(file_path, destination_path)

                    # إضافة الملف إلى الجدول
                    self.add_attachment_to_table(
                        os.path.basename(destination_path),
                        file_type,
                        description,
                        destination_path,
                        file_size
                    )

                    # تحديث الفلاتر والإحصائيات
                    self.update_attachments_type_filter()
                    self.update_attachments_statistics()

                    QMessageBox.information(self, "نجح", f"تم إرفاق الملف '{file_name}' بنجاح")

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إرفاق الملف: {str(e)}")

    # دالة الحصول على نوع الملف
    # احصل على نوع الملف
    def get_file_type(self, extension):
        # إزالة النقطة من الامتداد وتحويله إلى أحرف كبيرة للعرض
        if extension.startswith('.'):
            extension_display = extension[1:].upper()
        else:
            extension_display = extension.upper()

        # تصنيف الملفات حسب النوع مع عرض الامتداد الفعلي
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico']
        document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages']
        spreadsheet_extensions = ['.xls', '.xlsx', '.csv', '.ods', '.numbers']
        presentation_extensions = ['.ppt', '.pptx', '.odp', '.key']
        cad_extensions = ['.dwg', '.dxf', '.dwf', '.step', '.iges', '.3dm']
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz']
        code_extensions = ['.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.php', '.sql']

        extension_lower = extension.lower()

        if extension_lower in image_extensions:
            return f"{extension_display}"
        elif extension_lower in document_extensions:
            return f"{extension_display}"
        elif extension_lower in spreadsheet_extensions:
            return f"{extension_display}"
        elif extension_lower in presentation_extensions:
            return f"{extension_display}"
        elif extension_lower in cad_extensions:
            return f"{extension_display}"
        elif extension_lower in video_extensions:
            return f"{extension_display}"
        elif extension_lower in audio_extensions:
            return f"{extension_display}"
        elif extension_lower in archive_extensions:
            return f"{extension_display}"
        elif extension_lower in code_extensions:
            return f"{extension_display}"
        else:
            return extension_display if extension_display else "غير محدد"

    # دالة إضافة attachment_to_table
    # أضف مرفقًا إلى الجدول
    def add_attachment_to_table(self, file_name, file_type, description, file_path, file_size):
        from datetime import datetime

        # التحقق من وجود الجدول
        if not hasattr(self, 'attachments_table') or self.attachments_table is None:
            return

        row_count = self.attachments_table.rowCount()
        self.attachments_table.insertRow(row_count)

        # تحويل حجم الملف إلى تنسيق قابل للقراءة
        size_str = self.format_file_size(file_size)

        # إضافة البيانات إلى الجدول
        # الأعمدة: ["ID", "الرقم", "اسم الملف", "نوع الملف", "الوصف", "المسار", "تاريخ الإضافة", "حجم الملف"]
        self.attachments_table.setItem(row_count, 0, QTableWidgetItem(str(row_count + 1)))  # ID مؤقت
        self.attachments_table.setItem(row_count, 1, QTableWidgetItem(str(row_count + 1)))  # الرقم
        self.attachments_table.setItem(row_count, 2, QTableWidgetItem(file_name))  # اسم الملف
        self.attachments_table.setItem(row_count, 3, QTableWidgetItem(file_type))  # نوع الملف
        self.attachments_table.setItem(row_count, 4, QTableWidgetItem(description))  # الوصف
        self.attachments_table.setItem(row_count, 5, QTableWidgetItem(file_path))  # المسار (مخفي)
        self.attachments_table.setItem(row_count, 6, QTableWidgetItem(datetime.now().strftime("%d/%m/%Y %H:%M")))  # تاريخ الإضافة
        self.attachments_table.setItem(row_count, 7, QTableWidgetItem(size_str))  # حجم الملف

        # تحسين عرض البيانات
        # تلوين نوع الملف حسب النوع
        file_type_item = self.attachments_table.item(row_count, 3)
        if file_type_item:
            self.color_file_type_item(file_type_item, file_type)

        # تنسيق تاريخ الإضافة
        date_item = self.attachments_table.item(row_count, 6)
        if date_item:
            date_item.setTextAlignment(Qt.AlignCenter)

    # دالة تلوين file_type_item
    # عنصر نوع ملف اللون
    def color_file_type_item(self, item, file_type):
        from PySide6.QtGui import QBrush, QColor

        # تحديد اللون حسب نوع الملف
        extension = file_type.lower()

        # ألوان مختلفة لأنواع الملفات المختلفة
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg', 'webp', 'ico']:
            color = QColor(46, 125, 50)  # أخضر للصور
        elif extension in ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages']:
            color = QColor(33, 150, 243)  # أزرق للمستندات
        elif extension in ['xls', 'xlsx', 'csv', 'ods', 'numbers']:
            color = QColor(76, 175, 80)  # أخضر فاتح للجداول
        elif extension in ['ppt', 'pptx', 'odp', 'key']:
            color = QColor(255, 152, 0)  # برتقالي للعروض التقديمية
        elif extension in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v']:
            color = QColor(156, 39, 176)  # بنفسجي للفيديو
        elif extension in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a']:
            color = QColor(255, 87, 34)  # برتقالي محمر للصوت
        elif extension in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz']:
            color = QColor(121, 85, 72)  # بني للأرشيف
        elif extension in ['dwg', 'dxf', 'dwf', 'step', 'iges', '3dm']:
            color = QColor(63, 81, 181)  # أزرق غامق للـ CAD
        elif extension in ['py', 'js', 'html', 'css', 'cpp', 'c', 'java', 'php', 'sql']:
            color = QColor(96, 125, 139)  # رمادي مزرق للكود
        else:
            color = QColor(158, 158, 158)  # رمادي للملفات العامة

        item.setForeground(QBrush(color))
        item.setTextAlignment(Qt.AlignCenter)

    # دالة تنسيق حجم الملف
    # حجم الملف تنسيق
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    # دالة عرض المرفق
    # عرض المرفق
    def view_attachment(self):
        current_row = self.attachments_table.currentRow()
        if current_row >= 0:
            file_path_item = self.attachments_table.item(current_row, 5)  # عمود المسار
            if file_path_item:
                file_path = file_path_item.text()
                try:
                    import os
                    import subprocess
                    import platform

                    if os.path.exists(file_path):
                        # فتح الملف بالتطبيق الافتراضي
                        if platform.system() == 'Windows':
                            os.startfile(file_path)
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.call(['open', file_path])
                        else:  # Linux
                            subprocess.call(['xdg-open', file_path])
                    else:
                        QMessageBox.warning(self, "خطأ", "الملف غير موجود")

                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح الملف: {str(e)}")
        else:
            QMessageBox.information(self, "تنبيه", "الرجاء اختيار ملف من الجدول")

    # دالة تحميل المرفق
    # تنزيل المرفق
    def download_attachment(self):
        current_row = self.attachments_table.currentRow()
        if current_row >= 0:
            file_path_item = self.attachments_table.item(current_row, 5)  # عمود المسار
            file_name_item = self.attachments_table.item(current_row, 2)  # عمود اسم الملف

            if file_path_item and file_name_item:
                source_path = file_path_item.text()
                original_name = file_name_item.text()

                try:
                    from PySide6.QtWidgets import QFileDialog
                    import shutil

                    # اختيار مكان الحفظ
                    save_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "حفظ الملف",
                        original_name,
                        "جميع الملفات (*.*)"
                    )

                    if save_path:
                        shutil.copy2(source_path, save_path)
                        QMessageBox.information(self, "نجح", f"تم حفظ الملف في: {save_path}")

                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في حفظ الملف: {str(e)}")
        else:
            QMessageBox.information(self, "تنبيه", "الرجاء اختيار ملف من الجدول")

    # دالة حذف مرفق
    # حذف المرفق
    def delete_attachment(self):
        current_row = self.attachments_table.currentRow()
        if current_row >= 0:
            file_name_item = self.attachments_table.item(current_row, 2)  # عمود اسم الملف
            file_path_item = self.attachments_table.item(current_row, 5)  # عمود المسار

            if file_name_item:
                file_name = file_name_item.text()

                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    f"هل أنت متأكد من حذف الملف '{file_name}'؟\n\nسيتم حذف الملف نهائياً من النظام.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    try:
                        # حذف الملف من النظام
                        if file_path_item:
                            file_path = file_path_item.text()
                            import os
                            if os.path.exists(file_path):
                                os.remove(file_path)

                        # حذف الصف من الجدول
                        self.attachments_table.removeRow(current_row)

                        # تحديث الفلاتر والإحصائيات
                        self.update_attachments_type_filter()
                        self.update_attachments_statistics()

                        QMessageBox.information(self, "نجح", f"تم حذف الملف '{file_name}' بنجاح")

                    except Exception as e:
                        QMessageBox.warning(self, "خطأ", f"فشل في حذف الملف: {str(e)}")
        else:
            QMessageBox.information(self, "تنبيه", "الرجاء اختيار ملف من الجدول")

    # ==================== دوال معالجة تاب دفعات المشروع ====================

    # دالة تحميل بيانات الدفعات
    # تحميل بيانات المدفوعات
    def load_payments_data(self):
        try:
            if not self.project_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, المبلغ_المدفوع, تاريخ_الدفع, وصف_المدفوع, 
                       طريقة_الدفع, خصم, المستلم
                FROM المشاريع_المدفوعات
                WHERE معرف_المشروع = %s
                ORDER BY تاريخ_الدفع DESC, id DESC
            """, (self.project_id,))

            rows = cursor.fetchall()
            self.payments_table.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data):
                    if col_idx == 0:  # عمود ID (مخفي)
                        item = QTableWidgetItem(str(data) if data is not None else "")
                        self.payments_table.setItem(row_idx, 0, item)
                    else:  # باقي الأعمدة مع إزاحة بسبب عمود الرقم التلقائي
                        item = QTableWidgetItem(str(data) if data is not None else "")
                        
                        # تنسيق خاص للمبلغ
                        if col_idx == 1:  # عمود المبلغ
                            try:
                                amount = float(data) if data else 0
                                item.setText(f"{amount:,.2f}")
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            except:
                                item.setText(str(data) if data else "0")
                        
                        # تنسيق خاص للخصم
                        elif col_idx == 5:  # عمود الخصم
                            try:
                                discount = float(data) if data else 0
                                item.setText(f"{discount:,.2f}")
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            except:
                                item.setText(str(data) if data else "0")
                        
                        # تنسيق خاص للتاريخ
                        elif col_idx == 2:  # عمود التاريخ
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        self.payments_table.setItem(row_idx, col_idx + 1, item)

            # إضافة الأرقام التلقائية
            self.add_auto_numbers_to_table(self.payments_table)

            # تحديث الإحصائيات
            self.update_payments_statistics()

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الدفعات: {e}")

    # دالة تحديث payments_statistics
    # تحديث إحصائيات المدفوعات
    def update_payments_statistics(self):
        try:
            if not hasattr(self, 'total_payments_count_label'):
                return

            if not self.project_id:
                # تعيين قيم افتراضية عند عدم وجود مشروع
                self.total_payments_count_label.setText("0 دفعة")
                self.total_payments_amount_label.setText(f"0 {Currency_type}")
                self.this_month_payments_label.setText(f"0 {Currency_type}")
                self.this_year_payments_label.setText(f"0 {Currency_type}")
                self.average_payment_label.setText(f"0 {Currency_type}")
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إحصائيات عامة
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    COALESCE(SUM(المبلغ_المدفوع), 0) as total,
                    COALESCE(AVG(المبلغ_المدفوع), 0) as average
                FROM المشاريع_المدفوعات
                WHERE معرف_المشروع = %s
            """, (self.project_id,))

            general_stats = cursor.fetchone()
            if general_stats:
                count, total, average = general_stats
                self.total_payments_count_label.setText(f"{count} دفعة")
                self.total_payments_amount_label.setText(f"{total:,.0f} {Currency_type}")
                self.average_payment_label.setText(f"{average:,.0f} {Currency_type}")

            # دفعات هذا الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE معرف_المشروع = %s 
                AND MONTH(تاريخ_الدفع) = MONTH(CURDATE())
                AND YEAR(تاريخ_الدفع) = YEAR(CURDATE())
            """, (self.project_id,))

            this_month = cursor.fetchone()
            if this_month:
                self.this_month_payments_label.setText(f"{this_month[0]:,.0f} {Currency_type}")

            # دفعات هذا العام
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE معرف_المشروع = %s 
                AND YEAR(تاريخ_الدفع) = YEAR(CURDATE())
            """, (self.project_id,))

            this_year = cursor.fetchone()
            if this_year:
                self.this_year_payments_label.setText(f"{this_year[0]:,.0f} {Currency_type}")

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الدفعات: {e}")

    # دالة تحميل payment_years
    # سنوات الدفع
    def load_payment_years(self):
        try:
            if not self.project_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT YEAR(تاريخ_الدفع) as year
                FROM المشاريع_المدفوعات
                WHERE معرف_المشروع = %s AND تاريخ_الدفع IS NOT NULL
                ORDER BY year DESC
            """, (self.project_id,))

            years = cursor.fetchall()
            for year in years:
                self.payment_year_filter_combo.addItem(str(year[0]))

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل سنوات الدفعات: {e}")

    # دالة تصفية payments_combined
    # مرشح المدفوعات مجتمعة
    def filter_payments_combined(self):
        if not hasattr(self, 'payments_table') or self.payments_table is None:
            return

        selected_method = self.payment_method_filter_combo.currentText()
        selected_year = self.payment_year_filter_combo.currentText()
        search_text = self.payments_search.text().lower()

        for row in range(self.payments_table.rowCount()):
            show_row = True

            # فلترة حسب طريقة الدفع
            if selected_method != "جميع الطرق":
                method_item = self.payments_table.item(row, 5)  # عمود طريقة الدفع
                if method_item:
                    if selected_method not in method_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب السنة
            if show_row and selected_year != "جميع السنوات":
                date_item = self.payments_table.item(row, 3)  # عمود التاريخ
                if date_item:
                    try:
                        date_text = date_item.text()
                        if selected_year not in date_text:
                            show_row = False
                    except:
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب البحث
            if show_row and search_text:
                row_match = False
                for col in range(self.payments_table.columnCount()):
                    item = self.payments_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_match = True
                        break
                if not row_match:
                    show_row = False

            self.payments_table.setRowHidden(row, not show_row)

    # دالة إضافة دفعة
    # أضف الدفع
    def add_payment(self):
        dialog = PaymentDialog(self, project_id=self.project_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_payments_data()
            self.load_project_info()  # تحديث المعلومات المالية
            self.load_statistics()  # تحديث الإحصائيات العامة

    # دالة تعديل دفعة
    # تحرير الدفع
    def edit_payment(self):
        current_row = self.payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد دفعة للتعديل")
            return

        payment_id_item = self.payments_table.item(current_row, 0)
        if not payment_id_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف الدفعة")
            return

        payment_id = int(payment_id_item.text())
        dialog = PaymentDialog(self, project_id=self.project_id, payment_id=payment_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_payments_data()
            self.load_project_info()  # تحديث المعلومات المالية
            self.load_statistics()  # تحديث الإحصائيات العامة

    # دالة حذف دفعة
    # حذف الدفع
    def delete_payment(self):
        current_row = self.payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد دفعة للحذف")
            return

        payment_id_item = self.payments_table.item(current_row, 0)
        amount_item = self.payments_table.item(current_row, 2)

        if not payment_id_item or not amount_item:
            QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات الدفعة")
            return

        payment_id = int(payment_id_item.text())
        amount = amount_item.text()

        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف الدفعة بمبلغ {amount}؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("DELETE FROM المشاريع_المدفوعات WHERE id = %s", (payment_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف الدفعة بنجاح")
                self.load_payments_data()
                self.load_project_info()  # تحديث المعلومات المالية
                self.load_statistics()  # تحديث الإحصائيات العامة

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف الدفعة: {str(e)}")

    # دالة طباعة إيصال الدفعة
    # استلام الدفع الطباعة
    def print_payment_receipt(self):
        current_row = self.payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد دفعة لطباعة الإيصال")
            return

        QMessageBox.information(self, "طباعة الإيصال", "سيتم فتح نافذة طباعة الإيصال")

    # دالة معالجة payments_table_double_click
    # على جدول المدفوعات انقر نقرًا مزدوجًا
    def on_payments_table_double_click(self, item):
        if item is not None:
            self.edit_payment()

    # ==================== التابات الخاصة بالمقاولات ====================

    # دالة إنشاء integrated_custody_tabs
    # إنشاء علامات تبويب حضانة متكاملة
    def create_integrated_custody_tabs(self):
        try:
            from إدارة_العهد_المالية import CustodyTabWidget, CustodyPaymentsTabWidget, CustodyExpensesTabWidget

            # تحضير بيانات المشروع
            project_data = {
                'id': self.project_id,
                'اسم_المشروع': self.project_data.get('اسم_المشروع', 'غير محدد'),
                'اسم_العميل': self.project_data.get('اسم_العميل', 'غير محدد'),
                'التصنيف': self.project_data.get('التصنيف', 'غير محدد')
            }

            # إنشاء تاب العهد المالية المدمج
            self.custody_tab_widget = CustodyTabWidget(
                parent=self,
                project_id=self.project_id,
                project_data=project_data
            )
            self.tab_widget.addTab(
                self.custody_tab_widget,
                qta.icon('fa5s.credit-card', color='#27ae60'),
                "العهد المالية"
            )

            # إنشاء تاب دفعات العهد المدمج
            self.custody_payments_tab_widget = CustodyPaymentsTabWidget(
                parent=self,
                project_id=self.project_id,
                project_data=project_data
            )
            self.tab_widget.addTab(
                self.custody_payments_tab_widget,
                qta.icon('fa5s.money-bill', color='#2ecc71'),
                "دفعات العهد"
            )

            # إنشاء تاب المصروفات المدمج
            self.custody_expenses_tab_widget = CustodyExpensesTabWidget(
                parent=self,
                project_id=self.project_id,
                project_data=project_data
            )
            self.tab_widget.addTab(
                self.custody_expenses_tab_widget,
                qta.icon('fa5s.receipt', color='#e74c3c'),
                "المصروفات"
            )

            # ربط التحديث بين التابات
            self.setup_custody_tabs_connections()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنشاء تابات العهد المالية: {str(e)}")
            # في حالة الفشل، استخدم التابات القديمة
            self.create_expenses_tab()
            self.create_custody_tab()
            self.create_custody_payments_tab()

    # دالة إعداد custody_tabs_connections
    # اتصالات علامات تبويب الحضانة الإعداد
    def setup_custody_tabs_connections(self):
        # ربط تحديث البيانات بين التابات
        if hasattr(self, 'custody_tab_widget'):
            # إضافة دالة تحديث العهد المالية للوصول من التابات الأخرى
            self.load_custody_data = self.custody_tab_widget.load_data

        if hasattr(self, 'custody_payments_tab_widget'):
            # إضافة دالة تحديث دفعات العهد
            self.load_custody_payments_data = self.custody_payments_tab_widget.load_data

        if hasattr(self, 'custody_expenses_tab_widget'):
            # إضافة دالة تحديث المصروفات
            self.load_expenses_data = self.custody_expenses_tab_widget.load_data

    # دالة إنشاء expenses_tab
    # إنشاء علامة تبويب النفقات
    def create_expenses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_expense_btn = QPushButton("إضافة")
        add_expense_btn.setIcon(qta.icon('fa5s.plus'))
        add_expense_btn.clicked.connect(self.add_expense)
        buttons_layout.addWidget(add_expense_btn)

        edit_expense_btn = QPushButton("تعديل")
        edit_expense_btn.setIcon(qta.icon('fa5s.edit'))
        edit_expense_btn.clicked.connect(self.edit_expense)
        buttons_layout.addWidget(edit_expense_btn)

        delete_expense_btn = QPushButton("حذف")
        delete_expense_btn.setIcon(qta.icon('fa5s.trash'))
        delete_expense_btn.clicked.connect(self.delete_expense)
        buttons_layout.addWidget(delete_expense_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # ComboBox للفلترة حسب رقم العهدة
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("فلترة حسب رقم العهدة:"))
        self.expenses_custody_filter_combo = QComboBox()
        self.expenses_custody_filter_combo.addItem("جميع العهد")
        self.expenses_custody_filter_combo.currentTextChanged.connect(self.filter_expenses_by_custody)
        filter_layout.addWidget(self.expenses_custody_filter_combo)

        # شريط البحث (في الجانب الأيسر)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.expenses_search = QLineEdit()
        self.expenses_search.setPlaceholderText("ابحث في المصروفات...")
        self.expenses_search.textChanged.connect(self.filter_expenses)
        search_layout.addWidget(self.expenses_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # جدول المصروفات
        self.expenses_table = QTableWidget()
        self.setup_expenses_table()
        layout.addWidget(self.expenses_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.calculator', color='#e74c3c'), "المصروفات")

    # دالة إعداد expenses_table
    # جدول مصاريف الإعداد
    def setup_expenses_table(self):
        headers = ["ID", "الرقم", "وصف المصروف", "المبلغ", "تاريخ المصروف", "المستلم", "طريقة الدفع", "رقم الفاتورة", "المورد", "فئة المصروف"]
        self.expenses_table.setColumnCount(len(headers))
        self.expenses_table.setHorizontalHeaderLabels(headers)
        self.expenses_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.expenses_table)

        # إضافة قائمة السياق للجدول (جدول فرعي - بدون خيار عرض)
        setup_table_context_menu(self.expenses_table, self, "مصروفات المشروع", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.expenses_table.itemDoubleClicked.connect(self.on_expenses_table_double_click)

    # دالة إنشاء custody_tab
    # إنشاء علامة تبويب الحضانة
    def create_custody_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_custody_btn = QPushButton("إضافة")
        add_custody_btn.setIcon(qta.icon('fa5s.plus'))
        add_custody_btn.clicked.connect(self.add_custody)
        buttons_layout.addWidget(add_custody_btn)

        edit_custody_btn = QPushButton("تعديل")
        edit_custody_btn.setIcon(qta.icon('fa5s.edit'))
        edit_custody_btn.clicked.connect(self.edit_custody)
        buttons_layout.addWidget(edit_custody_btn)

        delete_custody_btn = QPushButton("حذف")
        delete_custody_btn.setIcon(qta.icon('fa5s.trash'))
        delete_custody_btn.clicked.connect(self.delete_custody)
        buttons_layout.addWidget(delete_custody_btn)

        # إضافة الأزرار الجديدة لتاب العهد المالية
        transfer_custody_btn = QPushButton("ترحيل العهدة")
        transfer_custody_btn.setIcon(qta.icon('fa5s.exchange-alt'))
        transfer_custody_btn.clicked.connect(self.transfer_custody)
        buttons_layout.addWidget(transfer_custody_btn)

        # زر فتح نظام إدارة العهد المالية الشامل
        custody_management_btn = QPushButton("إدارة العهد الشاملة")
        custody_management_btn.setIcon(qta.icon('fa5s.cogs'))
        custody_management_btn.clicked.connect(self.open_custody_management_system)
        buttons_layout.addWidget(custody_management_btn)

        close_custody_btn = QPushButton("إغلاق العهدة")
        close_custody_btn.setIcon(qta.icon('fa5s.lock'))
        close_custody_btn.clicked.connect(self.close_custody)
        buttons_layout.addWidget(close_custody_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # ComboBox للفلترة حسب رقم العهدة
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("فلترة حسب رقم العهدة:"))
        self.custody_filter_combo = QComboBox()
        self.custody_filter_combo.addItem("جميع العهد")
        self.custody_filter_combo.currentTextChanged.connect(self.filter_custody_by_number)
        filter_layout.addWidget(self.custody_filter_combo)

        # شريط البحث (في الجانب الأيسر)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.custody_search = QLineEdit()
        self.custody_search.setPlaceholderText("ابحث في العهد المالية...")
        self.custody_search.textChanged.connect(self.filter_custody)
        search_layout.addWidget(self.custody_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # جدول العهد المالية
        self.custody_table = QTableWidget()
        self.setup_custody_table()
        layout.addWidget(self.custody_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.credit-card', color='#27ae60'), "العهد المالية")

    # دالة إعداد custody_table
    # جدول حضانة الإعداد
    def setup_custody_table(self):
        headers = ["ID", "الرقم", "رقم العهدة", "وصف العهدة", "مبلغ العهدة", "نسبة المكتب", "تاريخ الاستلام", "حالة العهدة", "المصروف", "المتبقي"]
        self.custody_table.setColumnCount(len(headers))
        self.custody_table.setHorizontalHeaderLabels(headers)
        self.custody_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.custody_table)

        # إضافة قائمة السياق للجدول (جدول فرعي - بدون خيار عرض)
        setup_table_context_menu(self.custody_table, self, "العهد المالية", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.custody_table.itemDoubleClicked.connect(self.on_custody_table_double_click)

    # دالة إنشاء custody_payments_tab
    # إنشاء علامة تبويب مدفوعات الحضانة
    def create_custody_payments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_custody_payment_btn = QPushButton("إضافة")
        add_custody_payment_btn.setIcon(qta.icon('fa5s.plus'))
        add_custody_payment_btn.clicked.connect(self.add_custody_payment)
        buttons_layout.addWidget(add_custody_payment_btn)

        edit_custody_payment_btn = QPushButton("تعديل")
        edit_custody_payment_btn.setIcon(qta.icon('fa5s.edit'))
        edit_custody_payment_btn.clicked.connect(self.edit_custody_payment)
        buttons_layout.addWidget(edit_custody_payment_btn)

        delete_custody_payment_btn = QPushButton("حذف")
        delete_custody_payment_btn.setIcon(qta.icon('fa5s.trash'))
        delete_custody_payment_btn.clicked.connect(self.delete_custody_payment)
        buttons_layout.addWidget(delete_custody_payment_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # شريط البحث (في الجانب الأيسر)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.custody_payments_search = QLineEdit()
        self.custody_payments_search.setPlaceholderText("ابحث في دفعات العهد...")
        self.custody_payments_search.textChanged.connect(self.filter_custody_payments)
        search_layout.addWidget(self.custody_payments_search)

        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # جدول دفعات العهد
        self.custody_payments_table = QTableWidget()
        self.setup_custody_payments_table()
        layout.addWidget(self.custody_payments_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.money-bill', color='#f39c12'), "دفعات العهد")

    # دالة إعداد custody_payments_table
    # جدول مدفوعات الحضانة الإعداد
    def setup_custody_payments_table(self):
        headers = ["ID", "الرقم", "رقم العهدة", "وصف الدفعة", "المبلغ", "تاريخ الدفعة", "نوع الدفعة", "طريقة الدفع", "المستلم"]
        self.custody_payments_table.setColumnCount(len(headers))
        self.custody_payments_table.setHorizontalHeaderLabels(headers)
        self.custody_payments_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.custody_payments_table)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.custody_payments_table.itemDoubleClicked.connect(self.on_custody_payments_table_double_click)

    # دالة إنشاء contractors_tab
    # إنشاء علامة تبويب المقاولين
    def create_contractors_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_contractor_btn = QPushButton("إضافة")
        add_contractor_btn.setIcon(qta.icon('fa5s.plus'))
        add_contractor_btn.clicked.connect(self.add_contractor)
        buttons_layout.addWidget(add_contractor_btn)

        edit_contractor_btn = QPushButton("تعديل")
        edit_contractor_btn.setIcon(qta.icon('fa5s.edit'))
        edit_contractor_btn.clicked.connect(self.edit_contractor)

        buttons_layout.addWidget(edit_contractor_btn)

        delete_contractor_btn = QPushButton("حذف")
        delete_contractor_btn.setIcon(qta.icon('fa5s.trash'))
        delete_contractor_btn.clicked.connect(self.delete_contractor)

        buttons_layout.addWidget(delete_contractor_btn)

        # إضافة الأزرار الجديدة لتاب المقاولين
        insert_balance_btn = QPushButton("إدراج الرصيد")
        insert_balance_btn.setIcon(qta.icon('fa5s.user-plus'))
        insert_balance_btn.clicked.connect(self.insert_contractor_balance)

        buttons_layout.addWidget(insert_balance_btn)

        insert_all_balances_btn = QPushButton("إدراج جميع الأرصدة")
        insert_all_balances_btn.setIcon(qta.icon('fa5s.users-cog'))
        insert_all_balances_btn.clicked.connect(self.insert_all_contractor_balances)

        buttons_layout.addWidget(insert_all_balances_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # ComboBox للفلترة حسب اسم المقاول
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("فلترة حسب المقاول:"))
        self.contractors_filter_combo = QComboBox()
        self.contractors_filter_combo.addItem("جميع المقاولين")
        self.contractors_filter_combo.currentTextChanged.connect(self.filter_contractors_by_name)
        filter_layout.addWidget(self.contractors_filter_combo)

        # شريط البحث (في الجانب الأيسر)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.contractors_search = QLineEdit()
        self.contractors_search.setPlaceholderText("ابحث في المقاولين...")
        self.contractors_search.textChanged.connect(self.filter_contractors)
        search_layout.addWidget(self.contractors_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # جدول المقاولين
        self.contractors_table = QTableWidget()
        self.setup_contractors_table()
        layout.addWidget(self.contractors_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.hard-hat', color='#8b4513'), "المقاولين")

    # دالة إعداد contractors_table
    # جدول المقاولين الإعداد
    def setup_contractors_table(self):
        headers = ["ID", "الرقم", "اسم المقاول", "التخصص", "رقم الهاتف", "العنوان", "تقييم الأداء", "الحالة"]
        self.contractors_table.setColumnCount(len(headers))
        self.contractors_table.setHorizontalHeaderLabels(headers)
        self.contractors_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.contractors_table)

        # إضافة قائمة السياق للجدول (جدول فرعي - بدون خيار عرض)
        setup_table_context_menu(self.contractors_table, self, "المقاولين", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.contractors_table.itemDoubleClicked.connect(self.on_contractors_table_double_click)

    # دالة إنشاء workers_tab
    # إنشاء علامة تبويب العمال
    def create_workers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_worker_btn = QPushButton("إضافة")
        add_worker_btn.setIcon(qta.icon('fa5s.plus'))
        add_worker_btn.clicked.connect(self.add_worker)

        buttons_layout.addWidget(add_worker_btn)

        edit_worker_btn = QPushButton("تعديل")
        edit_worker_btn.setIcon(qta.icon('fa5s.edit'))
        edit_worker_btn.clicked.connect(self.edit_worker)

        buttons_layout.addWidget(edit_worker_btn)

        delete_worker_btn = QPushButton("حذف")
        delete_worker_btn.setIcon(qta.icon('fa5s.trash'))
        delete_worker_btn.clicked.connect(self.delete_worker)

        buttons_layout.addWidget(delete_worker_btn)

        # إضافة الأزرار الجديدة لتاب العمال
        insert_balance_btn = QPushButton("إدراج الرصيد")
        insert_balance_btn.setIcon(qta.icon('fa5s.user-plus'))
        insert_balance_btn.clicked.connect(self.insert_worker_balance)

        buttons_layout.addWidget(insert_balance_btn)

        insert_all_balances_btn = QPushButton("إدراج جميع الأرصدة")
        insert_all_balances_btn.setIcon(qta.icon('fa5s.users-cog'))
        insert_all_balances_btn.clicked.connect(self.insert_all_worker_balances)

        buttons_layout.addWidget(insert_all_balances_btn)

        top_layout.addLayout(buttons_layout)

        # مساحة فارغة
        top_layout.addStretch()

        # ComboBox للفلترة حسب اسم العامل
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("فلترة حسب العامل:"))
        self.workers_filter_combo = QComboBox()
        self.workers_filter_combo.addItem("جميع العمال")
        self.workers_filter_combo.currentTextChanged.connect(self.filter_workers_by_name)
        filter_layout.addWidget(self.workers_filter_combo)

        # شريط البحث (في الجانب الأيسر)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.workers_search = QLineEdit()
        self.workers_search.setPlaceholderText("ابحث في العمال...")
        self.workers_search.textChanged.connect(self.filter_workers)
        search_layout.addWidget(self.workers_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # جدول العمال
        self.workers_table = QTableWidget()
        self.setup_workers_table()
        layout.addWidget(self.workers_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.tools', color='#95a5a6'), "العمال")

    # دالة إعداد workers_table
    # جدول العمال الإعداد
    def setup_workers_table(self):
        headers = ["ID", "الرقم", "اسم العامل", "التخصص", "الراتب اليومي", "أيام العمل", "الإجمالي", "المدفوع", "المتبقي"]
        self.workers_table.setColumnCount(len(headers))
        self.workers_table.setHorizontalHeaderLabels(headers)
        self.workers_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.workers_table)

        # إضافة قائمة السياق للجدول (جدول فرعي - بدون خيار عرض)
        setup_table_context_menu(self.workers_table, self, "العمال", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.workers_table.itemDoubleClicked.connect(self.on_workers_table_double_click)

    # دالة إنشاء losses_tab
    # إنشاء علامة تبويب الخسائر
    def create_losses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_loss_btn = QPushButton("إضافة خسارة")
        add_loss_btn.setIcon(qta.icon('fa5s.plus'))
        add_loss_btn.clicked.connect(self.add_loss)
        buttons_layout.addWidget(add_loss_btn)

        edit_loss_btn = QPushButton("تعديل")
        edit_loss_btn.setIcon(qta.icon('fa5s.edit'))
        edit_loss_btn.clicked.connect(self.edit_loss)
        buttons_layout.addWidget(edit_loss_btn)

        delete_loss_btn = QPushButton("حذف")
        delete_loss_btn.setIcon(qta.icon('fa5s.trash'))
        delete_loss_btn.clicked.connect(self.delete_loss)
        buttons_layout.addWidget(delete_loss_btn)

        top_layout.addLayout(buttons_layout)

        # تخطيط التصفية والبحث (في الجانب الأيسر)
        filter_layout = QHBoxLayout()

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.losses_search = QLineEdit()
        self.losses_search.setPlaceholderText("ابحث في الخسائر...")
        self.losses_search.textChanged.connect(self.filter_losses)
        search_layout.addWidget(self.losses_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # جدول الخسائر
        self.losses_table = QTableWidget()
        self.setup_losses_table()
        layout.addWidget(self.losses_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.exclamation-triangle', color='#e74c3c'), "الخسائر")

    # دالة إنشاء returns_tab
    # إنشاء علامة تبويب إرجاع
    def create_returns_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # تخطيط أفقي للأزرار وشريط البحث
        top_layout = QHBoxLayout()

        # أزرار العمليات (في الجانب الأيمن)
        buttons_layout = QHBoxLayout()

        add_return_btn = QPushButton("إضافة مردود")
        add_return_btn.setIcon(qta.icon('fa5s.plus'))
        add_return_btn.clicked.connect(self.add_return)
        buttons_layout.addWidget(add_return_btn)

        edit_return_btn = QPushButton("تعديل")
        edit_return_btn.setIcon(qta.icon('fa5s.edit'))
        edit_return_btn.clicked.connect(self.edit_return)
        buttons_layout.addWidget(edit_return_btn)

        delete_return_btn = QPushButton("حذف")
        delete_return_btn.setIcon(qta.icon('fa5s.trash'))
        delete_return_btn.clicked.connect(self.delete_return)
        buttons_layout.addWidget(delete_return_btn)

        top_layout.addLayout(buttons_layout)

        # تخطيط التصفية والبحث (في الجانب الأيسر)
        filter_layout = QHBoxLayout()

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.returns_search = QLineEdit()
        self.returns_search.setPlaceholderText("ابحث في المردودات...")
        self.returns_search.textChanged.connect(self.filter_returns)
        search_layout.addWidget(self.returns_search)

        filter_layout.addLayout(search_layout)
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)

        # جدول المردودات
        self.returns_table = QTableWidget()
        self.setup_returns_table()
        layout.addWidget(self.returns_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.undo', color='#f39c12'), "المردودات")

    # دالة إعداد losses_table
    # جدول خسائر الإعداد
    def setup_losses_table(self):
        headers = ["المعرف", "وصف الخسارة", "المبلغ", "التاريخ", "المسؤول", "متحمل الخسارة", "طريقة الدفع", "ملاحظات"]
        self.losses_table.setColumnCount(len(headers))
        self.losses_table.setHorizontalHeaderLabels(headers)
        self.losses_table.hideColumn(0)  # إخفاء عمود المعرف

        # تطبيق إعدادات الجدول
        table_setting(self.losses_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.losses_table, self, "الخسائر", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.losses_table.itemDoubleClicked.connect(self.on_losses_table_double_click)

    # دالة إعداد returns_table
    # إرجاع الإعداد الجدول
    def setup_returns_table(self):
        headers = ["المعرف", "وصف المردود", "المبلغ", "التاريخ", "المسؤول", "العهدة المردودة", "طريقة الدفع", "ملاحظات"]
        self.returns_table.setColumnCount(len(headers))
        self.returns_table.setHorizontalHeaderLabels(headers)
        self.returns_table.hideColumn(0)  # إخفاء عمود المعرف

        # تطبيق إعدادات الجدول
        table_setting(self.returns_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.returns_table, self, "المردودات", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.returns_table.itemDoubleClicked.connect(self.on_returns_table_double_click)

    # ==================== دوال معالجة الأحداث للمقاولات ====================

    # دالة تصفية expenses
    # مصاريف التصفية
    def filter_expenses(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'expenses_table') or self.expenses_table is None:
            return

        search_text = self.expenses_search.text().lower()
        for row in range(self.expenses_table.rowCount()):
            show_row = False
            for col in range(self.expenses_table.columnCount()):
                item = self.expenses_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.expenses_table.setRowHidden(row, not show_row)

    # دالة تصفية custody
    # مرشح الحضانة
    def filter_custody(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'custody_table') or self.custody_table is None:
            return

        search_text = self.custody_search.text().lower()
        for row in range(self.custody_table.rowCount()):
            show_row = False
            for col in range(self.custody_table.columnCount()):
                item = self.custody_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.custody_table.setRowHidden(row, not show_row)

    # دالة تصفية custody_payments
    # تصفية مدفوعات الحضانة
    def filter_custody_payments(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'custody_payments_table') or self.custody_payments_table is None:
            return

        search_text = self.custody_payments_search.text().lower()
        for row in range(self.custody_payments_table.rowCount()):
            show_row = False
            for col in range(self.custody_payments_table.columnCount()):
                item = self.custody_payments_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.custody_payments_table.setRowHidden(row, not show_row)

    # دالة تصفية contractors
    # مرشح المقاولين
    def filter_contractors(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'contractors_table') or self.contractors_table is None:
            return

        search_text = self.contractors_search.text().lower()
        for row in range(self.contractors_table.rowCount()):
            show_row = False
            for col in range(self.contractors_table.columnCount()):
                item = self.contractors_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.contractors_table.setRowHidden(row, not show_row)

    # دالة تصفية workers
    # تصفية العمال
    def filter_workers(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'workers_table') or self.workers_table is None:
            return

        search_text = self.workers_search.text().lower()
        for row in range(self.workers_table.rowCount()):
            show_row = False
            for col in range(self.workers_table.columnCount()):
                item = self.workers_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.workers_table.setRowHidden(row, not show_row)

    # دالة تصفية losses
    # خسائر تصفية
    def filter_losses(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'losses_table') or self.losses_table is None:
            return

        search_text = self.losses_search.text().lower()
        for row in range(self.losses_table.rowCount()):
            show_row = False
            for col in range(self.losses_table.columnCount()):
                item = self.losses_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.losses_table.setRowHidden(row, not show_row)

    # دالة تصفية returns
    # عودة المرشح
    def filter_returns(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'returns_table') or self.returns_table is None:
            return

        search_text = self.returns_search.text().lower()
        for row in range(self.returns_table.rowCount()):
            show_row = False
            for col in range(self.returns_table.columnCount()):
                item = self.returns_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.returns_table.setRowHidden(row, not show_row)

    # دوال إضافة/تعديل/حذف للمقاولات
    # دالة إضافة expense
    # أضف المصاريف
    def add_expense(self):
        try:
            from إدارة_العهد_المالية import CustodyExpenseDialog
            dialog = CustodyExpenseDialog(self, project_id=self.project_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_expenses_data()
                QMessageBox.information(self, "نجح", "تم إضافة المصروف بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إضافة المصروف: {str(e)}")

    # دالة تعديل expense
    # تحرير المصاريف
    def edit_expense(self):
        current_row = self.expenses_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار مصروف للتعديل")
            return

        try:
            expense_id_item = self.expenses_table.item(current_row, 0)
            if not expense_id_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المصروف")
                return

            expense_id = int(expense_id_item.text())

            from إدارة_العهد_المالية import CustodyExpenseDialog
            dialog = CustodyExpenseDialog(self, project_id=self.project_id, expense_id=expense_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_expenses_data()
                QMessageBox.information(self, "نجح", "تم تعديل المصروف بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة تعديل المصروف: {str(e)}")

    # دالة حذف expense
    # حذف المصاريف
    def delete_expense(self):
        current_row = self.expenses_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار مصروف للحذف")
            return

        try:
            expense_id_item = self.expenses_table.item(current_row, 0)
            expense_desc_item = self.expenses_table.item(current_row, 4)  # عمود وصف المصروف

            if not expense_id_item or not expense_desc_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات المصروف")
                return

            expense_id = int(expense_id_item.text())
            expense_desc = expense_desc_item.text()

            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل تريد حذف المصروف '{expense_desc}'؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("DELETE FROM المقاولات_مصروفات_العهد WHERE id = %s", (expense_id,))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف المصروف بنجاح")
                self.load_expenses_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حذف المصروف: {str(e)}")

    # دالة إضافة custody
    # أضف الحضانة
    def add_custody(self):
        try:
            from إدارة_العهد_المالية import CustodyDialog
            dialog = CustodyDialog(self, project_id=self.project_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_custody_data()
                QMessageBox.information(self, "نجح", "تم إضافة العهدة بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إضافة العهدة: {str(e)}")

    # دالة تعديل custody
    # تحرير الحضانة
    def edit_custody(self):
        current_row = self.custody_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار عهدة للتعديل")
            return

        try:
            custody_id_item = self.custody_table.item(current_row, 0)
            if not custody_id_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف العهدة")
                return

            custody_id = int(custody_id_item.text())

            from إدارة_العهد_المالية import CustodyDialog
            dialog = CustodyDialog(self, project_id=self.project_id, custody_id=custody_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_custody_data()
                QMessageBox.information(self, "نجح", "تم تعديل العهدة بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة تعديل العهدة: {str(e)}")

    # دالة حذف custody
    # حذف الحضانة
    def delete_custody(self):
        current_row = self.custody_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار عهدة للحذف")
            return

        try:
            custody_id_item = self.custody_table.item(current_row, 0)
            custody_number_item = self.custody_table.item(current_row, 2)  # عمود رقم العهدة

            if not custody_id_item or not custody_number_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات العهدة")
                return

            custody_id = int(custody_id_item.text())
            custody_number = custody_number_item.text()

            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل تريد حذف العهدة رقم '{custody_number}'؟\n"
                "سيتم حذف جميع الدفعات والمصروفات المرتبطة بها.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("DELETE FROM المقاولات_العهد WHERE id = %s", (custody_id,))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف العهدة بنجاح")
                self.load_custody_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حذف العهدة: {str(e)}")

    # دالة إضافة custody_payment
    # أضف دفع الحضانة
    def add_custody_payment(self):
        try:
            from إدارة_العهد_المالية import CustodyPaymentDialog
            dialog = CustodyPaymentDialog(self, project_id=self.project_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_custody_payments_data()
                self.load_custody_data()  # تحديث العهد أيضاً
                QMessageBox.information(self, "نجح", "تم إضافة دفعة العهد بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إضافة دفعة العهد: {str(e)}")

    # دالة تعديل custody_payment
    # تحرير دفع الحضانة
    def edit_custody_payment(self):
        current_row = self.custody_payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للتعديل")
            return

        try:
            payment_id_item = self.custody_payments_table.item(current_row, 0)
            if not payment_id_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف الدفعة")
                return

            payment_id = int(payment_id_item.text())

            from إدارة_العهد_المالية import CustodyPaymentDialog
            dialog = CustodyPaymentDialog(self, project_id=self.project_id, payment_id=payment_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_custody_payments_data()
                self.load_custody_data()  # تحديث العهد أيضاً
                QMessageBox.information(self, "نجح", "تم تعديل دفعة العهد بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة تعديل دفعة العهد: {str(e)}")

    # دالة حذف custody_payment
    # حذف دفع الحضانة
    def delete_custody_payment(self):
        current_row = self.custody_payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للحذف")
            return

        try:
            payment_id_item = self.custody_payments_table.item(current_row, 0)
            payment_desc_item = self.custody_payments_table.item(current_row, 3)  # عمود وصف الدفعة

            if not payment_id_item or not payment_desc_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات الدفعة")
                return

            payment_id = int(payment_id_item.text())
            payment_desc = payment_desc_item.text()

            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل تريد حذف الدفعة '{payment_desc}'؟\n"
                "سيتم تحديث مبلغ العهدة تلقائياً.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("DELETE FROM المقاولات_دفعات_العهد WHERE id = %s", (payment_id,))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف دفعة العهد بنجاح")
                self.load_custody_payments_data()
                self.load_custody_data()  # تحديث العهد أيضاً

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حذف دفعة العهد: {str(e)}")

    # دالة إضافة contractor
    # إضافة المقاول
    def add_contractor(self):
        QMessageBox.information(self, "إضافة مقاول", "سيتم فتح نافذة إضافة مقاول جديد")

    # دالة تعديل contractor
    # تحرير المقاول
    def edit_contractor(self):
        QMessageBox.information(self, "تعديل مقاول", "سيتم فتح نافذة تعديل المقاول")

    # دالة حذف contractor
    # حذف المقاول
    def delete_contractor(self):
        QMessageBox.information(self, "حذف مقاول", "سيتم حذف المقاول المحدد")

    # دالة إضافة worker
    # إضافة عامل
    def add_worker(self):
        QMessageBox.information(self, "إضافة عامل", "سيتم فتح نافذة إضافة عامل جديد")

    # دالة تعديل worker
    # تحرير العامل
    def edit_worker(self):
        QMessageBox.information(self, "تعديل عامل", "سيتم فتح نافذة تعديل العامل")

    # دالة حذف worker
    # حذف العامل
    def delete_worker(self):
        QMessageBox.information(self, "حذف عامل", "سيتم حذف العامل المحدد")

    # دالة إضافة loss
    # أضف الخسارة
    def add_loss(self):
        try:
            from إدارة_العهد_المالية import CustodyExpenseDialog

            # فتح حوار إضافة مصروف خسارة
            dialog = CustodyExpenseDialog(
                parent=self,
                project_id=self.project_id,
                expense_type="خسائر"
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_losses_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إضافة الخسارة: {str(e)}")

    # دالة تعديل loss
    # تحرير الخسارة
    def edit_loss(self):
        current_row = self.losses_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد خسارة للتعديل")
            return

        try:
            # الحصول على معرف الخسارة
            loss_id_item = self.losses_table.item(current_row, 0)
            if not loss_id_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف الخسارة")
                return

            loss_id = int(loss_id_item.text())

            from إدارة_العهد_المالية import CustodyExpenseDialog

            # فتح حوار تعديل الخسارة
            dialog = CustodyExpenseDialog(
                parent=self,
                project_id=self.project_id,
                expense_id=loss_id,
                expense_type="خسائر"
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_losses_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تعديل الخسارة: {str(e)}")

    # دالة حذف loss
    # حذف الخسارة
    def delete_loss(self):
        current_row = self.losses_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد خسارة للحذف")
            return

        # تأكيد الحذف
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل أنت متأكد من حذف هذه الخسارة؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # الحصول على معرف الخسارة
                loss_id_item = self.losses_table.item(current_row, 0)
                if not loss_id_item:
                    QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف الخسارة")
                    return

                loss_id = int(loss_id_item.text())

                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # حذف الخسارة
                cursor.execute("""
                    DELETE FROM المقاولات_مصروفات_العهد
                    WHERE id = %s AND نوع_المصروف = 'خسائر'
                """, (loss_id,))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف الخسارة بنجاح")
                self.load_losses_data()

            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في حذف الخسارة: {str(e)}")

    # دالة إضافة return
    # أضف العودة
    def add_return(self):
        try:
            from إدارة_العهد_المالية import CustodyExpenseDialog

            # فتح حوار إضافة مصروف مردود
            dialog = CustodyExpenseDialog(
                parent=self,
                project_id=self.project_id,
                expense_type="مردودات"
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_returns_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إضافة المردود: {str(e)}")

    # دالة تعديل return
    # تحرير العودة
    def edit_return(self):
        current_row = self.returns_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مردود للتعديل")
            return

        try:
            # الحصول على معرف المردود
            return_id_item = self.returns_table.item(current_row, 0)
            if not return_id_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المردود")
                return

            return_id = int(return_id_item.text())

            from إدارة_العهد_المالية import CustodyExpenseDialog

            # فتح حوار تعديل المردود
            dialog = CustodyExpenseDialog(
                parent=self,
                project_id=self.project_id,
                expense_id=return_id,
                expense_type="مردودات"
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_returns_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تعديل المردود: {str(e)}")

    # دالة حذف return
    # حذف العودة
    def delete_return(self):
        current_row = self.returns_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مردود للحذف")
            return

        # تأكيد الحذف
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا المردود؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # الحصول على معرف المردود
                return_id_item = self.returns_table.item(current_row, 0)
                if not return_id_item:
                    QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المردود")
                    return

                return_id = int(return_id_item.text())

                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # حذف المردود
                cursor.execute("""
                    DELETE FROM المقاولات_مصروفات_العهد
                    WHERE id = %s AND نوع_المصروف = 'مردودات'
                """, (return_id,))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف المردود بنجاح")
                self.load_returns_data()

            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في حذف المردود: {str(e)}")

    # ==================== دوال الأزرار الجديدة ====================

    # دوال تاب مراحل المشروع
    # دالة إدراج phase_amount
    # أدخل مبلغ المرحلة
    def insert_phase_amount(self):
        # الحصول على الصفوف المحددة
        selected_rows = []
        selected_items = self.phases_table.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مرحلة أو أكثر لإدراج المبلغ")
            return

        # استخراج أرقام الصفوف المحددة (بدون تكرار)
        for item in selected_items:
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)

        selected_rows.sort()  # ترتيب الصفوف

        try:
            phases_to_insert = []
            total_amount = 0
            already_inserted_count = 0

            # فحص كل صف محدد
            for row in selected_rows:
                phase_id_item = self.phases_table.item(row, 0)
                amount_item = self.phases_table.item(row, 7)  # عمود الإجمالي
                status_item = self.phases_table.item(row, 9)  # عمود حالة المبلغ
                phase_name_item = self.phases_table.item(row, 2)  # عمود اسم المرحلة

                if not phase_id_item or not amount_item:
                    continue

                phase_id = phase_id_item.text()
                amount = float(amount_item.text())
                current_status = status_item.text() if status_item else "غير مدرج"
                phase_name = phase_name_item.text() if phase_name_item else "غير محدد"

                if current_status == "تم الإدراج":
                    already_inserted_count += 1
                    continue

                phases_to_insert.append({
                    'id': phase_id,
                    'amount': amount,
                    'name': phase_name
                })
                total_amount += amount

            # التحقق من وجود مراحل للإدراج
            if not phases_to_insert:
                if already_inserted_count > 0:
                    QMessageBox.information(self, "معلومات", f"جميع المراحل المحددة ({already_inserted_count}) تم إدراجها مسبقاً")
                else:
                    QMessageBox.warning(self, "تحذير", "لا توجد مراحل صالحة للإدراج")
                return

            # رسالة التأكيد
            message = f"سيتم إدراج {len(phases_to_insert)} مرحلة بإجمالي مبلغ {total_amount:,.2f}\n"
            if already_inserted_count > 0:
                message += f"تم تجاهل {already_inserted_count} مرحلة مدرجة مسبقاً\n"
            message += "\nهل أنت متأكد من المتابعة؟"

            reply = QMessageBox.question(
                self,
                "تأكيد الإدراج",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # تحديث حالة المراحل
                phase_ids = [phase['id'] for phase in phases_to_insert]
                if phase_ids:
                    cursor.execute(f"""
                        UPDATE المشاريع_المراحل
                        SET حالة_المبلغ = 'تم الإدراج'
                        WHERE id IN ({','.join(['%s'] * len(phase_ids))})
                    """, phase_ids)

                    # تحديث إجمالي قيمة المشروع
                    cursor.execute("""
                        UPDATE المشاريع
                        SET المبلغ = المبلغ + %s
                        WHERE id = %s
                    """, (total_amount, self.project_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج {len(phases_to_insert)} مرحلة بإجمالي مبلغ {total_amount:,.2f} بنجاح")

                # تحديث البيانات
                self.refresh_all_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج المبلغ: {str(e)}")

    # دالة تحديث all_data
    # تحديث جميع البيانات
    def refresh_all_data(self):
        try:
            # تحديث البيانات المحلية
            self.load_phases_data()
            self.load_project_info()
            self.load_statistics()
            self.load_additional_info()
            self.update_phases_statistics()

            # تحديث النافذة الرئيسية إذا كانت متاحة
            self.update_main_window()

        except Exception as e:
            print(f"خطأ في تحديث البيانات: {e}")

    # دالة تحديث main_window
    # تحديث النافذة الرئيسية
    def update_main_window(self):
        try:
            # البحث عن النافذة الرئيسية
            main_window = self.find_main_window()
            if main_window:
                # تحديد نوع المشروع لتحديث القسم المناسب
                section_name = "المقاولات" if self.project_type == "المقاولات" else "المشاريع"

                # تحديث القسم في النافذة الرئيسية
                if hasattr(main_window, 'show_section'):
                    main_window.show_section(section_name)

                # تحديث عرض البطاقات إذا كان متاحاً
                if hasattr(main_window, 'update_cards_view'):
                    from PySide6.QtCore import QDate
                    year = str(QDate.currentDate().year())
                    main_window.update_cards_view(section_name, year)

        except Exception as e:
            print(f"خطأ في تحديث النافذة الرئيسية: {e}")

    # دالة إدراج all_phase_amounts
    # أدخل جميع مبالغ الطور
    def insert_all_phase_amounts(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب المراحل غير المدرجة
            cursor.execute("""
                SELECT id, الإجمالي FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s AND حالة_المبلغ = 'غير مدرج'
            """, (self.project_id,))

            phases = cursor.fetchall()

            if not phases:
                QMessageBox.information(self, "معلومات", "جميع المراحل تم إدراجها مسبقاً")
                conn.close()
                return

            total_amount = sum(phase[1] for phase in phases)

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج إجمالي مبلغ {total_amount:,.2f} من {len(phases)} مرحلة إلى إجمالي قيمة المشروع؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # تحديث حالة جميع المراحل
                phase_ids = [str(phase[0]) for phase in phases]
                cursor.execute(f"""
                    UPDATE المشاريع_المراحل
                    SET حالة_المبلغ = 'تم الإدراج'
                    WHERE id IN ({','.join(['%s'] * len(phase_ids))})
                """, phase_ids)

                # تحديث إجمالي قيمة المشروع
                cursor.execute("""
                    UPDATE المشاريع
                    SET المبلغ = المبلغ + %s
                    WHERE id = %s
                """, (total_amount, self.project_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج إجمالي مبلغ {total_amount:,.2f} من {len(phases)} مرحلة بنجاح")

                # تحديث البيانات
                self.refresh_all_data()
            else:
                conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج المبالغ: {str(e)}")

    # دالة إلغاء phase_amount
    # إلغاء مبلغ المرحلة
    def cancel_phase_amount(self):
        # الحصول على الصفوف المحددة
        selected_rows = []
        selected_items = self.phases_table.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مرحلة أو أكثر لإلغاء إدراج المبلغ")
            return

        # استخراج أرقام الصفوف المحددة (بدون تكرار)
        for item in selected_items:
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)

        selected_rows.sort()  # ترتيب الصفوف

        try:
            phases_to_cancel = []
            total_amount = 0
            not_inserted_count = 0

            # فحص كل صف محدد
            for row in selected_rows:
                phase_id_item = self.phases_table.item(row, 0)
                amount_item = self.phases_table.item(row, 7)  # عمود الإجمالي
                status_item = self.phases_table.item(row, 9)  # عمود حالة المبلغ
                phase_name_item = self.phases_table.item(row, 2)  # عمود اسم المرحلة

                if not phase_id_item or not amount_item:
                    continue

                phase_id = phase_id_item.text()
                amount = float(amount_item.text())
                current_status = status_item.text() if status_item else "غير مدرج"
                phase_name = phase_name_item.text() if phase_name_item else "غير محدد"

                if current_status == "غير مدرج":
                    not_inserted_count += 1
                    continue

                phases_to_cancel.append({
                    'id': phase_id,
                    'amount': amount,
                    'name': phase_name
                })
                total_amount += amount

            # التحقق من وجود مراحل لإلغاء الإدراج
            if not phases_to_cancel:
                if not_inserted_count > 0:
                    QMessageBox.information(self, "معلومات", f"جميع المراحل المحددة ({not_inserted_count}) غير مدرجة أصلاً")
                else:
                    QMessageBox.warning(self, "تحذير", "لا توجد مراحل صالحة لإلغاء الإدراج")
                return

            # رسالة التأكيد
            message = f"سيتم إلغاء إدراج {len(phases_to_cancel)} مرحلة بإجمالي مبلغ {total_amount:,.2f}\n"
            if not_inserted_count > 0:
                message += f"تم تجاهل {not_inserted_count} مرحلة غير مدرجة أصلاً\n"
            message += "\nهل أنت متأكد من المتابعة؟"

            reply = QMessageBox.question(
                self,
                "تأكيد إلغاء الإدراج",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # تحديث حالة المراحل
                phase_ids = [phase['id'] for phase in phases_to_cancel]
                if phase_ids:
                    cursor.execute(f"""
                        UPDATE المشاريع_المراحل
                        SET حالة_المبلغ = 'غير مدرج'
                        WHERE id IN ({','.join(['%s'] * len(phase_ids))})
                    """, phase_ids)

                    # تحديث إجمالي قيمة المشروع (طرح المبلغ)
                    cursor.execute("""
                        UPDATE المشاريع
                        SET المبلغ = المبلغ - %s
                        WHERE id = %s
                    """, (total_amount, self.project_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إلغاء إدراج {len(phases_to_cancel)} مرحلة بإجمالي مبلغ {total_amount:,.2f} بنجاح")

                # تحديث البيانات
                self.refresh_all_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إلغاء إدراج المبلغ: {str(e)}")

    # دالة تصفية phases_by_name
    # مراحل التصفية بالاسم
    def filter_phases_by_name(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'phases_table') or self.phases_table is None:
            return

        selected_phase = self.phases_filter_combo.currentText()

        for row in range(self.phases_table.rowCount()):
            if selected_phase == "جميع المراحل":
                self.phases_table.setRowHidden(row, False)
            else:
                phase_name_item = self.phases_table.item(row, 2)  # عمود اسم المرحلة
                if phase_name_item:
                    show_row = selected_phase in phase_name_item.text()
                    self.phases_table.setRowHidden(row, not show_row)
                else:
                    self.phases_table.setRowHidden(row, True)

    # دالة تصفية phases_combined
    # مراحل المرشح مجتمعة
    def filter_phases_combined(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'phases_table') or self.phases_table is None:
            return

        selected_phase = self.phases_filter_combo.currentText()
        selected_status = self.phases_amount_status_filter_combo.currentText()
        search_text = self.phases_search.text().lower()

        for row in range(self.phases_table.rowCount()):
            show_row = True

            # فلترة حسب اسم المرحلة
            if selected_phase != "جميع المراحل":
                phase_name_item = self.phases_table.item(row, 2)  # عمود اسم المرحلة
                if phase_name_item:
                    if selected_phase not in phase_name_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب حالة المبلغ
            if show_row and selected_status != "جميع الحالات":
                status_item = self.phases_table.item(row, 9)  # عمود حالة المبلغ
                if status_item:
                    if selected_status != status_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلترة حسب البحث
            if show_row and search_text:
                row_match = False
                for col in range(self.phases_table.columnCount()):
                    item = self.phases_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_match = True
                        break
                if not row_match:
                    show_row = False

            self.phases_table.setRowHidden(row, not show_row)

        # تحديث إحصائيات المراحل بعد الفلترة
        self.update_phases_statistics()

    # دالة تحديث phases_statistics
    # تحديث إحصائيات المراحل
    def update_phases_statistics(self):
        try:
            # التحقق من وجود البطاقات
            if not hasattr(self, 'phases_total_amount_label'):
                return

            # التحقق من وجود الجدول
            if not hasattr(self, 'phases_table') or self.phases_table is None:
                return

            total_amount = 0
            posted_amount = 0
            unposted_amount = 0

            # حساب الإحصائيات من الصفوف المرئية في الجدول
            for row in range(self.phases_table.rowCount()):
                if not self.phases_table.isRowHidden(row):
                    # الحصول على المبلغ الإجمالي
                    amount_item = self.phases_table.item(row, 7)  # عمود الإجمالي
                    status_item = self.phases_table.item(row, 9)  # عمود حالة المبلغ

                    if amount_item and amount_item.text():
                        try:
                            amount = float(amount_item.text())
                            total_amount += amount

                            # تصنيف المبلغ حسب الحالة
                            if status_item and status_item.text() == "تم الإدراج":
                                posted_amount += amount
                            else:
                                unposted_amount += amount
                        except ValueError:
                            continue

            # تحديث البطاقات
            self.phases_total_amount_label.setText(f"{total_amount:,.0f} {Currency_type}")
            self.phases_posted_amount_label.setText(f"{posted_amount:,.0f} {Currency_type}")
            self.phases_unposted_amount_label.setText(f"{unposted_amount:,.0f} {Currency_type}")

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المراحل: {e}")

    # دوال تاب فريق العمل
    # دالة إدراج engineer_balance
    # إدراج توازن مهندس
    def insert_engineer_balance(self):
        current_row = self.engineers_tasks_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد عضو فريق العمل لإدراج الرصيد")
            return

        try:
            # الحصول على معرف المهندس والمبلغ
            engineer_id_item = self.engineers_tasks_table.item(current_row, 0)
            amount_item = self.engineers_tasks_table.item(current_row, 5)  # عمود مبلغ المهندس
            status_item = self.engineers_tasks_table.item(current_row, 6)  # عمود حالة المبلغ

            if not engineer_id_item or not amount_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات عضو فريق العمل")
                return

            engineer_id = engineer_id_item.text()
            amount = float(amount_item.text())
            current_status = status_item.text() if status_item else "غير مدرج"

            if current_status == "تم الإدراج":
                QMessageBox.information(self, "معلومات", "تم إدراج رصيد عضو فريق العمل هذا مسبقاً")
                return

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج مبلغ {amount:,.2f} إلى رصيد عضو فريق العمل؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # تحديث حالة المبلغ في جدول مهام المهندسين
                cursor.execute("""
                    UPDATE المشاريع_مهام_الفريق
                    SET حالة_مبلغ_الموظف = 'تم الإدراج'
                    WHERE id = %s
                """, (engineer_id,))

                # إدراج المعاملة المالية في جدول الموظفين_معاملات_مالية
                from datetime import datetime
                current_date = datetime.now().date()

                # الحصول على معرف الموظف
                cursor.execute("""
                    SELECT معرف_الموظف FROM المشاريع_مهام_الفريق WHERE id = %s
                """, (engineer_id,))
                employee_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO الموظفين_معاملات_مالية
                    (معرف_الموظف, نوع_العملية, نوع_المعاملة, المبلغ, التاريخ, الوصف, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    employee_id,
                    'إيداع',
                    'إيداع مبلغ',
                    amount,
                    current_date,
                    f'رصيد من مشروع - {self.project_data.get("اسم_المشروع", "غير محدد")}',
                    'admin'
                ))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج معاملة مالية بمبلغ {amount:,.2f} لعضو فريق العمل بنجاح")
                self.load_engineers_tasks_data()
                self.load_statistics()
                self.load_additional_info()  # تحديث المعلومات الإضافية

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج الرصيد: {str(e)}")

    # دالة إدراج all_engineer_balances
    # أدخل جميع أرصدة المهندسين
    def insert_all_engineer_balances(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب مهام أعضاء فريق العمل غير المدرجة باستخدام معرف المشروع مباشرة
            cursor.execute("""
                SELECT id, معرف_الموظف, مبلغ_الموظف
                FROM المشاريع_مهام_الفريق
                WHERE معرف_المشروع = %s AND حالة_مبلغ_الموظف = 'غير مدرج'
            """, (self.project_id,))

            tasks = cursor.fetchall()

            if not tasks:
                QMessageBox.information(self, "معلومات", "جميع أرصدة أعضاء فريق العمل تم إدراجها مسبقاً")
                conn.close()
                return

            total_amount = sum(task[2] for task in tasks)

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج إجمالي مبلغ {total_amount:,.2f} لأرصدة {len(tasks)} عضو فريق عمل؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # تحديث حالة جميع المهام
                for task in tasks:
                    task_id, engineer_id, amount = task

                    # تحديث حالة المبلغ
                    cursor.execute("""
                        UPDATE المشاريع_مهام_الفريق
                        SET حالة_مبلغ_الموظف = 'تم الإدراج'
                        WHERE id = %s
                    """, (task_id,))

                    # إضافة المبلغ إلى رصيد عضو فريق العمل
                    cursor.execute("""
                        UPDATE الموظفين
                        SET الرصيد = الرصيد + %s
                        WHERE id = %s
                    """, (amount, engineer_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج إجمالي مبلغ {total_amount:,.2f} لأرصدة {len(tasks)} عضو فريق عمل بنجاح")
                self.load_engineers_tasks_data()
                self.load_statistics()
                self.load_additional_info()  # تحديث المعلومات الإضافية
            else:
                conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج الأرصدة: {str(e)}")

    # دالة إدراج all_employee_transactions
    # أدخل جميع معاملات الموظفين
    def insert_all_employee_transactions(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب مهام أعضاء فريق العمل غير المدرجة
            cursor.execute("""
                SELECT مم.id, مم.معرف_الموظف, مم.مبلغ_الموظف, م.اسم_الموظف
                FROM المشاريع_مهام_الفريق مم
                LEFT JOIN الموظفين م ON مم.معرف_الموظف = م.id
                WHERE مم.معرف_القسم = %s AND مم.حالة_مبلغ_الموظف = 'غير مدرج'
                AND مم.نوع_المهمة IN ('مهمة مشروع', 'مهمة مقاولات')
            """, (self.project_id,))

            tasks = cursor.fetchall()

            if not tasks:
                QMessageBox.information(self, "معلومات", "جميع أرصدة أعضاء فريق العمل تم إدراجها مسبقاً")
                conn.close()
                return

            total_amount = sum(task[2] for task in tasks)

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج إجمالي مبلغ {total_amount:,.2f} كمعاملات مالية لـ {len(tasks)} عضو فريق عمل؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                from datetime import datetime
                current_date = datetime.now().date()

                # إدراج المعاملات المالية لكل موظف
                for task in tasks:
                    task_id, employee_id, amount, _ = task

                    # تحديث حالة المبلغ في جدول مهام فريق العمل
                    cursor.execute("""
                        UPDATE المشاريع_مهام_الفريق
                        SET حالة_مبلغ_الموظف = 'تم الإدراج'
                        WHERE id = %s
                    """, (task_id,))

                    # إدراج المعاملة المالية في جدول الموظفين_معاملات_مالية
                    cursor.execute("""
                        INSERT INTO الموظفين_معاملات_مالية
                        (معرف_الموظف, نوع_العملية, نوع_المعاملة, المبلغ, التاريخ, الوصف, المستخدم)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        employee_id,
                        'إيداع',
                        'إيداع مبلغ',
                        amount,
                        current_date,
                        f'رصيد من مشروع - {self.project_data.get("اسم_المشروع", "غير محدد")}',
                        'admin'
                    ))

                conn.commit()
                conn.close()

                QMessageBox.information(
                    self, "نجح",
                    f"تم إدراج {len(tasks)} معاملة مالية بإجمالي مبلغ {total_amount:,.2f} بنجاح"
                )
                self.load_engineers_tasks_data()
                self.load_statistics()
                self.load_additional_info()  # تحديث المعلومات الإضافية
            else:
                conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج المعاملات المالية: {str(e)}")

    # دالة تصفية مهام المهندسين
    # مهام مهندسي التصفية
    def filter_engineers_tasks(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'engineers_tasks_table') or self.engineers_tasks_table is None:
            return

        search_text = self.engineers_search.text().lower()
        selected_member_type = self.member_type_filter_combo.currentText()
        selected_engineer = self.engineers_filter_combo.currentText()
        selected_amount_status = self.amount_status_filter_combo.currentText()

        for row in range(self.engineers_tasks_table.rowCount()):
            show_row = True

            # فلتر البحث النصي
            if search_text:
                row_text = ""
                for col in range(1, self.engineers_tasks_table.columnCount()):  # تجاهل عمود ID
                    item = self.engineers_tasks_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                if search_text not in row_text:
                    show_row = False

            # فلتر نوع العضو
            if show_row and selected_member_type != "جميع الأنواع":
                member_type_item = self.engineers_tasks_table.item(row, 3)  # عمود نوع العضو
                if member_type_item:
                    if selected_member_type not in member_type_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلتر اسم عضو فريق العمل
            if show_row and selected_engineer != "جميع أعضاء فريق العمل":
                engineer_name_item = self.engineers_tasks_table.item(row, 2)  # عمود عضو فريق العمل
                if engineer_name_item:
                    if selected_engineer not in engineer_name_item.text():
                        show_row = False
                else:
                    show_row = False

            # فلتر حالة المبلغ
            if show_row and selected_amount_status != "جميع الحالات":
                amount_status_item = self.engineers_tasks_table.item(row, 7)  # عمود حالة المبلغ
                if amount_status_item:
                    if selected_amount_status not in amount_status_item.text():
                        show_row = False
                else:
                    show_row = False

            self.engineers_tasks_table.setRowHidden(row, not show_row)

    # دوال تاب المقاولين
    # دالة إدراج contractor_balance
    # ملحق التوازن المقاول
    def insert_contractor_balance(self):
        current_row = self.contractors_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مقاول لإدراج الرصيد")
            return

        try:
            # الحصول على معرف المقاول والمبلغ
            contractor_id_item = self.contractors_table.item(current_row, 0)
            amount_item = self.contractors_table.item(current_row, 5)  # عمود مبلغ المقاول
            status_item = self.contractors_table.item(current_row, 6)  # عمود حالة المبلغ

            if not contractor_id_item or not amount_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات المقاول")
                return

            contractor_id = contractor_id_item.text()
            amount = float(amount_item.text())
            current_status = status_item.text() if status_item else "غير مدرج"

            if current_status == "تم الإدراج":
                QMessageBox.information(self, "معلومات", "تم إدراج رصيد هذا المقاول مسبقاً")
                return

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج مبلغ {amount:,.2f} إلى رصيد المقاول؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # تحديث حالة المبلغ في جدول مهام المقاولين
                cursor.execute("""
                    UPDATE المقاولات_مهام_المقاولين
                    SET حالة_مبلغ_المقاول = 'تم الإدراج'
                    WHERE id = %s
                """, (contractor_id,))

                # إضافة المبلغ إلى رصيد المقاول
                cursor.execute("""
                    UPDATE المقاولين
                    SET الرصيد = الرصيد + %s
                    WHERE id = (
                        SELECT معرف_المقاول FROM المقاولات_مهام_المقاولين WHERE id = %s
                    )
                """, (amount, contractor_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج المبلغ {amount:,.2f} إلى رصيد المقاول بنجاح")
                self.load_contractors_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج الرصيد: {str(e)}")

    # دالة إدراج all_contractor_balances
    # أدخل جميع أرصدة المقاول
    def insert_all_contractor_balances(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب مهام المقاولين غير المدرجة باستخدام معرف المشروع مباشرة
            cursor.execute("""
                SELECT id, معرف_المقاول, مبلغ_المقاول
                FROM المقاولات_مهام_المقاولين
                WHERE معرف_المشروع = %s AND حالة_مبلغ_المقاول = 'غير مدرج'
            """, (self.project_id,))

            tasks = cursor.fetchall()

            if not tasks:
                QMessageBox.information(self, "معلومات", "جميع أرصدة المقاولين تم إدراجها مسبقاً")
                conn.close()
                return

            total_amount = sum(task[2] for task in tasks)

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج إجمالي مبلغ {total_amount:,.2f} لأرصدة {len(tasks)} مقاول؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # تحديث حالة جميع المهام
                for task in tasks:
                    task_id, contractor_id, amount = task

                    # تحديث حالة المبلغ
                    cursor.execute("""
                        UPDATE المقاولات_مهام_المقاولين
                        SET حالة_مبلغ_المقاول = 'تم الإدراج'
                        WHERE id = %s
                    """, (task_id,))

                    # إضافة المبلغ إلى رصيد المقاول
                    cursor.execute("""
                        UPDATE المقاولين
                        SET الرصيد = الرصيد + %s
                        WHERE id = %s
                    """, (amount, contractor_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج إجمالي مبلغ {total_amount:,.2f} لأرصدة {len(tasks)} مقاول بنجاح")
                self.load_contractors_data()
            else:
                conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج الأرصدة: {str(e)}")

    # دالة تصفية contractors_by_name
    # تصفية المقاولين بالاسم
    def filter_contractors_by_name(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'contractors_table') or self.contractors_table is None:
            return

        selected_contractor = self.contractors_filter_combo.currentText()

        for row in range(self.contractors_table.rowCount()):
            if selected_contractor == "جميع المقاولين":
                self.contractors_table.setRowHidden(row, False)
            else:
                contractor_name_item = self.contractors_table.item(row, 2)  # عمود اسم المقاول
                if contractor_name_item:
                    show_row = selected_contractor in contractor_name_item.text()
                    self.contractors_table.setRowHidden(row, not show_row)
                else:
                    self.contractors_table.setRowHidden(row, True)

    # دوال تاب العمال
    # دالة إدراج worker_balance
    # أدخل توازن العامل
    def insert_worker_balance(self):
        current_row = self.workers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد عامل لإدراج الرصيد")
            return

        try:
            # الحصول على معرف العامل والمبلغ
            worker_id_item = self.workers_table.item(current_row, 0)
            amount_item = self.workers_table.item(current_row, 5)  # عمود مبلغ العامل
            status_item = self.workers_table.item(current_row, 6)  # عمود حالة المبلغ

            if not worker_id_item or not amount_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات العامل")
                return

            worker_id = worker_id_item.text()
            amount = float(amount_item.text())
            current_status = status_item.text() if status_item else "غير مدرج"

            if current_status == "تم الإدراج":
                QMessageBox.information(self, "معلومات", "تم إدراج رصيد هذا العامل مسبقاً")
                return

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج مبلغ {amount:,.2f} إلى رصيد العامل؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # تحديث حالة المبلغ في جدول مهام العمال
                cursor.execute("""
                    UPDATE المقاولات_مهام_العمال
                    SET حالة_مبلغ_العامل = 'تم الإدراج'
                    WHERE id = %s
                """, (worker_id,))

                # إضافة المبلغ إلى رصيد العامل
                cursor.execute("""
                    UPDATE العمال
                    SET الرصيد = الرصيد + %s
                    WHERE id = (
                        SELECT معرف_العامل FROM المقاولات_مهام_العمال WHERE id = %s
                    )
                """, (amount, worker_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج المبلغ {amount:,.2f} إلى رصيد العامل بنجاح")
                self.load_workers_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج الرصيد: {str(e)}")

    # دالة إدراج all_worker_balances
    # أدخل جميع أرصدة العمال
    def insert_all_worker_balances(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب مهام العمال غير المدرجة باستخدام معرف المشروع مباشرة
            cursor.execute("""
                SELECT id, معرف_العامل, مبلغ_العامل
                FROM المقاولات_مهام_العمال
                WHERE معرف_المشروع = %s AND حالة_مبلغ_العامل = 'غير مدرج'
            """, (self.project_id,))

            tasks = cursor.fetchall()

            if not tasks:
                QMessageBox.information(self, "معلومات", "جميع أرصدة العمال تم إدراجها مسبقاً")
                conn.close()
                return

            total_amount = sum(task[2] for task in tasks)

            # تأكيد العملية
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج إجمالي مبلغ {total_amount:,.2f} لأرصدة {len(tasks)} عامل؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # تحديث حالة جميع المهام
                for task in tasks:
                    task_id, worker_id, amount = task

                    # تحديث حالة المبلغ
                    cursor.execute("""
                        UPDATE المقاولات_مهام_العمال
                        SET حالة_مبلغ_العامل = 'تم الإدراج'
                        WHERE id = %s
                    """, (task_id,))

                    # إضافة المبلغ إلى رصيد العامل
                    cursor.execute("""
                        UPDATE العمال
                        SET الرصيد = الرصيد + %s
                        WHERE id = %s
                    """, (amount, worker_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم إدراج إجمالي مبلغ {total_amount:,.2f} لأرصدة {len(tasks)} عامل بنجاح")
                self.load_workers_data()
            else:
                conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إدراج الأرصدة: {str(e)}")

    # دالة تصفية workers_by_name
    # تصفية العمال بالاسم
    def filter_workers_by_name(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'workers_table') or self.workers_table is None:
            return

        selected_worker = self.workers_filter_combo.currentText()

        for row in range(self.workers_table.rowCount()):
            if selected_worker == "جميع العمال":
                self.workers_table.setRowHidden(row, False)
            else:
                worker_name_item = self.workers_table.item(row, 2)  # عمود اسم العامل
                if worker_name_item:
                    show_row = selected_worker in worker_name_item.text()
                    self.workers_table.setRowHidden(row, not show_row)
                else:
                    self.workers_table.setRowHidden(row, True)





    # دوال تاب الجدول الزمني
    # دالة إدارة timeline_status
    # إدارة حالة الجدول الزمني
    def manage_timeline_status(self):
        current_row = self.timeline_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد مهمة لإدارة حالتها")
            return

        # قائمة الحالات المتاحة
        statuses = ["لم يبدأ", "قيد التنفيذ", "منتهي", "متوقف"]

        current_status_item = self.timeline_table.item(current_row, 7)  # عمود الحالة
        current_status = current_status_item.text() if current_status_item else "لم يبدأ"

        # حوار اختيار الحالة الجديدة
        new_status, ok = QInputDialog.getItem(
            self, "تغيير الحالة",
            f"الحالة الحالية: {current_status}\nاختر الحالة الجديدة:",
            statuses, 0, False
        )

        if ok and new_status != current_status:
            try:
                # الحصول على معرف المهمة
                task_id_item = self.timeline_table.item(current_row, 0)
                if not task_id_item:
                    QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على معرف المهمة")
                    return

                task_id = task_id_item.text()

                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                # تحديث حالة المهمة
                cursor.execute("""
                    UPDATE المشاريع_مهام_الفريق
                    SET الحالة = %s
                    WHERE id = %s
                """, (new_status, task_id))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", f"تم تغيير الحالة إلى '{new_status}' بنجاح")
                self.load_timeline_data()
                self.update_timeline_statistics()

            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في تغيير الحالة: {str(e)}")

    # دالة تصفية timeline_by_status
    # تصفية الجدول الزمني حسب الحالة
    def filter_timeline_by_status(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'timeline_table') or self.timeline_table is None:
            return

        selected_status = self.timeline_status_filter_combo.currentText()

        for row in range(self.timeline_table.rowCount()):
            if selected_status == "جميع الحالات":
                self.timeline_table.setRowHidden(row, False)
            else:
                status_item = self.timeline_table.item(row, 7)  # عمود الحالة
                if status_item:
                    show_row = selected_status == status_item.text()
                    self.timeline_table.setRowHidden(row, not show_row)
                else:
                    self.timeline_table.setRowHidden(row, True)

    # دوال تاب المصروفات
    # دالة تصفية expenses_by_custody
    # مصاريف التصفية عن طريق الحجز
    def filter_expenses_by_custody(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'expenses_table') or self.expenses_table is None:
            return

        selected_custody = self.expenses_custody_filter_combo.currentText()

        for row in range(self.expenses_table.rowCount()):
            if selected_custody == "جميع العهد":
                self.expenses_table.setRowHidden(row, False)
            else:
                # البحث في عمود رقم العهدة (يجب تحديد العمود المناسب)
                custody_item = self.expenses_table.item(row, 3)  # افتراض أن رقم العهدة في العمود الرابع
                if custody_item:
                    show_row = selected_custody in custody_item.text()
                    self.expenses_table.setRowHidden(row, not show_row)
                else:
                    self.expenses_table.setRowHidden(row, True)

    # دوال تاب العهد المالية
    # دالة نقل العهدة
    # نقل الحضانة
    def transfer_custody(self):
        current_row = self.custody_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد عهدة للترحيل")
            return

        QMessageBox.information(self, "ترحيل العهدة", "سيتم فتح نافذة ترحيل العهدة")

    # دالة إغلاق العهدة
    # وثيق الحضانة
    def close_custody(self):
        current_row = self.custody_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد عهدة للإغلاق")
            return

        try:
            custody_id_item = self.custody_table.item(current_row, 0)
            custody_number_item = self.custody_table.item(current_row, 2)

            if not custody_id_item or not custody_number_item:
                QMessageBox.warning(self, "خطأ", "لا يمكن الحصول على بيانات العهدة")
                return

            custody_id = int(custody_id_item.text())
            custody_number = custody_number_item.text()

            # تأكيد الإغلاق
            reply = QMessageBox.question(
                self, "تأكيد الإغلاق",
                f"هل تريد إغلاق العهدة رقم {custody_number}؟\n"
                "لن تتمكن من إضافة مصروفات جديدة لهذه العهدة بعد الإغلاق.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                conn = mysql.connector.connect(
                    host=host, user=user_r, password=password_r,
                    database="project_manager_V2"
                )
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE المقاولات_العهد
                    SET حالة_العهدة = 'مغلقة', تاريخ_الإغلاق = CURDATE()
                    WHERE id = %s
                """, (custody_id,))

                conn.commit()
                conn.close()

                QMessageBox.information(self, "نجح", "تم إغلاق العهدة بنجاح")
                self.load_custody_data()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إغلاق العهدة: {str(e)}")

    # دالة فتح نظام إدارة العهد
    # نظام إدارة الحضانة المفتوح
    def open_custody_management_system(self):
        try:
            from إدارة_العهد_المالية import open_custody_management_system

            # تحضير بيانات المشروع
            project_data = {
                'id': self.project_id,
                'اسم_المشروع': self.project_data.get('اسم_المشروع', 'غير محدد'),
                'اسم_العميل': self.project_data.get('اسم_العميل', 'غير محدد'),
                'التصنيف': self.project_data.get('التصنيف', 'غير محدد')
            }

            # فتح النظام الشامل
            custody_system = open_custody_management_system(
                parent=self,
                project_id=self.project_id,
                project_data=project_data
            )

            if custody_system:
                # ربط إشارة الإغلاق بتحديث البيانات
                custody_system.finished.connect(self.refresh_all_custody_data)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نظام إدارة العهد المالية: {str(e)}")

    # دالة تحديث all_custody_data
    # تحديث جميع بيانات الحضانة
    def refresh_all_custody_data(self):
        try:
            self.load_custody_data()
            self.load_custody_payments_data()
            self.load_expenses_data()
        except Exception as e:
            print(f"خطأ في تحديث بيانات العهد: {e}")

    # دالة تصفية custody_by_number
    # مرشح الحضانة حسب الرقم
    def filter_custody_by_number(self):
        # التحقق من وجود الجدول
        if not hasattr(self, 'custody_table') or self.custody_table is None:
            return

        selected_custody = self.custody_filter_combo.currentText()

        for row in range(self.custody_table.rowCount()):
            if selected_custody == "جميع العهد":
                self.custody_table.setRowHidden(row, False)
            else:
                custody_number_item = self.custody_table.item(row, 2)  # عمود رقم العهدة
                if custody_number_item:
                    show_row = selected_custody in custody_number_item.text()
                    self.custody_table.setRowHidden(row, not show_row)
                else:
                    self.custody_table.setRowHidden(row, True)

    # دوال تحميل البيانات للفلاتر
    # دالة تحميل filter_data
    # تحميل بيانات مرشح
    def load_filter_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحميل أسماء المراحل للفلتر
            if hasattr(self, 'phases_filter_combo'):
                cursor.execute("""
                    SELECT DISTINCT اسم_المرحلة FROM المشاريع_المراحل
                    WHERE معرف_المشروع = %s AND اسم_المرحلة IS NOT NULL
                """, (self.project_id,))
                phases = cursor.fetchall()
                self.phases_filter_combo.clear()
                self.phases_filter_combo.addItem("جميع المراحل")
                for phase in phases:
                    self.phases_filter_combo.addItem(phase[0])

            # تحميل أسماء أعضاء فريق العمل للفلتر
            if hasattr(self, 'engineers_filter_combo'):
                cursor.execute("""
                    SELECT DISTINCT م.اسم_الموظف
                    FROM الموظفين م
                    JOIN المشاريع_مهام_الفريق مم ON م.id = مم.معرف_الموظف
                    JOIN المشاريع_المراحل مر ON مم.معرف_المرحلة = مر.id
                    WHERE مر.معرف_المشروع = %s
                """, (self.project_id,))
                engineers = cursor.fetchall()
                self.engineers_filter_combo.clear()
                self.engineers_filter_combo.addItem("جميع أعضاء فريق العمل")
                for engineer in engineers:
                    self.engineers_filter_combo.addItem(engineer[0])

            # تحميل أرقام العهد للفلاتر
            if hasattr(self, 'expenses_custody_filter_combo'):
                cursor.execute("""
                    SELECT DISTINCT رقم_العهدة FROM المقاولات_العهد
                    WHERE معرف_المشروع = %s AND رقم_العهدة IS NOT NULL
                """, (self.project_id,))
                custodies = cursor.fetchall()
                self.expenses_custody_filter_combo.clear()
                self.expenses_custody_filter_combo.addItem("جميع العهد")
                for custody in custodies:
                    self.expenses_custody_filter_combo.addItem(custody[0])

                if hasattr(self, 'custody_filter_combo'):
                    self.custody_filter_combo.clear()
                    self.custody_filter_combo.addItem("جميع العهد")
                    for custody in custodies:
                        self.custody_filter_combo.addItem(custody[0])

            # تحميل أسماء المقاولين للفلتر
            if hasattr(self, 'contractors_filter_combo'):
                cursor.execute("""
                    SELECT DISTINCT م.اسم_المقاول
                    FROM الموظفين م
                    JOIN المقاولات_مهام_المقاولين مم ON م.id = مم.معرف_المقاول
                    JOIN المشاريع_المراحل مر ON مم.معرف_المرحلة = مر.id
                    WHERE مر.معرف_المشروع = %s
                """, (self.project_id,))
                contractors = cursor.fetchall()
                self.contractors_filter_combo.clear()
                self.contractors_filter_combo.addItem("جميع المقاولين")
                for contractor in contractors:
                    self.contractors_filter_combo.addItem(contractor[0])

            # تحميل أسماء العمال للفلتر
            if hasattr(self, 'workers_filter_combo'):
                cursor.execute("""
                    SELECT DISTINCT ع.اسم_العامل
                    FROM العمال ع
                    JOIN المقاولات_مهام_العمال مع ON ع.id = مع.معرف_العامل
                    JOIN المشاريع_المراحل مر ON مع.معرف_المرحلة = مر.id
                    WHERE مر.معرف_المشروع = %s
                """, (self.project_id,))
                workers = cursor.fetchall()
                self.workers_filter_combo.clear()
                self.workers_filter_combo.addItem("جميع العمال")
                for worker in workers:
                    self.workers_filter_combo.addItem(worker[0])



            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الفلاتر: {e}")



    # دالة إضافة أزرار الطباعة
    # إضافة أزرار الطباعة
    def add_print_buttons(self):
        try:
            # إضافة أزرار الطباعة تلقائياً لجميع التابات
            quick_add_print_button(self, self.tab_widget)

        except Exception as e:
            print(f"خطأ في إضافة أزرار الطباعة: {e}")


# نافذة إدارة مهام المهندس
# نافذة إدارة مهام المهندس
# EngineerTaskDialog
class EngineerTaskDialog(QDialog):

    # دالة الإنشاء
    # init
    def __init__(self, parent=None, project_id=None, task_id=None):
        super().__init__(parent)
        self.project_id = project_id
        self.task_id = task_id
        self.is_edit_mode = task_id is not None
        self._engineer_changed_manually = False  # علامة لتتبع تغيير عضو فريق العمل يدوياً

        # تحديد نوع المشروع (المشاريع/المقاولات)
        self.project_type = self.get_project_type()

        self.setup_dialog()
        self.create_ui()

        if self.is_edit_mode:
            self.load_task_data()
        else:
            # في وضع الإضافة، تفعيل التعبئة التلقائية من البداية
            self._engineer_changed_manually = True

        apply_stylesheet(self)

    # دالة إعداد النافذة
    # مربع الحوار الإعداد
    def setup_dialog(self):
        title = "تعديل عضو فريق العمل" if self.is_edit_mode else "إضافة عضو فريق عمل جديد"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 600, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # دالة الحصول على نوع المشروع
    # احصل على نوع المشروع
    def get_project_type(self):
        try:
            if not self.project_id:
                return "المشاريع"

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT اسم_القسم FROM المشاريع WHERE id = %s", (self.project_id,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else "المشاريع"
        except Exception as e:
            print(f"خطأ في تحديد نوع المشروع: {e}")
            return "المشاريع"

    # دالة إنشاء واجهة المستخدم
    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # معلومات المهمة - ترتيب حسب قاعدة البيانات
        form_group = QGroupBox("معلومات المهمة")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)

        current_row = 0

        # 1. نوع العضو (يظهر فقط للمقاولات)
        if self.project_type == "المقاولات":
            form_layout.addWidget(QLabel("نوع العضو:"), current_row, 0)
            self.member_type_combo = QComboBox()
            self.member_type_combo.addItems(["مهندس", "مقاول", "عامل", "موظف"])
            self.member_type_combo.currentTextChanged.connect(self.on_member_type_changed)
            form_layout.addWidget(self.member_type_combo, current_row, 1)
            current_row += 1
        else:
            # للمشاريع، نوع العضو ثابت = مهندس
            self.member_type_combo = None

        # 2. عضو فريق العمل
        form_layout.addWidget(QLabel("عضو فريق العمل:"), current_row, 0)
        self.engineer_combo = QComboBox()
        self.engineer_combo.addItem("-- اختر عضو فريق العمل --", None)
        self.load_engineers()
        form_layout.addWidget(self.engineer_combo, current_row, 1)
        current_row += 1

        # 3. نوع دور المهمة
        form_layout.addWidget(QLabel("نوع دور المهمة:"), current_row, 0)
        self.task_role_combo = QComboBox()
        self.task_role_combo.addItems(["ربط بمرحلة", "دور عام"])
        self.task_role_combo.currentTextChanged.connect(self.on_task_role_changed)
        form_layout.addWidget(self.task_role_combo, current_row, 1)
        current_row += 1

        # 4. اختيار المرحلة (يظهر عند اختيار "ربط بمرحلة")
        self.phase_label = QLabel("المرحلة:")
        form_layout.addWidget(self.phase_label, current_row, 0)
        self.phase_combo = QComboBox()
        self.phase_combo.addItem("-- اختر المرحلة --", None)
        self.phase_combo.currentIndexChanged.connect(self.on_phase_changed)
        self.load_phases()
        form_layout.addWidget(self.phase_combo, current_row, 1)
        current_row += 1

        # 5. عنوان المهمة
        form_layout.addWidget(QLabel("عنوان المهمة:"), current_row, 0)
        self.task_title_edit = QLineEdit()
        self.task_title_edit.setPlaceholderText("سيتم تعبئته تلقائياً من المرحلة أو أدخله يدوياً")
        form_layout.addWidget(self.task_title_edit, current_row, 1)
        current_row += 1

        # 6. وصف المهمة
        form_layout.addWidget(QLabel("وصف المهمة:"), current_row, 0)
        self.task_description_edit = QTextEdit()
        self.task_description_edit.setMaximumHeight(80)
        self.task_description_edit.setPlaceholderText("سيتم تعبئته تلقائياً من المرحلة أو أدخله يدوياً")
        form_layout.addWidget(self.task_description_edit, current_row, 1)
        current_row += 1

        # المعلومات المالية
        financial_group = QGroupBox("المعلومات المالية")
        financial_layout = QGridLayout(financial_group)
        financial_layout.setSpacing(15)

        financial_row = 0

        # 7. نسبة الموظف
        financial_layout.addWidget(QLabel("نسبة الموظف (%):"), financial_row, 0)
        self.percentage_spin = QSpinBox()
        self.percentage_spin.setRange(0, 100)
        self.percentage_spin.setValue(0)
        self.percentage_spin.valueChanged.connect(self.calculate_amount)
        financial_layout.addWidget(self.percentage_spin, financial_row, 1)
        financial_row += 1

        # 8. مبلغ الموظف
        financial_layout.addWidget(QLabel("مبلغ الموظف:"), financial_row, 0)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(0.0)
        self.amount_spin.valueChanged.connect(self.calculate_percentage_from_amount)
        financial_layout.addWidget(self.amount_spin, financial_row, 1)
        financial_row += 1

        # 9. حالة مبلغ الموظف
        financial_layout.addWidget(QLabel("حالة مبلغ الموظف:"), financial_row, 0)
        self.amount_status_combo = QComboBox()
        self.amount_status_combo.addItems(["غير مدرج", "تم الإدراج"])
        financial_layout.addWidget(self.amount_status_combo, financial_row, 1)
        financial_row += 1

        layout.addWidget(form_group)
        layout.addWidget(financial_group)

        # الجدول الزمني
        schedule_group = QGroupBox("الجدول الزمني")
        schedule_layout = QGridLayout(schedule_group)
        schedule_layout.setSpacing(15)

        schedule_row = 0

        # 10. تاريخ البدء
        schedule_layout.addWidget(QLabel("تاريخ البدء:"), schedule_row, 0)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.dateChanged.connect(self.validate_dates)
        self.start_date.dateChanged.connect(self.sync_end_date)
        schedule_layout.addWidget(self.start_date, schedule_row, 1)
        schedule_row += 1

        # 11. تاريخ الانتهاء (ديفولت نفس تاريخ البدء)
        schedule_layout.addWidget(QLabel("تاريخ الانتهاء:"), schedule_row, 0)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())  # نفس تاريخ البدء
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.dateChanged.connect(self.validate_dates)
        schedule_layout.addWidget(self.end_date, schedule_row, 1)
        schedule_row += 1

        # 12. الحالة (حذف "منتهي" وإضافة "مكتملة")
        schedule_layout.addWidget(QLabel("الحالة:"), schedule_row, 0)
        self.task_status_combo = QComboBox()
        self.task_status_combo.addItems(["لم يبدأ", "قيد التنفيذ", "مكتملة", "ملغاة", "متأخرة", "متوقف"])
        self.task_status_combo.setCurrentText("لم يبدأ")  # الديفولت
        schedule_layout.addWidget(self.task_status_combo, schedule_row, 1)
        schedule_row += 1

        # 13. ملاحظات
        schedule_layout.addWidget(QLabel("ملاحظات:"), schedule_row, 0)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("أدخل ملاحظات إضافية...")
        schedule_layout.addWidget(self.notes_edit, schedule_row, 1)

        layout.addWidget(schedule_group)

        # إعداد الحالة الأولية للحقول
        self.on_task_role_changed()

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.setIcon(qta.icon('fa5s.save'))
        save_btn.clicked.connect(self.save_task)


        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setIcon(qta.icon('fa5s.times'))
        cancel_btn.clicked.connect(self.reject)


        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    # دالة معالجة member_type_changed
    # على نوع العضو تغيرت
    def on_member_type_changed(self):
        self.load_engineers()

    # دالة معالجة task_role_changed
    # على دور المهمة تغيرت
    def on_task_role_changed(self):
        task_role = self.task_role_combo.currentText()

        if task_role == "ربط بمرحلة":
            # إظهار حقول المرحلة
            self.phase_label.setVisible(True)
            self.phase_combo.setVisible(True)
            # تفعيل التعبئة التلقائية من المرحلة
            self.on_phase_changed()
        else:  # دور عام
            # إخفاء حقول المرحلة
            self.phase_label.setVisible(False)
            self.phase_combo.setVisible(False)
            # مسح العنوان والوصف التلقائي
            if not self.is_edit_mode:
                self.task_title_edit.clear()
                self.task_description_edit.clear()

    # دالة مزامنة end_date
    # تاريخ نهاية المزامنة
    def sync_end_date(self):
        if not self.is_edit_mode:  # فقط في وضع الإضافة
            self.end_date.setDate(self.start_date.date())

    # دالة معالجة phase_changed
    # في المرحلة تغيرت
    def on_phase_changed(self):
        try:
            phase_id = self.phase_combo.currentData()
            if not phase_id or self.task_role_combo.currentText() != "ربط بمرحلة":
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT اسم_المرحلة, وصف_المرحلة, الإجمالي
                FROM المشاريع_المراحل
                WHERE id = %s
            """, (phase_id,))

            result = cursor.fetchone()
            if result:
                phase_name, phase_description, phase_total = result

                # تعبئة العنوان والوصف تلقائياً
                self.task_title_edit.setText(phase_name or "")
                self.task_description_edit.setText(phase_description or "")

                # حفظ إجمالي المرحلة للحسابات المالية
                self.phase_total = phase_total or 0

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات المرحلة: {e}")
            self.phase_total = 0

    # دالة حساب المبلغ
    # حساب المبلغ
    def calculate_amount(self):
        try:
            percentage = self.percentage_spin.value()

            # إذا كان مرتبط بمرحلة، احسب من إجمالي المرحلة
            if (self.task_role_combo.currentText() == "ربط بمرحلة" and
                hasattr(self, 'phase_total') and self.phase_total > 0):
                amount = (percentage / 100) * self.phase_total
                self.amount_spin.setValue(amount)
            # إذا كان دور عام، يجب إدخال المبلغ يدوياً

        except Exception as e:
            print(f"خطأ في حساب المبلغ: {e}")



    # دالة تحميل phases
    # مراحل التحميل
    def load_phases(self):
        try:
            if not self.project_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_المرحلة, وصف_المرحلة FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s
                ORDER BY اسم_المرحلة
            """, (self.project_id,))

            phases = cursor.fetchall()
            self.phase_combo.clear()

            for phase_id, phase_name, phase_description in phases:
                # تنسيق العرض: اسم المرحلة - وصف المرحلة
                if phase_description and phase_description.strip():
                    display_text = f"{phase_name} - {phase_description}"
                else:
                    display_text = phase_name
                self.phase_combo.addItem(display_text, phase_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المراحل: {str(e)}")

    # دالة تحميل engineers
    # مهندسي الحمل
    def load_engineers(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحديد نوع العضو
            if self.member_type_combo:
                member_type = self.member_type_combo.currentText()
            else:
                member_type = "مهندس"  # للمشاريع

            # استعلام موحد لجلب الموظفين حسب التصنيف
            cursor.execute("""
                SELECT id, اسم_الموظف, الوظيفة, النسبة, التصنيف
                FROM الموظفين
                WHERE الحالة = 'نشط' AND التصنيف = %s
                ORDER BY اسم_الموظف
            """, (member_type,))

            engineers = cursor.fetchall()

            # الاحتفاظ بالاختيار الحالي إذا وجد
            current_selection = self.engineer_combo.currentData()
            self.engineer_combo.clear()

            # إضافة خيار فارغ في البداية
            self.engineer_combo.addItem("-- اختر عضو فريق العمل --", None)

            for engineer_id, engineer_name, job_title, default_percentage, classification in engineers:
                # تنسيق العرض: اسم الموظف - الوظيفة
                if job_title:
                    display_text = f"{engineer_name} - {job_title}"
                else:
                    display_text = engineer_name

                self.engineer_combo.addItem(display_text, engineer_id)

                # حفظ البيانات الإضافية
                self.engineer_combo.setItemData(self.engineer_combo.count() - 1,
                                              {
                                                  'id': engineer_id,
                                                  'default_percentage': default_percentage or 0,
                                                  'classification': classification
                                              },
                                              Qt.UserRole + 1)

            # استعادة الاختيار السابق إذا وجد
            if current_selection:
                for i in range(self.engineer_combo.count()):
                    if self.engineer_combo.itemData(i) == current_selection:
                        self.engineer_combo.setCurrentIndex(i)
                        break

            # ربط إشارة تغيير الاختيار بدالة التعبئة التلقائية
            self.engineer_combo.currentIndexChanged.connect(self.on_engineer_changed)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل أعضاء فريق العمل: {str(e)}")

    # دالة معالجة engineer_changed
    # على المهندس تغير
    def on_engineer_changed(self):
        try:
            # الحصول على البيانات الإضافية للموظف المحدد
            current_data = self.engineer_combo.currentData(Qt.UserRole + 1)

            if current_data and isinstance(current_data, dict):
                default_percentage = current_data.get('default_percentage', 0)

                # تعبئة النسبة الافتراضية فقط إذا كانت أكبر من صفر
                if default_percentage > 0:
                    # في وضع الإضافة، أو في وضع التعديل عند تغيير الموظف
                    if not self.is_edit_mode or getattr(self, '_engineer_changed_manually', True):
                        self.percentage_spin.setValue(int(default_percentage))
                        # تحديث المبلغ بناءً على النسبة الجديدة
                        self.calculate_amount()

        except Exception as e:
            print(f"خطأ في تعبئة النسبة الافتراضية: {e}")

    # دالة الحصول على engineer_default_percentage
    # احصل على النسبة الافتراضية للمهندس
    def get_engineer_default_percentage(self, engineer_id):
        try:
            if not engineer_id:
                return 0

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT النسبة FROM الموظفين WHERE id = %s", (engineer_id,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result and result[0] else 0

        except Exception as e:
            print(f"خطأ في جلب النسبة الافتراضية: {e}")
            return 0

    # دالة حساب المبلغ
    # حساب المبلغ
    def calculate_amount(self):
        try:
            phase_id = self.phase_combo.currentData()
            if not phase_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT الإجمالي FROM المشاريع_المراحل WHERE id = %s", (phase_id,))
            result = cursor.fetchone()

            if result:
                phase_total = float(result[0]) if result[0] else 0.0
                percentage = self.percentage_spin.value()
                amount = (phase_total * percentage) / 100
                self.amount_spin.setValue(amount)

            conn.close()

        except Exception as e:
            print(f"خطأ في حساب المبلغ: {e}")

    # دالة حساب percentage_from_amount
    # احسب النسبة المئوية من المبلغ
    def calculate_percentage_from_amount(self):
        try:
            # إذا كان مرتبط بمرحلة، احسب النسبة من إجمالي المرحلة
            if (self.task_role_combo.currentText() == "ربط بمرحلة" and
                hasattr(self, 'phase_total') and self.phase_total > 0):
                amount = self.amount_spin.value()
                percentage = (amount / self.phase_total) * 100
                self.percentage_spin.setValue(int(percentage))

        except Exception as e:
            print(f"خطأ في حساب النسبة: {e}")

    # دالة التحقق من التواريخ
    # التحقق من صحة التواريخ
    def validate_dates(self):
        if self.start_date.date() > self.end_date.date():
            # تعيين تاريخ الانتهاء ليكون بعد تاريخ البدء بـ 30 يوم
            self.end_date.setDate(self.start_date.date().addDays(30))
            QMessageBox.warning(self, "تحذير", "تم تعديل تاريخ الانتهاء ليكون بعد تاريخ البدء")

    # دالة تحميل بيانات المهمة
    # تحميل بيانات المهمة
    def load_task_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT مم.معرف_المرحلة, مم.معرف_الموظف, م.التصنيف as نوع_العضو, مم.نوع_دور_المهمة,
                       مم.عنوان_المهمة, مم.وصف_المهمة, مم.نسبة_الموظف, مم.مبلغ_الموظف,
                       مم.حالة_مبلغ_الموظف, مم.تاريخ_البدء, مم.تاريخ_الانتهاء, مم.الحالة, مم.ملاحظات
                FROM المشاريع_مهام_الفريق مم
                JOIN الموظفين م ON مم.معرف_الموظف = م.id
                WHERE مم.id = %s
            """, (self.task_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                (phase_id, employee_id, member_type, task_role, task_title, task_description,
                 percentage, amount, amount_status, start_date, end_date, task_status, notes) = result

                # تعيين نوع العضو (للمقاولات فقط)
                if self.member_type_combo:
                    self.member_type_combo.setCurrentText(member_type or "مهندس")
                    self.load_engineers()  # إعادة تحميل الأعضاء بناءً على النوع

                # تعيين نوع دور المهمة
                if task_role == "دور_عام":
                    self.task_role_combo.setCurrentText("دور عام")
                else:
                    self.task_role_combo.setCurrentText("ربط بمرحلة")

                self.on_task_role_changed()  # تحديث إظهار/إخفاء الحقول

                # تعيين المرحلة (إذا كانت مرتبطة بمرحلة)
                if phase_id:
                    for i in range(self.phase_combo.count()):
                        if self.phase_combo.itemData(i) == phase_id:
                            self.phase_combo.setCurrentIndex(i)
                            break

                # تعيين عضو فريق العمل (بدون تشغيل التعبئة التلقائية)
                self._engineer_changed_manually = False  # تعطيل التعبئة التلقائية مؤقتاً
                for i in range(self.engineer_combo.count()):
                    if self.engineer_combo.itemData(i) == employee_id:
                        self.engineer_combo.setCurrentIndex(i)
                        break

                # تعيين عنوان ووصف المهمة
                self.task_title_edit.setText(task_title or "")
                self.task_description_edit.setText(task_description or "")

                # تعيين البيانات المالية
                self.percentage_spin.setValue(percentage or 0)
                self.amount_spin.setValue(float(amount) if amount else 0.0)
                self.amount_status_combo.setCurrentText(amount_status or "غير مدرج")

                # تعيين التواريخ
                if start_date:
                    self.start_date.setDate(QDate.fromString(str(start_date), "yyyy-MM-dd"))
                if end_date:
                    self.end_date.setDate(QDate.fromString(str(end_date), "yyyy-MM-dd"))

                # تعيين حالة المهمة والملاحظات
                self.task_status_combo.setCurrentText(task_status or "لم يبدأ")
                self.notes_edit.setPlainText(notes or "")

                # تفعيل التعبئة التلقائية للتغييرات المستقبلية
                self._engineer_changed_manually = True

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المهمة: {str(e)}")

    # دالة حفظ المهمة
    # حفظ المهمة
    def save_task(self):
        # التحقق من صحة البيانات
        employee_id = self.engineer_combo.currentData()

        if not employee_id:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار عضو فريق العمل")
            return

        # التحقق من عنوان المهمة
        task_title = self.task_title_edit.text().strip()
        if not task_title:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال عنوان المهمة")
            return

        # تحديد نوع دور المهمة والتحقق من البيانات المطلوبة
        task_role = self.task_role_combo.currentText()
        phase_id = None

        if task_role == "ربط بمرحلة":
            phase_id = self.phase_combo.currentData()
            if not phase_id:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار المرحلة")
                return

        # جمع البيانات
        task_description = self.task_description_edit.toPlainText().strip()
        percentage = self.percentage_spin.value()
        amount = self.amount_spin.value()
        amount_status = self.amount_status_combo.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        task_status = self.task_status_combo.currentText()
        notes = self.notes_edit.toPlainText().strip()

        # التحقق من صحة التواريخ
        if self.start_date.date() > self.end_date.date():
            QMessageBox.warning(self, "تحذير", "تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء")
            return

        # تحويل نوع دور المهمة إلى قيمة قاعدة البيانات
        db_task_role = "ربط_بمرحلة" if task_role == "ربط بمرحلة" else "دور_عام"

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحديد نوع المهمة بناءً على نوع المشروع
            db_task_type = 'مهمة مقاولات' if self.project_type == "المقاولات" else 'مهمة مشروع'

            if self.is_edit_mode:
                # تحديث المهمة الموجودة
                cursor.execute("""
                    UPDATE المشاريع_مهام_الفريق
                    SET معرف_القسم = %s, معرف_المرحلة = %s, معرف_الموظف = %s, نوع_المهمة = %s,
                        عنوان_المهمة = %s, وصف_المهمة = %s, نوع_دور_المهمة = %s,
                        نسبة_الموظف = %s, مبلغ_الموظف = %s, حالة_مبلغ_الموظف = %s,
                        تاريخ_البدء = %s, تاريخ_الانتهاء = %s, الحالة = %s, ملاحظات = %s
                    WHERE id = %s
                """, (self.project_id, phase_id, employee_id, db_task_type, task_title, task_description,
                      db_task_role, percentage, amount, amount_status,
                      start_date, end_date, task_status, notes, self.task_id))

                message = "تم تحديث عضو فريق العمل بنجاح"
            else:
                # إضافة مهمة جديدة
                cursor.execute("""
                    INSERT INTO المشاريع_مهام_الفريق
                    (معرف_الموظف, نوع_المهمة, معرف_القسم, معرف_المرحلة, عنوان_المهمة,
                     وصف_المهمة, نوع_دور_المهمة, نسبة_الموظف, مبلغ_الموظف,
                     حالة_مبلغ_الموظف, تاريخ_البدء, تاريخ_الانتهاء, الحالة, ملاحظات, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (employee_id, db_task_type, self.project_id, phase_id, task_title, task_description,
                      db_task_role, percentage, amount, amount_status,
                      start_date, end_date, task_status, notes, "admin"))

                message = "تم إضافة عضو فريق العمل بنجاح"

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", message)
            self.accept()

        except mysql.connector.IntegrityError:
            QMessageBox.warning(self, "تحذير", "عضو فريق العمل هذا مُعيّن بالفعل لهذه المرحلة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ البيانات: {str(e)}")


# نافذة إدارة الجدول الزمني
# الجدول الزمني
class TimelineEntryDialog(QDialog):

    # دالة الإنشاء
    # init
    def __init__(self, parent=None, project_id=None, entry_id=None):
        super().__init__(parent)
        self.project_id = project_id
        self.entry_id = entry_id
        self.is_edit_mode = entry_id is not None

        self.setup_dialog()
        self.create_ui()

        if self.is_edit_mode:
            self.load_entry_data()

        apply_stylesheet(self)

    # دالة إعداد النافذة
    # مربع الحوار الإعداد
    def setup_dialog(self):
        title = "تعديل الجدولة الزمنية" if self.is_edit_mode else "إضافة جدولة زمنية جديدة"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 600, 450)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # دالة إنشاء واجهة المستخدم
    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # معلومات الجدولة
        form_group = QGroupBox("معلومات الجدولة الزمنية")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)

        # اختيار المرحلة
        form_layout.addWidget(QLabel("المرحلة:"), 0, 0)
        self.phase_combo = QComboBox()
        self.load_phases()
        form_layout.addWidget(self.phase_combo, 0, 1)

        # اختيار عضو فريق العمل
        form_layout.addWidget(QLabel("عضو فريق العمل:"), 1, 0)
        self.engineer_combo = QComboBox()
        self.load_engineers()
        form_layout.addWidget(self.engineer_combo, 1, 1)

        # تاريخ البداية
        form_layout.addWidget(QLabel("تاريخ البداية:"), 2, 0)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        form_layout.addWidget(self.start_date, 2, 1)

        # تاريخ النهاية
        form_layout.addWidget(QLabel("تاريخ النهاية:"), 3, 0)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(30))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        form_layout.addWidget(self.end_date, 3, 1)

        # الحالة
        form_layout.addWidget(QLabel("الحالة:"), 4, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["لم يبدأ", "قيد التنفيذ", "منتهي", "متوقف"])
        form_layout.addWidget(self.status_combo, 4, 1)

        # ملاحظات
        form_layout.addWidget(QLabel("ملاحظات:"), 5, 0)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        form_layout.addWidget(self.notes_edit, 5, 1)

        layout.addWidget(form_group)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.setIcon(qta.icon('fa5s.save'))
        save_btn.clicked.connect(self.save_entry)


        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setIcon(qta.icon('fa5s.times'))
        cancel_btn.clicked.connect(self.reject)


        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    # دالة تحميل phases
    # مراحل التحميل
    def load_phases(self):
        try:
            if not self.project_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_المرحلة, وصف_المرحلة FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s
                ORDER BY اسم_المرحلة
            """, (self.project_id,))

            phases = cursor.fetchall()
            self.phase_combo.clear()

            for phase_id, phase_name, phase_description in phases:
                # تنسيق العرض: اسم المرحلة - وصف المرحلة
                if phase_description and phase_description.strip():
                    display_text = f"{phase_name} - {phase_description}"
                else:
                    display_text = phase_name
                self.phase_combo.addItem(display_text, phase_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المراحل: {str(e)}")

    # دالة تحميل engineers
    # مهندسي الحمل
    def load_engineers(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_الموظف, الوظيفة FROM الموظفين
                WHERE الحالة = 'نشط'
                AND (التصنيف = 'مهندس' OR الوظيفة LIKE '%مهندس%')
                AND الوظيفة NOT LIKE '%استقبال%'
                AND الوظيفة NOT LIKE '%موظف%'
                AND الوظيفة NOT LIKE '%عامل%'
                ORDER BY اسم_الموظف
            """)

            engineers = cursor.fetchall()
            self.engineer_combo.clear()

            for engineer_id, engineer_name, job_title in engineers:
                # تنسيق العرض: اسم عضو فريق العمل - الوظيفة
                display_text = f"{engineer_name} - {job_title}" if job_title else engineer_name
                self.engineer_combo.addItem(display_text, engineer_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل أعضاء فريق العمل: {str(e)}")

    # دالة تحميل بيانات الإدخال
    # تحميل بيانات الإدخال
    def load_entry_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT معرف_المرحلة, معرف_الموظف, تاريخ_البدء, تاريخ_الانتهاء,
                       الحالة, ملاحظات
                FROM المشاريع_مهام_الفريق
                WHERE id = %s
            """, (self.entry_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                phase_id, engineer_id, start_date, end_date, status, notes = result

                # تعيين المرحلة
                for i in range(self.phase_combo.count()):
                    if self.phase_combo.itemData(i) == phase_id:
                        self.phase_combo.setCurrentIndex(i)
                        break

                # تعيين عضو فريق العمل
                for i in range(self.engineer_combo.count()):
                    if self.engineer_combo.itemData(i) == engineer_id:
                        self.engineer_combo.setCurrentIndex(i)
                        break

                # تعيين التواريخ
                if start_date:
                    self.start_date.setDate(QDate.fromString(str(start_date), "yyyy-MM-dd"))
                if end_date:
                    self.end_date.setDate(QDate.fromString(str(end_date), "yyyy-MM-dd"))

                # تعيين الحالة والملاحظات
                self.status_combo.setCurrentText(status or "لم يبدأ")
                self.notes_edit.setPlainText(notes or "")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الجدولة: {str(e)}")

    # دالة حفظ الإدخال
    # حفظ الدخول
    def save_entry(self):
        # التحقق من صحة البيانات
        phase_id = self.phase_combo.currentData()
        engineer_id = self.engineer_combo.currentData()

        if not phase_id:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار المرحلة")
            return

        if not engineer_id:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار عضو فريق العمل")
            return

        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()
        notes = self.notes_edit.toPlainText().strip()

        # التحقق من صحة التواريخ
        if self.start_date.date() > self.end_date.date():
            QMessageBox.warning(self, "تحذير", "تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحديد نوع المهمة بناءً على نوع المشروع
            task_type = 'مهمة مقاولات' if self.project_type == "المقاولات" else 'مهمة مشروع'
            task_title = "جدولة زمنية - فريق العمل"

            if self.is_edit_mode:
                # تحديث الجدولة الموجودة
                cursor.execute("""
                    UPDATE المشاريع_مهام_الفريق
                    SET معرف_القسم = %s, معرف_المرحلة = %s, معرف_الموظف = %s, تاريخ_البدء = %s,
                        تاريخ_الانتهاء = %s, الحالة = %s, ملاحظات = %s
                    WHERE id = %s
                """, (self.project_id, phase_id, engineer_id, start_date, end_date, status, notes, self.entry_id))

                message = "تم تحديث الجدولة الزمنية بنجاح"
            else:
                # إضافة جدولة جديدة
                cursor.execute("""
                    INSERT INTO المشاريع_مهام_الفريق
                    (معرف_الموظف, نوع_المهمة, معرف_القسم, معرف_المرحلة, عنوان_المهمة,
                     تاريخ_البدء, تاريخ_الانتهاء, الحالة, ملاحظات, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (engineer_id, task_type, self.project_id, phase_id, task_title,
                      start_date, end_date, status, notes, "admin"))

                message = "تم إضافة الجدولة الزمنية بنجاح"

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", message)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الجدولة: {str(e)}")


# نافذة إدارة مراحل المشروع
# phasedialog
class PhaseDialog(QDialog):

    # دالة الإنشاء
    # init
    def __init__(self, parent=None, project_id=None, phase_id=None, project_type="تصميم"):
        super().__init__(parent)
        self.project_id = project_id
        self.phase_id = phase_id
        self.project_type = project_type
        self.is_edit_mode = phase_id is not None

        # الحصول على التصنيف الفعلي للمشروع من قاعدة البيانات
        self.project_category = self.get_project_category()

        # متغير لتجنب التحديث التلقائي أثناء تحميل البيانات
        self.loading_data = False

        self.setup_dialog()
        self.create_ui()

        if self.is_edit_mode:
            self.load_phase_data()

        apply_stylesheet(self)

    # دالة الحصول على project_category
    # الحصول على فئة المشروع
    def get_project_category(self):
        try:
            if not self.project_id:
                return self.project_type

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب التصنيف الفعلي للمشروع
            cursor.execute("""
                SELECT التصنيف, اسم_القسم
                FROM المشاريع
                WHERE id = %s
            """, (self.project_id,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result and result[0]:
                # إرجاع التصنيف الفعلي
                return result[0]
            else:
                # إذا لم يوجد تصنيف، استخدم نوع المشروع العام
                return self.project_type

        except Exception as e:
            print(f"خطأ في جلب تصنيف المشروع: {e}")
            return self.project_type

    # دالة الحصول على phases_list_by_type
    # احصل على قائمة المراحل حسب النوع
    def get_phases_list_by_type(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحديد القسم ونوع المشروع (استخدام التصنيف الفعلي)
            section = "المقاولات" if self.project_type == "المقاولات" else "المشاريع"
            project_category = self.project_category  # استخدام التصنيف الفعلي

            

            # جلب المراحل من جدول أسعار المراحل باستخدام التصنيف الفعلي
            cursor.execute("""
                SELECT DISTINCT اسم_المرحلة
                FROM اسعار_المراحل
                WHERE اسم_القسم = %s AND معرف_التصنيف = %s
                ORDER BY اسم_المرحلة
            """, (section, project_category))

            phases_from_db = [row[0] for row in cursor.fetchall()]
            conn.close()

            print(f"تم العثور على {len(phases_from_db)} مرحلة في قاعدة البيانات")

            # إذا لم توجد مراحل في قاعدة البيانات، استخدم القائمة الافتراضية
            if not phases_from_db:
                print("لم توجد مراحل في قاعدة البيانات، استخدام القائمة الافتراضية")
                return self.get_default_phases_list()

            return phases_from_db

        except Exception as e:
            print(f"خطأ في تحميل المراحل من قاعدة البيانات: {e}")
            # في حالة الخطأ، استخدم القائمة الافتراضية
            return self.get_default_phases_list()

    # دالة الحصول على default_phases_list
    # احصل على قائمة المراحل الافتراضية
    def get_default_phases_list(self):
        if self.project_type == "المقاولات":
            return [
                # مراحل التأسيس
                "حفر الأساسات", "صب الخرسانة المسلحة", "أعمال العزل", "ردم وتسوية",
                # مراحل التنفيذ
                "بناء الجدران", "أعمال السقف", "تمديدات الكهرباء", "تمديدات السباكة", "أعمال التكييف",
                # مراحل التشطيب
                "أعمال البلاط", "أعمال الدهان", "تركيب الأبواب والنوافذ", "أعمال الديكور", "تنسيق الحدائق"
            ]
        else:  # للتصميم والأنواع الأخرى
            return [
                "الرفع المساحي", "مقترح مبدئي 2D", "تصميم 2D", "تصميم 3D",
                "تصميم إنشائي", "خرائط كهربائية", "خرائط صحية", "(الرندر) الإظهار",
                "رسومات التنفيذية", "تشطيب اللوحات والطباعة", "خرائط التبريد والتكييف",
                "خرائط منظومة إطفاء الحرائق", "خرائط منظومة الكميرات", "خرائط التدفئة المركزية"
            ]

    # دالة إعداد النافذة
    # مربع الحوار الإعداد
    def setup_dialog(self):
        title = "تعديل المرحلة" if self.is_edit_mode else "إضافة مرحلة جديدة"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 700, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # دالة إنشاء واجهة المستخدم
    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان النافذة
        title_label = QLabel("بيانات المرحلة")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("dialog_title_label")
        layout.addWidget(title_label)

        # إنشاء نموذج الإدخال
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # اسم المرحلة
        self.phase_name_combo = QComboBox()

        # إضافة خيار فارغ في البداية مع نص توضيحي
        self.phase_name_combo.addItem("-- اختر مرحلة أو اكتب اسم جديد --")

        # إضافة باقي المراحل
        phases_list = self.get_phases_list_by_type()
        self.phase_name_combo.addItems(phases_list)

        self.phase_name_combo.setEditable(True)

        # تعيين الخيار الفارغ كافتراضي في وضع الإضافة
        if not self.is_edit_mode:
            self.phase_name_combo.setCurrentIndex(0)  # الخيار الفارغ

        # ربط إشارة تغيير اختيار المرحلة بدالة التعبئة التلقائية
        self.phase_name_combo.currentTextChanged.connect(self.on_phase_name_changed)
        # ربط إشارة تغيير النص المكتوب يدوياً أيضاً
        self.phase_name_combo.editTextChanged.connect(self.on_phase_name_changed)
        # ربط إشارة النقر لإزالة النص التوضيحي
        self.phase_name_combo.lineEdit().focusInEvent = self.on_phase_name_focus
        form_layout.addRow("اسم المرحلة:", self.phase_name_combo)

        # وصف المرحلة
        self.description_edit = QLineEdit()
        self.description_edit.setAlignment(Qt.AlignCenter)
        form_layout.addRow("وصف المرحلة:", self.description_edit)

        # الوحدة
        self.unit_combo = QComboBox()
        units_list = ["متر مربع", "متر طولي", "قطعة", "مجموعة", "لوحة", "نسخة", "خدمة"]
        self.unit_combo.addItems(units_list)
        self.unit_combo.setEditable(True)
        form_layout.addRow("الوحدة:", self.unit_combo)

        # الكمية
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setAlignment(Qt.AlignCenter)
        form_layout.addRow("المساحة/الكمية:", self.quantity_spin)

        # السعر
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 999999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(1.00)
        self.price_spin.setAlignment(Qt.AlignCenter)
        form_layout.addRow("السعر:", self.price_spin)

        # الإجمالي (للعرض فقط)
        self.total_label = QLabel("0.00")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setObjectName("total_amount_label")
        form_layout.addRow("الإجمالي:", self.total_label)

        # ربط تحديث الإجمالي
        self.quantity_spin.valueChanged.connect(self.update_total)
        self.price_spin.valueChanged.connect(self.update_total)

        # ملاحظات
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_edit)

        # إضافة قسم تعيين عضو فريق العمل
        engineer_group = QGroupBox("تعيين عضو فريق العمل المسؤول (اختياري)")

        engineer_layout = QFormLayout(engineer_group)
        engineer_layout.setSpacing(12)
        engineer_layout.setLabelAlignment(Qt.AlignRight)

        # عضو فريق العمل المسؤول
        self.engineer_combo = QComboBox()
        self.engineer_combo.addItem("-- لا يوجد عضو فريق عمل مُعيّن --", None)
        self.load_engineers()
        engineer_layout.addRow("عضو فريق العمل المسؤول:", self.engineer_combo)

        # نسبة عضو فريق العمل
        self.engineer_percentage_spin = QSpinBox()
        self.engineer_percentage_spin.setRange(0, 100)
        self.engineer_percentage_spin.setValue(0)
        self.engineer_percentage_spin.setSuffix("%")
        self.engineer_percentage_spin.setAlignment(Qt.AlignCenter)
        self.engineer_percentage_spin.valueChanged.connect(self.calculate_engineer_amount)
        engineer_layout.addRow("نسبة عضو فريق العمل:", self.engineer_percentage_spin)

        # مبلغ عضو فريق العمل
        self.engineer_amount_spin = QDoubleSpinBox()
        self.engineer_amount_spin.setRange(0, 999999999.99)
        self.engineer_amount_spin.setDecimals(2)
        self.engineer_amount_spin.setValue(0.0)
        self.engineer_amount_spin.setAlignment(Qt.AlignCenter)
        self.engineer_amount_spin.valueChanged.connect(self.calculate_engineer_percentage)
        engineer_layout.addRow("مبلغ عضو فريق العمل:", self.engineer_amount_spin)

        layout.addLayout(form_layout)
        layout.addWidget(engineer_group)

        # أزرار الإجراءات
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # زر الحفظ
        self.save_btn = QPushButton("حفظ")
        self.save_btn.setIcon(qta.icon('fa5s.save'))
        self.save_btn.clicked.connect(self.save_phase)
        buttons_layout.addWidget(self.save_btn)

        # زر الإلغاء
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setIcon(qta.icon('fa5s.times'))
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

        # تحديث الإجمالي الأولي
        self.update_total()

    # دالة تحديث total
    # إجمالي تحديث
    def update_total(self):
        quantity = self.quantity_spin.value()
        price = self.price_spin.value()
        total = quantity * price
        self.total_label.setText(f"{total:,.2f}")
        # تحديث مبلغ عضو فريق العمل إذا كانت النسبة محددة
        self.calculate_engineer_amount()

    # دالة تحميل engineers
    # مهندسي الحمل
    def load_engineers(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_الموظف, الوظيفة, النسبة FROM الموظفين
                WHERE الحالة = 'نشط'
                AND (التصنيف = 'مهندس' OR الوظيفة LIKE '%مهندس%')
                AND الوظيفة NOT LIKE '%استقبال%'
                AND الوظيفة NOT LIKE '%موظف%'
                AND الوظيفة NOT LIKE '%عامل%'
                ORDER BY اسم_الموظف
            """)

            engineers = cursor.fetchall()

            for engineer_id, engineer_name, job_title, default_percentage in engineers:
                display_text = f"{engineer_name} - {job_title}" if job_title else engineer_name
                self.engineer_combo.addItem(display_text, engineer_id)
                # حفظ النسبة الافتراضية كبيانات إضافية
                self.engineer_combo.setItemData(self.engineer_combo.count() - 1,
                                              {'id': engineer_id, 'default_percentage': default_percentage or 0},
                                              Qt.UserRole + 1)

            # ربط إشارة تغيير الاختيار بدالة التعبئة التلقائية
            self.engineer_combo.currentIndexChanged.connect(self.on_engineer_changed)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل أعضاء فريق العمل: {e}")

    # دالة معالجة phase_name_changed
    # على اسم المرحلة تغيرت
    def on_phase_name_changed(self):
        try:
            # تجنب التحديث أثناء تحميل البيانات
            if hasattr(self, 'loading_data') and self.loading_data:
                return

            phase_name = self.phase_name_combo.currentText().strip()
            if not phase_name or phase_name.startswith("--"):
                # إذا كان الخيار فارغاً أو النص التوضيحي، إعادة تعيين عنوان النافذة
                title = "إضافة مرحلة جديدة" if not self.is_edit_mode else "تعديل المرحلة"
                self.setWindowTitle(title)
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحديد القسم ونوع المشروع (استخدام التصنيف الفعلي)
            section = "المقاولات" if self.project_type == "المقاولات" else "المشاريع"
            project_category = self.project_category  # استخدام التصنيف الفعلي

            print(f"البحث عن بيانات المرحلة: القسم={section}, التصنيف={project_category}, المرحلة={phase_name}")

            # جلب بيانات المرحلة من جدول أسعار المراحل باستخدام التصنيف الفعلي
            cursor.execute("""
                SELECT وصف_المرحلة, الوحدة, السعر, ملاحظات
                FROM اسعار_المراحل
                WHERE اسم_القسم = %s AND معرف_التصنيف = %s AND اسم_المرحلة = %s
                LIMIT 1
            """, (section, project_category, phase_name))

            result = cursor.fetchone()
            conn.close()

            if result:
                description, unit, price, notes = result
                

                # تعبئة الحقول تلقائياً (تحديث دائماً عند تغيير اسم المرحلة)
                if description:
                    self.description_edit.setText(description)

                if unit:
                    self.unit_combo.setCurrentText(unit)

                if price and price > 0:
                    self.price_spin.setValue(float(price))

                if notes:
                    self.notes_edit.setPlainText(notes)

                # تحديث الإجمالي
                self.update_total()

                # عرض رسالة تأكيد للمستخدم
                self.show_auto_fill_message(phase_name)

                # إظهار رسالة صغيرة في شريط العنوان
                self.setWindowTitle(f"إضافة مرحلة جديدة - تم تحميل بيانات '{phase_name}' تلقائياً")
            else:
                print(f"لم يتم العثور على بيانات للمرحلة '{phase_name}' في التصنيف '{project_category}'")
                # إعادة تعيين عنوان النافذة إذا لم توجد بيانات
                title = "إضافة مرحلة جديدة" if not self.is_edit_mode else "تعديل المرحلة"
                self.setWindowTitle(title)

        except Exception as e:
            print(f"خطأ في تعبئة بيانات المرحلة تلقائياً: {e}")

    # دالة معالجة phase_name_focus
    # على تركيز اسم المرحلة
    def on_phase_name_focus(self, event):
        try:
            current_text = self.phase_name_combo.currentText()
            if current_text.startswith("--"):
                self.phase_name_combo.setCurrentText("")
        except Exception as e:
            print(f"خطأ في معالج التركيز: {e}")

        # استدعاء الدالة الأصلية
        QLineEdit.focusInEvent(self.phase_name_combo.lineEdit(), event)

    # دالة إظهار auto_fill_message
    # عرض رسالة تعبئة تلقائية
    def show_auto_fill_message(self, phase_name):
        try:
            # عرض رسالة صغيرة في شريط الحالة أو كتلميح
            if hasattr(self, 'save_btn'):
                self.save_btn.setToolTip(f"تم تحميل بيانات المرحلة '{phase_name}' تلقائياً من قاعدة البيانات")
        except:
            pass

    # دالة معالجة engineer_changed
    # على المهندس تغير
    def on_engineer_changed(self):
        try:
            current_data = self.engineer_combo.currentData(Qt.UserRole + 1)
            if current_data and isinstance(current_data, dict):
                default_percentage = current_data.get('default_percentage', 0)
                if default_percentage > 0:
                    self.engineer_percentage_spin.setValue(int(default_percentage))
                    # تحديث المبلغ بناءً على النسبة الجديدة
                    self.calculate_engineer_amount()
        except Exception as e:
            print(f"خطأ في تعبئة النسبة الافتراضية: {e}")

    # دالة حساب engineer_amount
    # حساب كمية المهندس
    def calculate_engineer_amount(self):
        try:
            percentage = self.engineer_percentage_spin.value()
            if percentage > 0:
                total = self.quantity_spin.value() * self.price_spin.value()
                amount = (total * percentage) / 100
                # تجنب التحديث المتكرر
                self.engineer_amount_spin.blockSignals(True)
                self.engineer_amount_spin.setValue(amount)
                self.engineer_amount_spin.blockSignals(False)
        except Exception as e:
            print(f"خطأ في حساب مبلغ عضو فريق العمل: {e}")

    # دالة حساب engineer_percentage
    # حساب نسبة المهندس
    def calculate_engineer_percentage(self):
        try:
            amount = self.engineer_amount_spin.value()
            total = self.quantity_spin.value() * self.price_spin.value()
            if total > 0 and amount > 0:
                percentage = (amount * 100) / total
                if percentage <= 100:
                    # تجنب التحديث المتكرر
                    self.engineer_percentage_spin.blockSignals(True)
                    self.engineer_percentage_spin.setValue(int(percentage))
                    self.engineer_percentage_spin.blockSignals(False)
                else:
                    # إذا تجاوزت النسبة 100%، اعرض تحذير وأعد تعيين المبلغ
                    QMessageBox.warning(self, "تحذير", "مبلغ عضو فريق العمل لا يمكن أن يتجاوز إجمالي المرحلة")
                    max_amount = total
                    self.engineer_amount_spin.setValue(max_amount)
                    self.engineer_percentage_spin.setValue(100)
        except Exception as e:
            print(f"خطأ في حساب نسبة عضو فريق العمل: {e}")

    # دالة تحميل بيانات المرحلة
    # تحميل بيانات المرحلة
    def load_phase_data(self):
        try:
            # تعيين علامة تحميل البيانات لتجنب التحديث التلقائي
            self.loading_data = True

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحميل بيانات المرحلة
            cursor.execute("""
                SELECT اسم_المرحلة, وصف_المرحلة, الوحدة, الكمية, السعر, ملاحظات
                FROM المشاريع_المراحل
                WHERE id = %s
            """, (self.phase_id,))

            result = cursor.fetchone()

            if result:
                phase_name, description, unit, quantity, price, notes = result

                # تعبئة الحقول
                self.phase_name_combo.setCurrentText(phase_name or "")
                self.description_edit.setText(description or "")
                self.unit_combo.setCurrentText(unit or "")
                self.quantity_spin.setValue(quantity or 1)
                self.price_spin.setValue(float(price) if price else 0.0)
                self.notes_edit.setPlainText(notes or "")

                # تحديث الإجمالي
                self.update_total()

            # تحميل بيانات عضو فريق العمل المُعيّن (إن وجد)
            cursor.execute("""
                SELECT معرف_الموظف, نسبة_الموظف, مبلغ_الموظف
                FROM المشاريع_مهام_الفريق
                WHERE معرف_المرحلة = %s
                LIMIT 1
            """, (self.phase_id,))

            engineer_result = cursor.fetchone()
            if engineer_result:
                engineer_id, percentage, amount = engineer_result

                # تعيين عضو فريق العمل
                for i in range(self.engineer_combo.count()):
                    if self.engineer_combo.itemData(i) == engineer_id:
                        self.engineer_combo.setCurrentIndex(i)
                        break

                # تعيين النسبة والمبلغ
                self.engineer_percentage_spin.setValue(percentage or 0)
                self.engineer_amount_spin.setValue(float(amount) if amount else 0.0)

            conn.close()

            # إعادة تعيين علامة تحميل البيانات
            self.loading_data = False

        except Exception as e:
            # إعادة تعيين علامة تحميل البيانات في حالة الخطأ أيضاً
            self.loading_data = False
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المرحلة: {str(e)}")

    # دالة حفظ المرحلة
    # حفظ المرحلة
    def save_phase(self):
        # التحقق من صحة البيانات
        phase_name = self.phase_name_combo.currentText().strip()
        if not phase_name or phase_name.startswith("--"):
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم المرحلة")
            self.phase_name_combo.setFocus()
            return

        description = self.description_edit.text().strip()
        unit = self.unit_combo.currentText().strip()
        quantity = self.quantity_spin.value()
        price = self.price_spin.value()
        notes = self.notes_edit.toPlainText().strip()

        if quantity <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال كمية أكبر من صفر")
            self.quantity_spin.setFocus()
            return

        if price <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال سعر أكبر من صفر")
            self.price_spin.setFocus()
            return

        # الحصول على بيانات عضو فريق العمل
        engineer_id = self.engineer_combo.currentData()
        engineer_percentage = self.engineer_percentage_spin.value()
        engineer_amount = self.engineer_amount_spin.value()

        # التحقق من صحة بيانات عضو فريق العمل
        if engineer_id and engineer_percentage > 100:
            QMessageBox.warning(self, "تحذير", "نسبة عضو فريق العمل لا يمكن أن تتجاوز 100%")
            return

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # بدء المعاملة
            conn.start_transaction()

            if self.is_edit_mode:
                # تحديث المرحلة الموجودة
                cursor.execute("""
                    UPDATE المشاريع_المراحل
                    SET اسم_المرحلة = %s, وصف_المرحلة = %s, الوحدة = %s,
                        الكمية = %s, السعر = %s, ملاحظات = %s
                    WHERE id = %s
                """, (phase_name, description, unit, quantity, price, notes, self.phase_id))

                action_msg = f"تم تحديث المرحلة '{phase_name}' بنجاح"
                new_phase_id = self.phase_id
            else:
                # إضافة مرحلة جديدة
                cursor.execute("""
                    INSERT INTO المشاريع_المراحل
                    (معرف_المشروع, اسم_المرحلة, وصف_المرحلة, الوحدة, الكمية, السعر, ملاحظات, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.project_id, phase_name, description, unit, quantity, price, notes,
                    "admin",
                ))

                new_phase_id = cursor.lastrowid
                action_msg = f"تم إضافة المرحلة '{phase_name}' بنجاح"

                # إنشاء مهمة عضو فريق عمل تلقائياً إذا تم تعيين عضو فريق عمل
                if engineer_id and not self.is_edit_mode:
                    self.create_engineer_task(cursor, new_phase_id, engineer_id, engineer_percentage, engineer_amount)
                    action_msg += f"\nتم تعيين عضو فريق العمل للمرحلة تلقائياً"

                # التحقق من إمكانية حفظ المرحلة في جدول أسعار المراحل
                self.check_and_save_to_pricing_database(cursor, phase_name, description, unit, price, notes)

            # تأكيد المعاملة
            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", action_msg)
            self.accept()

        except mysql.connector.IntegrityError as e:
            conn.rollback()
            conn.close()
            if "unq_مرحلة_مهندس" in str(e):
                QMessageBox.warning(self, "تحذير", "عضو فريق العمل هذا مُعيّن بالفعل لهذه المرحلة")
            else:
                QMessageBox.critical(self, "خطأ", f"خطأ في قاعدة البيانات: {str(e)}")
        except Exception as e:
            conn.rollback()
            conn.close()
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المرحلة: {str(e)}")

    # دالة فحص and_save_to_pricing_database
    # تحقق وحفظ قاعدة بيانات التسعير
    def check_and_save_to_pricing_database(self, cursor, phase_name, description, unit, price, notes):
        try:
            # تحديد القسم ونوع المشروع (استخدام التصنيف الفعلي)
            section = "المقاولات" if self.project_type == "المقاولات" else "المشاريع"
            project_category = self.project_category  # استخدام التصنيف الفعلي

          
            # التحقق من عدم وجود المرحلة في جدول الأسعار
            cursor.execute("""
                SELECT id FROM اسعار_المراحل
                WHERE اسم_القسم = %s AND معرف_التصنيف = %s AND اسم_المرحلة = %s
            """, (section, project_category, phase_name))

            if not cursor.fetchone():
                # المرحلة غير موجودة في جدول الأسعار، اسأل المستخدم
                reply = QMessageBox.question(
                    self, "حفظ في قاعدة أسعار المراحل",
                    f"هل تريد حفظ المرحلة '{phase_name}' في قاعدة أسعار المراحل؟\n"
                    f"هذا سيجعلها متاحة للاستخدام في مشاريع أخرى من نفس النوع.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    cursor.execute("""
                        INSERT INTO اسعار_المراحل
                        (اسم_القسم, معرف_التصنيف, اسم_المرحلة, وصف_المرحلة,
                         الوحدة, السعر, ملاحظات)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (section, project_category, phase_name, description,
                          unit, price, notes))

                    

                    QMessageBox.information(
                        self, "تم الحفظ",
                        f"تم حفظ المرحلة '{phase_name}' في قاعدة أسعار المراحل بنجاح\n"
                        f"القسم: {section}\n"
                        f"التصنيف: {project_category}"
                    )

        except Exception as e:
            print(f"خطأ في حفظ المرحلة في جدول الأسعار: {e}")
            # لا نرفع الخطأ هنا لأن العملية الأساسية نجحت

    # دالة إنشاء engineer_task
    # إنشاء مهمة مهندس
    def create_engineer_task(self, cursor, phase_id, engineer_id, percentage, amount):
        try:
            from datetime import date

            current_date = date.today()

            # تحديد نوع المهمة بناءً على نوع المشروع
            task_type = 'مهمة مقاولات' if self.project_type == "المقاولات" else 'مهمة مشروع'
            task_title = "مهمة فريق عمل - مهندس"

            cursor.execute("""
                INSERT INTO المشاريع_مهام_الفريق
                (معرف_الموظف, نوع_المهمة, معرف_القسم, معرف_المرحلة, عنوان_المهمة,
                 نوع_العضو, نوع_دور_المهمة, نسبة_الموظف, مبلغ_الموظف, حالة_مبلغ_الموظف,
                 تاريخ_البدء, تاريخ_الانتهاء, الحالة, المستخدم)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                engineer_id, task_type, self.project_id, phase_id, task_title, "مهندس",
                "ربط_بمرحلة", percentage, amount, "غير مدرج", current_date, current_date,
                "لم يبدأ", "admin"
            ))

        except Exception as e:
            raise Exception(f"فشل في إنشاء مهمة عضو فريق العمل: {str(e)}")


# فئة نافذة حوار تحرير حالة المشروع
# نافذة تعديل حالة المشروع
# ProjectStatusedItDialog
class ProjectStatusEditDialog(QDialog):

    # دالة الإنشاء
    # init
    def __init__(self, parent, project_data):
        super().__init__(parent)
        self.parent = parent
        self.project_data = project_data
        self.project_id = project_data.get('id')

        # قائمة حالات المشروع المتاحة من قاعدة البيانات
        self.project_statuses = [
            'معلق',
            'منتهي',
            'تم التسليم',
            'متوقف',
            'تأكيد التسليم',
            'قيد الإنجاز'
        ]

        self.setup_ui()
        self.load_current_data()

    # دالة إعداد ui
    # إعداد واجهة المستخدم
    def setup_ui(self):
        self.setWindowTitle("تحرير حالة المشروع")
        self.setFixedSize(450, 350)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

        # سيتم تطبيق نمط النافذة من خلال الدالة المركزية

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان النافذة
        title_label = QLabel(f"تحرير حالة المشروع: {self.project_data.get('اسم_المشروع', 'غير محدد')}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("dialog_title_label")
        layout.addWidget(title_label)

        # نموذج الإدخال
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # عرض الحالة الحالية
        current_status_label = QLabel("الحالة الحالية:")
        self.current_status_display = QLabel()
        self.current_status_display.setObjectName("current_status_display")
        form_layout.addRow(current_status_label, self.current_status_display)

        # قائمة منسدلة للحالة الجديدة
        status_label = QLabel("الحالة الجديدة:")
        self.status_combo = QComboBox()
        self.status_combo.addItem("")  # خيار فارغ أولاً
        self.status_combo.addItems(self.project_statuses)
        form_layout.addRow(status_label, self.status_combo)

        # حقل التاريخ
        date_label = QLabel("تاريخ التسليم:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(date_label, self.date_edit)

        # خانة اختيار لتحديث التاريخ
        self.update_date_checkbox = QCheckBox("تحديث تاريخ التسليم")
        self.update_date_checkbox.setChecked(True)
        self.update_date_checkbox.setObjectName("update_date_checkbox")
        form_layout.addRow("", self.update_date_checkbox)

        layout.addLayout(form_layout)

        # مساحة فارغة
        layout.addStretch()

        # أزرار العمليات
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.setIcon(qta.icon('fa5s.save'))
        save_btn.clicked.connect(self.save_status)


        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setIcon(qta.icon('fa5s.times'))
        cancel_btn.clicked.connect(self.reject)


        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    # دالة تحميل current_data
    # تحميل البيانات الحالية
    def load_current_data(self):
        try:
            current_status = self.project_data.get('الحالة', 'غير محدد')
            self.current_status_display.setText(current_status)

            # تعيين الحالة الحالية كقيمة افتراضية في القائمة المنسدلة
            if current_status in self.project_statuses:
                self.status_combo.setCurrentText(current_status)

            # تحميل تاريخ التسليم الحالي إذا كان متاحاً
            delivery_date = self.project_data.get('تاريخ_التسليم')
            if delivery_date:
                try:
                    if isinstance(delivery_date, str):
                        date_obj = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                    else:
                        date_obj = delivery_date
                    self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                except:
                    pass

        except Exception as e:
            print(f"خطأ في تحميل البيانات الحالية: {e}")

    # دالة حفظ status
    # حفظ الحالة
    def save_status(self):
        try:
            # التحقق من صحة البيانات
            new_status = self.status_combo.currentText().strip()
            if not new_status:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار حالة المشروع الجديدة")
                return

            # التحقق من أن الحالة الجديدة مختلفة عن الحالة الحالية
            current_status = self.project_data.get('الحالة', '')
            if new_status == current_status and not self.update_date_checkbox.isChecked():
                QMessageBox.information(self, "تنبيه", "لم يتم إجراء أي تغيير")
                return

            # الحصول على التاريخ المحدد
            selected_date = self.date_edit.date().toString(Qt.ISODate)

            # الاتصال بقاعدة البيانات وتحديث الحالة
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحديث قاعدة البيانات
            if self.update_date_checkbox.isChecked():
                sql = "UPDATE المشاريع SET الحالة = %s, تاريخ_التسليم = %s WHERE id = %s"
                params = [new_status, selected_date, self.project_id]
                success_message = f"تم تحديث حالة المشروع بنجاح\n\nالحالة الجديدة: {new_status}\nتاريخ التسليم: {selected_date}"
            else:
                sql = "UPDATE المشاريع SET الحالة = %s WHERE id = %s"
                params = [new_status, self.project_id]
                success_message = f"تم تحديث حالة المشروع بنجاح\n\nالحالة الجديدة: {new_status}"

            cursor.execute(sql, params)
            conn.commit()

            if cursor.rowcount > 0:
                cursor.close()
                conn.close()

                # تحديث البيانات المحلية
                self.project_data['الحالة'] = new_status
                if self.update_date_checkbox.isChecked():
                    self.project_data['تاريخ_التسليم'] = selected_date

                # رسالة نجاح
                QMessageBox.information(self, "نجح", success_message)

                # تحديث النافذة الرئيسية والنوافذ الفرعية
                self.update_all_windows()

                self.accept()
            else:
                cursor.close()
                conn.close()
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على المشروع لتحديث حالته")

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"فشل في تحديث حالة المشروع:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع:\n{str(e)}")
            print(f"خطأ في save_status: {e}")

    # دالة تحديث جميع النوافذ
    # تحديث جميع النوافذ
    def update_all_windows(self):
        try:
            # تحديث نافذة معلومات المشروع (النافذة الأب)
            if hasattr(self.parent, 'refresh_project_data'):
                self.parent.refresh_project_data()
            if hasattr(self.parent, 'load_project_info'):
                self.parent.load_project_info()
            if hasattr(self.parent, 'load_timing_status_info'):
                self.parent.load_timing_status_info()
            if hasattr(self.parent, 'load_additional_info'):
                self.parent.load_additional_info()

            # تحديث النافذة الرئيسية
            main_window = self.find_main_window()
            if main_window:
                # تحديد نوع المشروع لتحديث القسم المناسب
                project_type = getattr(self.parent, 'project_type', 'المشاريع')
                section_name = "المقاولات" if project_type == "المقاولات" else "المشاريع"

                # تحديث القسم في النافذة الرئيسية
                if hasattr(main_window, 'show_section'):
                    main_window.show_section(section_name)

                # تحديث عرض البطاقات إذا كان متاحاً
                if hasattr(main_window, 'update_cards_view'):
                    from PySide6.QtCore import QDate
                    year = str(QDate.currentDate().year())
                    main_window.update_cards_view(section_name, year)

        except Exception as e:
            print(f"خطأ في تحديث النوافذ: {e}")

    # دالة العثور على النافذة الرئيسية
    # ابحث عن النافذة الرئيسية
    def find_main_window(self):
        try:
            # البحث في التسلسل الهرمي للنوافذ
            current_widget = self.parent
            while current_widget:
                if hasattr(current_widget, 'get_db_connection') and hasattr(current_widget, 'show_section'):
                    return current_widget
                current_widget = getattr(current_widget, 'parent', None)

            # البحث باستخدام QApplication.activeWindow
            from PySide6.QtWidgets import QApplication
            active_window = QApplication.activeWindow()
            if active_window and hasattr(active_window, 'get_db_connection') and hasattr(active_window, 'show_section'):
                return active_window

            return None

        except Exception as e:
            print(f"خطأ في البحث عن النافذة الرئيسية: {e}")
            return None


# دالة فتح النافذة الجديدة
# دالة فتح project_phases_window
# فتح نافذة مراحل المشروع
def open_project_phases_window(parent, project_data, project_type="تصميم"):
    """
    فتح نافذة إدارة المشروع مع البيانات المطلوبة
    """
    try:
        # إنشاء نافذة إدارة المشروع
        window = ProjectPhasesWindow(parent, project_data, project_type)
        window.show()
        return window
    except Exception as e:
        print(f"خطأ في فتح نافذة إدارة المشروع: {e}")
        return None


# نافذة إدارة الدفعات
# PaymentDialog
class PaymentDialog(QDialog):

    # دالة الإنشاء
    # init
    def __init__(self, parent=None, project_id=None, payment_id=None):
        super().__init__(parent)
        self.project_id = project_id
        self.payment_id = payment_id
        self.is_edit_mode = payment_id is not None

        self.setup_dialog()
        self.create_ui()

        if self.is_edit_mode:
            self.load_payment_data()

        apply_stylesheet(self)

    # دالة إعداد النافذة
    # مربع الحوار الإعداد
    def setup_dialog(self):
        title = "تعديل الدفعة" if self.is_edit_mode else "إضافة دفعة جديدة"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 500, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # دالة إنشاء واجهة المستخدم
    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # عنوان النافذة
        title_label = QLabel("بيانات الدفعة")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("dialog_title_label")
        layout.addWidget(title_label)

        # نموذج الإدخال
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # المبلغ المدفوع
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 999999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(1000.00)
        self.amount_spin.setAlignment(Qt.AlignCenter)
        form_layout.addRow("المبلغ المدفوع:", self.amount_spin)

        # تاريخ الدفع
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("تاريخ الدفع:", self.payment_date)

        # وصف المدفوع
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("دفعة من قيمة المشروع")
        form_layout.addRow("وصف المدفوع:", self.description_edit)

        # طريقة الدفع
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["نقدي", "بطاقة", "أجل/دين", "شيك", "تحويل بنكي"])
        form_layout.addRow("طريقة الدفع:", self.payment_method_combo)

        # الخصم
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0.00, 999999999.99)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setValue(0.00)
        self.discount_spin.setAlignment(Qt.AlignCenter)
        form_layout.addRow("الخصم:", self.discount_spin)

        # المستلم
        self.receiver_edit = QLineEdit()
        self.receiver_edit.setPlaceholderText("اسم المستلم")
        form_layout.addRow("المستلم:", self.receiver_edit)

        layout.addLayout(form_layout)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.setIcon(qta.icon('fa5s.save'))
        save_btn.clicked.connect(self.save_payment)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setIcon(qta.icon('fa5s.times'))
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)



    # دالة تحميل بيانات الدفعة
    # تحميل بيانات الدفع
    def load_payment_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT المبلغ_المدفوع, تاريخ_الدفع, وصف_المدفوع, 
                       طريقة_الدفع, خصم, المستلم
                FROM المشاريع_المدفوعات
                WHERE id = %s
            """, (self.payment_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                amount, payment_date, description, method, discount, receiver = result

                # تعبئة الحقول
                self.amount_spin.setValue(float(amount) if amount else 0.0)
                
                if payment_date:
                    self.payment_date.setDate(QDate.fromString(str(payment_date), "yyyy-MM-dd"))
                
                self.description_edit.setText(description or "")
                self.payment_method_combo.setCurrentText(method or "نقدي")
                self.discount_spin.setValue(float(discount) if discount else 0.0)
                self.receiver_edit.setText(receiver or "")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الدفعة: {str(e)}")

    # دالة حفظ الدفعة
    # حفظ الدفع
    def save_payment(self):
        # التحقق من صحة البيانات
        amount = self.amount_spin.value()
        if amount <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ أكبر من صفر")
            self.amount_spin.setFocus()
            return

        description = self.description_edit.text().strip()
        if not description:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال وصف للدفعة")
            self.description_edit.setFocus()
            return

        payment_date = self.payment_date.date().toString("yyyy-MM-dd")
        method = self.payment_method_combo.currentText()
        discount = self.discount_spin.value()
        receiver = self.receiver_edit.text().strip()

        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            if self.is_edit_mode:
                # تحديث الدفعة الموجودة
                cursor.execute("""
                    UPDATE المشاريع_المدفوعات
                    SET المبلغ_المدفوع = %s, تاريخ_الدفع = %s, وصف_المدفوع = %s,
                        طريقة_الدفع = %s, خصم = %s, المستلم = %s
                    WHERE id = %s
                """, (amount, payment_date, description, method, discount, receiver, self.payment_id))

                action_msg = "تم تحديث الدفعة بنجاح"
            else:
                # إضافة دفعة جديدة
                cursor.execute("""
                    INSERT INTO المشاريع_المدفوعات
                    (معرف_المشروع, المبلغ_المدفوع, تاريخ_الدفع, وصف_المدفوع,
                     طريقة_الدفع, خصم, المستلم, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.project_id, amount, payment_date, description, method, discount, receiver, "admin"))

                action_msg = "تم إضافة الدفعة بنجاح"

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", action_msg)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الدفعة: {str(e)}")
