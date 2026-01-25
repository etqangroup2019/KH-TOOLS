# cSpell:disable
from الإعدادات_العامة import *
from أزرار_الواجهة import *
from DB import *
from ستايل import *

# نافذة إدارة التصنيفات الشاملة
class CategoriesManagementDialog(QDialog):
    
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_sections()
        self.load_categories()
        
    # إعداد واجهة المستخدم
    def setup_ui(self):
        self.setWindowTitle("إدارة التصنيفات")
        self.setGeometry(100, 100, 1000, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # الخط العربي
        font = QFont("Janna LT", 12)
        self.setFont(font)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        
        # العنوان
        title_label = QLabel("إدارة التصنيفات")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Janna LT", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # تخطيط أفقي للمحتوى
        content_layout = QHBoxLayout()

        # الجانب الأيسر - قائمة الأقسام (تقليل العرض)
        left_panel = self.create_sections_panel()
        content_layout.addWidget(left_panel, 1)

        # الجانب الأيمن - إدارة التصنيفات (زيادة العرض)
        right_panel = self.create_categories_panel()
        content_layout.addWidget(right_panel, 3)
        
        main_layout.addLayout(content_layout)
        
        # أزرار التحكم
        buttons_layout = self.create_buttons_panel()
        main_layout.addLayout(buttons_layout)
        
        # تطبيق الستايل
        apply_stylesheet(self)
        
    # إنشاء لوحة الأقسام
    def create_sections_panel(self):
        panel = QGroupBox("الأقسام المتاحة")
        panel.setFont(QFont("Janna LT", 12, QFont.Bold))
        panel.setMaximumWidth(250)  # تحديد عرض أقصى للوحة
        layout = QVBoxLayout(panel)

        # قائمة الأقسام
        self.sections_list = QListWidget()
        self.sections_list.setFont(QFont("Janna LT", 11))
        self.sections_list.itemClicked.connect(self.on_section_selected)
        # تحسين مظهر قائمة الأقسام
        self.sections_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
        """)
        layout.addWidget(self.sections_list)

        return panel
        
    # إنشاء لوحة إدارة التصنيفات
    def create_categories_panel(self):
        panel = QGroupBox("إدارة التصنيفات")
        panel.setFont(QFont("Janna LT", 12, QFont.Bold))
        layout = QVBoxLayout(panel)
        
        # معلومات القسم المحدد
        self.section_info_label = QLabel("اختر قسماً لعرض تصنيفاته")
        self.section_info_label.setAlignment(Qt.AlignCenter)
        self.section_info_label.setFont(QFont("Janna LT", 11))
        self.section_info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 3px;
            }
        """)
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
        form_group.setFont(QFont("Janna LT", 11, QFont.Bold))
        layout = QFormLayout(form_group)
        
        # اسم التصنيف
        self.category_name_edit = QLineEdit()
        self.category_name_edit.setPlaceholderText("أدخل اسم التصنيف...")
        self.category_name_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        layout.addRow("اسم التصنيف:", self.category_name_edit)

        # لون التصنيف مع اللون واسمه في نفس الصف
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 30)
        self.color_button.setStyleSheet("background-color: #3498db; border-radius: 5px; border: 2px solid #bdc3c7;")
        self.color_button.clicked.connect(self.choose_color)
        self.selected_color = "#3498db"

        self.color_label = QLabel("#3498db")
        self.color_label.setFont(QFont("Courier", 10))
        self.color_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 5px 10px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)

        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        color_layout.addStretch()

        layout.addRow("لون التصنيف:", color_layout)
        
        # وصف التصنيف (تحويل إلى LineEdit)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("وصف اختياري للتصنيف...")
        self.description_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        layout.addRow("الوصف:", self.description_edit)
        
        # زر الإضافة
        self.add_button = QPushButton("➕ إضافة التصنيف")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.add_button.clicked.connect(self.add_category)
        self.add_button.setEnabled(False)
        layout.addRow("", self.add_button)
        
        # ربط تغيير النص بتفعيل الزر
        self.category_name_edit.textChanged.connect(self.validate_form)
        
        return form_group
        
    # إنشاء جدول التصنيفات الموجودة
    def create_categories_table(self):
        table_group = QGroupBox("التصنيفات الموجودة")
        table_group.setFont(QFont("Janna LT", 11, QFont.Bold))
        layout = QVBoxLayout(table_group)

        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels([
            "التصنيف واللون", "الوصف", "تاريخ الإنشاء", "الإجراءات"
        ])

        # تحسين مظهر الجدول
        self.categories_table.setAlternatingRowColors(True)
        self.categories_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categories_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.categories_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # زيادة ارتفاع الصفوف لتحسين القراءة
        self.categories_table.verticalHeader().setDefaultSectionSize(45)
        self.categories_table.verticalHeader().setVisible(False)

        # تخصيص عرض الأعمدة
        header = self.categories_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # التصنيف واللون
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # الوصف
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # التاريخ
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # الإجراءات

        self.categories_table.setColumnWidth(0, 200)  # عرض عمود التصنيف واللون
        self.categories_table.setColumnWidth(3, 120)  # عرض عمود الإجراءات

        # تطبيق ستايل محسن للجدول
        self.categories_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.categories_table)

        return table_group
        
    # إنشاء لوحة الأزرار
    def create_buttons_panel(self):
        layout = QHBoxLayout()
        
        # زر التحديث
        refresh_button = QPushButton("🔄 تحديث")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_button.clicked.connect(self.refresh_data)

        # زر الإغلاق
        close_button = QPushButton("❌ إغلاق")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_button.clicked.connect(self.close)
        
        layout.addStretch()
        layout.addWidget(refresh_button)
        layout.addWidget(close_button)
        
        return layout
        
    # تحميل قائمة الأقسام المتاحة
    def load_sections(self):
        sections = [
            "المشاريع",
            "المقاولات", 
            "العملاء",
            "الحسابات",
            "الموظفين",
            "التدريب",
            "الموردين"
        ]
        
        for section in sections:
            item = QListWidgetItem(section)
            item.setFont(QFont("Janna LT", 11))
            self.sections_list.addItem(item)
            
    # تحميل التصنيفات من قاعدة البيانات
    def load_categories(self):
        if not hasattr(self, 'current_section') or not self.current_section:
            return
            
        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                return
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT اسم_التصنيف, لون_التصنيف, وصف_التصنيف, تاريخ_الإنشاء, id
                FROM التصنيفات 
                WHERE اسم_القسم = %s AND حالة_التصنيف = 'نشط'
                ORDER BY اسم_التصنيف
            """, (self.current_section,))
            
            categories = cursor.fetchall()
            
            # تنظيف الجدول
            self.categories_table.setRowCount(0)
            
            # إضافة التصنيفات
            for row, (name, color, description, created_date, cat_id) in enumerate(categories):
                self.categories_table.insertRow(row)

                # التصنيف واللون (دمج في عمود واحد)
                category_widget = QWidget()
                category_layout = QHBoxLayout(category_widget)
                category_layout.setContentsMargins(8, 5, 8, 5)
                category_layout.setSpacing(10)

                # مؤشر اللون
                color_label = QLabel()
                color_label.setFixedSize(25, 25)
                color_label.setStyleSheet(f"""
                    background-color: {color};
                    border-radius: 12px;
                    border: 2px solid white;
                    
                """)

                # اسم التصنيف
                name_label = QLabel(name)
                name_label.setFont(QFont("Janna LT", 11, QFont.Bold))
                name_label.setStyleSheet("color: #2c3e50; padding: 2px;")

                category_layout.addWidget(color_label)
                category_layout.addWidget(name_label)
                category_layout.addStretch()

                self.categories_table.setCellWidget(row, 0, category_widget)

                # الوصف
                desc_text = description if description else "لا يوجد وصف"
                desc_item = QTableWidgetItem(desc_text)
                desc_item.setFont(QFont("Janna LT", 10))
                desc_item.setForeground(QColor("#6c757d"))
                self.categories_table.setItem(row, 1, desc_item)

                # تاريخ الإنشاء
                date_str = created_date.strftime("%Y-%m-%d") if created_date else ""
                date_item = QTableWidgetItem(date_str)
                date_item.setFont(QFont("Janna LT", 10))
                date_item.setTextAlignment(Qt.AlignCenter)
                self.categories_table.setItem(row, 2, date_item)

                # أزرار الإجراءات
                actions_widget = self.create_action_buttons(cat_id, name)
                self.categories_table.setCellWidget(row, 3, actions_widget)
                
            cursor.close()
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل التصنيفات: {e}")
            
    # إنشاء أزرار الإجراءات لكل تصنيف
    def create_action_buttons(self, category_id, category_name):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # زر التعديل (محسن)
        edit_button = QPushButton("✏️ تعديل")
        edit_button.setToolTip("تعديل التصنيف")
        edit_button.setFixedSize(50, 30)
        edit_button.setFont(QFont("Janna LT", 9))
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 2px 4px;
            }
            QPushButton:hover {
                background-color: #e67e22;
                
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        edit_button.clicked.connect(lambda: self.edit_category(category_id, category_name))

        # زر الحذف (محسن)
        delete_button = QPushButton("🗑️ حذف")
        delete_button.setToolTip("حذف التصنيف")
        delete_button.setFixedSize(50, 30)
        delete_button.setFont(QFont("Janna LT", 9))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 2px 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_category(category_id, category_name))

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch()

        return widget

    # معالج اختيار قسم
    def on_section_selected(self, item):
        self.current_section = item.text()
        self.section_info_label.setText(f"إدارة تصنيفات قسم: {self.current_section}")
        self.load_categories()
        self.add_button.setEnabled(bool(self.category_name_edit.text().strip()))

    # التحقق من صحة النموذج
    def validate_form(self):
        has_section = hasattr(self, 'current_section') and self.current_section
        has_name = bool(self.category_name_edit.text().strip())
        self.add_button.setEnabled(has_section and has_name)

    # اختيار لون التصنيف
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}; border-radius: 5px;")
            self.color_label.setText(self.selected_color)

    # إضافة تصنيف جديد
    def add_category(self):
        if not hasattr(self, 'current_section') or not self.current_section:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار قسم أولاً")
            return

        category_name = self.category_name_edit.text().strip()
        if not category_name:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم التصنيف")
            return

        description = self.description_edit.text().strip()

        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()

            # التحقق من عدم وجود التصنيف مسبقاً
            cursor.execute("""
                SELECT id FROM التصنيفات
                WHERE اسم_القسم = %s AND اسم_التصنيف = %s
            """, (self.current_section, category_name))

            if cursor.fetchone():
                QMessageBox.warning(self, "تحذير", f"التصنيف '{category_name}' موجود بالفعل في قسم {self.current_section}")
                cursor.close()
                conn.close()
                return

            # إضافة التصنيف الجديد
            cursor.execute("""
                INSERT INTO التصنيفات
                (اسم_القسم, اسم_التصنيف, لون_التصنيف, وصف_التصنيف, المستخدم)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.current_section, category_name, self.selected_color, description, "المدير"))

            conn.commit()
            cursor.close()
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

    # تعديل تصنيف موجود
    def edit_category(self, category_id, category_name):
        dialog = EditCategoryDialog(self, category_id, category_name, self.current_section)
        if dialog.exec() == QDialog.Accepted:
            self.load_categories()

    # حذف تصنيف
    def delete_category(self, category_id, category_name):
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف التصنيف '{category_name}'؟\n\nملاحظة: سيتم تعطيل التصنيف وليس حذفه نهائياً",
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

                # تعطيل التصنيف بدلاً من حذفه
                cursor.execute("""
                    UPDATE التصنيفات
                    SET حالة_التصنيف = 'غير نشط'
                    WHERE id = %s
                """, (category_id,))

                conn.commit()
                cursor.close()
                conn.close()

                self.load_categories()
                QMessageBox.information(self, "نجح", f"تم تعطيل التصنيف '{category_name}' بنجاح")

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف التصنيف: {e}")

    # تحديث البيانات
    def refresh_data(self):
        if hasattr(self, 'current_section') and self.current_section:
            self.load_categories()
        QMessageBox.information(self, "تحديث", "تم تحديث البيانات بنجاح")


# نافذة تعديل التصنيف
class EditCategoryDialog(QDialog):

    # init
    def __init__(self, parent, category_id, category_name, section_name):
        super().__init__(parent)
        self.parent = parent
        self.category_id = category_id
        self.category_name = category_name
        self.section_name = section_name
        self.setup_ui()
        self.load_category_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        self.setWindowTitle(f"تعديل التصنيف: {self.category_name}")
        self.setGeometry(200, 200, 400, 300)
        self.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(self)

        # نموذج التعديل
        form_layout = QFormLayout()

        # اسم التصنيف
        self.name_edit = QLineEdit(self.category_name)
        form_layout.addRow("اسم التصنيف:", self.name_edit)

        # لون التصنيف
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 30)
        self.color_button.clicked.connect(self.choose_color)

        self.color_label = QLabel()
        self.color_label.setFont(QFont("Courier", 10))

        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        color_layout.addStretch()

        form_layout.addRow("لون التصنيف:", color_layout)

        # وصف التصنيف (تحويل إلى LineEdit)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("وصف اختياري للتصنيف...")
        form_layout.addRow("الوصف:", self.description_edit)

        layout.addLayout(form_layout)

        # أزرار التحكم (محسنة)
        buttons_layout = QHBoxLayout()

        save_button = QPushButton("💾 حفظ")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_button.clicked.connect(self.save_changes)

        cancel_button = QPushButton("❌ إلغاء")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

    # تحميل بيانات التصنيف
    def load_category_data(self):
        try:
            conn = self.parent.parent.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()
            cursor.execute("""
                SELECT لون_التصنيف, وصف_التصنيف
                FROM التصنيفات
                WHERE id = %s
            """, (self.category_id,))

            result = cursor.fetchone()
            if result:
                color, description = result
                self.selected_color = color or "#3498db"
                self.color_button.setStyleSheet(f"background-color: {self.selected_color}; border-radius: 5px;")
                self.color_label.setText(self.selected_color)
                self.description_edit.setText(description or "")

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل بيانات التصنيف: {e}")

    # اختيار لون التصنيف
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}; border-radius: 5px;")
            self.color_label.setText(self.selected_color)

    # حفظ التغييرات
    def save_changes(self):
        new_name = self.name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم التصنيف")
            return

        description = self.description_edit.text().strip()

        try:
            conn = self.parent.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()

            # التحقق من عدم تكرار الاسم (إذا تم تغييره)
            if new_name != self.category_name:
                cursor.execute("""
                    SELECT id FROM التصنيفات
                    WHERE اسم_القسم = %s AND اسم_التصنيف = %s AND id != %s
                """, (self.section_name, new_name, self.category_id))

                if cursor.fetchone():
                    QMessageBox.warning(self, "تحذير", f"التصنيف '{new_name}' موجود بالفعل")
                    cursor.close()
                    conn.close()
                    return

            # تحديث التصنيف
            cursor.execute("""
                UPDATE التصنيفات
                SET اسم_التصنيف = %s, لون_التصنيف = %s, وصف_التصنيف = %s
                WHERE id = %s
            """, (new_name, self.selected_color, description, self.category_id))

            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "نجح", "تم حفظ التغييرات بنجاح")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ التغييرات: {e}")
