from ast import Return
from DB import*
from ستايل import*
from الدوال_الأساسية import*
from التحديثات import*
from الإعدادات_العامة import*
from متغيرات import*

# عرض البطاقات العصرية (لجميع الأقسام)
from نظام_البطاقات import ModernCardsContainer


# إنشاء شريط القوائم الرئيسي للتطبيق
def menu_bar(self):
    # إنشاء شريط القوائم القابل للسحب
    self.draggable_toolbar = DraggableToolBar("شريط الأدوات", self)
    self.addToolBar(Qt.TopToolBarArea, self.draggable_toolbar)
    
    # ربط أزرار القائمة بالقوائم المنسدلة
    self.draggable_toolbar.file_btn.setMenu(self.draggable_toolbar.file_menu)
    self.draggable_toolbar.customize_btn.setMenu(self.draggable_toolbar.customize_menu)
    self.draggable_toolbar.security_btn.setMenu(self.draggable_toolbar.security_menu)
    self.draggable_toolbar.help_btn.setMenu(self.draggable_toolbar.help_menu)
    self.draggable_toolbar.info_btn.setMenu(self.draggable_toolbar.info_menu)
    self.draggable_toolbar.accounting_btn.setMenu(self.draggable_toolbar.accounting_menu)
    
    # إعداد القوائم
    self._setup_file_menu()
    self.setup_security_menu()
    self._setup_customize_menu()
    self._setup_help_menu()
    self._setup_info_menu()
    self._setup_shortcuts_menu()
    
    # ربط حقل البحث بدالة البحث
    self.draggable_toolbar.search_input.textChanged.connect(
        lambda text: self.search_data(text, self.get_current_section_name())
    )
    
    # ربط زر الإشعارات
    self.draggable_toolbar.notification_btn.clicked.connect(self.check_for_updates_pottom)


# DragGableToolbar
class DraggableToolBar(QToolBar):
    # init
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setMovable(True)
        self.setFloatable(True)
        self.setAllowedAreas(Qt.AllToolBarAreas)
        self.setObjectName("DraggableToolBar")
        self.parent = parent

        # Set initial position to top
        self.setOrientation(Qt.Horizontal)

        # Create layout for toolbar contents
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(3, 0, 3, 0)
        self.main_layout.setSpacing(5)

        # Add the widget to the toolbar
        self.addWidget(self.main_widget)

        # Create menus
        self._create_menus()

        # Initialize components in the correct order for proper layout
        self._setup_menu_buttons()      # أزرار القائمة على اليمين
        self._setup_search_bar()        # شريط البحث في المنتصف
        self._setup_notifications()     # زر الإشعارات بعد شريط البحث
        self._setup_username_display()  # عرض اسم المستخدم بعد زر الإشعارات
        self._setup_datetime_display()  # عرض الوقت والتاريخ في أقصى اليسار


        # Timer for updating date/time
        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self._update_datetime)
        self.datetime_timer.start(1000)  # Update every second

        # Apply stylesheet
        self._apply_stylesheet()

    # قم بإنشاء جميع القوائم لشرب الأدوات
    def _create_menus(self):
        # إنشاء القوائم الرئيسية
        self.file_menu = QMenu("ملف")
        self.file_menu.setObjectName("ملف")

        self.customize_menu = QMenu("تخصيص")
        self.customize_menu.setObjectName("تخصيص")

        self.security_menu = QMenu("الحماية")
        self.security_menu.setObjectName("الحماية")

        self.help_menu = QMenu("مساعدة")
        self.help_menu.setObjectName("مساعدة")

        self.info_menu = QMenu("معلومات")
        self.info_menu.setObjectName("معلومات")

        self.accounting_menu = QMenu("محاسبة")
        self.accounting_menu.setObjectName("محاسبة")

        # Set layout direction for all menus
        for menu in [self.file_menu, self.customize_menu, self.security_menu,
                    self.help_menu, self.info_menu, self.accounting_menu]:
            menu.setLayoutDirection(Qt.RightToLeft)

    # أزرار قائمة الإعداد على شريط الأدوات
    def _setup_menu_buttons(self):
        menu_widget = QWidget()
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(3)

        # Create menu buttons
        self.file_btn = QPushButton("ملف")
        self.file_btn.setObjectName("ToolbarMenuButton")

        self.customize_btn = QPushButton("تخصيص")
        self.customize_btn.setObjectName("ToolbarMenuButton")

        self.security_btn = QPushButton("الحماية")
        self.security_btn.setObjectName("ToolbarMenuButton")

        self.help_btn = QPushButton("مساعدة")
        self.help_btn.setObjectName("ToolbarMenuButton")

        self.info_btn = QPushButton("معلومات")
        self.info_btn.setObjectName("ToolbarMenuButton")

        self.accounting_btn = QPushButton("محاسبة")
        self.accounting_btn.setObjectName("ToolbarMenuButton")

        # Add buttons to layout (عكس الترتيب من اليمين إلى اليسار)
        menu_layout.addWidget(self.file_btn)
        menu_layout.addWidget(self.customize_btn)
        menu_layout.addWidget(self.security_btn)
        menu_layout.addWidget(self.help_btn)
        menu_layout.addWidget(self.info_btn)
        menu_layout.addWidget(self.accounting_btn)

        # Add to main layout
        self.main_layout.addWidget(menu_widget)

    # الإعداد شريط البحث على شريط الأدوات
    def _setup_search_bar(self):
        # إنشاء حاوية لشريط البحث
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)

        # إضافة مساحة مرنة قبل شريط البحث لدفعه للمنتصف
        search_layout.addStretch(1)

        # إنشاء شريط البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setMaximumWidth(350)
        self.search_input.setObjectName("ToolbarSearchInput")

        # إضافة أيقونة البحث
        search_icon = QIcon(أيقونة_بحث)
        self.search_input.addAction(search_icon, QLineEdit.LeadingPosition)

        # إضافة شريط البحث إلى الحاوية
        search_layout.addWidget(self.search_input)

        # إضافة مساحة مرنة بعد شريط البحث لإبقائه في المنتصف
        #search_layout.addStretch(1)

        # إضافة الحاوية إلى التخطيط الرئيسي
        self.main_layout.addWidget(search_container)

    # عرض تاريخ الإعداد والوقت على شريط الأدوات
    def _setup_datetime_display(self):
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("ToolbarDateTimeLabel")
        self._update_datetime()  # Initial update

        self.main_layout.addWidget(self.datetime_label)

    # قم بتحديث عرض التاريخ والوقت
    def _update_datetime(self):
        now = datetime.now()

        # Get Arabic day name
        day_of_week = now.weekday() + 1  # Convert from 0-6 to 1-7
        arabic_days = {
            1: "الإثنين",
            2: "الثلاثاء",
            3: "الأربعاء",
            4: "الخميس",
            5: "الجمعة",
            6: "السبت",
            7: "الأحد"
        }
        arabic_day = arabic_days.get(day_of_week, "")

        # Format date
        date_str = now.strftime("%Y-%m-%d")

        # Format time with Arabic AM/PM
        hour = now.hour
        am_pm = "ص" if hour < 12 else "م"

        # Convert to 12-hour format
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12

        time_str = f"{hour_12}:{now.minute:02d}:{now.second:02d} {am_pm}"

        # Combine all parts with separators
        self.datetime_label.setText(f"{arabic_day} | {date_str} | {time_str}")

    # إعداد اسم المستخدم على شريط الأدوات
    def _setup_username_display(self):
        # Get account type from settings
        account_type = settings.value("account_type", "admin")

        self.username_label = QLabel(f"👤 {account_type}")
        self.username_label.setObjectName("ToolbarUsernameLabel")

        self.main_layout.addWidget(self.username_label)

    # إخطارات الإعداد على شريط الأدوات
    def _setup_notifications(self):
        self.notification_btn = QPushButton()
        self.notification_btn.setObjectName("ToolbarNotificationButton")

        # Set bell icon
        bell_icon_path = os.path.join(icons_dir, 'check.png')
        if os.path.exists(bell_icon_path):
            self.notification_btn.setIcon(QIcon(bell_icon_path))
        else:
            self.notification_btn.setText("🔔")

        self.notification_btn.setIconSize(QSize(20, 30))
        #self.notification_btn.setFixedSize(20, 18)

        # Add notification button after the search bar
        # We'll simply add it to the main layout since the order is now controlled
        # by the initialization sequence in __init__
        self.main_layout.addWidget(self.notification_btn)

    # أضف زرًا إلى قائمة
    def addMenuButton(self, menu, text, function, icon_path=None):
        button = QPushButton(text)
        button.clicked.connect(function)
        button.setFixedWidth(220)  # تحديد عرض ثابت للزر
        if icon_path:
            button.setIcon(QIcon(icon_path))  # تعيين الأيقونة من المسار المحدد
            button.setIconSize(QSize(20, 20))  # تحديد حجم الأيقونة
        action = QWidgetAction(menu)
        action.setDefaultWidget(button)
        menu.addAction(action)

    # قم بتطبيق ورقة الأنماط على شريط الأدوات
    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QToolBar {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #24384a,
                    stop:1 #1b3459
                );
                border-bottom: 1px solid #5a4765;
                padding: 2px;
                min-height: 35px;
                max-height: 40px;
                font-weight: bold;
            }

            #ToolbarMenuButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                padding: 2px 8px;
                font-weight: bold;
                font-size: 14px;
                font-family:'Janna LT';
                border-radius: 3px;
                margin: 0 2px;
                max-height: 25px;
            }

            #ToolbarMenuButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-bottom: 3px solid #f39c12;
            }

            #ToolbarSearchInput {
                border: 1px solid #3498db;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 2px 8px;
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                font-weight: bold;
                min-height: 10px;
                max-height: 25px;
                font-size: 14px;
                font-family:'Janna LT';

            }

            #ToolbarSearchInput:focus {
                border:2px solid #f39c12;
                background-color: rgba(255, 255, 255, 0.2);
            }

            #ToolbarDateTimeLabel, #ToolbarUsernameLabel {
                padding: 2px 8px;
                font-weight: bold;
                color: white;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                margin: 0 3px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-height: 25px;
                font-size: 14px;
                font-family:'Janna LT';
            }

            #ToolbarNotificationButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 2px 5px;
                margin: 0 3px;

                max-height: 25px;
                font-size: 14px;
                font-family:'Janna LT';

            }

            #ToolbarNotificationButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border:2px solid #f39c12;
            }

            QMenu {
                background-color: #2c3e50;
                border: 1px solid #5d6d7e;
                border-radius: 6px;
                padding: 5px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-width: 180px;

                border-bottom: 2px solid #6B1F659C;
            }

            QMenu::item {
                padding: 8px 25px 8px 15px;
                border-radius: 4px;
                margin: 3px 5px;
                font-weight: bold;

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
        """)

# الاتصالات
class SideMenuButton(QPushButton):
    # init
    def __init__(self, icon_path, text, parent=None):
        super().__init__("", parent)
        #self.setIconSize(QSize(32, 32))
        #self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignCenter) # Align contents top-center

        icon_label = QLabel()
        if os.path.exists(icon_path):
             pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
             icon_label.setPixmap(pixmap)
        else:
             icon_label.setText("?")
             #icon_label.setFont(QFont("Janna LT", 16))

        icon_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        #text_label.setFont(QFont("Janna LT", 10)) # خط أصغر للنص
        #خلّي النص داخل  يلف (يُنزل للسطر اللي بعده) لما يكون طويل وما يكفي في السطر.
        text_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()

        self.setFixedSize(100, 80) # حجم ثابت للزر
        self.setObjectName("SideMenuButton")

        layout.setSpacing(2)
        layout.setContentsMargins(5, 6, 5, 2)
        text_label.setMinimumHeight(text_label.fontMetrics().height())
        self._apply_stylesheet()

    # تطبيق ستايل شيت على الزر
    def _apply_stylesheet(self):
        apply_stylesheet(self)


# ايقونه فوق النص للازرار المخصصة
# CustomActionbutton
class CustomActionButton(QPushButton):
    # init
    def __init__(self, icon_path, text, parent=None):
        super().__init__("", parent)
        #self.setIconSize(QSize(32, 32))
        self.setObjectName("CustomActionButton")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_size = 38 # Smaller icon size for in-page buttons
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("?")
            #icon_label.setFont(QFont("Arial", 12))

        icon_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        #text_label.setFont(QFont("Janna LT", 11))
        text_label.setWordWrap(True)
        text_label.setMinimumHeight(text_label.fontMetrics().height())

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        #self.setFixedSize(100, 80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        apply_stylesheet(self)

#بوكسات الاحصائية
# Statbox
class StatBox(QFrame):
    # init
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("StatBox")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # Allow horizontal stretch
        self.setMinimumHeight(60) # Ensure minimum height

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5) # هوامش داخلية
        layout.setSpacing(3) # تباعد بين العناصر
        layout.setAlignment(Qt.AlignCenter) # Center content vertically

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("StatTitle")
        title_label.setWordWrap(True) # Allow wrapping if title is long
        # Use fallback font
        font_title = QFont("Janna LT", 12)
        title_label.setFont(font_title)

        value_label = QLabel(str(value))

        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("StatValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

    # تحديث قيمة الإحصائية
    def update_value(self, new_value):
        value_label = self.findChild(QLabel, "StatValue")
        if value_label:
            value_label.setText(str(new_value))


#إنشاء صفحات لكل قسم في
# إنشاء أقسام
def create_sections(self):
    self.sections = {} 
    for section_name in self.interactive_sections:
        page = QWidget()
        page.setObjectName(f"{section_name.replace(' ', '_')}_Page")
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(10, 10, 10, 10)
        page_layout.setSpacing(5)
        page_layout.setAlignment(Qt.AlignTop)

        # --- Header Row: Title, Std Actions, Search, Year ---
        header_row_frame = QFrame()
        header_row_frame.setObjectName("SectionHeaderRowFrame")

        header_row_layout = QHBoxLayout(header_row_frame)
        header_row_layout.setContentsMargins(0, 0, 0, 0)
        header_row_layout.setSpacing(5)
        header_row_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # Section Title (Right)
        section_title_label = QLabel(f"{section_name}")
        section_title_label.setObjectName("SectionTitleLabel")
        section_title_label.setAlignment(Qt.AlignCenter)
        # تعيين نفس ارتفاع البطاقات وتلوين البوردر الأيسر
        section_title_label.setMinimumHeight(46)
        section_title_label.setMaximumHeight(100)
        section_title_label.setProperty("border_type", "stat_border_blue")  # لون أزرق للعنوان
        header_row_layout.addWidget(section_title_label)

        # Spacer to push search/year to the left
        #header_row_layout.addStretch()

        # Year Selector and Search Input (Left)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)
        controls_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        header_row_layout.addLayout(controls_layout)
        page_layout.addWidget(header_row_frame)

        # --- إنشاء تخطيط عمودي للتحكمات الجانبية (بحث + سنة + حالة) ---------------------------------------
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)
        controls_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        # نضيف كل شيء إلى الهيدر
        header_row_layout.addLayout(controls_layout)



        # --- احصاءات Stat Boxes ---
        stat_names = []
        if section_name == "المشاريع":
                stat_names = ["مشاريع قيد الإنجاز", "الوارد السنوي", "إجمالي الباقي"]
        elif section_name == "المقاولات":
                stat_names = ["مقاولات قيد الإنجاز", "الوارد السنوي", "إجمالي الباقي"]
        elif section_name == "الحسابات":
                stat_names = ["مصروفات الشهر", "مصروفات السنة", "إجمالي المصروفات"]
        elif section_name == "الموظفين":
                stat_names = ["عدد الموظفين", "إجمالي الرصيد", "إجمالي السحب"]
        elif section_name == "العملاء":
                stat_names = ["إجمالي العملاء", "عملاء جدد هذا الشهر", "عملاء لهم مشاريع نشطة"]


        elif section_name == "التدريب":
                stat_names = ["دورات قيد التسجيل", "دورات جارية", "إجمالي الإيرادات", "إجمالي المشاركين"]

        elif section_name == "الموردين":
                stat_names = ["موردين قيد الإنجاز", "الوارد السنوي", "إجمالي الباقي"]
        

        elif section_name == "التقارير":
                stat_names = ["إجمالي الإيرادات", "إجمالي المصروفات", "صافي الربح", "الأرصدة المدينة", "الأرصدة الدائنة"]

        current_stat_boxes = {}
        # Cycle through STAT_BORDER_TYPES for different borders
        for i, name in enumerate(stat_names):
                stat_box = StatBox(name, "جار التحميل...")
                # Assign a dynamic property to determine border color
                border_type = STAT_BORDER_TYPES[i % len(STAT_BORDER_TYPES)]
                stat_box.setProperty("border_type", border_type)
                current_stat_boxes[name] = stat_box
                controls_layout.addWidget(stat_box)

        # إنشاء كومبو السنة منفصل لكل قسم - بعد الإحصائيات وقبل الفلاتر
        year_combo = QComboBox()
        year_combo.setObjectName("YearComboBox")
        self.populate_years(year_combo)
        year_combo.currentIndexChanged.connect(lambda index, sec_name=section_name: self.change_year(index, sec_name))
        ComboBox_Center_item(year_combo)
        # تعيين نفس ارتفاع البطاقات وتلوين البوردر الأيسر
        year_combo.setMinimumHeight(46)
        year_combo.setMaximumHeight(100)
        year_combo.setProperty("border_type", "stat_border_green")  # لون أخضر للسنة
        controls_layout.addWidget(year_combo)

        # إنشاء فلتر التصنيف لجميع الأقسام التي تحتوي على عمود التصنيف
        sections_with_classification = ["المشاريع", "المقاولات", "العملاء", "الحسابات", "الموظفين", "التدريب"]
        if section_name in sections_with_classification:
            classification_filter_combo = QComboBox()
            classification_filter_combo.setObjectName("ClassificationFilterComboBox")
            self.populate_classification_filter(classification_filter_combo, section_name)
            ComboBox_Center_item(classification_filter_combo)
            # تعيين نفس ارتفاع البطاقات وتلوين البوردر الأيسر
            classification_filter_combo.setMinimumHeight(46)
            classification_filter_combo.setMaximumHeight(100)
            classification_filter_combo.setProperty("border_type", "stat_border_purple")  # لون بنفسجي للتصنيف
            classification_filter_combo.currentTextChanged.connect(lambda text, sec=section_name: self.filter_table_by_classification(sec, text))
            controls_layout.addWidget(classification_filter_combo)
        else:
            classification_filter_combo = None

        # إنشاء فلتر الحالة منفصل لكل قسم
        filter_combo = QComboBox()
        filter_combo.setObjectName("StatusFilterComboBox")

        # معالجة خاصة لقسم التقارير المالية
        if section_name == "التقارير":
            filter_combo.addItems(["كل التقارير", "التقارير المالية", "تقارير المشاريع", "تقارير الموظفين"])
        else:
            self.populate_status_filter(filter_combo, section_name)
        ComboBox_Center_item(filter_combo)
        # تعيين نفس ارتفاع البطاقات وتلوين البوردر الأيسر
        filter_combo.setMinimumHeight(46)
        filter_combo.setMaximumHeight(100)
        filter_combo.setProperty("border_type", "stat_border_lime")  # لون ليموني للحالة
        filter_combo.currentTextChanged.connect(lambda text, sec=section_name: self.filter_table(sec, text))
        controls_layout.addWidget(filter_combo)

        # إنشاء فلتر الوظيفة لقسم الموظفين فقط
        job_filter_combo = None
        if section_name == "الموظفين":
            job_filter_combo = QComboBox()
            job_filter_combo.setObjectName("JobFilterComboBox")
            self.populate_job_filter(job_filter_combo, section_name)
            ComboBox_Center_item(job_filter_combo)
            # تعيين نفس ارتفاع البطاقات وتلوين البوردر الأيسر
            job_filter_combo.setMinimumHeight(46)
            job_filter_combo.setMaximumHeight(100)
            job_filter_combo.setProperty("border_type", "stat_border_brown")  # لون بني للوظيفة
            job_filter_combo.currentTextChanged.connect(lambda text, sec=section_name: self.filter_table_by_job(sec, text))
            controls_layout.addWidget(job_filter_combo)

        # إنشاء فلتر المسؤول للمشاريع والمقاولات فقط
        responsible_filter_combo = None
        if section_name in ["المشاريع", "المقاولات"]:
            responsible_filter_combo = QComboBox()
            responsible_filter_combo.setObjectName("ResponsibleFilterComboBox")
            self.populate_responsible_filter(responsible_filter_combo, section_name)
            ComboBox_Center_item(responsible_filter_combo)
            # تعيين نفس ارتفاع البطاقات وتلوين البوردر الأيسر - نفس تصميم الفلاتر الأخرى
            responsible_filter_combo.setMinimumHeight(46)
            responsible_filter_combo.setMaximumHeight(100)
            responsible_filter_combo.setProperty("border_type", "stat_border_blue")  # لون أزرق للمسؤول
            responsible_filter_combo.currentTextChanged.connect(lambda text, sec=section_name: self.filter_table_by_responsible(sec, text))
            controls_layout.addWidget(responsible_filter_combo)


        # --- ازرار اضافية Custom Action Buttons ---
        custom_actions_container = QWidget()
        custom_actions_layout = QHBoxLayout(custom_actions_container)
        custom_actions_layout.setContentsMargins(0, 0, 0, 0)
        custom_actions_layout.setSpacing(8)
        custom_actions_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        section_custom_config = CUSTOM_ACTIONS_CONFIG.get(section_name, [])
        custom_buttons_list = []

        if not section_custom_config:
            custom_actions_container.hide()
        else:
            for item in section_custom_config:
                if len(item) >= 4:  # إذا كان العنصر يحتوي على 4 عناصر أو أكثر (النص، الأيقونة، اسم الإجراء، نوع البوردر)
                    btn_text, btn_icon, action_name, border_type = item
                    btn = CustomActionButton(btn_icon, btn_text)
                    # تعيين خصائص الزر
                    btn.setProperty("action", action_name)
                    btn.setProperty("border_type", border_type)
                elif len(item) == 3:  # إذا كان العنصر يحتوي على 3 عناصر فقط (النص، الأيقونة، اسم الإجراء)
                    btn_text, btn_icon, action_name = item
                    btn = CustomActionButton(btn_icon, btn_text)
                    # تعيين خاصية الإجراء فقط
                    btn.setProperty("action", action_name)

                # ربط الزر بمعالج الإجراء المخصص
                btn.clicked.connect(lambda checked=False, act=action_name, sec=section_name: self.handle_custom_action(act, sec))
                custom_actions_layout.addWidget(btn)
                custom_buttons_list.append(btn) # إضافة إلى القائمة

            #custom_actions_layout.addStretch() # Push custom buttons to the right

        # Scroll Area to wrap the custom action buttons
        custom_actions_scroll = QScrollArea()
        custom_actions_scroll.verticalScrollBar().setObjectName("customScrollBar")
        custom_actions_scroll.setWidgetResizable(True)
        custom_actions_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        custom_actions_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        custom_actions_scroll.setFrameShape(QScrollArea.NoFrame)
        custom_actions_scroll.setWidget(custom_actions_container)
        custom_actions_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        custom_actions_scroll.setFixedHeight(110)  # عدل الارتفاع حسب حجم الأزرار
        custom_actions_scroll.setStyleSheet("background-color: transparent;")


        #page_layout.addWidget(custom_actions_frame)
        page_layout.addWidget(custom_actions_scroll)

        # البحث يبقى في تخطيط أفقي لحاله
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setAlignment(Qt.AlignCenter)
        search_input.setPlaceholderText(f"بحث في {section_name}...")
        search_input.setObjectName("SearchInput")
        search_input.setStyleSheet("""
            QLineEdit {
                min-width: 80px;
                min-height: 40px;

            }
            """)
        search_input.textChanged.connect(lambda text, sec_name=section_name: self.search_data(text, sec_name))
        # إضافة أيقونة البحث
        search_icon = QIcon(أيقونة_بحث)
        search_input.addAction(search_icon, QLineEdit.LeadingPosition)

        #search_layout.addWidget(search_input, 1)
        #controls_layout.addLayout(search_layout, 1)

        # تم نقل كومبو السنة والتصنيف والحالة إلى أعلى قبل بطاقات المعلومات


        # --- Empty State Widget (Logo + Button) ---
        # This widget will be shown when the table is empty
        empty_state_widget = QWidget()
        empty_state_widget.setObjectName("EmptyStateWidget")
        empty_state_layout = QVBoxLayout(empty_state_widget)
        empty_state_layout.setContentsMargins(0, 0, 0, 0)
        empty_state_layout.setSpacing(0)
        empty_state_layout.setAlignment(Qt.AlignCenter) # Center contents vertically and horizontally

        # # استخدام QGridLayout بدلاً من QVBoxLayout
        # empty_state_layout = QGridLayout(empty_state_widget)
        # empty_state_layout.setContentsMargins(20, 20, 20, 20) # هوامش حول الشبكة كلها
        # empty_state_layout.setSpacing(25) # المسافات بين الأزرار
        # empty_state_layout.setAlignment(Qt.AlignCenter) # محاذاة الشبكة في المنتصف

        empty_state_logo_label = QLabel()
        empty_state_logo_label.setObjectName("EmptyStateLogo")
        logo_size_large = 350 # Larger logo for empty state
        if os.path.exists(أيقونة_الشعار):
            pixmap = QPixmap(أيقونة_الشعار).scaled(logo_size_large, logo_size_large, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            empty_state_logo_label.setPixmap(pixmap)
        else:
                empty_state_logo_label.setText(f"{self.company_name}\nLogo")
                empty_state_logo_label.setAlignment(Qt.AlignCenter)
                empty_state_logo_label.setFont(QFont("Janna LT", 24, QFont.Bold))

        empty_state_layout.addWidget(empty_state_logo_label)

        # Text under logo
        version_label = QLabel(f"منظومة المهندس V{CURRENT_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        #version_label.setFont(QFont("Janna LT", 50, QFont.Bold))
        version_label.setStyleSheet("""
        QLabel {
            background-color: transparent;
            color: #cccccc;
            border: none;
            padding: 10px 10px; /* Larger padding */
            border-radius: 8px; /* More rounded corners */
            font-size: 20pt; /* Larger font */
            font-weight: bold;
            min-height: 20;
            max-height: 80;
            font-family: "Janna LT"; /* اسم الخط */
        }"""
        )

        empty_state_layout.addWidget(version_label)

        if section_name in section_labels:
            label = section_labels[section_name]
            empty_state_add_button = QPushButton(f"           إضافة {label} جديد")

        empty_state_add_button.setObjectName("EmptyStateAddButton")

        empty_state_add_button.setIcon(QIcon(أيقونة_إضافة))
        empty_state_add_button.setIconSize(QSize(24, 24))

        empty_state_add_button.setFont(QFont("Janna LT", 16, QFont.Bold))
        # ضبط التنسيق باستخدام StyleSheet
        empty_state_add_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                text-align: center;
                qproperty-iconSize: 24px;
            }
            QPushButton::icon {
                padding-left: 04px; /* تقلل المسافة بين الأيقونة والنص */
            }
        """)
        # تأكيد على المحاذاة (احتياط)
        empty_state_add_button.setLayoutDirection(Qt.RightToLeft)  # مهم لو تبي الأيقونة يمين
        empty_state_add_button.clicked.connect(lambda checked=False, sec_name=section_name: self.handle_action_button("اضافة", sec_name))


        #empty_state_layout.addStretch() # Push logo/button to center


        empty_state_layout.addWidget(empty_state_add_button)
        #empty_state_layout.addStretch() # Push logo/button to center

        # Initially hide the empty state widget
        empty_state_widget.hide()
        # Set a size policy so it can expand if needed, but respects layout minimums
        # empty_state_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        page_layout.addWidget(empty_state_widget, 1) # Add empty state widget, give it stretch factor


        # --- Bottom Area: The Table and Cards View -------------------------------------------------
        # معالجة خاصة لقسم التقارير المالية
        if section_name == "التقارير":
            # استخدام النظام المخصص للتقارير المالية
            try:
                from محتوى_التقارير_المالية import FinancialSummaryWidget
                financial_widget = FinancialSummaryWidget(self, page)
                page_layout.addWidget(financial_widget, 1)

                # إخفاء الويدجت الفارغ لأننا نستخدم النظام المخصص
                empty_state_widget.hide()

            except Exception as e:
                print(f"خطأ في تحميل النظام المالي المخصص: {e}")
                # في حالة الفشل، استخدم النظام العادي
                view_stack = QStackedWidget()
                view_stack.setObjectName("ViewStack")

                table = QTableWidget()
                table.setObjectName("DataTable")
                columns = TABLE_COLUMNS.get(section_name, [])
                self._setup_table(table, columns)
                view_stack.addWidget(table)

                cards_view = ModernCardsContainer("financial")
                view_stack.addWidget(cards_view)
                page_layout.addWidget(view_stack, 1)
        else:
            # إنشاء StackedWidget للتبديل بين عرض الجدول والبطاقات (منفصل لكل قسم)
            view_stack = QStackedWidget()  # إنشاء view_stack منفصل لكل قسم
            view_stack.setObjectName("ViewStack")

            # عرض الجدول (الافتراضي)
            table = QTableWidget()
            table.setObjectName("DataTable")
            columns = TABLE_COLUMNS.get(section_name, []) # Get columns from the map
            self._setup_table(table, columns) # Call setup later after filling data
            view_stack.addWidget(table)

            # تحديد نوع البطاقة حسب القسم
            card_type_mapping = {
                "المشاريع": "project",
                "المقاولات": "project",  # المقاولات تستخدم نفس نوع بطاقة المشاريع
                "العملاء": "client",
                "الموظفين": "employee",
                "الحسابات": "expense",  # إضافة قسم الحسابات
                "المصروفات": "expense",
                "التدريب": "training",
                "الموردين": "supplier"
            }

            card_type = card_type_mapping.get(section_name, "project")
            cards_view = ModernCardsContainer(card_type)
            view_stack.addWidget(cards_view)

        # إضافة زر التبديل فقط للأقسام العادية (ليس التقارير)
        if section_name != "التقارير":
            # إضافة زر التبديل الفردي لكل قسم - محسن ليتماشى مع تصميم البطاقات والفلاتر
            view_toggle_btn = QPushButton()
            view_toggle_btn.setObjectName("ViewToggleBtn")
            view_toggle_btn.setMinimumHeight(46)
            view_toggle_btn.setMaximumHeight(100)
            view_toggle_btn.setFixedWidth(120)
            view_toggle_btn.setProperty("border_type", "stat_border_red")

            # تحديد النص الأولي حسب التفضيل المحفوظ
            # استخدام الافتراضي إذا لم تكن الدالة متوفرة بعد
            try:
                preferred_view = self.get_section_view_preference(section_name)
            except AttributeError:
                # استخدام الافتراضي المؤقت
                preferred_view = "table" if section_name == "الحسابات" else "cards"
            if preferred_view == "cards":
                view_toggle_btn.setText("📊 جدول")
                view_toggle_btn.setToolTip(f"التبديل إلى عرض الجدول لقسم {section_name}")
            else:
                view_toggle_btn.setText("🎴 بطاقات")
                view_toggle_btn.setToolTip(f"التبديل إلى عرض البطاقات لقسم {section_name}")

            view_toggle_btn.clicked.connect(lambda checked=False, sec_name=section_name: self.toggle_section_view_and_update_button(sec_name))
            controls_layout.addWidget(view_toggle_btn)

            page_layout.addWidget(view_stack, 1) # Set stretch factor to 1 so view takes remaining space

        self.main_content_area.addWidget(page)

        # تخزين المعلومات الخاصة بهذا القسم/الصفحة
        if section_name == "التقارير":
            # معلومات خاصة لقسم التقارير المالية
            section_data = {
                "page": page,
                "table": None,  # لا يوجد جدول عادي
                "view_stack": None,  # لا يوجد view stack
                "view_toggle_btn": None,  # لا يوجد زر تبديل
                "stats": current_stat_boxes,
                "search_input": search_input,
                "year_combo": year_combo,
                "filter_combo": filter_combo,
                "classification_filter_combo": classification_filter_combo,
                "job_filter_combo": job_filter_combo,
                "responsible_filter_combo": responsible_filter_combo,
                "custom_buttons": custom_buttons_list,
                "title_label": section_title_label,
                "empty_state_widget": empty_state_widget,
                "empty_state_add_button": empty_state_add_button,
                "current_view": "financial_reports"  # نوع خاص للتقارير المالية
            }
        else:
            # معلومات عادية للأقسام الأخرى
            section_data = {
                "page": page,
                "table": table,
                "view_stack": view_stack,  # Reference to the view stack (منفصل لكل قسم)
                "view_toggle_btn": view_toggle_btn,  # Reference to the toggle button
                "stats": current_stat_boxes,
                "search_input": search_input, # Reference to THIS section's search input
                "year_combo": year_combo,     # Reference to THIS section's year combo (منفصل لكل قسم)
                "filter_combo": filter_combo, # Reference to filter combo (منفصل لكل قسم)
                "classification_filter_combo": classification_filter_combo, # Reference to classification filter combo (منفصل لكل قسم)
                "job_filter_combo": job_filter_combo, # Reference to job filter combo (للموظفين فقط)
                "responsible_filter_combo": responsible_filter_combo, # Reference to responsible filter combo (للمشاريع والمقاولات فقط)
                "custom_buttons": custom_buttons_list, # List of THIS section's custom buttons
                "title_label": section_title_label, # Reference to THIS section's title
                "empty_state_widget": empty_state_widget, # Reference to the empty state widget
                "empty_state_add_button": empty_state_add_button, # Reference to the button inside empty state
                "current_view": "table"  # Track current view (table or cards)
            }

        # تم حفظ classification_filter_combo بالفعل في section_data أعلاه
        # لا حاجة لإعادة تعيينه هنا

        self.sections[section_name] = section_data




    # Connect year combo box signals after all sections are created
    # This ensures that the lambda correctly captures the section_name
    for section_name, section_info in self.sections.items():
            section_info["year_combo"].currentIndexChanged.connect(
                lambda index, sec_name=section_name: self.change_year(index, sec_name)
            )

    center_all_widgets(page)


# الانتقال إلى قسم معين وتحميل بياناته من قاعدة البيانات
# عرض قسم
def show_section(self, section_name):

    # معالجة خاصة للصفحة الرئيسية
    if section_name == "الرئيسية" and "الرئيسية" not in self.sections:
        self._create_home_page()
        
    # تحديث حالة الأزرار - إزالة خاصية active من جميع الأزرار
    for button in self.findChildren(SideMenuButton):
        button.setProperty("active", "false")
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    # تعيين خاصية active للزر الحالي
    for button in self.findChildren(SideMenuButton):
        if button.property("section") == section_name:
            button.setProperty("active", "true")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
            break

    # لا توجد معالجة خاصة لقسم التقارير - سيتم عرضه في المنطقة الرئيسية

    if section_name in self.sections:
        section_info = self.sections[section_name]
        self.main_content_area.setCurrentWidget(section_info["page"])


        self.setWindowTitle(f"{self.company_name} - {section_name}")

        # التحقق من صحة كائن اختيار السنة قبل الوصول إليه
        selected_year_widget = section_info.get("year_combo")
        if selected_year_widget and hasattr(selected_year_widget, 'currentText'):
            try:
                selected_year = selected_year_widget.currentText()
            except RuntimeError:
                # إذا كان الكائن محذوف، استخدم السنة الحالية
                selected_year = str(QDate.currentDate().year())
        else:
            # إذا لم يوجد كائن اختيار السنة، استخدم السنة الحالية
            selected_year = str(QDate.currentDate().year())

        data = self._load_data_from_db(section_info["table"], section_name)

        if data is None or not data:
            data = []


        self._update_stats(section_info["stats"], section_name, selected_year)

        # إعادة تعيين حقل البحث بأمان
        search_input = section_info.get("search_input")
        if search_input and hasattr(search_input, 'clear'):
            try:
                search_input.clear()
            except RuntimeError:
                pass  # تجاهل إذا كان الكائن محذوف

        # إعادة تعيين مرشح الحالة/التصنيف بأمان
        filter_combo = section_info.get("filter_combo")
        if filter_combo and hasattr(filter_combo, 'count'):
            try:
                if filter_combo.count() > 0:
                    # تحديد النص الصحيح حسب نوع القسم
                    if section_name in ["المشاريع", "المقاولات", "الموظفين", "التدريب"]:
                        filter_combo.setCurrentText("كل الحالات")
                    else:
                        filter_combo.setCurrentText("كل التصنيفات")
            except RuntimeError:
                pass  # تجاهل إذا كان الكائن محذوف

        # إعادة تعيين مرشح التصنيف بأمان
        classification_filter_combo = section_info.get("classification_filter_combo")
        if classification_filter_combo and hasattr(classification_filter_combo, 'count'):
            try:
                if classification_filter_combo.count() > 0:
                    classification_filter_combo.setCurrentText("كل التصنيفات")
            except RuntimeError:
                pass  # تجاهل إذا كان الكائن محذوف

        # إعادة تعيين مرشح الوظائف بأمان
        job_filter_combo = section_info.get("job_filter_combo")
        if job_filter_combo and hasattr(job_filter_combo, 'count'):
            try:
                if job_filter_combo.count() > 0:
                    job_filter_combo.setCurrentText("كل الوظائف")
            except RuntimeError:
                pass  # تجاهل إذا كان الكائن محذوف

        # إعادة تعيين مرشح المسؤولين بأمان
        responsible_filter_combo = section_info.get("responsible_filter_combo")
        if responsible_filter_combo and hasattr(responsible_filter_combo, 'count'):
            try:
                if responsible_filter_combo.count() > 0:
                    responsible_filter_combo.setCurrentText("كل المسؤولين")
            except RuntimeError:
                pass  # تجاهل إذا كان الكائن محذوف

        # Update remaining time for projects and contracting sections
        if section_name in ["المشاريع", "المقاولات"]:
            for row in data:
                # التحقق من حالة المشروع - التحديث التلقائي فقط للمشاريع قيد الإنجاز
                project_status = row.get("الحالة", "")
                current_remaining_time = row.get("الوقت_المتبقي", "")

                # تأكد من وجود حقل الوقت_المتبقي في البيانات
                if "الوقت_المتبقي" not in row:
                    row["الوقت_المتبقي"] = ""

                # تحديث الوقت المتبقي فقط إذا كانت الحالة "قيد الإنجاز"
                # ولا يحتوي الوقت المتبقي على نصوص خاصة
                if (project_status == "قيد الإنجاز" and
                    "تم الإنجاز" not in str(current_remaining_time) and
                    "متوقف" not in str(current_remaining_time) and
                    "معلق" not in str(current_remaining_time)):

                    delivery_date = row.get("تاريخ_التسليم")
                    if isinstance(delivery_date, date):
                        # Convert datetime.date to QDate
                        delivery_date_qdate = QDate(delivery_date.year, delivery_date.month, delivery_date.day)
                    elif isinstance(delivery_date, str) and delivery_date:
                        # Handle string dates
                        delivery_date_qdate = QDate.fromString(delivery_date, Qt.ISODate)
                    else:
                        # Handle None or invalid dates
                        delivery_date_qdate = QDate()

                    current_date = QDate.currentDate()
                    remaining_days = current_date.daysTo(delivery_date_qdate) if delivery_date_qdate.isValid() else 0

                    if remaining_days > 0:
                        row["الوقت_المتبقي"] = f"متبقي {remaining_days} يوم"
                    elif remaining_days == 0:
                        row["الوقت_المتبقي"] = f"اليوم"
                    else:
                        # إذا كان أقل من 0، نعرض "متأخر" مع عدد الأيام المتأخرة
                        delayed_days = abs(remaining_days)
                        row["الوقت_المتبقي"] = f"متأخر {delayed_days} يوم"

            # Update table to reflect changes in الوقت_المتبقي
            if data:
                table = section_info["table"]
                try:
                    # Find column index for الوقت_المتبقي
                    col_index = -1
                    for i in range(table.columnCount()):
                        if table.horizontalHeaderItem(i).text().strip() == "الوقت المتبقي":
                            col_index = i
                            break

                    if col_index == -1:
                        # If not found by header text, try to find by data keys
                        try:
                            if data and len(data) > 0:
                                col_index = list(data[0].keys()).index("الوقت_المتبقي")
                        except (ValueError, IndexError, KeyError):
                            print("Error: Column الوقت_المتبقي not found in table headers or data keys")

                    # Update the الوقت_المتبقي column in the table
                    for row_index, row_data in enumerate(data):
                        if col_index >= 0 and "الوقت_المتبقي" in row_data:
                            item = QTableWidgetItem(str(row_data.get("الوقت_المتبقي", "")))
                            item.setTextAlignment(Qt.AlignCenter)
                            table.setItem(row_index, col_index, item)
                except Exception as e:
                    print(f"Error updating الوقت_المتبقي column: {e}")

        # Emit signal for data update (optional)
            self.data_updated.emit(section_name)

        # الحصول على الجدول من معلومات القسم
        table = section_info["table"]
        self.colorize_cells(table, section_name)

        # استعادة تفضيل العرض المحفوظ للقسم (فقط للأقسام التي تدعم view_stack)
        if section_name != "التقارير" and section_info.get("view_stack") is not None:
            try:
                preferred_view = self.get_section_view_preference(section_name)
            except AttributeError:
                # استخدام الافتراضي المؤقت
                preferred_view = "table" if section_name == "الحسابات" else "cards"
            current_view = section_info.get("current_view", "table")

            # إذا كان العرض الحالي مختلف عن المفضل، قم بتطبيق المفضل
            if current_view != preferred_view:
                try:
                    is_cards_view = preferred_view == "cards"
                    self.apply_view_to_section(section_name, is_cards_view)
                    current_view = preferred_view

                except Exception as e:
                    print(f"فشل في استعادة تفضيل العرض للقسم {section_name}: {e}")
        else:
            # للأقسام الخاصة مثل التقارير المالية
            current_view = section_info.get("current_view", "financial_reports")

        # تحديث زر التبديل
        self.update_section_toggle_button(section_name)

        # تحديث عرض البطاقات إذا كان نشطاً (لجميع الأقسام)
        if current_view == "cards":
            view_stack = section_info.get("view_stack")
            if view_stack and hasattr(view_stack, 'count'):
                try:
                    if view_stack.count() > 1:
                        cards_view = view_stack.widget(1)
                        if hasattr(cards_view, 'add_cards') and data:
                            cards_view.add_cards(data)
                except RuntimeError:
                    # تجاهل إذا كان الكائن محذوف
                    pass
        # معالجة خاصة للصفحة الرئيسية
    if section_name == "الرئيسية" :
        create_home_page(self)
    
        
# إنشاء الصفحة الرئيسية
# إنشاء الصفحة الرئيسية بتصميم متطور مع إحصائيات وإجراءات سريعة
def create_home_page(self):
    # إعادة تعيين فهرس اللون للأزرار
    global _button_color_index
    _button_color_index = 0
    
    # إنشاء صفحة جديدة مع إمكانية التمرير
    page = QWidget()
    page.setObjectName("الرئيسية_Page")
    main_layout = QVBoxLayout(page)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # إنشاء منطقة قابلة للتمرير
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setFrameShape(QScrollArea.NoFrame)
    scroll_area.setObjectName("HomeScrollArea")

    
    # إنشاء الحاوية الداخلية للمحتوى
    content_widget = QWidget()
    content_widget.setObjectName("HomeContentWidget")
    content_widget.setStyleSheet("""
        QWidget#HomeContentWidget {
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0,
                x2:1, y2:1,
                stop:0 #24384a,
                stop:1 #57225f
            );
        }
    """)
    page_layout = QVBoxLayout(content_widget)
    # page_layout.setContentsMargins(20, 20, 20, 20)
    page_layout.setSpacing(15)
    page_layout.setAlignment(Qt.AlignTop)

    # إضافة خط فاصل
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setObjectName("HomeDividerLine")

    page_layout.addWidget(line)

    # ===== قسم البطاقات الإحصائية =====
    stats_label = QLabel("الإحصائيات الرئيسية")
    stats_label.setObjectName("HomeSectionLabel")
    stats_label.setAlignment(Qt.AlignRight)
    stats_font = QFont("Janna LT", 16, QFont.Bold)
    stats_label.setFont(stats_font)
    #page_layout.addWidget(stats_label)

    # إنشاء صف البطاقات الإحصائية - صف أول (سيتم إضافته بعد الوصف)
    stats_cards_container1 = QWidget()
    stats_cards_layout1 = QHBoxLayout(stats_cards_container1)
    #stats_cards_layout1.setSpacing(15)
    stats_cards_layout1.setContentsMargins(0, 0, 0, 0)

    #إضافة البطاقات الإحصائية - صف أول
    _add_stat_card(self, stats_cards_layout1, "المشاريع قيد الإنجاز", lambda: _get_active_projects_count(self), "#3498db", "المشاريع.svg")
    _add_stat_card(self, stats_cards_layout1, "المهام المتأخرة", lambda: _get_overdue_tasks_count(self), "#e74c3c", "تكليف_مهمة.svg")
    _add_stat_card(self, stats_cards_layout1, "المهام المسندة", lambda: _get_assigned_tasks_count(self), "#f39c12", "مهام.svg")
    _add_stat_card(self, stats_cards_layout1, "المشاريع المكتملة", lambda: _get_completed_projects_count(self), "#27ae60", "نجاح.svg")
    _add_stat_card(self, stats_cards_layout1, "مراحل قيد الإنجاز", lambda: _get_active_phases_count(self), "#8e44ad", "جدول_زمني.svg")
    _add_stat_card(self, stats_cards_layout1, "عدد العملاء", lambda: _get_total_clients_count(self), "#2ecc71", "العملاء1.svg")

    # إضافة شعار التطبيق في الأعلى
    logo_container = QWidget()
    logo_layout = QVBoxLayout(logo_container)
    logo_layout.setAlignment(Qt.AlignCenter)
    logo_layout.setContentsMargins(0, 0, 0, 0)
    logo_layout.setSpacing(10)

   
    
    logo_path = settings.value("company_logo", أيقونة_الشعار)  # القيمة الافتراضية
    app_icon_label = QLabel()
    app_icon_path = os.path.join(icons_dir, 'icon_app.ico')
    if os.path.exists(app_icon_path):
        pixmap = QPixmap(logo_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_icon_label.setPixmap(pixmap)
    app_icon_label.setAlignment(Qt.AlignCenter)
    logo_layout.addWidget(app_icon_label)

    # إضافة عنوان الترحيب
    company_name = settings.value("company_name", "منظومة المهندس")
    welcome_label = QLabel(f"مرحباً بك {company_name}")
    welcome_label.setObjectName("HomeWelcomeLabel")
    welcome_label.setAlignment(Qt.AlignCenter)
    welcome_font = QFont("Janna LT", 60, QFont.Bold)
    welcome_label.setStyleSheet("color: white; font-size: 40px;")
    welcome_label.setFont(welcome_font)
    logo_layout.addWidget(welcome_label)

    # إضافة وصف موجز للنظام
    desc_label = QLabel("منظومة المهندس هي الخيار الافضل لإدارة أعمال المهندسين والمكاتب والشركات الهندسية ")
    desc_label.setObjectName("HomeDescLabel")
    desc_label.setAlignment(Qt.AlignCenter)
    desc_font = QFont("Janna LT", 24)
    desc_label.setStyleSheet("color: white; font-size: 28px;")
    desc_label.setFont(desc_font)
    logo_layout.addWidget(desc_label)

    # إضافة رسالة ترحيبية إضافية
    welcome_msg_label = QLabel("نتمنى لك يوم سعيد - دعنا نبدأ العمل")
    welcome_msg_label.setObjectName("HomeWelcomeMsgLabel")
    welcome_msg_label.setAlignment(Qt.AlignCenter)
    welcome_msg_font = QFont("Janna LT", 18)
    welcome_msg_label.setStyleSheet("color: white; font-size: 28px;")
    # welcome_msg_label.setStyleSheet("""
    #     color: #f39c12;
    #     font-size: 22px;
    #     font-weight: bold;
    #     margin: 15px 0px;
    #     padding: 10px;
    #     background: rgba(255, 255, 255, 0.1);
    #     border-radius: 10px;
    #     border: 2px solid #f39c12;
    # """)
    welcome_msg_label.setFont(welcome_msg_font)
    logo_layout.addWidget(welcome_msg_label)

    page_layout.addWidget(logo_container)

    # إضافة عنوان الإحصائيات بنفس ستايل عناوين الأقسام
    stats_title = QLabel("الإحصائيات")
    stats_title.setObjectName("HomeStatsTitle")
    stats_title.setAlignment(Qt.AlignCenter)
    stats_title_font = QFont("Janna LT", 16, QFont.Bold)
    stats_title.setStyleSheet("""
        QLabel {
            color: white;
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0,
                x2:1, y2:0,
                stop:0 #3f51b5,
                stop:1 #9c27b0
            );
            padding: 12px 12px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            margin: 10px 0px;
        }
    """)
    stats_title.setFont(stats_title_font)
    #page_layout.addWidget(stats_title)

    # إضافة خط فاصل بين العنوان والإحصائيات
    stats_separator = QFrame()
    stats_separator.setFrameShape(QFrame.HLine)
    stats_separator.setFrameShadow(QFrame.Sunken)
    stats_separator.setObjectName("StatsSeparatorLine")
    stats_separator.setStyleSheet("""
        QFrame {
            background-color: rgba(255, 255, 255, 0.0);
            border: none;
            height: 0px;
            margin: 20px 20px;
        }
    """)
    page_layout.addWidget(stats_separator)

    # إضافة البطاقات الإحصائية العلوية بعد الوصف مباشرة
    page_layout.addWidget(stats_cards_container1)

    # إنشاء صف البطاقات الإحصائية - صف ثاني
    stats_cards_container2 = QWidget()
    stats_cards_layout2 = QHBoxLayout(stats_cards_container2)
    stats_cards_layout2.setSpacing(5)
    stats_cards_layout2.setContentsMargins(0, 0, 0, 0)

    #إضافة البطاقات الإحصائية - صف ثاني
    _add_stat_card(self, stats_cards_layout2, "الديون المستحقة", lambda: _get_unpaid_debts(self), "#9b59b6", "سجل_الديون.svg")
    _add_stat_card(self, stats_cards_layout2, "المرتبات المستحقة", lambda: _get_unpaid_salaries(self), "#e67e22", "رصيد.svg")
    _add_stat_card(self, stats_cards_layout2, "إجمالي الدفعات", lambda: _get_total_payments(self), "#16a085", "دفعات.svg")
    _add_stat_card(self, stats_cards_layout2, "إجمالي المصروفات", lambda: _get_total_expenses(self), "#c0392b", "المصروفات.svg")
    _add_stat_card(self, stats_cards_layout2, "إجمالي الباقي", lambda: _get_total_remaining(self), "#34495e", "كشف_حساب.svg")
    _add_stat_card(self, stats_cards_layout2, "مستحقات الموردين", lambda: _get_suppliers_dues(self), "#d35400", "موردين.svg")

    page_layout.addWidget(stats_cards_container2)

    # إضافة خط فاصل
    line2 = QFrame()
    line2.setFrameShape(QFrame.HLine)
    line2.setFrameShadow(QFrame.Sunken)
    line2.setObjectName("HomeDividerLine")

    #page_layout.addWidget(line2)

    # ===== قسم الإجراءات السريعة مدمج مباشرة =====
    # تم حذف تسمية "الإجراءات السريعة"

    # إضافة أقسام الإجراءات السريعة مقسمة إلى ثلاثة صفوف
    
    # الصف الأول - الإضافات الأساسية
    _add_quick_action_row_direct(self, page_layout, "", [
        {"text": "إضافة عميل", "icon": "العملاء1.svg", "action": lambda: self.handle_custom_action("اضافة", "العملاء")},
        {"text": "إضافة مشروع تصميم", "icon": "المشاريع.svg", "action": lambda: self.handle_custom_action("اضافة", "المشاريع")},
        {"text": "إضافة مشروع مقاولات", "icon": "مقاولات.svg", "action": lambda: self.handle_custom_action("اضافة", "المقاولات")},
        {"text": "إضافة موظف", "icon": "الموظفين.svg", "action": lambda: self.handle_custom_action("اضافة", "الموظفين")},
        {"text": "إضافة دورة تدريبية", "icon": "تدريب2.svg", "action": lambda: self.handle_custom_action("اضافة", "التدريب")},
        {"text": "إضافة مصروف", "icon": "المصروفات.svg", "action": lambda: self.handle_custom_action("اضافة", "الحسابات")},
        {"text": "إضافة مورد", "icon": "موردين.svg", "action": lambda: self.handle_custom_action("اضافة", "الموردين")}
    ])
    
    # الصف الثاني - المعاملات المالية
    _add_quick_action_row_direct(self, page_layout, "", [
        {"text": "إضافة دفعة مشروع", "icon": "دفعات.svg", "action": lambda: self.handle_custom_action("إضافة_دفعة", "المشاريع")},
        {"text": "إضافة عهدة مالية", "icon": "عهد_مالية.svg", "action": lambda: self.handle_custom_action("إضافة_عهدة", "المقاولات")},
        {"text": "إضافة دفعة عهدة", "icon": "دفعات.svg", "action": lambda: self.handle_custom_action("إضافة_دفعة_عهدة", "المقاولات")},
        {"text": "إضافة مصروف مشروع", "icon": "المصروفات.svg", "action": lambda: self.handle_custom_action("إضافة_مصروف", "المشاريع")},
        {"text": "إضافة معاملة موظف", "icon": "رصيد_الموظفين.svg", "action": lambda: self.handle_custom_action("إضافة_معاملة", "الموظفين")},
        {"text": "دفعات الطلبة", "icon": "دفعات.svg", "action": lambda: self.handle_custom_action("دفعات_الطلبة", "التدريب")},
        {"text": "إضافة مورد", "icon": "موردين.svg", "action": lambda: self.handle_custom_action("اضافة", "الموردين")}
    ])
    
    # الصف الثالث - الإدارة والمتابعة
    _add_quick_action_row_direct(self, page_layout, "", [
        {"text": "حضور وانصراف", "icon": "حضور_انصراف.svg", "action": lambda: self.handle_custom_action("تسجيل_حضور", "الموظفين")},
        {"text": "مهام الموظفين", "icon": "تكليف_مهمة.svg", "action": lambda: self.handle_custom_action("إدارة_المهام", "الموظفين")},
        {"text": "إدارة الديون", "icon": "سجل_الديون.svg", "action": lambda: self.handle_custom_action("إدارة_الديون", "العملاء")},
        {"text": "إدارة الموردين", "icon": "موردين.svg", "action": lambda: self.handle_custom_action("إدارة_الموردين", "الحسابات")},
        {"text": "مراحل مشروع", "icon": "جدول_زمني1.svg", "action": lambda: self.handle_custom_action("إدارة_المراحل", "المشاريع")},
        {"text": "تقرير مالي", "icon": "كشف.svg", "action": lambda: self.handle_custom_action("تقرير_مالي", "التقارير")}
    ])

    
    
    # إضافة التذييل
    if hasattr(self, 'company_name') and self.company_name:
        footer_label = QLabel(f"© {QDate.currentDate().year()} {self.company_name} - جميع الحقوق محفوظة")
    else:
        footer_label = QLabel(f"© {QDate.currentDate().year()} منظومة المهندس - جميع الحقوق محفوظة")
    footer_label.setAlignment(Qt.AlignCenter)
    footer_label.setObjectName("HomeFooterLabel")

    page_layout.addWidget(footer_label)
    
    # إضافة المحتوى إلى منطقة التمرير
    scroll_area.setWidget(content_widget)
    main_layout.addWidget(scroll_area)
    
    # إضافة الصفحة إلى واجهة البرنامج
    if "الرئيسية" not in self.sections:
        section_info = {"page": page, "table": None, "empty_state_widget": None}
        self.sections["الرئيسية"] = section_info
    else:
        old_page = self.sections["الرئيسية"]["page"]
        if old_page:
            self.main_content_area.removeWidget(old_page)
            old_page.deleteLater()
        self.sections["الرئيسية"]["page"] = page

    self.main_content_area.addWidget(page)
    self.main_content_area.setCurrentWidget(page)
    
    return page

# دالة مساعدة لإضافة بطاقة إحصائية
# إضافة بطاقة إحصائية مع أيقونة اختيارية
def _add_stat_card(self, layout, title, value_function, color, icon_name=None):
    # تحويل hex color إلى rgba مع شفافية 50%
    # عرافة إلى RGBA
    def hex_to_rgba(hex_color, opacity=0.5):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {opacity})"
    
    card = QFrame()
    card.setObjectName("HomeStatCard")
    card.setFrameShape(QFrame.StyledPanel)
    card.setFrameShadow(QFrame.Raised)
    
    # استخدام لون شفاف
    transparent_color = hex_to_rgba(color, 0.2)
    
    card.setStyleSheet(f"""
        #HomeStatCard {{
            background-color: {transparent_color};
            color: white;
            border-radius: 10px;
            min-height: 180px;
            max-height: 250px;
            border: 2px solid {color};
        }}
    """)
    
    card_layout = QVBoxLayout(card)
    card_layout.setAlignment(Qt.AlignCenter)
    card_layout.setSpacing(8)
    card_layout.setContentsMargins(10, 15, 10, 15)
    
    # إضافة الأيقونة إذا تم تمريرها
    if icon_name:
        icon_label = QLabel()
        icon_path = os.path.join(icons_dir, icon_name)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("📊")  # أيقونة افتراضية
            icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label)
    
    title_label = QLabel(title)
    title_label.setObjectName("HomeStatCardTitle")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
    title_label.setWordWrap(True)
    card_layout.addWidget(title_label)
    
    # استدعاء الدالة لجلب القيمة
    try:
        value = value_function()
    except Exception as e:
        print(f"خطأ في جلب قيمة الإحصائية '{title}': {e}")
        value = "غير متاح"
    
    value_label = QLabel(str(value))
    value_label.setObjectName("HomeStatCardValue")
    value_label.setAlignment(Qt.AlignCenter)
    value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
    card_layout.addWidget(value_label)
    
    layout.addWidget(card)
    return card

# دالة مساعدة لإضافة قسم إجراءات سريعة
# إضافة قسم للإجراءات السريعة
def _add_quick_action_section(self, parent_layout, section_name, actions):
    section_container = QWidget()
    section_layout = QVBoxLayout(section_container)
    section_layout.setContentsMargins(0, 0, 0, 0)
    section_layout.setSpacing(0)
    
    # عنوان القسم
    section_header = QLabel(f"{section_name}")
    section_header.setObjectName(f"QuickActionHeader_{section_name}")
    section_header.setAlignment(Qt.AlignRight)
    header_font = QFont("Janna LT", 14, QFont.Bold)
    section_header.setFont(header_font)
    section_layout.addWidget(section_header)
    
    # أزرار الإجراءات السريعة
    buttons_container = QWidget()
    buttons_layout = QHBoxLayout(buttons_container)
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons_layout.setSpacing(10)
    
    for action in actions:
        button = _create_quick_action_button(self,
            action["text"], 
            action["icon"], 
            action["action"]
        )
        buttons_layout.addWidget(button)
    
    section_layout.addWidget(buttons_container)
    
    # إضافة خط فاصل
    if section_name != list(actions)[-1]:
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("QuickActionSeparator")
        separator.setStyleSheet("background-color: #ddd; height: 1px;")
        section_layout.addWidget(separator)
    
    parent_layout.addWidget(section_container)
    return section_container

# دالة مساعدة لإضافة قسم إجراءات سريعة مباشرة في التخطيط الرئيسي
# إضافة قسم للإجراءات السريعة مباشرة في التخطيط الرئيسي
def _add_quick_action_section_direct(self, parent_layout, section_name, actions):
    # عنوان القسم
    section_header = QLabel(f"{section_name}")
    section_header.setObjectName(f"QuickActionHeader_{section_name}")
    section_header.setAlignment(Qt.AlignRight)
    header_font = QFont("Janna LT", 14, QFont.Bold)
    section_header.setFont(header_font)
    section_header.setStyleSheet("""
        QLabel {
            color: #2c3e50;
            padding: 5px 5px;
            /*margin-top: 0px;-*
            font-weight: bold;
        }
    """)
    parent_layout.addWidget(section_header)
    
    # أزرار الإجراءات السريعة
    buttons_container = QWidget()
    buttons_layout = QHBoxLayout(buttons_container)
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    #buttons_layout.setSpacing(10)
    buttons_layout.setAlignment(Qt.AlignCenter)
    
    for action in actions:
        button = _create_quick_action_button(self,
            action["text"], 
            action["icon"], 
            action["action"]
        )
        buttons_layout.addWidget(button)
    
    parent_layout.addWidget(buttons_container)
    
    # إضافة خط فاصل
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setObjectName("QuickActionSeparator")
    separator.setStyleSheet("background-color: #ddd; height: 1px; margin: 0px 0px;")
    parent_layout.addWidget(separator)
    
    return buttons_container

# دالة مساعدة لإضافة صف من أزرار الإجراءات السريعة
# إضافة صف من الأزرار للإجراءات السريعة
def _add_quick_action_row_direct(self, parent_layout, row_name, actions):
    # عنوان الصف (فقط إذا لم يكن فارغاً)
    if row_name and row_name.strip():
        row_header = QLabel(f"{row_name}")
        row_header.setObjectName(f"QuickActionRowHeader_{row_name}")
        row_header.setAlignment(Qt.AlignCenter)
        header_font = QFont("Janna LT", 16, QFont.Bold)
        row_header.setFont(header_font)
        row_header.setStyleSheet("""
            QLabel {
                color: white;
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #3f51b5,
                    stop:1 #9c27b0
                );
                padding: 12px 12px;
                /*margin: 5px 0px 5px 0px;*/
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        parent_layout.addWidget(row_header)
    
    # أزرار الإجراءات السريعة في صف واحد
    buttons_container = QWidget()
    buttons_layout = QHBoxLayout(buttons_container)
    #buttons_layout.setContentsMargins(20, 10, 20, 10)
    #buttons_layout.setSpacing(10)
    buttons_layout.setAlignment(Qt.AlignCenter)
    
    for action in actions:
        button = _create_quick_action_button(self,
            action["text"], 
            action["icon"], 
            action["action"]
        )
        # تمديد الزر ليأخذ مساحة متساوية
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttons_layout.addWidget(button)
    
    # تمديد حاوية الأزرار لتأخذ العرض الكامل
    buttons_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    parent_layout.addWidget(buttons_container)
    
    # إضافة مساحة بين الصفوف
    spacer = QWidget()
    spacer.setFixedHeight(0)
    parent_layout.addWidget(spacer)
    
    return buttons_container

# متغير عالمي لتتبع فهرس اللون الحالي
_button_color_index = 0

# دالة مساعدة لإنشاء زر إجراء سريع
# إنشاء زر إجراء سريع مع أيقونة ونص
def _create_quick_action_button(self, text, icon_name, action_func):
    global _button_color_index
    
    button = QPushButton()
    button.setObjectName("QuickActionButton")
    button.setCursor(QCursor(Qt.PointingHandCursor))
    
    layout = QVBoxLayout(button)
    layout.setAlignment(Qt.AlignCenter)
    # layout.setContentsMargins(10, 10, 10, 10)
    # layout.setSpacing(5)
    
    # أيقونة الزر
    icon_label = QLabel()
    icon_path = os.path.join(icons_dir, icon_name)
    if os.path.exists(icon_path):
        pixmap = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
    else:
        icon_label.setText("?")
        icon_label.setStyleSheet("font-size: 24px; font-weight: bold;")
    icon_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(icon_label)
    
    # نص الزر
    text_label = QLabel(text)
    text_label.setAlignment(Qt.AlignCenter)
    text_label.setWordWrap(True)
    text_label.setStyleSheet("""
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 13px;
            padding: 5px;
        }
    """)
    layout.addWidget(text_label)
    
    button.setMinimumSize(150, 140)
    button.setMinimumHeight(180)
    button.setMaximumHeight(250)
    
    # قائمة الألوان للأزرار
    button_colors = [
        "#e91e63",  # وردي
        "#3f51b5",  # أزرق
        "#4caf50",  # أخضر
        "#ff9800",  # برتقالي
        "#9c27b0",  # بنفسجي
        "#f44336",  # أحمر
        "#00bcd4",  # سماوي
        "#795548",  # بني
        "#607d8b",  # رمادي مزرق
        "#8bc34a",  # أخضر فاتح
        "#ffc107",  # أصفر
        "#673ab7",  # بنفسجي غامق
        "#ff5722",  # أحمر برتقالي
        "#009688",  # أخضر مزرق
        "#ff6f00",  # برتقالي غامق
        "#ad1457",  # وردي غامق
        "#1976d2",  # أزرق غامق
        "#388e3c",  # أخضر غامق
        "#7b1fa2",  # بنفسجي فاتح
        "#d32f2f",  # أحمر غامق
    ]
    
    # الحصول على لون من القائمة بالتتابع
    color = button_colors[_button_color_index % len(button_colors)]
    _button_color_index += 1
    
    button.setStyleSheet(f"""
        QPushButton#QuickActionButton {{
            background-color: rgba(255, 255, 255, 0.1);
            border: none;
            border-bottom: 4px solid {color};
            border-radius: 12px;
            color: white;
            font-weight: bold;
            padding: 15px 15px;
            font-size: 14px;
        }}
        QPushButton#QuickActionButton:hover {{
            background-color: rgba(255, 255, 255, 0.2);
            border-bottom: 5px solid {color};
            color: white;
            
           
        }}
        QPushButton#QuickActionButton QLabel {{
            color: white;
            font-weight: bold;
            font-size: 13px;
        }}
    """)
    
    button.clicked.connect(action_func)
    return button

# دوال مساعدة لجلب البيانات الإحصائية
# جلب عدد المشاريع قيد الإنجاز
def _get_active_projects_count(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        year = QDate.currentDate().year()
        
        # استعلام المشاريع النشطة (غير المكتملة)
        cursor.execute(f"""
            SELECT COUNT(*) FROM `المشاريع`
            WHERE الحالة NOT IN ('منتهي', 'ملغي')
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"خطأ في جلب عدد المشاريع النشطة: {e}")
        return "0"

# جلب عدد المهام المتأخرة
def _get_overdue_tasks_count(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        year = QDate.currentDate().year()
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        
        # استعلام المهام المتأخرة (تاريخ الانتهاء أقل من التاريخ الحالي والحالة ليست منتهية)
        cursor.execute(f"""
            SELECT COUNT(*) FROM `المشاريع_مهام_الفريق`
            WHERE تاريخ_الانتهاء < '{current_date}' AND الحالة NOT IN ('منتهي', 'ملغي')
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"خطأ في جلب عدد المهام المتأخرة: {e}")
        return "0"

# جلب عدد المهام المسندة
def _get_assigned_tasks_count(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        year = QDate.currentDate().year()
        
        # استعلام المهام المسندة والنشطة
        cursor.execute(f"""
            SELECT COUNT(*) FROM `المشاريع_مهام_الفريق`
            WHERE الحالة NOT IN ('منتهي', 'ملغي')
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"خطأ في جلب عدد المهام المسندة: {e}")
        return "0"

# جلب عدد المشاريع المكتملة
def _get_completed_projects_count(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        year = QDate.currentDate().year()
        
        # استعلام المشاريع المكتملة
        cursor.execute(f"""
            SELECT COUNT(*) FROM `المشاريع`
            WHERE الحالة = 'منتهي'
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"خطأ في جلب عدد المشاريع المكتملة: {e}")
        return "0"

# جلب إجمالي الديون المستحقة
def _get_unpaid_debts(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # استعلام الديون المستحقة (غير المدفوعة)
        cursor.execute("""
            SELECT COALESCE(SUM(المبلغ), 0) FROM الحسابات_سجل_الديون
            WHERE حالة_الدين = 'غير مسدد'
        """)
        amount = cursor.fetchone()[0]
        conn.close()
        
        # تنسيق المبلغ
        if amount:
            return f"{amount:,.0f}"
        return "0"
    except Exception as e:
        print(f"خطأ في جلب إجمالي الديون المستحقة: {e}")
        return "0"

# جلب إجمالي المرتبات المستحقة
def _get_unpaid_salaries(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # استعلام مجموع رواتب الموظفين المستحقة
        cursor.execute("""
            SELECT COALESCE(SUM(الرصيد), 0) FROM الموظفين
            WHERE الرصيد > 0
        """)
        amount = cursor.fetchone()[0]
        conn.close()
        
        # تنسيق المبلغ
        if amount:
            return f"{amount:,.0f}"
        return "0"
    except Exception as e:
        print(f"خطأ في جلب إجمالي المرتبات المستحقة: {e}")
        return "0"

# جلب إجمالي الدفعات
def _get_total_payments(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        year = QDate.currentDate().year()
        
        # استعلام إجمالي دفعات المشاريع لهذا العام
        cursor.execute(f"""
            SELECT COALESCE(SUM(المبلغ_المدفوع), 0) FROM `المشاريع_المدفوعات`
        """)
        amount = cursor.fetchone()[0]
        conn.close()
        
        # تنسيق المبلغ
        if amount:
            return f"{amount:,.0f}"
        return "0"
    except Exception as e:
        print(f"خطأ في جلب إجمالي الدفعات: {e}")
        return "0"

# جلب إجمالي المصروفات
def _get_total_expenses(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        year = QDate.currentDate().year()
        
        # استعلام إجمالي المصروفات لهذا العام
        cursor.execute(f"""
            SELECT COALESCE(SUM(المبلغ), 0) FROM `الحسابات`
        """)
        amount = cursor.fetchone()[0]
        conn.close()
        
        # تنسيق المبلغ
        if amount:
            return f"{amount:,.0f}"
        return "0"
    except Exception as e:
        print(f"خطأ في جلب إجمالي المصروفات: {e}")
        return "0"

# جلب عدد مراحل قيد الإنجاز
def _get_active_phases_count(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # استعلام المراحل النشطة - نحسب المراحل للمشاريع قيد الإنجاز
        cursor.execute("""
            SELECT COUNT(DISTINCT مر.id) 
            FROM `المشاريع_المراحل` مر
            JOIN `المشاريع` م ON مر.معرف_المشروع = م.id
            WHERE م.الحالة = 'قيد الإنجاز'
            AND مر.حالة_المبلغ = 'تم الإدراج'
        """)
        result = cursor.fetchone()
        count = result[0] if result else 0
        conn.close()
        return count
    except Exception as e:
        print(f"خطأ في جلب عدد مراحل قيد الإنجاز: {e}")
        return "0"

# جلب عدد العملاء الإجمالي
def _get_total_clients_count(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # استعلام إجمالي عدد العملاء
        cursor.execute("""
            SELECT COUNT(*) FROM `العملاء`
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"خطأ في جلب عدد العملاء: {e}")
        return "0"

# جلب إجمالي الباقي من المشاريع
def _get_total_remaining(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # استعلام إجمالي المبالغ المتبقية من المشاريع
        cursor.execute("""
            SELECT COALESCE(SUM(الباقي), 0) FROM `المشاريع`
            WHERE الحالة NOT IN ('منتهي', 'ملغي')
        """)
        result = cursor.fetchone()
        amount = result[0] if result else 0
        conn.close()
        
        # تنسيق المبلغ
        if amount:
            return f"{amount:,.0f}"
        return "0"
    except Exception as e:
        print(f"خطأ في جلب إجمالي الباقي: {e}")
        return "0"

# جلب مستحقات الموردين
def _get_suppliers_dues(self):
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # استعلام مستحقات الموردين (الديون غير المسددة)
        cursor.execute("""
            SELECT COALESCE(SUM(المبلغ), 0) FROM `الحسابات_سجل_الديون`
            WHERE حالة_الدين = 'غير مسدد'
        """)
        result = cursor.fetchone()
        amount = result[0] if result else 0
        conn.close()
        
        # تنسيق المبلغ
        if amount:
            return f"{amount:,.0f}"
        return "0"
    except Exception as e:
        print(f"خطأ في جلب مستحقات الموردين: {e}")
        return "0"




