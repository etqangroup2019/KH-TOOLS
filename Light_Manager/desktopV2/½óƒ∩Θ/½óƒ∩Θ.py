from الإعدادات_العامة import*

#تحميل الاعدادات=====================================================================
# إعدادات أنماط التحميل
def load_Styles_settings(self):
    default_settings = {
        "المشاريع": "#8dad9c",
        "المشاريع": "#30738b",
        "الحسابات": "#be716b",
        "الموظفين": "#799fa8",
        "الموظفين": "#6a8f70",
        "التدريب": "#89b178",

        "لون الازرار": "#e0e0e0",
        "لون الادخال": "#f5f5f5",

        "لون الجدول": "#efefef",
        "نوع خط الجدول": font_app_defolt,
        "حجم خط الجدول": "16px",
        "وزن خط الجدول": "700",

        "لون الخط العام": "#000000",
        "نوع الخط العام": font_app_defolt,
        "حجم الخط العام": "16px",
        "وزن الخط العام": "700",

        "نوع خط الازرار": font_app_defolt,
        "حجم خط الازرار": "16px",
        "وزن خط الازرار": "700"
    }
    # تحميل البيانات من JSON إذا كان الملف موجودًا
    if os.path.exists(Customize_json_path):
        with open(Customize_json_path, "r", encoding="utf-8") as file:
            try:
                settings_data = json.load(file)
            except json.JSONDecodeError:
                settings_data = default_settings  # في حال كان الملف تالفًا، استخدم القيم الافتراضية
    else:
        settings_data = default_settings  # إذا لم يكن الملف موجودًا، استخدم القيم الافتراضية

    if hasattr(self, "Interface_combo"):
        # حميل الوان الواجهة
        table_name = self.Interface_combo.currentText()
        # الحصول على اللون المحفوظ أو اللون الافتراضي إذا لم يكن موجودًا
        background_color = settings_data.get(table_name, default_settings.get(table_name, "#f0f0f0"))
    else:
        background_color = "#f0f0f0"

    # استخراج القيم المحفوظة أو استخدام القيم الافتراضية
    Buttom_color = settings_data.get("لون الازرار", default_settings["لون الازرار"])
    inpt_color = settings_data.get("لون الادخال", default_settings["لون الادخال"])

    Table_color= settings_data.get("لون الجدول", default_settings["لون الجدول"])
    Table_font= settings_data.get("نوع خط الجدول", default_settings["نوع خط الجدول"])
    Table_size = settings_data.get("حجم خط الجدول", default_settings["حجم خط الجدول"])
    Table_weight = settings_data.get("وزن خط الجدول", default_settings["وزن خط الجدول"])

    font_color = settings_data.get("لون الخط العام", default_settings["لون الخط العام"])
    font_app = settings_data.get("نوع الخط العام", default_settings["نوع الخط العام"])
    font_size = settings_data.get("حجم الخط العام", default_settings["حجم الخط العام"])
    font_weight = settings_data.get("حجم الخط العام", default_settings["وزن الخط العام"])

    Buttom_font = settings_data.get("نوع خط الازرار", default_settings["نوع خط الازرار"])
    Buttom_size = settings_data.get("حجم خط الازرار", default_settings["حجم خط الازرار"])
    Buttom_weight = settings_data.get("وزن خط الازرار", default_settings["وزن خط الازرار"])

    return background_color,Buttom_color,inpt_color,Table_color,font_color,Table_font, Table_size,Table_weight,font_app,font_size,font_weight,Buttom_font,Buttom_size,Buttom_weight, # إرجاع القيم المحفوظة

# ستايل ==========================================================================================
# تمرير الأنماط
def Pass_Styles(self):
        self.setStyleSheet(f"""
                    QLabel {{font-family: {font_app}
                    ;font-weight: bold; font-size: 16px;
                    border-radius: 10px;
                    color: black;

                    }}

                    QLineEdit, QComboBox, QLCDNumber {{
                        font-family: {font_app};
                        font-weight: bold;
                        font-size: 18px;
                        height: 33px;
                        background-color: #f5f5f5;
                        border: 4px solid #f5f5f5;
                        border-radius: 10px;
                        color: black;
                    }}

                    QDialog {{ background-color: #a1b997; }}
                    QDialog {{ background-color: #30738b; }}


                    QPushButton {{
                        font-family: {font_app};
                        font-weight: bold;
                        font-size: 18px;
                        height: 20px;
                        width:150px;
                        background-color: #e0e0e0;
                        border: 2px solid #d4d4d4;
                        border-radius: 10px;
                        padding: 5px;
                        color: black;
                    }}
                    QPushButton:hover {{
                        font-family: {font_app};
                        font-weight: bold;
                        background-color: #c3d7d3;
                    }}

                    QPushButton:pressed {{
                        font-family: {font_app};
                        font-weight: bold;
                        background-color: #849c79; /* اللون الأخضر */;
                    }}

                    QPushButton:disabled {{
                        color: #808080;  /* لون النص يصبح رمادي */
                        border: 2px solid #d4d4d4;
                        padding: 5px;
                    }}

                    QHeaderView::section {{
                        font-family: {font_app};
                        font-weight: bold;
                        background-color: #abd5dd;
                        padding: 4px;
                        font-size: 14px;
                        text-align: center;
                    }}
                    QVBoxLayout{{
                        background-color: #a1b997;
                    }}

                    QMessageBox {{
                        background-color: #e0e0e0;
                        color: black;
                    }}

                    QMenuBar {{
                    text-align: right;
                    }}

                    QMenu::item {{
                        text-align: right; padding: 5px;
                        }}

                """)

# الأساليب الأساسية
def Basic_Styles(self):
    app = QApplication.instance()  # Get the existing instance if it exists
    if app is None:
        app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    background_color,Buttom_color,inpt_color,Table_color,font_color,Table_font, Table_size,Table_weight,font_app,font_size,font_weight,Buttom_font,Buttom_size,Buttom_weight,= load_Styles_settings(self)
    self.setStyleSheet(f"""
                QWidget {{
                    background-color: {background_color};

                }}

                QGroupBox {{
                    background: transparent;
                    font-family:  "Janna LT";
                    font-weight:  "500";
                    font-size: 10px;
                    color: {font_color};
                    margin: 2px;
                    padding: 2px;
                    border-radius: 6px;
                }}

                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top center; /* يمكنك تعديل الموضع حسب الحاجة */
                    padding: 0 5px;   /* إضافة بعض الهوامش الجانبية لعنوان القروب */
                    margin-top: -15px;  /* قيمة سالبة لتحريك العنوان إلى الأعلى */
                }}


                QDialog{{
                    background-color: #ededed;
                    color: #000000;
                    font-size: {font_size};
                    font-family: {font_app};
                    font-weight: {font_weight};
                    border-radius: 0px;
                }}

                QFontDialog{{
                    background-color: #ededed;
                    color: #000000;
                    font-size: 14px;
                    border-radius: 10px;
                }}

                /* إضافة حدود زرقاء عند التركيز */
                QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, QPushButton:focus{{
                    border: 2px solid #0078D7;
                    background-color: #E6F0FF;
                }}

                QLabel {{
                    background-color: {Buttom_color};
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    font-weight: Label_font_weight;
                    color: {font_color};
                    height: 30px;
                    border: 1px solid #d4d4d4;
                    border-radius: 3px;
                }}

                QLineEdit{{
                    background-color: {inpt_color};
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    border-radius: 4px;
                    color: {font_color};
                    border: 2px solid #d4d4d4;
                    height: 30px;
                    text-align: center;

                }}

                QDateEdit{{
                    background-color: {inpt_color};
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    border-radius: 5px;
                    color: {font_color};
                    border: 2px solid #d4d4d4;
                    height: 30px;
                }}

                /* تنسيق التقويم المنبثق */
                QCalendarWidget {{
                    background-color: #e6f2ff;
                }}
                QCalendarWidget QWidget {{
                    background-color: #e6f2ff;
                }}
                QCalendarWidget QToolButton {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    border-radius: 3px;
                    padding: 5px;
                }}
                QCalendarWidget QMenu {{
                    background-color: #e6f2ff;
                }}
                QCalendarWidget QSpinBox {{
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                }}
                QCalendarWidget QAbstractItemView:enabled {{
                    background-color: white;
                    color: #333;
                    selection-background-color: #3498db;
                    selection-color: white;
                }}
                QCalendarWidget QAbstractItemView:disabled {{
                    color: #ccc;
                }}


                /* كمبو بوكس*/
                QComboBox {{
                    background-color: {inpt_color};
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};

                    width:200px;
                    border: 1px solid #6c7c55; /* حدود الكمبو بوكس */
                    padding:2px;
                    color: {font_color};
                }}


                /* تخصيص قائمة العناصر */
                QComboBox QAbstractItemView {{
                    background-color: {inpt_color};
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    color: {font_color};
                    selection-background-color: #d0e0e3; /* تظليل النص عند تمرير الماوس */
                    selection-color: {font_color};  لون النص بعد التحديد */
                    border: 2px solid #e8e8e8;
                    padding: 2px;
                }}

                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top left; /* زر القائمة المنسدلة في اليسار */
                    width: 20px; /* عرض زر القائمة المنسدلة */
                    border-left-width: 1px;
                    border-left-color: darkgray;
                    border-left-style: solid;
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                    background-color: {background_color}; /* تلوين الجهة اليمنى بالأزرق */
                }}

                /* إضافة الحدود بين الخيارات */
                QComboBox QAbstractItemView::item {{
                    border-bottom: 1px solid #d1d1d1;  /* حدود بين الخيارات */
                    padding: 5px;
                }}

                /* تغيير اللون عند التمرير على العناصر */
                QComboBox QAbstractItemView::item:hover {{
                    background-color: #bdc5c7;  /* تظليل العنصر عند تمرير الماوس */
                    color: {font_color};               /* تغيير لون النص عند التمرير */
                }}

                QComboBox:hover {{
                    background-color: #B0BEC5; /* تغيير اللون عند التمرير */
                }}

                QComboBox:focus {{
                    border: 2px solid #caccc8; /* تغيير الحدود عند التركيز */
                    border: 2px solid #0078D7;
                    background-color: #E6F0FF;
                }}

                QLabel, QComboBox, QPushButton {{
                    height: 30px;
                }}

                /* الازرار*/
                QPushButton {{
                    background-color: {Buttom_color};
                    font-family: {Buttom_font};
                    font-weight: {Buttom_weight};
                    font-size: {Buttom_size};
                    height: 20px;
                    width:150px;
                    border: 2px solid #d4d4d4;
                    border: 2px solid #7192a8;
                    border-radius: 5px;
                    padding: 5px;
                    color: {font_color};
                }}
                QPushButton:hover {{
                    background-color: #B0BEC5;
                    font-family: {Buttom_font};
                    font-weight: {Buttom_weight};
                    font-size: {Buttom_size};
                    font-size: {Buttom_size};

                }}
                QPushButton:pressed {{
                    background-color: #849c79; /* اللون الأخضر */;
                    font-family: {Buttom_font};
                    font-weight: {Buttom_weight};
                    font-size: {Buttom_size};

                }}
                QPushButton:disabled {{
                    color: #808080;  /* لون النص يصبح رمادي */
                    border: 2px solid #d4d4d4;
                    padding: 5px;
                }}

                QPushButton:focus{{
                    border: 2px solid #0078D7;

                }}

                /* الجدول*/
                QTableWidget {{
                    background-color: {Table_color}; /*لون خلفية الجدول*/
                    font-family: {Table_font};
                    font-weight: {Table_weight};
                    font-size: {Table_size};
                    text-align: center;
                    color: {font_color};
                    alternate-background-color:#e7e7e7; /*لون  صف بعد صف*/

                }}

                QHeaderView::section {{
                    background-color: #e0e0e0;
                    font-family: {Table_font};
                    font-weight: {Table_weight};
                    font-size: {Table_size};
                    padding: 2; /* زيادة حجم الخط العنوان للجدول   */
                    text-align: center;
                    border: 2px;  /* إزالة الحدود */
                    border: 2px solid #c6c6c6;  /* إضافة خط فاصل حول العناوين */
                    color: {font_color};
                    background-color: {Buttom_color};

                }}
                QTableWidget::item:selected {{
                    background-color: #8aa8a6;
                    font-family: {Table_font};
                    font-weight: {Table_weight};
                    font-size: {Table_size};
                    color: {font_color};
                }}

                QTableWidget::item {{
                    height: 20px;
                    text-align: center;
                }}


                QInputDialog{{
                    background-color: #e0e0e0;
                    color: black;
                    text-align: center;
                }}

                /* المينو بار */
                QMenuBar {{
                    background: qlineargradient(
                        spread:pad,
                        x1:0, y1:0,
                        x2:1, y2:0,
                        stop:0 #f0f0f0,
                        stop:1 #e0e0e0
                    );
                    font-family: "Janna LT";
                    color: {font_color};
                    padding: 4px 2px;
                    border-bottom: 2px solid #3498db;
                    font-weight: bold;
                    font-size: 15px;
                    text-align: right;
                    min-height: 30px;
                    spacing: 5px;
                }}

                QMenuBar::item {{
                    background: transparent;
                    padding: 6px 15px;
                    margin: 1px 2px;
                    border-radius: 4px;
                    text-align: right; /* محاذاة النص لليمين */
                }}

                QMenuBar::item:hover {{
                    background: qlineargradient(
                        spread:pad,
                        x1:0, y1:0,
                        x2:0, y2:1,
                        stop:0 #e1f0fa,
                        stop:1 #c7e3f5
                    );
                    border: 1px solid #a6c9e2;
                }}

                QMenuBar::item:selected {{
                    background: qlineargradient(
                        spread:pad,
                        x1:0, y1:0,
                        x2:0, y2:1,
                        stop:0 #c7e3f5,
                        stop:1 #a6c9e2
                    );
                    border: 1px solid #7cb4e2;
                }}

                /* القوائم المنسدلة */
                QMenu {{
                    background-color: #f9f9f9;
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 5px;
                    color: {font_color};
                    font-size: 15px;
                    font-weight: bold;
                    min-width: 150px;
                    border-bottom: 3px solid #3498db;
                    text-align: right;
                    margin: 2px;
                }}

                QMenu::item {{
                    padding: 8px 25px 8px 15px;
                    border-radius: 4px;
                    margin: 3px 5px;
                }}

                QMenu::item:hover {{
                    background-color: #e1f0fa;
                    border: 1px solid #a6c9e2;
                }}

                QMenu::item:selected {{
                    background-color: #c7e3f5;
                    color: {font_color};
                    border: 1px solid #7cb4e2;
                }}

                QMenu::separator {{
                    height: 1px;
                    background-color: #bdc3c7;
                    margin: 5px 10px;
                }}

                QAction{{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 15px;
                    background-color: transparent;
                    text-align: right;
                    color: {font_color};
                }}

                QSpinBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 14px;
                    height: 30px;
                    width:10px;
                    background-color: {inpt_color};
                    text-align: center; /* Center align text in QLineEdit */;
                }}

                QCheckBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 14px;
                    background-color: #e0e0e0;
                }}

                /*خيار  احادي*/
                QRadioButton {{
                    font-family: {font_app};
                    font-weight: bold; font-size: 16px;
                    background-color: #e0e0e0;
                    color: {font_color};

                }}

                QStatusBar {{
                    background-color: {Buttom_color};  /* تغيير لون شريط الحالة إلى الأبيض */
                    color: {font_color};             /* لون النص في شريط الحالة */
                }}

                QMessageBox {{
                    background-color: #ededed;
                    color: #000000;
                    font-size: 14px;
                }}
                QMessageBox QLabel {{
                    background-color: #ededed;
                    color: #000000;
                }}

                QProgressBar {{
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(236, 240, 241, 0.3);
                    text-align: center;
                    color: #2c3e50;
                    font-weight: bold;
                    font-size: 14px;
                    height: 25px;
                    padding: 0px;
                    margin: 0px 10px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:0.3 #2980b9,
                        stop:0.6 #16a085, stop:1 #2ecc71
                    );
                    border-radius: 10px;
                    margin: 0px;
                }}


                /* منع تلوين المساحة الفارغة */
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                    background: #c7c9c1;
                }}

                QTabWidget{{
                    background-color: #ededed;
                }}


                QTabWidget::pane {{
                    background-color: #ededed;
                }}

                QTabBar::tab {{
                    background-color: {Buttom_color};
                    padding: 3px 3px; /* توسيع التبويب */
                    font-family: {font_app};
                    font-weight: bold; font-size: 16px;
                    border: 2px solid #d4d4d4;  /* تحديد إطار الشريط */
                    margin-right: 1px; /* إضافة تباعد بين التبويبات */
                }}
                QTabBar::tab:selected {{
                    background-color: #8dad9c;
                    background-color: #30738b;

                    border: 2px solid #2980b9;  /* تحديد إطار الشريط */
                    border-radius: 5px;
                }}

                QTabWidget::pane {{
                    border: 2px solid #0077cc;
                    background: #f0f0f0;
                    border-radius: 6px;
                    padding: 4px;
                }}

                QTabBar::tab {{
                    background: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    border-top-left-radius: 0px;
                    border-top-right-radius: 0px;
                    padding: 4px 12px; /* تقليل الارتفاع هنا */
                    margin-right: 2px;
                    font-weight: bold;
                    min-height: 20px;  /* ضمان ألا يكون الارتفاع كبير */
                }}

                QTabBar::tab:selected {{
                    background: #0077cc;
                    color: white;
                    border-color: #0077cc;
                }}

                QTabBar::tab:hover {{
                    background: #e6f2ff;
                    color: #0077cc;
                }}




            """)
    if self.is_dark_mode:
        app.setStyle("Fusion")
        self.setStyleSheet(f"""
                QWidget {{
                    background-color: {background_color};
                    background-color: #39587d;

                    color: #ffffff;

                    }}

                QGroupBox {{
                    background: transparent;
                    font-family:  "Janna LT";
                    font-weight:  "500";
                    font-size: 10px;
                    color: #ffffff;
                    margin: 2px;
                    padding: 2px;
                }}

                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top center; /* يمكنك تعديل الموضع حسب الحاجة */
                    padding: 0 5px;   /* إضافة بعض الهوامش الجانبية لعنوان القروب */
                    margin-top: -15px;  /* قيمة سالبة لتحريك العنوان إلى الأعلى */
                }}


                QDialog{{
                    background-color: #1e1e2f;
                    color: #ffffff;
                    font-size: 14px;
                    border-radius: 10px;
                }}

                QFontDialog{{
                    background-color: #ededed;
                    color: #ffffff;
                    font-size: 14px;
                    border-radius: 10px;
                }}

                /* إضافة حدود زرقاء عند التركيز */
                QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus QPushButton:focus{{
                    border: 2px solid #6b48ff;
                    background-color: #3e3e5f;
                }}

                QLabel {{
                    background-color: #3e3e5f;
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    font-weight: Label_font_weight;
                    color: #ffffff;
                    height: 30px;
                }}

                QLineEdit{{
                    background-color: #2d2d44;
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    border-radius: 4px;
                    color: #ffffff;
                    border: 2px solid #3e3e5f;
                    height: 30px;
                    text-align: center;

                }}

                QDateEdit{{
                    background-color: #2d2d44;
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    border-radius: 5px;
                    color: #ffffff;
                    border: 2px solid #3e3e5f;
                    height: 30px;
                }}

                /* تنسيق التقويم المنبثق - الوضع الداكن */
                QCalendarWidget {{
                    background-color: #252537;
                }}
                QCalendarWidget QWidget {{
                    background-color: #252537;
                }}
                QCalendarWidget QToolButton {{
                    background-color: #3e3e5f;
                    color: white;
                    font-weight: bold;
                    border-radius: 3px;
                    padding: 5px;
                }}
                QCalendarWidget QMenu {{
                    background-color: #252537;
                }}
                QCalendarWidget QSpinBox {{
                    background-color: #2d2d44;
                    color: white;
                    border: 1px solid #3e3e5f;
                    border-radius: 3px;
                }}
                QCalendarWidget QAbstractItemView:enabled {{
                    background-color: #2d2d44;
                    color: white;
                    selection-background-color: #6b48ff;
                    selection-color: white;
                }}
                QCalendarWidget QAbstractItemView:disabled {{
                    color: #666666;
                }}

                /* كمبو بوكس*/
                QComboBox {{
                    background-color: #2d2d44;
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};

                    width:200px;
                    border: 1px solid  #3e3e5f; /* حدود الكمبو بوكس */
                    padding:2px;
                    color: #ffffff;
                }}


                /* تخصيص قائمة العناصر */
                QComboBox QAbstractItemView {{
                    background-color: #2d2d44;
                    font-family: {font_app};
                    font-weight: {font_weight};
                    font-size: {font_size};
                    color: #ffffff;
                    selection-background-color: #d0e0e3; /* تظليل النص عند تمرير الماوس */
                    selection-color: {font_color};  لون النص بعد التحديد */
                    border: 2px solid #3e3e5f;
                    padding: 2px;
                }}

                /* إضافة الحدود بين الخيارات */
                QComboBox QAbstractItemView::item {{
                    border-bottom: 1px solid #d1d1d1;  /* حدود بين الخيارات */
                    padding: 5px;
                }}

                /* تغيير اللون عند التمرير على العناصر */
                QComboBox QAbstractItemView::item:hover {{
                    background-color: #bdc5c7;  /* تظليل العنصر عند تمرير الماوس */
                    color: #ffffff;              /* تغيير لون النص عند التمرير */
                }}

                QComboBox:hover {{
                    background-color: #B0BEC5; /* تغيير اللون عند التمرير */
                }}

                QComboBox:focus {{
                    border: 2px solid #caccc8; /* تغيير الحدود عند التركيز */
                }}

                QLabel, QComboBox, QPushButton {{
                    height: 30px;
                }}

                /* الازرار*/
                QPushButton {{
                    background-color: #7876b7;
                    font-family: {Buttom_font};
                    font-weight: {Buttom_weight};
                    font-size: {Buttom_size};
                    height: 20px;
                    width:150px;
                    border: 2px solid #8a63ff;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                }}
                QPushButton:hover {{
                    background-color: #8a63ff;
                    font-family: {Buttom_font};
                    font-weight: {Buttom_weight};
                    font-size: {Buttom_size};
                    font-size: {Buttom_size};

                }}
                QPushButton:pressed {{
                    background-color: #4b2ecc; /* اللون الأخضر */;
                    font-family: {Buttom_font};
                    font-weight: {Buttom_weight};
                    font-size: {Buttom_size};

                }}
                QPushButton:disabled {{
                    color: #8aa8a6;  /* لون النص يصبح رمادي */
                    border: 2px solid #d4d4d4;
                    padding: 5px;
                }}

                QPushButton:focus{{
                    border: 2px solid #0078D7;

                }}

                /* الجدول*/
                QTableWidget {{
                    background-color: #252537; /*لون خلفية الجدول*/
                    font-family: {Table_font};
                    font-weight: {Table_weight};
                    font-size: {Table_size};
                    text-align: center;
                    color: #ffffff;
                    alternate-background-color:#3e3e5f; /*لون  صف بعد صف*/

                }}

                QHeaderView::section {{
                    background-color: #2d2d44;
                    font-family: {Table_font};
                    font-weight: {Table_weight};
                    font-size: {Table_size};
                    padding: 2; /* زيادة حجم الخط العنوان للجدول   */
                    text-align: center;
                    border: 2px;  /* إزالة الحدود */
                    border: 2px solid #3e3e5f;  /* إضافة خط فاصل حول العناوين */
                    color: #ffffff;
                    background-color: #2d2d44;

                }}
                QTableWidget::item:selected {{
                    background-color: #8aa8a6;
                    font-family: {Table_font};
                    font-weight: {Table_weight};
                    font-size: {Table_size};
                    color: #ffffff;
                }}

                QTableWidget::item {{
                    height: 20px;
                    text-align: center;
                }}



                QInputDialog{{
                    background-color: #3e3e5f;
                    color: #ffffff;
                    text-align: center;
                }}

                /* المينو بار */
                QMenuBar {{
                    background: qlineargradient(
                        spread:pad,
                        x1:0, y1:0,
                        x2:1, y2:0,
                        stop:0 #2c3e50,
                        stop:1 #34495e
                    );
                    font-family: "Janna LT";
                    color: #ffffff;
                    padding: 4px 2px;
                    border-bottom: 2px solid #6b48ff;
                    font-weight: bold;
                    font-size: 15px;
                    text-align: right;
                    min-height: 30px;
                    spacing: 5px;
                }}

                QMenuBar::item {{
                    background: transparent;
                    padding: 6px 15px;
                    margin: 1px 2px;
                    border-radius: 4px;
                    text-align: right; /* محاذاة النص لليمين */
                }}

                QMenuBar::item:hover {{
                    background: qlineargradient(
                        spread:pad,
                        x1:0, y1:0,
                        x2:0, y2:1,
                        stop:0 #3e4a5b,
                        stop:1 #4a5c70
                    );
                    border: 1px solid #5d6d7e;
                }}

                QMenuBar::item:selected {{
                    background: qlineargradient(
                        spread:pad,
                        x1:0, y1:0,
                        x2:0, y2:1,
                        stop:0 #4a5c70,
                        stop:1 #5d6d7e
                    );
                    border: 1px solid #7cb4e2;
                }}

                /* القوائم المنسدلة */
                QMenu {{
                    background-color: #2c3e50;
                    border: 1px solid #5d6d7e;
                    border-radius: 6px;
                    padding: 5px;
                    color: #ffffff;
                    font-size: 15px;
                    font-weight: bold;
                    min-width: 150px;
                    border-bottom: 3px solid #6b48ff;
                    text-align: right;
                    margin: 2px;
                }}

                QMenu::item {{
                    padding: 8px 25px 8px 15px;
                    border-radius: 4px;
                    margin: 3px 5px;
                }}

                QMenu::item:hover {{
                    background-color: #3e4a5b;
                    border: 1px solid #5d6d7e;
                }}

                QMenu::item:selected {{
                    background-color: #4a5c70;
                    color: #ffffff;
                    border: 1px solid #7cb4e2;
                }}

                QMenu::separator {{
                    height: 1px;
                    background-color: #5d6d7e;
                    margin: 5px 10px;
                }}

                QAction{{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 15px;
                    background-color: transparent;
                    text-align: right;
                    color: #ffffff;
                }}

                QSpinBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 14px;
                    height: 25px;
                    width:10px;
                    background-color: #2d2d44;
                    text-align: center; /* Center align text in QLineEdit */;
                }}

                QCheckBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 14px;
                    background-color: #e0e0e0;
                }}

                /*خيار  احادي*/
                QRadioButton {{
                    font-family: {font_app};
                    font-weight: bold; font-size: 16px;
                    background-color: #e0e0e0;
                    color: #ffffff;

                }}

                QStatusBar {{
                    background-color: {Buttom_color};  /* تغيير لون شريط الحالة إلى الأبيض */
                    color: #ffffff;            /* لون النص في شريط الحالة */
                }}

                QMessageBox {{
                    background-color: #39587d;
                    color: #ffffff;
                    font-size: 14px;
                }}
                QMessageBox QLabel {{
                    background-color: #39587d;
                    color: #ffffff;
                }}

                QProgressBar {{
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(52, 73, 94, 0.5);
                    text-align: center;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 14px;
                    height: 25px;
                    padding: 0px;
                    margin: 0px 10px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:0.3 #2980b9,
                        stop:0.6 #9b59b6, stop:1 #8e44ad
                    );
                    border-radius: 10px;
                    margin: 0px;
                }}


                /* منع تلوين المساحة الفارغة */
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                    background: #c7c9c1;
                }}

                QTabWidget::pane {{
                    border: 1px solid #3e3e5f;
                    background-color: #252537;
                }}
                QTabBar::tab {{
                    background-color: #2d2d44;
                    padding: 10px 20px;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }}
                QTabBar::tab:selected {{
                    background-color: #6b48ff;
                }}

        """)

# أنماط KSHF
def kshf_Styles(self):
    self.setStyleSheet(f"""
                QLabel {{
                    font-family: {font_app};
                    font-weight: bold; font-size: 16px;
                    background-color: #e0e0e0;

                }}

                QAction{{
                    font-family: {font_app};
                    font-weight: bold; font-size: 16px;
                    background-color: #e0e0e0;

                }}

                QLineEdit{{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 5px;
                }}

                QDateEdit{{
                    font-family: {font_app}
                    ;font-weight: bold; font-size: 16px;
                    border-radius: 5px;
                }}

                QGroupBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 12px;
                }}

                QComboBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 16px;
                    height: 30px;
                    width:200px;
                }}

                QTextBrowser {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 14px;
                    height: 30px;
                    width:250px;

                }}

                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                }}
                QComboBox QAbstractItemView {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 16px;
                    height: 30px;
                    text-align: center; /* Center text in dropdown */;
                }}


                QSpinBox {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 14px;
                    height: 25px;
                    width:10px;
                    background-color: #d4d4d4;
                    text-align: center; /* Center align text in QLineEdit */;
                }}
                QPushButton {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 18px;
                    height: 18px;
                    width:140px;
                    background-color: #e0e0e0;
                    border: 2px solid #d4d4d4;
                    border-radius: 10px;
                    padding: 5px;
                }}

                QPushButton:hover {{
                    font-family: {font_app};
                    font-weight: bold;
                    background-color: #cdd7b9;
                }}

                QPushButton:pressed {{
                    font-family: {font_app};
                    font-weight: bold;
                    background-color: #849c79; /* اللون الأخضر */;
                }}

                QTableWidget {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 16px;
                    background-color: #e3e3e3;
                    text-align: center;
                }}

                QHeaderView::section {{
                    font-family: {font_app};
                    font-weight: bold;
                    background-color: #ccdcdf;
                    padding: 4px;
                    font-size: 16px;
                    text-align: center;
                }}

                QTableWidget::item:selected {{
                    background-color: #a1b997;font-size: 16px;
                }}

                QCheckBox {{
                    font-family: {font_app}
                    ;font-weight: bold; font-size: 14px;background-color: #e0e0e0;
                }}

                QMessageBox {{
                    background-color: #e0e0e0;
                    color: black;
                }}

                QInputDialog{{
                    background-color: #e0e0e0;
                    color: black;
                }}

            """)


# تطبيق ورقة الأنماط
def apply_stylesheet(self):
    stylesheet = """
    /* General Window and Background */
    QMainWindow {
        background-color: #34495e;
        border: none;
    }

    /* أزرار الطباعة الموحدة */
    QPushButton#print_button {
        background-color: #e67e22;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 14px;
        min-width: 80px;
        margin: 2px;
    }

    QPushButton#print_button:hover {
        background-color: #d35400;
    }

    QPushButton#print_button:pressed {
        background-color: #c0392b;
    }

    QPushButton#print_button:disabled {
        background-color: #bdc3c7;
        color: #7f8c8d;
    }

    QMainWindow {
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:1, y2:1,
            stop:0 #1b3459,   /* أزرق */
            stop:1 #a64d79  /* بنفسجي */
        );
    }
    QMainWindow {
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:1, y2:1,
            stop:0 #1b3459,
            stop:1 #57216b
        );
    }


    QWidget#MainCentralWidget {
        background-color: transparent;
        border: none;
    }
    #MainCentralWidget {
        background-color: transparent;
        border: none;
    }

    /*حاويةالازرار الجانبية*/
    #حاوية_الازرار_الجانبية  {
        /*background-color: transparent;*/
        text-align: center;
        border: 0px solid #dcdcdc;

    }

    QFrame{
        background-color: transparent;
        border: none;
    }


    QWidget#حاوية_الازرار_الجانبية {
        /* background-color: transparent;*/
        border: none;
    }

    QWidget#MainCentralWidget {
        background-color: transparent;
    }


    /* Menu Bar */
    QMenuBar {
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:1, y2:0,
            stop:0 #2c3e50,
            stop:1 #34495e
        );
        color: #ecf0f1;
        border-bottom: 2px solid #3498db;
        padding: 4px 2px;
        font-weight: bold;
        font-size: 15px;
        min-height: 30px;
        spacing: 5px;
    }
    QMenuBar::item {
        padding: 6px 15px;
        margin: 1px 2px;
        border-radius: 4px;
        background-color: transparent;
    }
    QMenuBar::item:hover {
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:0, y2:1,
            stop:0 #3e4a5b,
            stop:1 #4a5c70
        );
        border: 1px solid #5d6d7e;
    }
    QMenuBar::item:selected {
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:0, y2:1,
            stop:0 #4a5c70,
            stop:1 #5d6d7e
        );
        border: 1px solid #7cb4e2;
    }
    QMenu {
        background-color: #2c3e50;
        border: 1px solid #5d6d7e;
        border-radius: 6px;
        padding: 5px;
        qproperty-layoutDirection: RightToLeft;
        color: #ecf0f1;
        font-size: 15px;
        font-weight: bold;
        min-width: 150px;
        border-bottom: 3px solid #3498db;
        margin: 2px;
    }
    QMenu::item {
        padding: 8px 25px 8px 15px;
        border-radius: 4px;
        margin: 3px 5px;
        color: #ecf0f1;
        text-align: right;
    }
    QMenu::item:hover {
        background-color: #3e4a5b;
        border: 1px solid #5d6d7e;
    }
    QMenu::item:selected {
        background-color: #4a5c70;
        color: white;
        border: 1px solid #7cb4e2;
    }
    QMenu::separator {
        height: 1px;
        background-color: #5d6d7e;
        margin: 5px 10px;
    }

    /* Right Panel (Side Menu) */
    #RightPanel {
        background-color: transparent;
        color: #ecf0f1;
        border-left: 1px solid #5a4765;
        border-top: 0px solid #243342;
        border-top-left-radius: 0px;
    }

    #RightPanel QLabel {
        color: #ecf0f1;
    }


    QScrollBar:vertical#customScrollBar {
        border: none;
        background: #34495e;
        width: 12px;
        margin: 2px 0 2px 0;
        border-radius: 0px;
    }


    #RightPanel #SideMenuButton {
        background-color:transparent;
        color: #ffffff;
        padding: 6px;
        min-height: 60px;
        max-height: 70px;
        margin: 0px 0;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        font-family: "Janna LT";
        border-bottom: 3px solid transparent; /* Default transparent bottom border */
    }
    #RightPanel #SideMenuButton:hover {
        background-color: #f39c12;
    }
    #RightPanel #SideMenuButton:pressed {
        background-color: #e67e22;
    }


    #RightPanel #SideMenuButton[active="true"] {
        background-color: #159279; /* تغيير لون الزر النشط إلى الأصفر */
        border-bottom: 3px solid #3498db; /* Blue for المشاريع */
    }

    #RightPanel #SideMenuButton QLabel {
        color: white;
        font-size: 14px;
        font-family: "Janna LT";
        font-weight: bold;
    }


    /* Main Content Area */
    #MainContentArea QWidget {
        /*background-color: #34495e;*/
    }

    /* Header Row */
    #SectionHeaderRowFrame {
        background-color: transparent;
        border: 0px solid #dcdcdc;
        border-radius: 8px;
        padding: 0px 0px;
        margin-bottom: 0px;
    }

    /* Standard Action Buttons */
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
        min-width: 70px;
        text-align: center;
        font-weight: normal;
    }
    QPushButton:hover {
        background-color: #2980b9;
    }
    QPushButton:pressed {
        background-color: #2471a3;
    }


    /* Custom Actions Frame */
    #CustomActionsFrame {
        padding: 5px 0;
        margin-bottom: 10px;
        font-size: 8px;
        font-family: "Janna LT";
    }

    /* Custom Action Buttons */
    #CustomActionButton {
        background-color: transparent;
        color: #ffffff;
        border: 0px solid #bdc3c7;
        padding: 6px;
        border-radius: 6px;
        min-width: 100;
        min-height: 60px;
        max-height: 80px;
        font-weight: bold;
        text-align: center;
        margin: 0px;
        font-size: 16px;
        font-family: "Janna LT";
        border-bottom: 3px solid transparent; /* Default transparent bottom border */
    }
    #CustomActionButton QLabel {
        color: #ffffff;
        font-size: 14px;
        font-family: "Janna LT";
    }
    #CustomActionButton:hover {
        background-color: #f39c12;
        border-color: #a6c9e2;
    }
    #CustomActionButton:pressed {
        background-color: #e67e22;
    }

    /* الوان الهامش السفلي للازار الرئيسية */
    #RightPanel #SideMenuButton[border_type="bottom_border_green"] {
        border-bottom: 3px solid #2ecc71; /* أخضر */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_yellow"] {
        border-bottom: 3px solid #f1c40f; /* أصفر */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_blue"] {
        border-bottom: 3px solid #3498db; /* أزرق */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_orange"] {
        border-bottom: 3px solid #e67e22; /* برتقالي */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_red"] {
        border-bottom: 3px solid #e74c3c; /* أحمر */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_purple"] {
        border-bottom: 3px solid #9b59b6; /* بنفسجي */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_teal"] {
        border-bottom: 3px solid #1abc9c; /* برتقالي */
    }
    #RightPanel #SideMenuButton[border_type="bottom_border_lime"] {
        border-bottom: 3px solid #c7e0c2; /* برتقالي */
    }


    /* الوان الهامش السفلي للازرار الفرعية */
    #CustomActionButton[border_type="bottom_border_green"] {
        border-bottom: 3px solid #2ecc71; /* أخضر */
    }
    #CustomActionButton[border_type="bottom_border_yellow"] {
        border-bottom: 3px solid #f1c40f; /* أصفر */
    }
    #CustomActionButton[border_type="bottom_border_blue"] {
        border-bottom: 3px solid #3498db; /* أزرق */
    }
    #CustomActionButton[border_type="bottom_border_orange"] {
        border-bottom: 3px solid #e67e22; /* برتقالي */
    }
    #CustomActionButton[border_type="bottom_border_red"] {
        border-bottom: 3px solid #e74c3c; /* أحمر */
    }
    #CustomActionButton[border_type="bottom_border_purple"] {
        border-bottom: 3px solid #9b59b6; /* بنفسجي */
    }
    #CustomActionButton[border_type="bottom_border_teal"] {
        border-bottom: 3px solid #1abc9c; /* برتقالي */
    }
    #CustomActionButton[border_type="bottom_border_pink"] {
        border-bottom: 3px solid #e91e63; /* برتقالي */
    }
    #CustomActionButton[border_type="bottom_border_gray"] {
        border-bottom: 3px solid #95a5a6; /* برتقالي */
    }
    #CustomActionButton[border_type="bottom_border_brown"] {
        border-bottom: 3px solid #b45c49; /* برتقالي */
    }
    #CustomActionButton[border_type="bottom_border_indigo"] {
        border-bottom: 3px solid #5d6d7e; /* برتقالي */
    }
    #CustomActionButton[border_type="bottom_border_lime"] {
        border-bottom: 3px solid #c7e0c2; /* برتقالي */
    }


    /* General Labels */
    QLabel {
        color: #333;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }

    /* Input Fields */
    QLineEdit {
        padding: 8px;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        background-color: #ffffff;
        selection-background-color: #3498db;
        selection-color: white;
        color: #333;
        text-align: center;
        /*min-height: 40px;*/
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    QLineEdit:focus {
        border-color: #3498db;
        background-color: #ffffff;
        text-align: center;
    }

    /* Combo Boxes */
    QComboBox {
        padding: 8px;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        background-color: #ffffff;
        combobox-popup: 0;
        min-width: 200px;
        color: #333;
        text-align: center;
        /*min-height: 40px;*/
        font-weight: bold;
        font-size: 16px;
        font-family: "Janna LT";
    }


    QComboBox:hover {
        border-color: #3498db;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top left;
        width: 20px;
        border-left-width: 1px;
        border-left-color: #bdc3c7;
        border-left-style: solid;
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
    }
    QComboBox::down-arrow {
        image: none;
        background-color: #bdc3c7;
        border: none;
        font-weight: bold;
        text-align: center;
        font-size: 16px;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        background-color: #ffffff;
        selection-background-color: #3498db;
        selection-color: white;
        color: #333;
        font-weight: bold;
        text-align: center;
        font-size: 16px;
    }

    /* Stat Boxes */
    #StatBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 6px;
        min-width: 150px;
        min-height: 46px;
        max-height: 50px;
        margin: 2px;
    }
    #StatBox[border_type="stat_border_blue"] {
        border-left: 5px solid #3498db;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }
    #StatBox[border_type="stat_border_green"] {
        border-left: 5px solid #2ecc71;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }
    #StatBox[border_type="stat_border_orange"] {
        border-left: 5px solid #f39c12;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }
    #StatBox[border_type="stat_border_red"] {
        border-left: 5px solid #e74c3c;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    #StatBox[border_type="stat_border_purple"] {
        border-left: 5px solid #9b59b6;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }
    #StatBox[border_type="stat_border_teal"] {
        border-left: 5px solid #1abc9c;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    #StatBox[border_type="stat_border_brown"] {
        border-left: 5px solid #b45c49;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }
    #StatBox[border_type="stat_border_indigo"] {
        border-left: 5px solid #5d6d7e;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }
    #StatBox[border_type="stat_border_lime"] {
        border-left: 5px solid #c7e0c2;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }


    #StatTitle {
        color: #555;
        font-weight: bold;
        font-size: 14px;
        padding: 0px;       /* يلغيه بالكامل */
        margin: 0px;        /* اختياري لو تبي تلغي الفراغات الخارجية */
    }

    #StatValue {
        color: #34495e;
        font-size: 16px;
        font-weight: bold;
        padding: 0px;       /* يلغيه بالكامل */
        margin: 0px;        /* يبعد الفاليو عن التايتل */
    }

    /* Section Title Label - نفس تصميم البطاقات */
    #SectionTitleLabel {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        min-width: 75px;
        margin: 2px;
        color: #34495e;
        font-size: 16px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    #SectionTitleLabel[border_type="stat_border_blue"] {
        border-left: 5px solid #3498db;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    /* Year ComboBox - نفس تصميم البطاقات */
    #YearComboBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 2px;
        color: #34495e;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    #YearComboBox[border_type="stat_border_green"] {
        border-left: 5px solid #2ecc71;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    /* Classification Filter ComboBox - نفس تصميم البطاقات */
    #ClassificationFilterComboBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 2px;
        color: #34495e;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    #ClassificationFilterComboBox[border_type="stat_border_purple"] {
        border-left: 5px solid #78d1e4;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    /* Status Filter ComboBox - نفس تصميم البطاقات */
    #StatusFilterComboBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 2px;
        color: #34495e;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    #StatusFilterComboBox[border_type="stat_border_lime"] {
        border-left: 5px solid #b471f0;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    /* Responsible Filter ComboBox - نفس تصميم البطاقات */
    #ResponsibleFilterComboBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 2px;
        color: #34495e;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    #ResponsibleFilterComboBox[border_type="stat_border_blue"] {
        border-left: 5px solid #3498db;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    /* Job Filter ComboBox - فلتر الوظيفة */
    #JobFilterComboBox {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 2px;
        color: #34495e;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
    }
    #JobFilterComboBox[border_type="stat_border_brown"] {
        border-left: 5px solid #b45c49;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }

    /* View Toggle Button - محسن ليتماشى مع تصميم البطاقات والفلاتر */
    #ViewToggleBtn {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 2px;
        color: #34495e;
        font-size: 14px;
        font-weight: bold;
        font-family: "Janna LT";
        text-align: center;
    }
    #ViewToggleBtn:hover {
        background-color: #f8f9fa;
        border-color: #bdc3c7;
    }
    #ViewToggleBtn:pressed {
        background-color: #e9ecef;
        border-color: #95a5a6;
    }
    #ViewToggleBtn[border_type="stat_border_red"] {
        border-left: 5px solid #e74c3c;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-bottom: 1px solid #dcdcdc;
    }


    /* تخصيص البوردر السفلي */
    #BottomBorderBox[border_type="bottom_border_green"] {
        border-bottom: 5px solid #2ecc71;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-left: 1px solid #dcdcdc;
    }
    #BottomBorderBox[border_type="bottom_border_yellow"] {
        border-bottom: 5px solid #f1c40f;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-left: 1px solid #dcdcdc;
    }
    #BottomBorderBox[border_type="bottom_border_blue"] {
        border-bottom: 5px solid #3498db;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-left: 1px solid #dcdcdc;
    }
    #BottomBorderBox[border_type="bottom_border_orange"] {
        border-bottom: 5px solid #f39c12;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-left: 1px solid #dcdcdc;
    }
    #BottomBorderBox[border_type="bottom_border_red"] {
        border-bottom: 5px solid #e74c3c;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-left: 1px solid #dcdcdc;
    }
    #BottomBorderBox[border_type="bottom_border_gold"] {
        border-bottom: 5px solid #f1c40f;
        border-right: 1px solid #dcdcdc;
        border-top: 1px solid #dcdcdc;
        border-left: 1px solid #dcdcdc;
    }

    #EmptyStateWidget{
        border-top: 1px solid #5a4765;
    }
    /* Table */
    QTableWidget {
        background-color: #f4f4f4;
        border: 1px solid #34495e;
        selection-background-color: #a6c9e2;
        selection-color: #333;
        gridline-color: #eeeeee;
        border-radius: 2px;
        alternate-background-color: #f8f8f8;
        font-size: 16px;
    }
    QTableWidget::item {
        padding: 15px;
        /*color: #34495e;*/
        text-align: center;
    }
    QTableWidget::item:selected {
        background-color: #2471a3;
        color: #FFFFFF;
    }
    QHeaderView::section {
        background-color: #24384a;
        color: #ecf0f1;
        padding: 0px;
        border: 1px solid #2c3e50;
        /*font-weight: bold;*/
        text-align: center;
        font-size: 14px;
        font-family: "Janna LT";
    }


    QHeaderView::section:vertical {
        background-color: #f4f4f4;
        color: #2c3e50;
        text-align: center;
        font-size: 14px;
        gridline-color: #eeeeee;
        min-width: 25px;
        /* خصائص إضافية */
    }

    QHeaderView::section:horizontal {
        border-top: 1px solid #2c3e50;
    }

    QTableCornerButton::section {
        background-color: #dcdcdc;
        border: 1px solid #bdc3c7;
    }
    QTableWidget::item:!selected[flags=0x00000020] {
        background-color: #ffffff;
        color: #555;
        font-weight: bold;
    }

    /* ستايل البروغرس بار */
    QProgressBar {
        border: none;
        border-radius: 10px;
        background-color: rgba(52, 73, 94, 0.2);
        text-align: center;
        color: #2c3e50;
        font-weight: bold;
        font-size: 14px;
        height: 25px;
        padding: 0px;
        margin: 5px 10px;
    }

    QProgressBar::chunk {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #3498db, stop:0.2 #2980b9,
            stop:0.5 #16a085, stop:0.8 #27ae60, stop:1 #2ecc71
        );
        border-radius: 10px;
        margin: 0px;
    }

    /* تأثير الظل للبروغرس بار */
    QProgressBar {
        background-color: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(240, 240, 240, 0.2),
            stop:1 rgba(240, 240, 240, 0.1)
        );
        
    }

    QTabWidget {
        background-color: transparent;
        border: none;
    }
    QTabWidget::pane {
        background-color: #ffffff;
        border: 3px solid #3498db;
        border-radius: 12px;
        padding: 10px;
        margin-top: 8px;
    }
    QTabBar::tab {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #ffffff, stop:1 #f8f9fa);
        color: #2c3e50;
        border: 2px solid #bdc3c7;
        border-bottom: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        padding: 12px 25px;
        margin-right: 3px;
        margin-left: 3px;
        font-weight: bold;
        font-size: 18px;
        min-width: 130px;
        min-height: 40px;
    }
    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #3498db, stop:1 #2980b9);
        color: white;
        border: 3px solid #2980b9;
        border-bottom: none;
        font-size: 19px;
    }
    QTabBar::tab:hover:!selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #ecf0f1, stop:1 #d5dbdb);
        color: #2980b9;
        border: 2px solid #3498db;
        border-bottom: none;
    }
     


    /* أنماط نظام البطاقات */
    /* تم إزالة أنماط ViewToggleBtn لأنه لم يعد يستخدم - العرض يتم التحكم فيه من القائمة المركزية */

    QStackedWidget#ViewStack {
        background-color: transparent;
        border: none;
    }

    """
    self.setStyleSheet(stylesheet)
