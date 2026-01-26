from الإعدادات_العامة import *
from ستايل import *

# نافذة تخصيص عرض الأقسام
class SectionViewSettingsDialog(QDialog):
    
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("تخصيص عرض الأقسام")
        self.setModal(True)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(600, 500)
        
        # تطبيق الستايل
        self.setObjectName("SectionViewSettingsDialog")
        
        # إعداد الواجهة
        self.setup_ui()
        self.load_current_settings()
        
    # إعداد واجهة النافذة
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان الرئيسي مع أيقونة
        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 10, 10, 10)

        # أيقونة العنوان
        title_icon = QLabel("⚙️")
        title_icon.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(title_icon)

        # نص العنوان
        title_label = QLabel("تخصيص العرض الافتراضي للأقسام")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel#TitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # تطبيق ستايل الإطار
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                margin-bottom: 15px;
            }
            QLabel {
                color: white;
            }
        """)
        layout.addWidget(title_frame)
        
        # وصف مع معلومات إضافية
        desc_frame = QFrame()
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(15, 10, 15, 10)

        main_desc = QLabel("اختر نوع العرض الافتراضي لكل قسم")
        main_desc.setAlignment(Qt.AlignCenter)
        main_desc.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        """)
        desc_layout.addWidget(main_desc)

        # معلومات إضافية
        info_layout = QHBoxLayout()

        # معلومات عرض الجدول
        table_info = QLabel("📊 الجدول: عرض تفصيلي للبيانات في صفوف وأعمدة")
        table_info.setStyleSheet("""
            font-size: 12px;
            color: #495057;
            padding: 5px;
            background-color: #e3f2fd;
            border-radius: 5px;
            border-left: 3px solid #2196f3;
        """)
        info_layout.addWidget(table_info)

        # معلومات عرض البطاقات
        cards_info = QLabel("🎴 البطاقات: عرض مرئي أنيق للبيانات في شكل بطاقات")
        cards_info.setStyleSheet("""
            font-size: 12px;
            color: #495057;
            padding: 5px;
            background-color: #f3e5f5;
            border-radius: 5px;
            border-left: 3px solid #9c27b0;
        """)
        info_layout.addWidget(cards_info)

        desc_layout.addLayout(info_layout)

        desc_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(desc_frame)
        
        # منطقة التمرير للأقسام
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("SectionsScrollArea")
        
        # ويدجت المحتوى
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        
        # قائمة الأقسام
        self.sections_list = [
            "المشاريع", "المقاولات", "العملاء", 
            "الحسابات", "الموظفين", "التدريب", "الموردين", "التقارير"
        ]
        
        # قاموس لحفظ أزرار الراديو
        self.section_radio_buttons = {}
        
        # إنشاء عنصر لكل قسم
        for section_name in self.sections_list:
            section_frame = self.create_section_frame(section_name)
            content_layout.addWidget(section_frame)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # إضافة إحصائيات سريعة
        self.stats_frame = self.create_stats_frame()
        layout.addWidget(self.stats_frame)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # زر الحفظ والتطبيق
        save_btn = QPushButton("💾 حفظ وتطبيق الإعدادات")
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setMinimumHeight(40)
        save_btn.setToolTip("حفظ الإعدادات وتطبيقها فوراً على جميع الأقسام")
        
        # زر الإلغاء
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(40)
        
        # زر استعادة الافتراضي
        reset_btn = QPushButton("🔄 استعادة الافتراضي")
        reset_btn.setObjectName("ResetButton")
        reset_btn.clicked.connect(self.reset_to_default)
        reset_btn.setMinimumHeight(40)
        reset_btn.setToolTip("استعادة الإعدادات الافتراضية لجميع الأقسام")

        # زر معاينة سريعة
        preview_btn = QPushButton("👁️ معاينة")
        preview_btn.setObjectName("PreviewButton")
        preview_btn.clicked.connect(self.show_preview)
        preview_btn.setMinimumHeight(40)
        preview_btn.setToolTip("عرض ملخص سريع للإعدادات الحالية")
        
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(preview_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # تطبيق الستايل على الأزرار
        self.apply_button_styles()
        
    # إنشاء إطار لقسم واحد
    def create_section_frame(self, section_name):
        frame = QFrame()
        frame.setObjectName("SectionFrame")
        frame.setFrameStyle(QFrame.Box)
        frame.setLineWidth(1)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        # أيقونة القسم
        section_icons = {
            "المشاريع": "🏗️",
            "المقاولات": "🏢",
            "العملاء": "👥",
            "الحسابات": "💰",
            "الموظفين": "👨‍💼",
            "التدريب": "📚",
            "الموردين": "💼",
            "التقارير": "📊"
        }

        icon_label = QLabel(section_icons.get(section_name, "📁"))
        icon_label.setStyleSheet("font-size: 20px; margin-right: 5px;")
        layout.addWidget(icon_label)

        # اسم القسم
        section_label = QLabel(section_name)
        section_label.setObjectName("SectionLabel")
        section_label.setMinimumWidth(120)
        section_label.setStyleSheet("""
            QLabel#SectionLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        layout.addWidget(section_label)
        
        layout.addStretch()
        
        # مجموعة أزرار الراديو
        radio_group = QButtonGroup(frame)
        
        # زر الجدول مع أيقونة
        table_radio = QRadioButton("📊 جدول")
        table_radio.setObjectName("TableRadio")
        table_radio.setMinimumHeight(35)
        table_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                font-weight: bold;
                color: #495057;
                spacing: 8px;
                padding: 5px;
            }
        """)

        # زر البطاقات مع أيقونة
        cards_radio = QRadioButton("🎴 بطاقات")
        cards_radio.setObjectName("CardsRadio")
        cards_radio.setMinimumHeight(35)
        cards_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                font-weight: bold;
                color: #495057;
                spacing: 8px;
                padding: 5px;
            }
        """)
        
        # إضافة الأزرار للمجموعة
        radio_group.addButton(table_radio, 0)
        radio_group.addButton(cards_radio, 1)

        # ربط تحديث الإحصائيات عند التغيير
        table_radio.toggled.connect(self.update_stats)
        cards_radio.toggled.connect(self.update_stats)

        # حفظ المراجع
        self.section_radio_buttons[section_name] = {
            'table': table_radio,
            'cards': cards_radio,
            'group': radio_group
        }
        
        # تخطيط أزرار الراديو
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(20)
        radio_layout.addWidget(table_radio)
        radio_layout.addWidget(cards_radio)
        
        layout.addLayout(radio_layout)
        
        # تطبيق ستايل الإطار مع تأثيرات بصرية محسنة
        frame.setStyleSheet("""
            QFrame#SectionFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 3px;
                padding: 5px;
            }
            QFrame#SectionFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f8ff, stop:1 #e6f3ff);
                border-color: #007bff;
                
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #6c757d;
                background-color: white;
            }
            QRadioButton::indicator:unchecked:hover {
                border: 2px solid #007bff;
                background-color: #f0f8ff;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #007bff;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 #007bff, stop:0.6 #007bff, stop:0.7 white, stop:1 white);
            }
            QRadioButton::indicator:checked:hover {
                border: 2px solid #0056b3;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 #0056b3, stop:0.6 #0056b3, stop:0.7 white, stop:1 white);
            }
        """)
        
        return frame

    # إنشاء إطار الإحصائيات
    def create_stats_frame(self):
        stats_frame = QFrame()
        stats_frame.setObjectName("StatsFrame")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        stats_layout.setSpacing(20)

        # عنوان الإحصائيات
        stats_title = QLabel("📈 الإحصائيات:")
        stats_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        stats_layout.addWidget(stats_title)

        # إحصائية الجداول
        self.table_count_label = QLabel("📊 الجداول: 0")
        self.table_count_label.setStyleSheet("""
            font-size: 13px;
            color: #2196f3;
            background-color: #e3f2fd;
            padding: 5px 10px;
            border-radius: 15px;
            border: 1px solid #2196f3;
        """)
        stats_layout.addWidget(self.table_count_label)

        # إحصائية البطاقات
        self.cards_count_label = QLabel("🎴 البطاقات: 0")
        self.cards_count_label.setStyleSheet("""
            font-size: 13px;
            color: #9c27b0;
            background-color: #f3e5f5;
            padding: 5px 10px;
            border-radius: 15px;
            border: 1px solid #9c27b0;
        """)
        stats_layout.addWidget(self.cards_count_label)

        stats_layout.addStretch()

        # تطبيق ستايل الإطار
        stats_frame.setStyleSheet("""
            QFrame#StatsFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px 0px;
            }
        """)

        return stats_frame

    # تحديث الإحصائيات
    def update_stats(self):
        try:
            table_count = 0
            cards_count = 0

            for section_name in self.sections_list:
                radio_buttons = self.section_radio_buttons[section_name]
                if radio_buttons['table'].isChecked():
                    table_count += 1
                else:
                    cards_count += 1

            self.table_count_label.setText(f"📊 الجداول: {table_count}")
            self.cards_count_label.setText(f"🎴 البطاقات: {cards_count}")

        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")

    # تطبيق ستايل الأزرار
    def apply_button_styles(self):
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
                min-width: 100px;
            }
            QPushButton#SaveButton {
                background-color: #28a745;
                color: white;
            }
            QPushButton#SaveButton:hover {
                background-color: #218838;
            }
            QPushButton#SaveButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton#CancelButton {
                background-color: #6c757d;
                color: white;
            }
            QPushButton#CancelButton:hover {
                background-color: #5a6268;
            }
            QPushButton#CancelButton:pressed {
                background-color: #545b62;
            }
            QPushButton#ResetButton {
                background-color: #ffc107;
                color: #212529;
            }
            QPushButton#ResetButton:hover {
                background-color: #e0a800;
            }
            QPushButton#ResetButton:pressed {
                background-color: #d39e00;
            }
            QPushButton#PreviewButton {
                background-color: #17a2b8;
                color: white;
            }
            QPushButton#PreviewButton:hover {
                background-color: #138496;
            }
            QPushButton#PreviewButton:pressed {
                background-color: #117a8b;
            }
        """
        self.setStyleSheet(button_style)
        
    # تحميل الإعدادات الحالية
    def load_current_settings(self):
        try:
            for section_name in self.sections_list:
                # الحصول على التفضيل الحالي
                if hasattr(self.parent, 'get_section_view_preference'):
                    current_view = self.parent.get_section_view_preference(section_name)
                else:
                    # استخدام الافتراضي
                    default_views = {
                        "الحسابات": "table",
                        "المشاريع": "cards",
                        "المقاولات": "cards",
                        "العملاء": "cards",
                        "الموظفين": "cards",
                        "التدريب": "cards",
                        "الموردين": "cards",
                        "التقارير": "cards"
                    }
                    current_view = default_views.get(section_name, "cards")
                
                # تعيين الزر المناسب
                radio_buttons = self.section_radio_buttons[section_name]
                if current_view == "table":
                    radio_buttons['table'].setChecked(True)
                else:
                    radio_buttons['cards'].setChecked(True)
                    
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
            # تعيين القيم الافتراضية
            self.reset_to_default()

        # تحديث الإحصائيات بعد التحميل
        self.update_stats()
            
    # حفظ الإعدادات الجديدة
    def save_settings(self):
        try:
            saved_count = 0
            for section_name in self.sections_list:
                radio_buttons = self.section_radio_buttons[section_name]
                
                # تحديد النوع المختار
                if radio_buttons['table'].isChecked():
                    view_type = "table"
                else:
                    view_type = "cards"
                
                # حفظ الإعداد
                if hasattr(self.parent, 'set_section_view_preference'):
                    self.parent.set_section_view_preference(section_name, view_type)
                    saved_count += 1
                else:
                    # حفظ مباشر في الإعدادات
                    settings.setValue(f"section_view_{section_name}", view_type)
                    saved_count += 1
            
            # فرض الحفظ
            settings.sync()
            
            # إغلاق النافذة بنجاح
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الحفظ", f"حدث خطأ أثناء حفظ الإعدادات:\n{str(e)}")
            
    # استعادة الإعدادات الافتراضية
    def reset_to_default(self):
        try:
            reply = QMessageBox.question(
                self,
                "استعادة الافتراضي",
                "هل تريد استعادة الإعدادات الافتراضية لعرض الأقسام؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # الإعدادات الافتراضية
                default_views = {
                    "الحسابات": "table",
                    "المشاريع": "cards",
                    "المقاولات": "cards",
                    "العملاء": "cards",
                    "الموظفين": "cards",
                    "التدريب": "cards",
                    "الموردين": "cards",
                    "التقارير": "cards"
                }
                
                # تطبيق الإعدادات الافتراضية على الواجهة
                for section_name in self.sections_list:
                    default_view = default_views.get(section_name, "cards")
                    radio_buttons = self.section_radio_buttons[section_name]
                    
                    if default_view == "table":
                        radio_buttons['table'].setChecked(True)
                    else:
                        radio_buttons['cards'].setChecked(True)
                
                # تحديث الإحصائيات
                self.update_stats()

                QMessageBox.information(self, "تم الاستعادة", "تم استعادة الإعدادات الافتراضية")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء استعادة الإعدادات:\n{str(e)}")

    # عرض معاينة سريعة للإعدادات الحالية
    def show_preview(self):
        try:
            # جمع الإعدادات الحالية
            table_sections = []
            cards_sections = []

            for section_name in self.sections_list:
                radio_buttons = self.section_radio_buttons[section_name]
                if radio_buttons['table'].isChecked():
                    table_sections.append(section_name)
                else:
                    cards_sections.append(section_name)

            # إنشاء رسالة المعاينة
            preview_message = "📋 معاينة الإعدادات الحالية:\n\n"

            if table_sections:
                preview_message += "📊 الأقسام التي ستعرض كجداول:\n"
                for section in table_sections:
                    preview_message += f"   • {section}\n"
                preview_message += "\n"

            if cards_sections:
                preview_message += "🎴 الأقسام التي ستعرض كبطاقات:\n"
                for section in cards_sections:
                    preview_message += f"   • {section}\n"
                preview_message += "\n"

            preview_message += f"📈 الإحصائيات:\n"
            preview_message += f"   • عدد الجداول: {len(table_sections)}\n"
            preview_message += f"   • عدد البطاقات: {len(cards_sections)}\n"
            preview_message += f"   • إجمالي الأقسام: {len(self.sections_list)}"

            # عرض رسالة المعاينة
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("معاينة الإعدادات")
            msg_box.setText(preview_message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setLayoutDirection(Qt.RightToLeft)

            # تطبيق ستايل مخصص لرسالة المعاينة
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f8f9fa;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)

            msg_box.exec_()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء عرض المعاينة:\n{str(e)}")
