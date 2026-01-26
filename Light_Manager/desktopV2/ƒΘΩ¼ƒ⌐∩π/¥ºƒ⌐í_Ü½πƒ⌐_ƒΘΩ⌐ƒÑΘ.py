# cSpell:disable
from الإعدادات_العامة import *
from أزرار_الواجهة import *
from DB import *
from ستايل import *
from تكوين_المشاريع import PROJECT_TYPES_CONFIG


# نافذة إدارة أسعار المراحل الشاملة
class PhasePricingManagementDialog(QDialog):
    
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_section = None
        self.current_project_type = None
        self.setup_ui()
        self.load_data()
        
    # إعداد واجهة المستخدم
    def setup_ui(self):
        self.setWindowTitle("إدارة أسعار المراحل")
        self.setGeometry(100, 100, 1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تطبيق الستايل
        apply_stylesheet(self)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # شريط الأدوات العلوي
        toolbar_layout = self.create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # المحتوى الرئيسي
        content_layout = QHBoxLayout()

        # الجانب الأيمن - قائمة الأقسام وأنواع المشاريع
        right_panel = self.create_sections_panel()
        content_layout.addWidget(right_panel, 1)

        # الجانب الأيسر - المحتوى الرئيسي (الجدول والإجراءات)
        left_panel = self.create_main_content_panel()
        content_layout.addWidget(left_panel, 4)
        
        main_layout.addLayout(content_layout)
        
        # شريط الحالة
        status_layout = self.create_status_bar()
        main_layout.addLayout(status_layout)
        
    # إنشاء شريط الأدوات العلوي
    def create_toolbar(self):
        toolbar_layout = QHBoxLayout()
        
        # زر إضافة مرحلة جديدة
        add_button = QPushButton("➕ إضافة مرحلة جديدة")
        add_button.setFont(QFont("Janna LT", 11, QFont.Bold))
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        add_button.clicked.connect(self.add_phase)
        toolbar_layout.addWidget(add_button)
        
        toolbar_layout.addStretch()
        
        # زر تحديث البيانات
        refresh_button = QPushButton("🔄 تحديث")
        refresh_button.setFont(QFont("Janna LT", 10))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        refresh_button.clicked.connect(self.refresh_all_data)
        toolbar_layout.addWidget(refresh_button)
        
        return toolbar_layout

    # إنشاء لوحة الأقسام وأنواع المشاريع
    def create_sections_panel(self):
        panel = QGroupBox("الأقسام وأنواع المشاريع")
        panel.setFont(QFont("Janna LT", 12, QFont.Bold))
        panel.setMaximumWidth(300)
        layout = QVBoxLayout(panel)

        # شجرة الأقسام وأنواع المشاريع
        self.sections_tree = QTreeWidget()
        self.sections_tree.setFont(QFont("Janna LT", 11))
        self.sections_tree.setHeaderLabel("الأقسام وأنواع المشاريع")
        self.sections_tree.itemClicked.connect(self.on_section_item_selected)

        # تحسين مظهر الشجرة
        self.sections_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 8px 5px;
                margin: 1px;
                border-radius: 3px;
                min-height: 25px;
            }
            QTreeWidget::item:selected {
                background-color: #007bff;
                color: white;
                font-weight: bold;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTreeWidget::branch {
                background: transparent;
                width: 20px;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
                background: transparent;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
                background: transparent;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed:hover,
            QTreeWidget::branch:closed:has-children:has-siblings:hover {
                background-color: #e3f2fd;
                border-radius: 3px;
            }
            QTreeWidget::branch:open:has-children:!has-siblings:hover,
            QTreeWidget::branch:open:has-children:has-siblings:hover {
                background-color: #e3f2fd;
                border-radius: 3px;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
                background-color: transparent;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
                background-color: transparent;
            }
        """)

        layout.addWidget(self.sections_tree)

        # تحميل الأقسام وأنواع المشاريع
        self.load_sections_tree()

        return panel


    # إنشاء اللوحة الرئيسية
    def create_main_content_panel(self):
        panel = QGroupBox("أسعار المراحل")
        panel.setFont(QFont("Janna LT", 12, QFont.Bold))
        layout = QVBoxLayout(panel)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث:")
        search_label.setFont(QFont("Janna LT", 11, QFont.Bold))
        search_layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ابحث في اسم المرحلة أو الوصف...")
        self.search_edit.setFont(QFont("Janna LT", 10))
        self.search_edit.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_edit)

        layout.addLayout(search_layout)

        # إنشاء الجدول
        self.phases_table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.phases_table)

        return panel
        
    # إعداد جدول أسعار المراحل
    def setup_table(self):
        headers = [
            "ID", "القسم", "نوع المشروع", "اسم المرحلة", 
            "وصف المرحلة", "الوحدة", "السعر", "ملاحظات", 
            "تاريخ الإنشاء", "الإجراءات"
        ]
        
        self.phases_table.setColumnCount(len(headers))
        self.phases_table.setHorizontalHeaderLabels(headers)
        self.phases_table.hideColumn(0)  # إخفاء عمود ID
        
        # تطبيق إعدادات الجدول
        table_setting(self.phases_table)
        
        # تعيين عرض الأعمدة
        self.phases_table.setColumnWidth(1, 100)  # القسم
        self.phases_table.setColumnWidth(2, 120)  # نوع المشروع
        self.phases_table.setColumnWidth(3, 200)  # اسم المرحلة
        self.phases_table.setColumnWidth(4, 250)  # وصف المرحلة
        self.phases_table.setColumnWidth(5, 80)   # الوحدة
        self.phases_table.setColumnWidth(6, 100)  # السعر
        self.phases_table.setColumnWidth(7, 200)  # ملاحظات
        self.phases_table.setColumnWidth(8, 120)  # تاريخ الإنشاء
        self.phases_table.setColumnWidth(9, 150)  # الإجراءات
        
        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.phases_table.itemDoubleClicked.connect(self.edit_phase_double_click)
        
    # إنشاء شريط الحالة
    def create_status_bar(self):
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("جاهز")
        self.status_label.setFont(QFont("Janna LT", 10))
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.count_label = QLabel("عدد المراحل: 0")
        self.count_label.setFont(QFont("Janna LT", 10))
        self.count_label.setStyleSheet("color: #34495e; padding: 5px;")
        status_layout.addWidget(self.count_label)
        
        return status_layout

    # تحميل شجرة الأقسام وأنواع المشاريع
    def load_sections_tree(self):
        self.sections_tree.clear()

        # إضافة قسم المشاريع
        projects_item = QTreeWidgetItem(self.sections_tree)
        projects_item.setText(0, "🏗️ المشاريع")
        projects_item.setFont(0, QFont("Janna LT", 12, QFont.Bold))
        projects_item.setData(0, Qt.UserRole, {"type": "section", "name": "المشاريع"})
        projects_item.setBackground(0, QColor("#e3f2fd"))
        projects_item.setToolTip(0, "انقر لعرض جميع مراحل المشاريع")

        # تحميل أنواع المشاريع من قاعدة البيانات
        self.load_project_types(projects_item)

        # إضافة قسم المقاولات
        contracts_item = QTreeWidgetItem(self.sections_tree)
        contracts_item.setText(0, "🔧 المقاولات")
        contracts_item.setFont(0, QFont("Janna LT", 12, QFont.Bold))
        contracts_item.setData(0, Qt.UserRole, {"type": "section", "name": "المقاولات"})
        contracts_item.setBackground(0, QColor("#fff3e0"))
        contracts_item.setToolTip(0, "انقر لعرض جميع مراحل المقاولات")

        # تحميل أنواع المقاولات من قاعدة البيانات
        self.load_contract_types(contracts_item)

        # توسيع جميع العقد
        self.sections_tree.expandAll()

    # تحميل أنواع المشاريع من قاعدة البيانات
    def load_project_types(self, parent_item):
        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                # في حالة عدم وجود اتصال، استخدم أنواع افتراضية
                self.add_default_project_types(parent_item)
                return

            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT اسم_التصنيف, لون_التصنيف
                FROM التصنيفات
                WHERE اسم_القسم = 'المشاريع' AND حالة_التصنيف = 'نشط'
                ORDER BY اسم_التصنيف
            """)

            project_types = cursor.fetchall()

            if project_types:
                for project_type, color in project_types:
                    project_item = QTreeWidgetItem(parent_item)
                    project_item.setText(0, f"📋 {project_type}")
                    project_item.setFont(0, QFont("Janna LT", 11))
                    project_item.setData(0, Qt.UserRole, {"type": "project_type", "section": "المشاريع", "name": project_type})

                    # إضافة لون للعنصر إذا كان متوفراً
                    if color:
                        project_item.setBackground(0, QColor(color).lighter(180))
                    else:
                        project_item.setBackground(0, QColor("#f5f5f5"))

                    project_item.setToolTip(0, f"انقر لعرض مراحل {project_type}")
            else:
                # إذا لم توجد تصنيفات، استخدم الافتراضية
                self.add_default_project_types(parent_item)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل أنواع المشاريع: {e}")
            # إضافة أنواع افتراضية في حالة الخطأ
            self.add_default_project_types(parent_item)

    # إضافة أنواع المشاريع الافتراضية
    def add_default_project_types(self, parent_item):
        for project_type in PROJECT_TYPES_CONFIG.keys():
            project_item = QTreeWidgetItem(parent_item)
            project_item.setText(0, f"📋 {project_type}")
            project_item.setFont(0, QFont("Janna LT", 11))
            project_item.setData(0, Qt.UserRole, {"type": "project_type", "section": "المشاريع", "name": project_type})
            project_item.setBackground(0, QColor("#f5f5f5"))
            project_item.setToolTip(0, f"انقر لعرض مراحل {project_type}")

    # تحميل أنواع المقاولات من قاعدة البيانات
    def load_contract_types(self, parent_item):
        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                # في حالة عدم وجود اتصال، استخدم أنواع افتراضية
                self.add_default_contract_types(parent_item)
                return

            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT اسم_التصنيف, لون_التصنيف
                FROM التصنيفات
                WHERE اسم_القسم = 'المقاولات' AND حالة_التصنيف = 'نشط'
                ORDER BY اسم_التصنيف
            """)

            contract_types = cursor.fetchall()

            if contract_types:
                for contract_type, color in contract_types:
                    contract_item = QTreeWidgetItem(parent_item)
                    contract_item.setText(0, f"🔨 {contract_type}")
                    contract_item.setFont(0, QFont("Janna LT", 11))
                    contract_item.setData(0, Qt.UserRole, {"type": "project_type", "section": "المقاولات", "name": contract_type})

                    # إضافة لون للعنصر إذا كان متوفراً
                    if color:
                        contract_item.setBackground(0, QColor(color).lighter(180))
                    else:
                        contract_item.setBackground(0, QColor("#f5f5f5"))

                    contract_item.setToolTip(0, f"انقر لعرض مراحل {contract_type}")
            else:
                # إذا لم توجد تصنيفات، استخدم الافتراضية
                self.add_default_contract_types(parent_item)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل أنواع المقاولات: {e}")
            # إضافة أنواع افتراضية في حالة الخطأ
            self.add_default_contract_types(parent_item)

    # إضافة أنواع المقاولات الافتراضية
    def add_default_contract_types(self, parent_item):
        default_types = ["مقاولات عامة", "مقاولات متخصصة", "صيانة وترميم", "مقاولات كهربائية", "مقاولات سباكة"]
        for contract_type in default_types:
            contract_item = QTreeWidgetItem(parent_item)
            contract_item.setText(0, f"🔨 {contract_type}")
            contract_item.setFont(0, QFont("Janna LT", 11))
            contract_item.setData(0, Qt.UserRole, {"type": "project_type", "section": "المقاولات", "name": contract_type})
            contract_item.setBackground(0, QColor("#f5f5f5"))
            contract_item.setToolTip(0, f"انقر لعرض مراحل {contract_type}")

    # معالج اختيار عنصر من شجرة الأقسام
    def on_section_item_selected(self, item, column):
        if not item:
            return

        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return

        # إضافة تأثير بصري للعنصر المحدد
        self.highlight_selected_item(item)

        if item_data["type"] == "section":
            # إذا تم اختيار قسم، عرض جميع المراحل في هذا القسم
            self.current_section = item_data["name"]
            self.current_project_type = None
            self.filter_phases_by_section(item_data["name"])

        elif item_data["type"] == "project_type":
            # إذا تم اختيار نوع مشروع، عرض المراحل الخاصة به فقط
            self.current_section = item_data["section"]
            self.current_project_type = item_data["name"]
            self.filter_phases_by_project_type(item_data["section"], item_data["name"])

    # إضافة تمييز بصري للعنصر المحدد
    def highlight_selected_item(self, selected_item):
        # إزالة التمييز من جميع العناصر
        iterator = QTreeWidgetItemIterator(self.sections_tree)
        while iterator.value():
            item = iterator.value()
            item.setFont(0, QFont("Janna LT", 11))
            iterator += 1

        # تمييز العنصر المحدد
        selected_item.setFont(0, QFont("Janna LT", 11, QFont.Bold))

    # تصفية المراحل حسب القسم
    def filter_phases_by_section(self, section_name):
        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()

            # جلب المراحل الخاصة بالقسم المحدد
            cursor.execute("""
                SELECT id, اسم_القسم, معرف_التصنيف, اسم_المرحلة,
                       وصف_المرحلة, الوحدة, السعر, ملاحظات,
                       DATE_FORMAT(تاريخ_الإنشاء, '%Y-%m-%d')
                FROM اسعار_المراحل
                WHERE اسم_القسم = %s
                ORDER BY معرف_التصنيف, اسم_المرحلة
            """, (section_name,))

            data = cursor.fetchall()
            cursor.close()
            conn.close()

            # تحديث الجدول
            self.populate_table(data)

            # تحديث شريط الحالة
            self.count_label.setText(f"عدد المراحل في {section_name}: {len(data)}")
            self.status_label.setText(f"عرض مراحل قسم: {section_name}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل البيانات: {e}")

    # تصفية المراحل حسب نوع المشروع
    def filter_phases_by_project_type(self, section_name, project_type):
        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()

            # جلب المراحل الخاصة بنوع المشروع المحدد
            cursor.execute("""
                SELECT id, اسم_القسم, معرف_التصنيف, اسم_المرحلة,
                       وصف_المرحلة, الوحدة, السعر, ملاحظات,
                       DATE_FORMAT(تاريخ_الإنشاء, '%Y-%m-%d')
                FROM اسعار_المراحل
                WHERE اسم_القسم = %s AND معرف_التصنيف = %s
                ORDER BY اسم_المرحلة
            """, (section_name, project_type))

            data = cursor.fetchall()
            cursor.close()
            conn.close()

            # تحديث الجدول
            self.populate_table(data)

            # تحديث شريط الحالة
            self.count_label.setText(f"عدد المراحل في {project_type}: {len(data)}")
            self.status_label.setText(f"عرض مراحل: {section_name} - {project_type}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل البيانات: {e}")

    # تحديث جميع البيانات (الشجرة والجدول)
    def refresh_all_data(self):
        self.load_sections_tree()
        self.load_data()

    # تحميل بيانات أسعار المراحل
    def load_data(self):
        try:
            # إذا كان هناك تصفية نشطة، استخدمها
            if self.current_section and self.current_project_type:
                self.filter_phases_by_project_type(self.current_section, self.current_project_type)
                return
            elif self.current_section:
                self.filter_phases_by_section(self.current_section)
                return

            # إذا لم تكن هناك تصفية، عرض جميع البيانات
            conn = self.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()

            # جلب جميع أسعار المراحل
            cursor.execute("""
                SELECT id, اسم_القسم, معرف_التصنيف, اسم_المرحلة,
                       وصف_المرحلة, الوحدة, السعر, ملاحظات,
                       DATE_FORMAT(تاريخ_الإنشاء, '%Y-%m-%d')
                FROM اسعار_المراحل
                ORDER BY اسم_القسم, معرف_التصنيف, اسم_المرحلة
            """)

            data = cursor.fetchall()
            cursor.close()
            conn.close()

            # تحديث الجدول
            self.populate_table(data)

            # تحديث شريط الحالة
            self.count_label.setText(f"عدد المراحل: {len(data)}")
            self.status_label.setText("تم تحميل جميع البيانات")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل البيانات: {e}")
            
    # ملء الجدول بالبيانات
    def populate_table(self, data):
        self.phases_table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                if col == 6:  # عمود السعر
                    item = QTableWidgetItem(f"{float(value):,.2f}" if value else "0.00")
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item = QTableWidgetItem(str(value) if value else "")
                    if col in [1, 2, 5]:  # القسم، نوع المشروع، الوحدة
                        item.setTextAlignment(Qt.AlignCenter)
                
                self.phases_table.setItem(row, col, item)
            
            # إضافة أزرار الإجراءات
            actions_widget = self.create_action_buttons(record[0])
            self.phases_table.setCellWidget(row, 9, actions_widget)

    # إنشاء أزرار الإجراءات لكل مرحلة
    def create_action_buttons(self, phase_id):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # زر التعديل
        edit_button = QPushButton("✏️")
        edit_button.setToolTip("تعديل المرحلة")
        edit_button.setFixedSize(30, 30)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        edit_button.clicked.connect(lambda: self.edit_phase(phase_id))
        layout.addWidget(edit_button)

        # زر الحذف
        delete_button = QPushButton("🗑️")
        delete_button.setToolTip("حذف المرحلة")
        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_phase(phase_id))
        layout.addWidget(delete_button)

        return widget

    # تصفية البيانات حسب البحث النصي
    def filter_data(self):
        search_text = self.search_edit.text().strip()

        for row in range(self.phases_table.rowCount()):
            show_row = True

            # البحث النصي في اسم المرحلة والوصف
            if search_text:
                phase_name_item = self.phases_table.item(row, 3)  # اسم المرحلة
                description_item = self.phases_table.item(row, 4)  # وصف المرحلة

                phase_name_match = phase_name_item and search_text.lower() in phase_name_item.text().lower()
                description_match = description_item and search_text.lower() in description_item.text().lower()

                if not (phase_name_match or description_match):
                    show_row = False

            self.phases_table.setRowHidden(row, not show_row)

        # تحديث عداد المراحل المعروضة
        visible_count = sum(1 for row in range(self.phases_table.rowCount())
                           if not self.phases_table.isRowHidden(row))
        self.count_label.setText(f"عدد المراحل المعروضة: {visible_count}")

    # إضافة مرحلة جديدة
    def add_phase(self):
        # تمرير المعلومات الحالية من القائمة الجانبية إلى النافذة
        dialog = AddEditPhaseDialog(self, mode="add",
                                  default_section=self.current_section,
                                  default_project_type=self.current_project_type)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            # تحديث الشجرة في حالة إضافة نوع مشروع جديد
            self.load_sections_tree()

    # تعديل مرحلة موجودة
    def edit_phase(self, phase_id):
        dialog = AddEditPhaseDialog(self, mode="edit", phase_id=phase_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            # تحديث الشجرة في حالة تعديل نوع المشروع
            self.load_sections_tree()

    # تعديل مرحلة عند النقر المزدوج
    def edit_phase_double_click(self, item):
        row = item.row()
        phase_id_item = self.phases_table.item(row, 0)
        if phase_id_item:
            phase_id = int(phase_id_item.text())
            self.edit_phase(phase_id)

    # حذف مرحلة
    def delete_phase(self, phase_id):
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل أنت متأكد من حذف هذه المرحلة؟\nسيتم حذف جميع البيانات المرتبطة بها.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = self.parent.get_db_connection()
                if conn is None:
                    QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                    return

                cursor = conn.cursor()
                cursor.execute("DELETE FROM اسعار_المراحل WHERE id = %s", (phase_id,))
                conn.commit()
                cursor.close()
                conn.close()

                QMessageBox.information(self, "نجح", "تم حذف المرحلة بنجاح")
                self.load_data()

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف المرحلة: {e}")


# حوار إضافة/تعديل مرحلة
class AddEditPhaseDialog(QDialog):

    # init
    def __init__(self, parent=None, mode="add", phase_id=None, default_section=None, default_project_type=None):
        super().__init__(parent)
        self.parent = parent
        self.default_section = default_section
        self.default_project_type = default_project_type
        self.mode = mode
        self.phase_id = phase_id
        self.setup_ui()

        # تحديث قائمة أنواع المشاريع عند فتح الحوار
        self.update_project_types()

        # تعيين القيم الافتراضية إذا تم تمريرها
        if mode == "add":
            if self.default_section:
                self.section_combo.setCurrentText(self.default_section)
                self.update_project_types()  # تحديث قائمة أنواع المشاريع
            if self.default_project_type:
                self.project_type_combo.setCurrentText(self.default_project_type)

        if mode == "edit" and phase_id:
            self.load_phase_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        title = "إضافة مرحلة جديدة" if self.mode == "add" else "تعديل المرحلة"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 500, 400)
        self.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # القسم
        self.section_combo = QComboBox()
        self.section_combo.addItems(["المشاريع", "المقاولات"])
        self.section_combo.setFont(QFont("Janna LT", 10))
        # ربط تغيير القسم بتحديث أنواع المشاريع
        self.section_combo.currentTextChanged.connect(self.update_project_types)
        form_layout.addRow("القسم:", self.section_combo)

        # نوع المشروع
        self.project_type_combo = QComboBox()
        self.project_type_combo.setFont(QFont("Janna LT", 10))
        self.update_project_types()
        form_layout.addRow("نوع المشروع:", self.project_type_combo)

        # اسم المرحلة
        self.phase_name_edit = QLineEdit()
        self.phase_name_edit.setFont(QFont("Janna LT", 10))
        self.phase_name_edit.setPlaceholderText("أدخل اسم المرحلة...")
        form_layout.addRow("اسم المرحلة:", self.phase_name_edit)

        # وصف المرحلة
        self.description_edit = QTextEdit()
        self.description_edit.setFont(QFont("Janna LT", 10))
        self.description_edit.setPlaceholderText("أدخل وصف المرحلة...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("وصف المرحلة:", self.description_edit)

        # الوحدة
        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)
        self.unit_combo.addItems([
            "متر مربع", "متر طولي", "قطعة", "لوحة",
            "مجموعة", "باقة", "خدمة", "أخرى"
        ])
        self.unit_combo.setFont(QFont("Janna LT", 10))
        form_layout.addRow("الوحدة:", self.unit_combo)

        # السعر
        self.price_edit = QLineEdit()
        self.price_edit.setFont(QFont("Janna LT", 10))
        self.price_edit.setPlaceholderText("0.00")
        form_layout.addRow("السعر:", self.price_edit)

        # ملاحظات
        self.notes_edit = QTextEdit()
        self.notes_edit.setFont(QFont("Janna LT", 10))
        self.notes_edit.setPlaceholderText("ملاحظات إضافية...")
        self.notes_edit.setMaximumHeight(60)
        form_layout.addRow("ملاحظات:", self.notes_edit)

        layout.addLayout(form_layout)

        # أزرار الإجراءات
        buttons_layout = QHBoxLayout()

        save_button = QPushButton("💾 حفظ")
        save_button.setFont(QFont("Janna LT", 11, QFont.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_button.clicked.connect(self.save_phase)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("❌ إلغاء")
        cancel_button.setFont(QFont("Janna LT", 11))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        # تطبيق الستايل
        apply_stylesheet(self)

    # تحديث قائمة أنواع المشاريع من جدول التصنيفات حسب القسم المختار
    def update_project_types(self):
        self.project_type_combo.clear()

        # الحصول على القسم المختار
        selected_section = self.section_combo.currentText()

        try:
            conn = self.parent.parent.get_db_connection()
            if conn is None:
                # في حالة فشل الاتصال، استخدم التصنيفات الافتراضية
                self.load_default_project_types()
                return

            cursor = conn.cursor()

            # جلب التصنيفات للقسم المحدد
            cursor.execute("""
                SELECT DISTINCT اسم_التصنيف
                FROM التصنيفات
                WHERE اسم_القسم = %s
                AND حالة_التصنيف = 'نشط'
                ORDER BY اسم_التصنيف
            """, (selected_section,))

            categories = cursor.fetchall()
            cursor.close()
            conn.close()

            # إضافة التصنيفات إلى القائمة
            for category in categories:
                self.project_type_combo.addItem(category[0])

            # إذا لم توجد تصنيفات، استخدم الافتراضية
            if not categories:
                self.load_default_project_types()

        except Exception as e:
            print(f"خطأ في تحميل التصنيفات للقسم {selected_section}: {e}")
            self.load_default_project_types()

    # تحميل أنواع المشاريع الافتراضية من التكوين
    def load_default_project_types(self):
        for project_type in PROJECT_TYPES_CONFIG.keys():
            self.project_type_combo.addItem(project_type)

    # تحميل بيانات المرحلة للتعديل
    def load_phase_data(self):
        try:
            conn = self.parent.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()
            cursor.execute("""
                SELECT اسم_القسم, معرف_التصنيف, اسم_المرحلة,
                       وصف_المرحلة, الوحدة, السعر, ملاحظات
                FROM اسعار_المراحل
                WHERE id = %s
            """, (self.phase_id,))

            data = cursor.fetchone()
            cursor.close()
            conn.close()

            if data:
                # تعيين القسم أولاً
                self.section_combo.setCurrentText(data[0])
                # تحديث قائمة أنواع المشاريع بناءً على القسم
                self.update_project_types()
                # ثم تعيين نوع المشروع
                self.project_type_combo.setCurrentText(data[1])
                self.phase_name_edit.setText(data[2])
                self.description_edit.setPlainText(data[3] or "")
                self.unit_combo.setCurrentText(data[4] or "متر مربع")
                self.price_edit.setText(str(data[5]) if data[5] else "0.00")
                self.notes_edit.setPlainText(data[6] or "")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل بيانات المرحلة: {e}")

    # حفظ بيانات المرحلة
    def save_phase(self):
        # التحقق من صحة البيانات
        if not self.phase_name_edit.text().strip():
            QMessageBox.warning(self, "تحذير", "يجب إدخال اسم المرحلة")
            self.phase_name_edit.setFocus()
            return

        try:
            price = float(self.price_edit.text() or "0")
            if price < 0:
                QMessageBox.warning(self, "تحذير", "السعر يجب أن يكون رقماً موجباً")
                self.price_edit.setFocus()
                return
        except ValueError:
            QMessageBox.warning(self, "تحذير", "السعر يجب أن يكون رقماً صحيحاً")
            self.price_edit.setFocus()
            return

        try:
            conn = self.parent.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()

            section = self.section_combo.currentText()
            project_type = self.project_type_combo.currentText()
            phase_name = self.phase_name_edit.text().strip()
            description = self.description_edit.toPlainText().strip()
            unit = self.unit_combo.currentText()
            notes = self.notes_edit.toPlainText().strip()

            if self.mode == "add":
                # التحقق من عدم وجود المرحلة مسبقاً
                cursor.execute("""
                    SELECT id FROM اسعار_المراحل
                    WHERE اسم_القسم = %s AND معرف_التصنيف = %s AND اسم_المرحلة = %s
                """, (section, project_type, phase_name))

                if cursor.fetchone():
                    QMessageBox.warning(self, "تحذير",
                                      f"المرحلة '{phase_name}' موجودة بالفعل في {section} - {project_type}")
                    cursor.close()
                    conn.close()
                    return

                # إضافة المرحلة الجديدة
                cursor.execute("""
                    INSERT INTO اسعار_المراحل
                    (اسم_القسم, معرف_التصنيف, اسم_المرحلة, وصف_المرحلة,
                     الوحدة, السعر, ملاحظات)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (section, project_type, phase_name, description,
                      unit, price, notes))

                message = f"تم إضافة المرحلة '{phase_name}' بنجاح"

            else:  # تعديل
                # التحقق من عدم تكرار الاسم (إذا تم تغييره)
                cursor.execute("""
                    SELECT id FROM اسعار_المراحل
                    WHERE اسم_القسم = %s AND معرف_التصنيف = %s AND اسم_المرحلة = %s AND id != %s
                """, (section, project_type, phase_name, self.phase_id))

                if cursor.fetchone():
                    QMessageBox.warning(self, "تحذير",
                                      f"المرحلة '{phase_name}' موجودة بالفعل في {section} - {project_type}")
                    cursor.close()
                    conn.close()
                    return

                # تحديث المرحلة
                cursor.execute("""
                    UPDATE اسعار_المراحل
                    SET اسم_القسم = %s, معرف_التصنيف = %s, اسم_المرحلة = %s,
                        وصف_المرحلة = %s, الوحدة = %s, السعر = %s, ملاحظات = %s
                    WHERE id = %s
                """, (section, project_type, phase_name, description,
                      unit, price, notes, self.phase_id))

                message = f"تم تحديث المرحلة '{phase_name}' بنجاح"

            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "نجح", message)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ المرحلة: {e}")
