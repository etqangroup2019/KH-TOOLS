from الدوال_الأساسية import*
from أزرار_الواجهة import*
from DB import*
from الأدوات import*
from النسخة_التجريبية import*
from الطباعة_والتصدير import open_print_export_dialog, ExpenseVoucherDialog
from الإعدادات_العامة import*
from تخصيص_الواجهة import*
from ستايل import*
from الطباعة import*
from التحديثات import*

from المستخدمين import*

from متغيرات import*


# type: ignore

from نظام_البطاقات import ModernCardsContainer
from قائمة_الجداول import setup_table_context_menu
from نافذة_تخصيص_عرض_الأقسام import SectionViewSettingsDialog
from ادارة_الموردين import SuppliersManagementWindow
from إدارة_الموردين import open_supplier_management_window
from المشاريع.إدارة_المشروع import*

# إعداد locale مخصص للحصول على أرقام إنجليزية مع تنسيق تاريخ dd/mm/yyyy
custom_locale = QLocale(QLocale.English, QLocale.UnitedKingdom)  # استخدام UK للحصول على dd/mm/yyyy
QLocale.setDefault(custom_locale)

# إعداد تسجيل الأخطاء لكتم تحذيرات Qt SVG
def setup_qt_logging():
    """
    إعداد تسجيل Qt لكتم تحذيرات SVG المتداخلة
    """
    import logging
    import os
    
    # كتم تحذيرات Qt SVG المحددة
    os.environ['QT_LOGGING_RULES'] = 'qt.svg.debug=false'
    
    # تثبيت معالج رسائل Qt المخصص
    def qt_message_handler(mode, context, message):
        # تجاهل تحذيرات SVG المتداخلة
        if "nested svg element" in message.lower():
            return
        if "svg document must not contain nested svg elements" in message.lower():
            return
        if "skipping a nested svg element" in message.lower():
            return
        
        # السماح بباقي الرسائم الهامة فقط
        if mode == QtMsgType.QtCriticalMsg:
            print(f"Qt Critical: {message}")
        elif mode == QtMsgType.QtFatalMsg:
            print(f"Qt Fatal: {message}")
    
    # تثبيت معالج الرسائم
    qInstallMessageHandler(qt_message_handler)

# تطبيق إعدادات Qt
setup_qt_logging()

# Mainwindow
# Mainwindow
class MainWindow(QMainWindow):
    data_updated = Signal(str)
    # init
    # init
    def __init__(self):
        super().__init__()

        self.create_database_if_not_exists()

        check_and_copy_password()
        # تثبيت الخط
        install_all_fonts(self,fonts_dir)
        # انشاء ملف التخصيص
        create_customization_json()
        #تثبيت قاعدة البيانات
        instll_db()
        self.is_dark_mode = settings.value("dark_mode", False, type=bool)
        #/////////////////////////////////////////////////////////////////////////////////////////
        if password!= pm_password:
            self.askPassword()

        #//////////////////////////////////////////////////////////////////////
        # التحقق من وجود المفتاح وتنفيذ العملية
        key = get_or_create_key("FOLDERKEY","FOLDERKEY")
        if key:
            fak_tashfer()
        #/////////////////////////////////////////////////////////////////////////////////////////
        # قم بتعريف الخصائص هنا
        self.license_type = None
        self.start_date = None
        self.end_date = None
        self.remaining_days = None
        #self.load_license_data()
        tashfer()

        #------------------------الواجهة----------------------------------------------------
        self.company_name = settings.value("company_name", "منظومة المهندس")
        self.setWindowTitle(f"{self.company_name}")

        screen = QGuiApplication.primaryScreen().geometry()
        width = screen.width()
        height = screen.height()
        self.setGeometry(0, 0, width, height)
        self.setWindowFlags(Qt.Window)
        self.showMaximized()

        app_icon_path = os.path.join(icons_dir, 'icon_app.ico')
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        self.setLayoutDirection(Qt.RightToLeft)

        # تحميل إعدادات العرض قبل إنشاء القوائم
        self.is_cards_view = settings.value("view_mode_cards", True, type=bool)

        # إعدادات العرض الافتراضية لكل قسم
        self.section_default_views = {
            "الحسابات": "table",  # الحسابات افتراضياً عرض جدول
            "المشاريع": "cards",
            "المقاولات": "cards",
            "العملاء": "cards",
            "الموظفين": "cards",
            "التدريب": "cards",
            "الموردين": "cards",
            "التقارير": "cards"
        }

        from أزرار_الواجهة import menu_bar
        menu_bar(self)

        central_widget = QWidget()
        central_widget.setObjectName("MainCentralWidget")
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        #اللوحة اليمنى (Side Menu) -------------------------------
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(130) # عرض ثابت
        self.right_panel.setObjectName("RightPanel") # اسم لتطبيق الستايل

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(5, 10, 5, 10)
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # إضافة الشعار إلى لوحة التحكم اليمنى
        self.logo_label = QLabel()
        logo_size = 90 # Slightly smaller logo to save space
        logo_path = os.path.join(icons_dir, 'لوقو.svg')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText(self.company_name.split()[0]) # Use first word if logo not found
            # Use fallback font
            font_logo = QFont("Janna LT", 12, QFont.Bold)
            self.logo_label.setFont(font_logo)

        self.logo_label.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(1, 1, 0, 0)  # (left, top, right, bottom)
        self.logo_label.setContentsMargins(0, 0, 0, 2)  # (left, top, right, bottom)

        # إنشاء حاوية للأزرار
        buttons_container = QWidget()
        buttons_container.setObjectName("حاوية_الازرار_الجانبية") # اسم لتطبيق الستايل
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        buttons_layout.setSpacing(1)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # # إضافة الأزرار إلى التخطيط
        #buttons_layout.addWidget(self.logo_label)

        # إضافة الأزرار الجانبية
        RIGHT_BUTTONS = [
           ( أيقونة_الشعار, "الرئيسية", lambda: self.show_section("الرئيسية"), "bottom_border_blue"), #"home.png"
            (أيقونة_المشاريع, "المشاريع", lambda: self.show_section("المشاريع"), "bottom_border_blue"),
            (أيقونة_مقاولات, "المقاولات", lambda: self.show_section("المقاولات"), "bottom_border_blue"),
            (أيقونة_العملاء, "العملاء", lambda: self.show_section("العملاء"), "bottom_border_green"),
            (أيقونة_المصروفات, "الحسابات", lambda: self.show_section("الحسابات"), "bottom_border_red"),
            (أيقونة_الموظفين, "الموظفين", lambda: self.show_section("الموظفين"), "bottom_border_yellow"),
            (أيقونة_التدريب, "التدريب", lambda: self.show_section("التدريب"), "bottom_border_green"),
            (أيقونة_موردين, "الموردين", lambda: self.show_section("الموردين"), "bottom_border_red"),
            (أيقونة_التقارير, "تقارير مالية", lambda: self.show_section("التقارير"), "bottom_border_lime")
        ]

        for item in RIGHT_BUTTONS:
            if len(item) >= 4:  # إذا كان العنصر يحتوي على 4 عناصر أو أكثر (الأيقونة، النص، الإجراء، نوع البوردر)
                icon_name, text, action, border_type = item
                icon_path = os.path.join(icons_dir, icon_name)
                button = SideMenuButton(icon_path, text)
                button.clicked.connect(action)
                button.setProperty("section", text)
                button.setProperty("border_type", border_type)
            else:  # إذا كان العنصر يحتوي على 3 عناصر فقط (الأيقونة، النص، الإجراء)
                icon_name, text, action = item
                icon_path = os.path.join(icons_dir, icon_name)
                button = SideMenuButton(icon_path, text)
                button.clicked.connect(action)
                button.setProperty("section", text)

            buttons_layout.addWidget(button)

        # إنشاء QScrollArea وإضافة الحاوية إليها
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(buttons_container)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.verticalScrollBar().setObjectName("customScrollBar")
        scroll_area.setLayoutDirection(Qt.LeftToRight)
        scroll_area.setStyleSheet("background-color: transparent;")
        right_layout.addWidget(scroll_area)

        self.main_layout.addWidget(self.right_panel)

        self.main_content_area = QStackedWidget()
        self.main_content_area.setObjectName("MainContentArea")
        self.main_layout.addWidget(self.main_content_area, 1)
        self.interactive_sections = list(TABLE_COLUMNS.keys())

        

        self._create_sections()

        # # تطبيق إعداد العرض المحفوظ على جميع الأقسام
        self.apply_initial_view_settings()

        # التحقق من ثبات إعدادات العرض بعد التطبيق
        #QTimer.singleShot(1000, self.verify_view_settings_persistence)
        #self.verify_view_settings_persistence()

        # إنشاء label للمستخدم (مطلوب للطباعة)
        self.profits_label2 = QLabel("المستخدم\nAdmin")
        self.profits_label2.setVisible(False)  # مخفي لأنه يستخدم فقط للطباعة

        ueser_database(self)
        apply_stylesheet(self)
        self.show_section("الرئيسية")
        
        center_all_widgets(self)

        # معالجة المرتبات التلقائية عند بدء التشغيل
        self.process_automatic_salaries()

        
    #الدوال ---------------------------------------------------------------------------------------------


    # معالجة المرتبات التلقائية عند بدء التشغيل
    # معالجة الرواتب التلقائية
    def process_automatic_salaries(self):
        try:
            from جدولة_المرتبات import process_scheduled_salaries
            # تشغيل المعالجة في خيط منفصل لتجنب تجميد الواجهة
            QTimer.singleShot(2000, lambda: process_scheduled_salaries(self))
        except Exception as e:
            print(f"خطأ في معالجة المرتبات التلقائية: {str(e)}")
            
    # تحويل رقم اليوم في الأسبوع إلى اسمه بالعربية
    # احصل على اسم اليوم العربي
    # احصل على اسم اليوم العربي
    def get_arabic_day_name(self, day_number):
        arabic_days = {
            1: "الإثنين",
            2: "الثلاثاء",
            3: "الأربعاء",
            4: "الخميس",
            5: "الجمعة",
            6: "السبت",
            7: "الأحد"
        }
        return arabic_days.get(day_number, "")

    # إنشاء صفحات لكل قسم في النظام
    # إنشاء أقسام
    # إنشاء أقسام
    def _create_sections(self):
        create_sections(self)

    # عرض القسم المحدد
    # عرض قسم
    # عرض قسم
    def show_section(self, section_name):
        show_section(self, section_name)
                
    # إعداد قائمة ملف
    # الإعداد قائمة ملف
    # الإعداد قائمة ملف
    def _setup_file_menu(self):
        company_info_icon = os.path.join(icons_dir, 'enterprise.png')
        Backup_DB_icon = os.path.join(icons_dir, 'database.png')
        import_db_icon = os.path.join(icons_dir, 'file-backup.png')
        data_transfer_icon = os.path.join(icons_dir, 'data-transfer.png')
        #google_drive_icon = os.path.join(icons_dir, 'google-drive.png')

        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.file_menu, "     تعديل إعدادات الشركة  ", self.open_company_info_dialog, company_info_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.file_menu, "        إنشاء نسخة إحتياطية  ", self.Backup_DB, Backup_DB_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.file_menu, "    إسترداد نسخة احتياطية  ", self.import_db, import_db_icon)
        #self.draggable_toolbar.addMenuButton(self.draggable_toolbar.file_menu, "            نقل ونسخ البيانات  ", self.Copy_selected_rows, data_transfer_icon)

    # إعداد قائمة الحماية
    # إعداد قائمة الأمان
    # إعداد قائمة الأمان
    def setup_security_menu(self):
        if password != pm_password:
            open_login_icon = os.path.join(icons_dir, 'personalization.png')
            openAddUser_icon = os.path.join(icons_dir, 'profile.png')
            changePassword_icon = os.path.join(icons_dir, 'reset_password.png')
            disableSecurity_icon = os.path.join(icons_dir, 'unlock.png')

            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.security_menu, "   تبديل المستخدم F9  ", self.open_login, open_login_icon)
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.security_menu, "       إدارة المستخدمين  ", self.openAddUserDialog, openAddUser_icon)
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.security_menu, "         تغيير كلمة المرور  ", self.changePassword, changePassword_icon)
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.security_menu, "         حذف كلمة المرور  ", self.disableSecurity, disableSecurity_icon)
        else:
            createPassword_icon = os.path.join(icons_dir, 'lock_password.png')
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.security_menu, "      إنشاء كلمة مرور ", self.createPassword, createPassword_icon)

    # إعداد قائمة التخصيص
    # الإعداد تخصيص القائمة
    # الإعداد تخصيص القائمة
    def _setup_customize_menu(self):
        changeInterfaceColor_icon = os.path.join(icons_dir, 'art.png')
        changeTableFont_icon = os.path.join(icons_dir, 'font-selection.png')
        resetToDefault_icon = os.path.join(icons_dir, 'restore.png')
        light_icon = os.path.join(icons_dir, 'light.png')
        svg_icon = os.path.join(icons_dir, 'svg.png')  # أيقونة لتغيير لون الأيقونات

        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "                تغيير لون الخلفية ", self.changeInterfaceColor, changeInterfaceColor_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "                 تغيير لون الأزرار ", self.changeButtonsColor, changeInterfaceColor_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "               تغيير لون الجدول ", self.changeTableColor, changeInterfaceColor_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "               تغيير لون الخطوط ", self.changefontColor, changeInterfaceColor_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "     تغيير لون حقول الإدخال ", self.changeinputColor, changeInterfaceColor_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "          تغيير لون الأيقونات ", self.openSvgColorChanger, svg_icon)
        self.draggable_toolbar.customize_menu.addSeparator()

        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "          تغيير خطوط الجدول ", self.changeTableFont, changeTableFont_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "                  تغيير خط الأزرار ", self.changeButtonsFont, changeTableFont_icon)
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "                 تغيير الخط العام ", self.changeGenralFont, changeTableFont_icon)
        self.draggable_toolbar.customize_menu.addSeparator()

        self.is_dark_mode = settings.value("dark_mode", False, type=bool)
        if self.is_dark_mode:
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "           تفعيل الوضع الفاتح ", self.toggle_theme, light_icon)
        else:
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "           تفعيل الوضع الداكن ", self.toggle_theme, light_icon)

        # إضافة خيار تبديل العرض المركزي
        self.draggable_toolbar.customize_menu.addSeparator()
        view_icon = os.path.join(icons_dir, 'art.png')  # استخدام أيقونة مناسبة

        # استخدام إعداد العرض المحمل مسبقاً
        if self.is_cards_view:
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "           التبديل إلى عرض الجدول ", self.toggle_global_view, view_icon)
        else:
            self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "         التبديل إلى عرض البطاقات ", self.toggle_global_view, view_icon)

        # إضافة زر تخصيص عرض الأقسام
        self.draggable_toolbar.customize_menu.addSeparator()
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "           تخصيص عرض الأقسام ", self.open_section_view_settings, view_icon)

        # إضافة خيار الإعدادات الموحدة
        unified_settings_icon = os.path.join(icons_dir, 'art.png')  # استخدام أيقونة موجودة
        self.draggable_toolbar.customize_menu.addSeparator()
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "                    الإعدادات الموحدة ", self.open_unified_settings, unified_settings_icon)

        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.customize_menu, "إستعادة التنسيق الإفتراضي", self.resetToDefault, resetToDefault_icon)

    # إعداد قائمة المساعدة
    # قائمة مساعدة الإعداد
    # قائمة مساعدة الإعداد
    def _setup_help_menu(self):
        report_problem_icon = os.path.join(icons_dir, 'problem.png')
        Tutoril_icon = os.path.join(icons_dir, 'youtube.png')
        update_icon = os.path.join(icons_dir, 'update_icon.png')
        license_icon = os.path.join(icons_dir, 'license.png')

        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.help_menu, "         الإبلاغ عن مشكلة  ", self.report_problem, report_problem_icon)
        self.draggable_toolbar.help_menu.addSeparator()
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.help_menu, "             دروس تعليمية  ", self.open_tutorial_link, Tutoril_icon)
        self.draggable_toolbar.help_menu.addSeparator()
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.help_menu, "         البحث عن تحديثات  ", self.check_for_updates_pottom, update_icon)
        self.draggable_toolbar.help_menu.addSeparator()
        self.draggable_toolbar.addMenuButton(self.draggable_toolbar.help_menu, "      تغيير مفتاح الترخيص  ", self.changing_activation_dialog, license_icon)
        self.draggable_toolbar.help_menu.addSeparator()

    # إعداد قائمة المعلومات
    # قائمة معلومات الإعداد
    # قائمة معلومات الإعداد
    def _setup_info_menu(self):
        license_v = self.license_type
        remaining_days = self.remaining_days
        end_date = self.end_date

        if license_v == "trial":
            license_v = "ترخيص تجريبي"
        if license_v == "annual":
            license_v = "إشتراك سنوي"
        if license_v == "permanent":
            license_v = "ترخيص دائم"

        if end_date == "permanent":
            end_date = "مدى الحياة"

        # قائمة الميزات الأساسية
        features = [
            "----------------------------",
            "--- مميزات قيد التطوير ---",
            "          إدارة التصميم",
            "         مهام الموظفين",
            "        الإشراف والتنفيذ",
            "      مصروفات المشروع",
            "       الدورات التدريبية",
            "     Excel إستيراد ملفات",

            "----------------------------",
            f" ( V{CURRENT_VERSION}) منظومة المهندس",
            f"        ( {license_v} )",
        ]

        # إضافة عدد الأيام المتبقية وتاريخ الانتهاء إذا لم يكن الترخيص دائمًا
        if license_v != "ترخيص دائم":
            features.append(f"     الوقت المتبقي: ( {remaining_days} ) ")
            features.append(f"    الإنتهاء: ( {end_date} ) ")

        # إضافة المطور
        features.append("   المطور: خالد النويصري")

        # إضافة الميزات إلى القائمة
        for feature in features:
            feature_action = QAction(f"{feature}", self)
            # يمكنك اختيار تعطيل العناصر النصية إذا كنت تريدها غير تفاعلية
            # feature_action.setEnabled(False)
            self.draggable_toolbar.info_menu.addAction(feature_action)

    # إعداد قائمة الاختصارات
    # قائمة اختصارات الإعداد
    # قائمة اختصارات الإعداد
    def _setup_shortcuts_menu(self):
        shortcuts = [
            " ----إختصارات لوحة المفاتيح----",
            "      (ALT+V) الأوامر الصوتية",
            "      ( ALT+C ) الألة الحاسبة",
            "         (Q)  نافذة المشاريع",
            "       (W)  نافذة الحسابات",
            "         (E)  نافذة الموظفين",
            "       (R) نافذة دورات تدريبية",
            "         (F9) تبديل المستخدم",
        ]

        # إضافة الميزات إلى القائمة
        for shortcut in shortcuts:
            shortcut_action = QAction(f"{shortcut}", self)
            self.draggable_toolbar.info_menu.addAction(shortcut_action)

    # حدث الرسم لتطبيق الخلفية المخصصة
    # ألم
    # ألم
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.height(),self.width() )
        gradient.setColorAt(0, QColor("#24384a"))  # الأزرق
        gradient.setColorAt(1, QColor("#57225f"))  # البنفسجي
        painter.fillRect(self.rect(), gradient)

    # الحصول على اسم المشروع من id المشروع
    # احصل على اسم المشروع
    # احصل على اسم المشروع
    def get_project_name(self, project_id):
        try:
            conn = self.get_db_connection()
            if conn is None:
                return f"مشروع رقم {project_id}"
            
            cursor = conn.cursor()
            cursor.execute("SELECT اسم_المشروع FROM المشاريع WHERE id = %s", (project_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return result[0]
            else:
                return f"مشروع رقم {project_id}"
        except Exception as e:
            print(f"خطأ في الحصول على اسم المشروع: {e}")
            return f"مشروع رقم {project_id}"

    # الحصول على اسم العميل من id المشروع
    # احصل على اسم العميل حسب المشروع
    # احصل على اسم العميل حسب المشروع
    def get_client_name_by_project(self, project_id):
        try:
            
            conn = self.get_db_connection()
            if conn is None:
                return "غير محدد"
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.اسم_العميل 
                FROM المشاريع p 
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id 
                WHERE p.id = %s
            """, (project_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result and result[0]:
                return result[0]
            else:
                return "غير محدد"
        except Exception as e:
            print(f"خطأ في الحصول على اسم العميل: {e}")
            return "غير محدد"

    # إنشاء اتصال بقاعدة بيانات السنة المحددة مع معالجة أخطاء محسنة
    # احصل على اتصال DB
    # احصل على اتصال DB
    def get_db_connection(self):
        db_name = f"project_manager_V2"

        # محاولة الاتصال بطرق مختلفة
        connection_configs = [
            # المحاولة الأولى: استخدام الإعدادات الافتراضية
            {
                'host': DB_HOST,
                'user': DEFAULT_DB_USER,
                'password': DEFAULT_DB_PASSWORD,
                'database': db_name,
                'charset': 'utf8mb4',
                'autocommit': True
            },
            # المحاولة الثانية: استخدام إعدادات بديلة
            {
                'host': host,
                'user': user_r,
                'password': password_r,
                'database': db_name,
                'charset': 'utf8mb4',
                'autocommit': True
            },
            # المحاولة الثالثة: استخدام المستخدم العادي
            {
                'host': host,
                'user': user,
                'password': pm_password,
                'database': db_name,
                'charset': 'utf8mb4',
                'autocommit': True
            }
        ]

        for i, config in enumerate(connection_configs):
            try:
                conn = mysql.connector.connect(**config)
                if conn.is_connected():
                    return conn
            except mysql.connector.Error as err:
                if i == len(connection_configs) - 1:  # آخر محاولة
                    print(f"⚠️ لا يمكن الحصول على اتصال قاعدة البيانات: {err}")
                    # لا نعرض رسالة خطأ للمستخدم لتجنب الإزعاج
                    return None
                else:
                    continue  # جرب الإعداد التالي

        return None

    # إنشاء اتصال بقاعدة البيانات باستخدام مستخدم root
    # الحصول على اتصال الجذر
    # الحصول على اتصال الجذر
    def get_root_connection(self):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=ROOT_USER,
                password=ROOT_PASSWORD
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Root Database Connection Error: {err}")
            QMessageBox.critical(self, "خطأ في اتصال Root",
                                 f"حدث خطأ عند الاتصال بقاعدة البيانات بصلاحيات المدير:\n{err}")
            return None

    # إنشاء قاعدة البيانات والجداول للسنة المحددة إذا لم تكن موجودة
    # إنشاء قاعدة بيانات إذا لم تكن موجودة
    # إنشاء قاعدة بيانات إذا لم تكن موجودة
    def create_database_if_not_exists(self):
        create_database_if_not_exists(self)

    # إعدادات الجدول
    # جدول الإعداد
    # جدول الإعداد
    def _setup_table(self, table, columns):
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels([col["label"] for col in columns])
        # نحتاج إلى تخزين اسم القسم في خاصية للجدول لاستخدامه لاحقًا
        current_section = self.get_current_section_name()
        table.setProperty("section_name", current_section)
        table_setting(table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(table, self, current_section, is_main_table=True)

        # قطع الاتصال بأي إشارات سابقة لتجنب تكرار الاستدعاء
        # التحقق من وجود اتصالات سابقة قبل محاولة قطعها
        if hasattr(table, '_double_click_connected') and table._double_click_connected:
            try:
                table.itemDoubleClicked.disconnect(self.handle_table_double_click)
            except (TypeError, RuntimeError):
                pass

        # ربط الإشارة الجديدة
        table.itemDoubleClicked.connect(self.handle_table_double_click)
        # تسجيل أن الاتصال تم
        table._double_click_connected = True
     
    # الحصول على اسم الجدول في قاعدة البيانات من اسم القسم في الواجهة
    # احصل على اسم جدول DB
    # احصل على اسم جدول DB
    def get_db_table_name(self, ui_section_name):
         # معالجة خاصة لقسم التقارير
         if ui_section_name == "التقارير":
             return None  # قسم التقارير لا يستخدم جدول محدد
         return UI_SECTION_TO_DB_TABLE_MAP.get(ui_section_name, ui_section_name)

    # معالجة النقر المزدوج على عنصر في الجدول وفتح نافذة التعديل
    # معالجة جدول انقر نقرًا مزدوجًا
    # معالجة جدول انقر نقرًا مزدوجًا
    def handle_table_double_click(self, item):
        if not item:
            print("No item selected!")
            return

        # الحصول على الجدول الذي تم النقر عليه
        table = self.sender()
        if not table:
            print("Could not determine source table!")
            return

        # الحصول على اسم القسم من خاصية الجدول
        section_name = table.property("section_name")
        if not section_name:
            print("No section name found for table!")
            return

        row = item.row()
        # الحصول على id الصف من العمود الأول (عمود الid)
        معرف_item = table.item(row, 0)
        if not معرف_item:
            print("No valid row_id found!")
            return

        # محاولة الحصول على الid من بيانات UserRole أولاً (التي تحتوي على القيمة الأصلية)
        # إذا لم تكن متوفرة، استخدم النص المعروض
        row_id = معرف_item.data(Qt.UserRole) if معرف_item.data(Qt.UserRole) is not None else معرف_item.text()

        if not row_id:
            print("No valid row_id found!")
            return


        # جلب بيانات الصف الكاملة من قاعدة البيانات
        db_table_name = self.get_db_table_name(section_name)
        
        try:
            conn = self.get_db_connection()
            if conn is None:
                print(f"Could not connect to database for")
                return

            cursor = conn.cursor(dictionary=True)

            # معالجة خاصة لأقسام المشاريع والمقاولات للحصول على اسم العميل واسم المهندس
            if section_name == "المشاريع":
                sql = f"""
                    SELECT p.*, c.اسم_العميل, c.رقم_الهاتف as رقم_هاتف_العميل, c.العنوان as عنوان_العميل, c.التصنيف as كود_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM `{db_table_name}` p
                    LEFT JOIN `العملاء` c ON p.معرف_العميل = c.id
                    LEFT JOIN `الموظفين` e ON p.معرف_المهندس = e.id
                    WHERE p.id = %s
                """

            else:
                sql = f"SELECT * FROM `{db_table_name}` WHERE id = %s"

            cursor.execute(sql, (row_id,))
            entry_data = cursor.fetchone()

            cursor.close()
            conn.close()

            if not entry_data:
                print(f"No data found in database for row_id {row_id}")
                return

        except Exception as e:
            print(f"Error fetching data from database: {e}")
            return

        # معالجة خاصة لكل قسم لفتح النافذة المناسبة
        if section_name == "الموظفين":
            # فتح نافذة إدارة الموظف
            try:
                from إدارة_الموظفين import open_employee_management_window
                self.employee_management_window = open_employee_management_window(self, entry_data)
                return
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة الموظف: {str(e)}")
                print(f"تفاصيل الخطأ: {e}")

        elif section_name == "التدريب":
            # فتح نافذة إدارة التدريب
            try:
                from إدارة_التدريب import open_training_management_window
                self.training_management_window = open_training_management_window(self, entry_data)
                return
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة التدريب: {str(e)}")
                # في حالة الفشل، استخدم النافذة العادية
                self.handle_action_button("تعديل", section_name, entry_data)
                
        elif section_name == "الموردين":
            # فتح نافذة إدارة المورد
            try:
                from إدارة_الموردين import open_supplier_management_window
                self.supplier_management_window = open_supplier_management_window(self, entry_data)
                return
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المورد: {str(e)}")

        elif section_name in ["المشاريع", "المقاولات"]:
            # فتح نافذة إدارة المشروع للمشاريع والمقاولات فقط
            try:
                #from إدارة_المشروع import open_project_phases_window
                
                project_type = entry_data.get('اسم_القسم', section_name)
                self.project_phases_window = open_project_phases_window(self, entry_data, project_type)
                return
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المشروع: {str(e)}")

        # للأقسام الأخرى، استخدم النافذة العادية للتعديل
        dialog = AddEntryDialog(
            main_window=self,
            section_name =section_name,
            
            entry_data=entry_data,
            row_id=row_id
        )

        if dialog.exec() == QDialog.Accepted:
            self.show_section(section_name)
            # تحديث عرض البطاقات إذا كان نشطاً
            if hasattr(self, 'update_cards_view'):
                self.update_cards_view(section_name)

    # ملء صندوق الاختيار بالسنوات المتاحة
    # ملء سنوات
    # ملء سنوات
    def populate_years(self, combo_box):
        try:
            conn = self.get_root_connection()
            if conn is None:
                 # If root connection fails, try connecting with default user to access user DB
                 conn = mysql.connector.connect(host=self.db_host, user=self.db_user, password=self.db_password)
                 if conn is None:
                     print("Could not connect as root or default user to populate years.")
                     # QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات لجلب السنوات.")
                     return # Cannot populate if no connection

            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            # Use a regex pattern to find database names matching 'project_manager2_YYYY'
            pattern = re.compile(r'project_manager2_(\d{4})')
            current_year = QDate.currentDate().year()
            years = set()
            for db in cursor:
                db_name = str(db[0])
                match = pattern.match(db_name)
                if match:
                    years.add(int(match.group(1)))

            # Always include the current year, even if no DB exists for it yet
            if current_year not in years:
                years.add(current_year)

            # Sort years in descending order (most recent first)
            years = sorted(years, reverse=True)

            # Clear existing items and add sorted years
            combo_box.clear()
            for year in years:
                combo_box.addItem(str(year))

            # Set the current year as the default selected item
            if str(current_year) in [combo_box.itemText(i) for i in range(combo_box.count())]:
                combo_box.setCurrentText(str(current_year))
            elif combo_box.count() > 0:
                 combo_box.setCurrentIndex(0) # Select the first available year

            # combo_box.setItemDelegate(AlignedItemDelegate(combo_box)) # Apply delegate if needed and available

            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            print(f"Error populating years: {e}")
            # QMessageBox.warning(self, "خطأ في قاعدة البيانات", f"حدث خطأ أثناء جلب سنوات قواعد البيانات:\n{e}")
        except Exception as e:
            print(f"Unexpected Error populating years: {e}")
            # QMessageBox.critical(self, "خطأ غير متوقع", f"حدث خطأ غير متوقع أثناء جلب سنوات قواعد البيانات:\n{e}")

    #تحميل البيانات من قاعدة البيانات إلى الجدول
    # تحميل البيانات من DB
    # تحميل البيانات من DB
    def _load_data_from_db(self, table, section_name):
        # معالجة خاصة للصفحة الرئيسية التي لا تستخدم جدول
        if section_name == "الرئيسية":
            return []
            
        # معالجة خاصة للأقسام التي لا تستخدم جدول تقليدي (مثل التقارير المالية)
        if table is None:
            print(f"⚠️ القسم '{section_name}' لا يستخدم جدول تقليدي - تخطي تحميل البيانات")

            # معالجة خاصة لقسم التقارير المالية
            if section_name == "التقارير":
                try:
                    # تحديث الإحصائيات المالية
                    section_info = self.sections.get(section_name)
                    if section_info:
                        self.update_financial_stats(section_info)

                        # البحث عن ويدجت التقارير المالية وتحديث بياناته
                        if "page" in section_info:
                            page = section_info["page"]
                            for child in page.findChildren(QWidget):
                                if hasattr(child, 'refresh_data'):
                                    child.refresh_data()
                                    break

                        

                    return []  # إرجاع قائمة فارغة للأقسام الخاصة

                except Exception as e:
                    print(f"⚠️ خطأ في تحديث بيانات التقارير المالية: {e}")
                    return []

            return []  # إرجاع قائمة فارغة للأقسام الأخرى التي لا تستخدم جدول

        # للأقسام التي تستخدم جدول تقليدي
        table.setUpdatesEnabled(False)
        table.setSortingEnabled(False)

        db_table_name = self.get_db_table_name(section_name)  # الحصول على اسم الجدول
        conn = None
        cursor = None

        section_info = self.sections.get(section_name)
        empty_state_widget = section_info.get("empty_state_widget")
        if empty_state_widget is None:
            print(f"Error: empty_state_widget not found for section {section_name}")

        try:
            conn = self.get_db_connection()
            if conn is None:
                table.setRowCount(0)
                if empty_state_widget:
                    table.hide()
                    empty_state_widget.show()
                print(f"No DB connection , cannot load data for {section_name}")
                return []  # إرجاع قائمة فارغة

            cursor = conn.cursor(dictionary=True)  # استخدام dictionary=True لإرجاع القواميس

            # Special handling for Projects and Contracting sections to get client name and engineer name
            if section_name == "المشاريع":
                sql = f"""
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM `{db_table_name}` p
                    LEFT JOIN `العملاء` c ON p.معرف_العميل = c.id
                    LEFT JOIN `الموظفين` e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المشاريع'
                """
            elif section_name == "المقاولات":
                sql = f"""
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM `{db_table_name}` p
                    LEFT JOIN `العملاء` c ON p.معرف_العميل = c.id
                    LEFT JOIN `الموظفين` e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المقاولات'
                """
            elif section_name == "العملاء":
                sql = f"""
                    SELECT c.*,
                           COUNT(p.id) as عدد_المشاريع,
                           COALESCE(SUM(p.المبلغ), 0) as إجمالي_القيمة,
                           COALESCE(SUM(p.المدفوع), 0) as إجمالي_المدفوع,
                           COALESCE(SUM(p.الباقي), 0) as إجمالي_الباقي
                    FROM `{db_table_name}` c
                    LEFT JOIN المشاريع p ON c.id = p.معرف_العميل
                    GROUP BY c.id
                    ORDER BY c.اسم_العميل
                """
            else:
                sql = f"SELECT * FROM `{db_table_name}`"

            # Add filter logic based on section and filter combo
            if section_name in ["المشاريع", "المقاولات"]:
                # معالجة فلتر التصنيف والحالة والمسؤول للمشاريع والمقاولات
                classification_filter_combo = section_info.get("classification_filter_combo")
                filter_combo = section_info.get("filter_combo")
                responsible_filter_combo = section_info.get("responsible_filter_combo")

                where_conditions = []
                params = []

                # فلتر التصنيف
                if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                    classification_value = classification_filter_combo.currentText()
                    where_conditions.append("p.`التصنيف` = %s")
                    params.append(classification_value)

                # فلتر المسؤول
                if responsible_filter_combo and responsible_filter_combo.currentText() != "كل المسؤولين":
                    responsible_value = responsible_filter_combo.currentText()
                    where_conditions.append("e.`اسم_الموظف` = %s")
                    params.append(responsible_value)

                # فلتر الحالة
                if filter_combo and filter_combo.currentText() != "كل الحالات":
                    status_value = filter_combo.currentText()

                    # إذا كان الفلتر هو "غير مكتمل"، نعرض المعاملات قيد الإنجاز والغير خالصة وتأكيد التسليم
                    if status_value == "غير مكتمل":
                        where_conditions.append("p.`الحالة` IN ('قيد الإنجاز', 'غير خالص', 'تأكيد التسليم')")
                        # إضافة ترتيب خاص للحالات غير المكتملة
                        if where_conditions:
                            sql += " AND " + " AND ".join(where_conditions)
                            sql += """
                                ORDER BY
                                    CASE
                                        WHEN p.`الحالة` = 'قيد الإنجاز' THEN 1
                                        WHEN p.`الحالة` = 'غير خالص' THEN 2
                                        WHEN p.`الحالة` = 'تأكيد التسليم' THEN 3
                                    END,
                                    CASE
                                        WHEN p.`الحالة` = 'قيد الإنجاز' THEN p.`تاريخ_التسليم`
                                    END
                            """
                        cursor.execute(sql, params)
                    else:
                        where_conditions.append("p.`الحالة` = %s")
                        params.append(status_value)

                        # إضافة شروط WHERE إذا وجدت
                        if where_conditions:
                            sql += " AND " + " AND ".join(where_conditions)
                            cursor.execute(sql, params)
                        else:
                            cursor.execute(sql)
                else:
                    # إضافة شروط WHERE إذا وجدت (فقط التصنيف)
                    if where_conditions:
                        sql += " AND " + " AND ".join(where_conditions)
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
            elif section_name in ["التدريب"]:
                # معالجة فلتر التصنيف والحالة  والتدريب
                classification_filter_combo = section_info.get("classification_filter_combo")
                filter_combo = section_info.get("filter_combo")

                where_conditions = []
                params = []

                # فلتر التصنيف
                if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                    classification_value = classification_filter_combo.currentText()
                    where_conditions.append("`التصنيف` = %s")
                    params.append(classification_value)

                # فلتر الحالة
                if filter_combo and filter_combo.currentText() != "كل الحالات":
                    status_value = filter_combo.currentText()
                    where_conditions.append("`الحالة` = %s")
                    params.append(status_value)

                # إضافة شروط WHERE إذا وجدت
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

            elif section_name == "الموردين":
                # معالجة فلتر التصنيف والحالة والوظيفة للموظفين
                classification_filter_combo = section_info.get("classification_filter_combo")
                filter_combo = section_info.get("filter_combo")
                job_filter_combo = section_info.get("job_filter_combo")

                where_conditions = []
                params = [] 

                # فلتر التصنيف
                if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                    classification_value = classification_filter_combo.currentText()
                    where_conditions.append("`التصنيف` = %s")
                    params.append(classification_value) 

                

                # إضافة شروط WHERE إذا وجدت
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                    
            elif section_name == "الموظفين":
                # معالجة فلتر التصنيف والحالة والوظيفة للموظفين
                classification_filter_combo = section_info.get("classification_filter_combo")
                filter_combo = section_info.get("filter_combo")
                job_filter_combo = section_info.get("job_filter_combo")

                where_conditions = []
                params = []

                # فلتر التصنيف
                if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                    classification_value = classification_filter_combo.currentText()
                    where_conditions.append("`التصنيف` = %s")
                    params.append(classification_value)

                # فلتر الحالة للموظفين
                if filter_combo and filter_combo.currentText() != "كل الحالات":
                    status_value = filter_combo.currentText()
                    where_conditions.append("`الحالة` = %s")
                    params.append(status_value)

                # فلتر الوظيفة للموظفين
                if job_filter_combo and job_filter_combo.currentText() != "كل الوظائف":
                    job_value = job_filter_combo.currentText()
                    where_conditions.append("`الوظيفة` = %s")
                    params.append(job_value)

                # إضافة شروط WHERE إذا وجدت
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

            elif section_name == "العملاء":
                # معالجة فلتر التصنيف للعملاء مع الاستعلام المحدث
                classification_filter_combo = section_info.get("classification_filter_combo")
                filter_combo = section_info.get("filter_combo")

                where_conditions = []
                params = []

                # فلتر التصنيف الجديد
                if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                    classification_value = classification_filter_combo.currentText()
                    where_conditions.append("c.`التصنيف` = %s")
                    params.append(classification_value)

                # فلتر التصنيف القديم (للتوافق مع الكود القديم)
                elif filter_combo and filter_combo.currentText() != "كل التصنيفات":
                    filter_value = filter_combo.currentText()
                    where_conditions.append("c.`التصنيف` = %s")
                    params.append(filter_value)

                # إضافة شروط WHERE إذا وجدت
                if where_conditions:
                    # إضافة WHERE قبل GROUP BY
                    sql = sql.replace("GROUP BY c.id", "WHERE " + " AND ".join(where_conditions) + " GROUP BY c.id")
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

            elif section_name == "الحسابات":
                # معالجة فلتر التصنيف للحسابات
                classification_filter_combo = section_info.get("classification_filter_combo")
                filter_combo = section_info.get("filter_combo")

                where_conditions = []
                params = []

                # فلتر التصنيف الجديد
                if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                    classification_value = classification_filter_combo.currentText()
                    where_conditions.append("`التصنيف` = %s")
                    params.append(classification_value)

                # فلتر التصنيف القديم (للتوافق مع الكود القديم)
                elif filter_combo and filter_combo.currentText() != "كل التصنيفات":
                    filter_value = filter_combo.currentText()
                    where_conditions.append("`التصنيف` = %s")
                    params.append(filter_value)

                # إضافة شروط WHERE إذا وجدت
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

            elif section_name == "التقارير":
                # معالجة خاصة لقسم التقارير المالية - تحميل البيانات المالية
                from محتوى_التقارير_المالية import load_financial_data_for_table
                results = load_financial_data_for_table()

                # تحديث الإحصائيات المالية
                self.update_financial_stats(section_info)

                # إرجاع البيانات مباشرة بدون استعلام قاعدة البيانات
                if len(results) == 0:
                    table.setRowCount(0)
                    table.hide()
                    if empty_state_widget:
                        empty_state_widget.show()
                else:
                    if empty_state_widget:
                        empty_state_widget.hide()
                    table.show()

                    # تحديد الأعمدة للتقارير المالية
                    columns = ["نوع الحساب", "اسم الحساب", "الرصيد المدين", "الرصيد الدائن", "صافي الرصيد", "النسبة %"]
                    table.setColumnCount(len(columns))
                    table.setHorizontalHeaderLabels(columns)

                    # ملء الجدول بالبيانات
                    table.setRowCount(len(results))
                    for row, data in enumerate(results):
                        table.setItem(row, 0, QTableWidgetItem(str(data.get("نوع_الحساب", ""))))
                        table.setItem(row, 1, QTableWidgetItem(str(data.get("اسم_الحساب", ""))))
                        table.setItem(row, 2, QTableWidgetItem(f"{data.get('الرصيد_المدين', 0):,.2f}"))
                        table.setItem(row, 3, QTableWidgetItem(f"{data.get('الرصيد_الدائن', 0):,.2f}"))
                        table.setItem(row, 4, QTableWidgetItem(f"{data.get('صافي_الرصيد', 0):,.2f}"))
                        table.setItem(row, 5, QTableWidgetItem(f"{data.get('النسبة', 0):.1f}%"))

                        # تلوين الخلايا
                        for col in range(6):
                            item = table.item(row, col)
                            if item:
                                item.setTextAlignment(Qt.AlignCenter)
                                # تلوين صافي الرصيد
                                if col == 4:  # عمود صافي الرصيد
                                    if data.get('صافي_الرصيد', 0) < 0:
                                        item.setForeground(QColor(231, 76, 60))  # أحمر للسالب
                                    else:
                                        item.setForeground(QColor(46, 125, 50))  # أخضر للموجب

                table.setUpdatesEnabled(True)
                table.setSortingEnabled(True)
                return results

            else:
                cursor.execute(sql)

            results = cursor.fetchall()

            # --- Show Empty State or Table ---
            if len(results) == 0:
                if table is not None:
                    table.setRowCount(0)
                    table.hide()
                if empty_state_widget:
                    empty_state_widget.show()

            else:
                if empty_state_widget:
                    empty_state_widget.hide()
                if table is not None:
                    table.show()

                    columns = TABLE_COLUMNS.get(section_name, [])
                    num_columns = len(results[0]) if results else len(columns)
                    table.setColumnCount(num_columns)

                    if len(columns) == num_columns:
                        table.setHorizontalHeaderLabels(columns)
                    else:
                        db_column_names = [desc[0] for desc in cursor.description] if cursor.description else []
                        table.setHorizontalHeaderLabels(db_column_names)

                    table.setRowCount(len(results))

                # استخدام قائمة الأعمدة الidة في TABLE_COLUMNS للتأكد من وضع البيانات في الأعمدة الصحيحة
                if table is not None:
                    columns = TABLE_COLUMNS.get(section_name, [])
                    column_keys = [col["key"] for col in columns]

                    for row_index, row_data in enumerate(results):
                        # استخدام مفاتيح الأعمدة الidة في TABLE_COLUMNS بدلاً من ترتيب البيانات في قاعدة البيانات
                        for col_index, col_key in enumerate(column_keys):
                            # التحقق من عمود الرقم وتوليد رقم تسلسلي تلقائي
                            if col_key == "الرقم":
                                # إنشاء رقم تسلسلي تلقائي بدءاً من 1
                                sequential_number = row_index + 1
                                item = QTableWidgetItem(str(sequential_number))
                                item.setTextAlignment(Qt.AlignCenter)
                                item.setData(Qt.UserRole, sequential_number)
                                # تطبيق لون النص الافتراضي
                                default_text_color = self.get_default_table_text_color()
                                item.setForeground(QBrush(default_text_color))
                                table.setItem(row_index, col_index, item)
                                continue

                            if col_key in row_data:
                                col_data = row_data[col_key]
                                item = QTableWidgetItem()

                                if isinstance(col_data, datetime):
                                    # فصل الوقت عن التاريخ وإضافة الوقت ص/م (بدون اسم اليوم)
                                    date_part = col_data.strftime("%Y-%m-%d")

                                    # تحديد ص/م للوقت
                                    hour = col_data.hour
                                    am_pm = "ص" if hour < 12 else "م"

                                    # تنسيق الساعة بنظام 12 ساعة
                                    hour_12 = hour % 12
                                    if hour_12 == 0:
                                        hour_12 = 12

                                    # تنسيق الوقت بشكل منفصل
                                    time_part = f"{hour_12}:{col_data.minute:02d} {am_pm}"

                                    # الجمع بين التاريخ والوقت بشكل منظم (بدون اسم اليوم)
                                    formatted_datetime = f"{date_part} | {time_part}"

                                    item.setData(Qt.DisplayRole, formatted_datetime)
                                    item.setData(Qt.UserRole, col_data)
                                elif isinstance(col_data, date):
                                    # تنسيق التاريخ بدون إضافة اسم اليوم
                                    date_part = col_data.strftime("%Y-%m-%d")

                                    # تعيين التاريخ مباشرة بدون اسم اليوم
                                    formatted_date = date_part

                                    item.setData(Qt.DisplayRole, formatted_date)
                                    item.setData(Qt.UserRole, col_data)
                                elif isinstance(col_data, (int, float, complex)):
                                    display_text = str(col_data)
                                    try:
                                        header_name = table.horizontalHeaderItem(col_index).text() if table.horizontalHeaderItem(col_index) else ""
                                        col_key_name = col_key if col_key else ""

                                        # تنسيق الأرقام المالية
                                        if any(curr_header in header_name for curr_header in ["المبلغ", "المدفوع", "الباقي", "المرتب", "الرصيد", "التكلفة", "إجمالي", "الإجمالي"]):
                                            formatted_value = f"{col_data:,.2f}".rstrip('0').rstrip('.') if isinstance(col_data, float) else f"{col_data:,}"
                                            display_text = formatted_value
                                        else:
                                            display_text = str(col_data)
                                    except Exception as format_e:
                                        print(f"Error formatting number {col_data}: {format_e}")
                                        display_text = str(col_data)

                                    item.setData(Qt.DisplayRole, display_text)
                                    item.setData(Qt.UserRole, col_data)
                                    item.setTextAlignment(Qt.AlignCenter)

                                    # تلوين خاص للعملاء
                                    if section_name == "العملاء":
                                        col_key_name = col_key if col_key else ""
                                        # إجمالي الباقي
                                        if col_key_name == "إجمالي_الباقي":
                                            if col_data == 0:
                                                item.setData(Qt.DisplayRole, "خالص")
                                                item.setForeground(QBrush(QColor(39, 174, 96)))  # أخضر
                                                item.setFont(QFont("Arial", 10, QFont.Bold))
                                            else:
                                                item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                                                item.setFont(QFont("Arial", 10, QFont.Bold))
                                        # إجمالي القيمة
                                        elif col_key_name == "إجمالي_القيمة":
                                            item.setForeground(QBrush(QColor(52, 152, 219)))  # أزرق
                                            item.setFont(QFont("Arial", 10, QFont.Bold))
                                        # إجمالي المدفوع
                                        elif col_key_name == "إجمالي_المدفوع":
                                            if col_data == 0:
                                                item.setData(Qt.DisplayRole, "لا شيء")
                                                item.setForeground(QBrush(QColor(243, 156, 18)))  # برتقالي
                                                item.setFont(QFont("Arial", 10, QFont.Bold))
                                            else:
                                                item.setForeground(QBrush(QColor(39, 174, 96)))  # أخضر
                                                item.setFont(QFont("Arial", 10, QFont.Bold))

                                    # تلوين خاص للمشاريع والمقاولات - سيتم تطبيقه لاحقاً في colorize_projects_table
                                    elif section_name in ["المشاريع", "المقاولات"]:
                                        # حفظ القيم الأصلية فقط بدون تلوين هنا
                                        pass
                                elif col_data is None:
                                    item.setData(Qt.DisplayRole, "")
                                    item.setData(Qt.UserRole, None)
                                else:
                                    item.setData(Qt.DisplayRole, str(col_data))
                                    item.setData(Qt.UserRole, col_data)
                                    item.setTextAlignment(Qt.AlignCenter)

                                # تطبيق لون النص الافتراضي لجميع العناصر
                                if not item.foreground().color().isValid() or item.foreground().color() == QColor():
                                    # تطبيق لون النص الافتراضي حسب الثيم
                                    default_text_color = self.get_default_table_text_color()
                                    item.setForeground(QBrush(default_text_color))

                                table.setItem(row_index, col_index, item)

                    self._setup_table(table, columns)

                    # تطبيق لون النص الافتراضي على جميع الخلايا أولاً
                    self.apply_default_text_color_to_table(table)

                    # تطبيق التلوين للعملاء
                    if section_name == "العملاء":
                        self.colorize_clients_table(table)
                    # تطبيق التلوين للمشاريع والمقاولات
                    elif section_name in ["المشاريع", "المقاولات"]:
                        self.colorize_projects_table(table, section_name)
                if table is not None:
                    table.resizeRowsToContents()

                if table is not None:
                    table.setUpdatesEnabled(True)
                    table.setSortingEnabled(True)

            if table is not None:
                table.verticalHeader().setDefaultSectionSize(40)

            return results  # إرجاع البيانات لاستخدامها في show_section
        except mysql.connector.Error as err:
            print(f"Error loading data for {section_name} (DB: {db_table_name}): {err}")
            if table is not None:
                table.setRowCount(0)
                table.hide()
            if empty_state_widget:
                empty_state_widget.show()
            return []
        except Exception as e:
            print(f"Unexpected Error loading data: {e}")
            if table is not None:
                table.setRowCount(0)
                table.hide()
            if empty_state_widget:
                empty_state_widget.show()
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # الحصول على لون النص الافتراضي للجدول
    # احصل على لون نص الجدول الافتراضي
    # احصل على لون نص الجدول الافتراضي
    def get_default_table_text_color(self):
        try:
            # استخدام لون رمادي غامق كلون افتراضي آمن
            # هذا اللون يعمل جيداً مع معظم خلفيات الجداول
            return QColor(51, 51, 51)  # رمادي غامق

        except Exception as e:
            print(f"خطأ في تحديد لون النص الافتراضي: {e}")
            # لون احتياطي
            return QColor(0, 0, 0)  # أسود

    # تطبيق لون النص الافتراضي على جميع خلايا الجدول
    # تطبيق لون النص الافتراضي على الجدول
    # تطبيق لون النص الافتراضي على الجدول
    def apply_default_text_color_to_table(self, table):
        try:
            default_text_color = self.get_default_table_text_color()

            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        # التحقق من أن العنصر لا يحتوي على لون مخصص بالفعل
                        current_color = item.foreground().color()
                        if not current_color.isValid() or current_color == QColor():
                            item.setForeground(QBrush(default_text_color))

        except Exception as e:
            print(f"خطأ في تطبيق لون النص الافتراضي على الجدول: {e}")

    # تطبيق التلوين على جدول العملاء
    # تلوين جدول العملاء
    # تلوين جدول العملاء
    def colorize_clients_table(self, table):
        try:
            columns = TABLE_COLUMNS.get("العملاء", [])
            column_keys = [col["key"] for col in columns]

            # العثور على فهارس الأعمدة المالية
            remaining_col = -1
            total_col = -1
            paid_col = -1

            for i, col_key in enumerate(column_keys):
                if col_key == "إجمالي_الباقي":
                    remaining_col = i
                elif col_key == "إجمالي_القيمة":
                    total_col = i
                elif col_key == "إجمالي_المدفوع":
                    paid_col = i

            # تطبيق التلوين على الصفوف
            for row in range(table.rowCount()):
                # إجمالي الباقي
                if remaining_col >= 0:
                    item = table.item(row, remaining_col)
                    if item:
                        original_value = item.data(Qt.UserRole)
                        if original_value is not None:
                            if original_value == 0:
                                item.setText("خالص")
                                item.setForeground(QBrush(QColor(39, 174, 96)))  # أخضر
                            else:
                                item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                            item.setFont(QFont("Arial", 10, QFont.Bold))

                # إجمالي القيمة
                if total_col >= 0:
                    item = table.item(row, total_col)
                    if item:
                        item.setForeground(QBrush(QColor(52, 152, 219)))  # أزرق
                        item.setFont(QFont("Arial", 10, QFont.Bold))

                # إجمالي المدفوع
                if paid_col >= 0:
                    item = table.item(row, paid_col)
                    if item:
                        original_value = item.data(Qt.UserRole)
                        if original_value is not None:
                            if original_value == 0:
                                item.setText("لا شيء")
                                item.setForeground(QBrush(QColor(243, 156, 18)))  # برتقالي
                            else:
                                item.setForeground(QBrush(QColor(39, 174, 96)))  # أخضر
                            item.setFont(QFont("Arial", 10, QFont.Bold))

        except Exception as e:
            print(f"خطأ في تطبيق التلوين على جدول العملاء: {e}")

    # تطبيق التلوين على جدول المشاريع والمقاولات
    # تلوين جدول المشاريع
    # تلوين جدول المشاريع
    def colorize_projects_table(self, table, section_name):
        try:
            columns = TABLE_COLUMNS.get(section_name, [])
            column_keys = [col["key"] for col in columns]

            # العثور على فهارس الأعمدة المالية
            total_col = -1
            paid_col = -1
            remaining_col = -1

            for i, col_key in enumerate(column_keys):
                if col_key == "المبلغ":
                    total_col = i
                elif col_key == "المدفوع":
                    paid_col = i
                elif col_key == "الباقي":
                    remaining_col = i

            # تطبيق التلوين على الصفوف
            for row in range(table.rowCount()):
                # الإجمالي (المبلغ)
                if total_col >= 0:
                    item = table.item(row, total_col)
                    if item:
                        original_value = item.data(Qt.UserRole)
                        if original_value is not None:
                            try:
                                total_amount = float(original_value)
                            except (ValueError, TypeError):
                                total_amount = 0

                            if total_amount == 0:
                                item.setText("غير محدد")
                                item.setForeground(QBrush(QColor(52, 152, 219)))  # أزرق
                            else:
                                item.setForeground(QBrush(QColor(52, 152, 219)))  # أزرق
                            item.setFont(QFont("Arial", 10, QFont.Bold))

                # المدفوع
                if paid_col >= 0:
                    paid_item = table.item(row, paid_col)
                    total_item = table.item(row, total_col) if total_col >= 0 else None

                    if paid_item:
                        paid_value = paid_item.data(Qt.UserRole)
                        total_value = total_item.data(Qt.UserRole) if total_item else 0

                        # التأكد من أن القيم رقمية
                        try:
                            paid_value = float(paid_value) if paid_value is not None else 0
                            total_value = float(total_value) if total_value is not None else 0
                        except (ValueError, TypeError):
                            paid_value = 0
                            total_value = 0

                        if paid_value == 0:
                            paid_item.setText("لا شيء")
                            paid_item.setForeground(QBrush(QColor(243, 156, 18)))  # برتقالي
                        elif total_value > 0 and paid_value >= total_value:
                            paid_item.setForeground(QBrush(QColor(39, 174, 96)))  # أخضر
                        else:
                            paid_item.setForeground(QBrush(QColor(243, 156, 18)))  # برتقالي
                        paid_item.setFont(QFont("Arial", 10, QFont.Bold))

                # الباقي
                if remaining_col >= 0:
                    item = table.item(row, remaining_col)
                    if item:
                        original_value = item.data(Qt.UserRole)
                        if original_value is not None:
                            try:
                                remaining_value = float(original_value)
                            except (ValueError, TypeError):
                                remaining_value = 0

                            if remaining_value == 0:
                                item.setText("خالص")
                                item.setForeground(QBrush(QColor(39, 174, 96)))  # أخضر
                            else:
                                item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                            item.setFont(QFont("Arial", 10, QFont.Bold))

        except Exception as e:
            print(f"خطأ في تطبيق التلوين على جدول {section_name}: {e}")
         
    # تحديث قيم بوكسات الإحصائيات من قاعدة البيانات للسنة المحددة
    # تحديث الإحصائيات
    # تحديث الإحصائيات
    def _update_stats(self, stat_boxes, section_name, year):
        # لا حاجة لتحديث الإحصائيات للصفحة الرئيسية
        if section_name == "الرئيسية":
            return
        conn = None
        cursor = None
        try:
            conn = self.get_db_connection()
            if conn is None:
                for box in stat_boxes.values():
                    value_label = box.findChild(QLabel, "StatValue")
                    if value_label:
                        value_label.setText("خطأ")
                return

            cursor = conn.cursor()

            # حساب بداية ونهاية السنة والشهر المطلوبين بناءً على السنة المختارة
            try:
                selected_year_int = int(year)
                year_start = f"{selected_year_int}-01-01"
                year_end = f"{selected_year_int}-12-31"

                today = QDate.currentDate()
                # Use the month from today's date, but the year from the combo box
                current_month_num = today.month()

                # Check if the selected year is the current year
                if selected_year_int == today.year():
                    # If it's the current year, the month end is today's date
                    month_end_date = today
                else:
                    # If it's a past or future year, use the end of the *current month* of that year
                    # Example: If selected year is 2023, and today is June 15, 2024,
                    # monthly stats for 2023 will be for June 2023.
                    month_start_date_for_month = QDate(selected_year_int, current_month_num, 1)
                    month_end_date = QDate(selected_year_int, current_month_num, month_start_date_for_month.daysInMonth())


                month_start = QDate(selected_year_int, current_month_num, 1).toString(Qt.ISODate)
                month_end = month_end_date.toString(Qt.ISODate)


            except ValueError:
                print(f"Invalid year selected for stats: {year}")
                for box in stat_boxes.values():
                     value_label = box.findChild(QLabel, "StatValue")
                     if value_label:
                        value_label.setText("سنة غير صالحة")
                return


            stats_values = {}

            if section_name == "المشاريع":
                 cursor.execute("SELECT COUNT(*) FROM `المشاريع` WHERE `الحالة` = 'قيد الإنجاز' AND `اسم_القسم` = 'المشاريع'")
                 result = cursor.fetchone()
                 stats_values["مشاريع قيد الإنجاز"] = result[0] if result else 0

                 cursor.execute("SELECT SUM(`المبلغ_المدفوع`) FROM `المشاريع_المدفوعات` WHERE `تاريخ_الدفع` >= %s AND `تاريخ_الدفع` <= %s", (year_start, year_end))
                 result = cursor.fetchone()
                 yearly_income = result[0] if result and result[0] is not None else 0
                 stats_values["الوارد السنوي"] = f"{yearly_income:,.0f}  {Currency_type}" # Or your currency

                 # إجمالي الباقي لجميع المشاريع في هذه السنة (غير المكتملة)
                 # استعلام الباقي المحسوب (GENERATED ALWAYS) لا يحتاج فلتر على التاريخ
                 # لأنه خاص ببيانات هذه القاعدة (السنة المحددة)
                 # Only sum remaining for projects that are not fully paid or delivered
                 cursor.execute("SELECT SUM(`الباقي`) FROM `المشاريع` WHERE `الحالة` != 'تم التسليم' AND `اسم_القسم` = 'المشاريع'")
                 result = cursor.fetchone()
                 total_remaining = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي الباقي"] = f"{total_remaining:,.0f}  {Currency_type}" # Or your currency

            elif section_name == "المقاولات":
                 cursor.execute("SELECT COUNT(*) FROM `المشاريع` WHERE `الحالة` = 'قيد الإنجاز' AND `اسم_القسم` = 'المقاولات'")
                 result = cursor.fetchone()
                 stats_values["مقاولات قيد الإنجاز"] = result[0] if result else 0

                 # الوارد السنوي للمقاولات
                 cursor.execute("""
                     SELECT SUM(pm.`المبلغ_المدفوع`)
                     FROM `المشاريع_المدفوعات` pm
                     JOIN `المشاريع` p ON pm.`معرف_المشروع` = p.`id`
                     WHERE pm.`تاريخ_الدفع` >= %s AND pm.`تاريخ_الدفع` <= %s
                     AND p.`اسم_القسم` = 'المقاولات'
                 """, (year_start, year_end))
                 result = cursor.fetchone()
                 yearly_income = result[0] if result and result[0] is not None else 0
                 stats_values["الوارد السنوي"] = f"{yearly_income:,.0f}  {Currency_type}"

                 # إجمالي الباقي للمقاولات (غير المكتملة)
                 cursor.execute("SELECT SUM(`الباقي`) FROM `المشاريع` WHERE `الحالة` != 'تم التسليم' AND `اسم_القسم` = 'المقاولات'")
                 result = cursor.fetchone()
                 total_remaining = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي الباقي"] = f"{total_remaining:,.0f}  {Currency_type}"


            elif section_name == "الحسابات":
                 cursor.execute("SELECT SUM(`المبلغ`) FROM `الحسابات` WHERE `تاريخ_المصروف` >= %s AND `تاريخ_المصروف` <= %s", (month_start, month_end))
                 result = cursor.fetchone()
                 monthly_expense = result[0] if result and result[0] is not None else 0
                 stats_values["مصروفات الشهر"] = f"{monthly_expense:,.0f}  {Currency_type}"

                 cursor.execute("SELECT SUM(`المبلغ`) FROM `الحسابات` WHERE `تاريخ_المصروف` >= %s AND `تاريخ_المصروف` <= %s", (year_start, year_end))
                 result = cursor.fetchone()
                 yearly_expense = result[0] if result and result[0] is not None else 0
                 stats_values["مصروفات السنة"] = f"{yearly_expense:,.0f}  {Currency_type}"

                 cursor.execute("SELECT SUM(`المبلغ`) FROM `الحسابات`")
                 result = cursor.fetchone()
                 total_expense = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي المصروفات"] = f"{total_expense:,.0f}  {Currency_type}"

            elif section_name == "الموظفين":
                 cursor.execute("SELECT COUNT(*) FROM `الموظفين`")
                 result = cursor.fetchone()
                 stats_values["عدد الموظفين"] = result[0] if result else 0

                 cursor.execute("SELECT SUM(`الرصيد`) FROM `الموظفين`")
                 result = cursor.fetchone()
                 total_balance = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي الرصيد"] = f"{total_balance:,.0f}  {Currency_type}"

                 # حساب إجمالي السحوبات من جدول المعاملات المالية
                 cursor.execute("""
                     SELECT COALESCE(SUM(المبلغ), 0)
                     FROM الموظفين_معاملات_مالية
                     WHERE نوع_العملية IN ('سحب', 'خصم')
                 """)
                 result = cursor.fetchone()
                 total_withdrawal = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي السحب"] = f"{total_withdrawal:,.0f}  {Currency_type}"

            elif section_name == "العملاء":
                 cursor.execute("SELECT COUNT(*) FROM `العملاء`")
                 result = cursor.fetchone()
                 stats_values["إجمالي العملاء"] = result[0] if result else 0

                 cursor.execute("SELECT COUNT(*) FROM `العملاء` WHERE `تاريخ_الإضافة` >= %s AND `تاريخ_الإضافة` <= %s", (month_start, month_end))
                 result = cursor.fetchone()
                 new_clients_month = result[0] if result else 0
                 stats_values["عملاء جدد هذا الشهر"] = new_clients_month

                 # Count clients with active projects *in the current year's database*
                 # This assumes a client might exist in the العملاء table of a year's DB
                 # but their active project is in a different year's DB. This query
                 # only counts clients with active projects *within the currently selected year*.
                 cursor.execute("""
                    SELECT COUNT(DISTINCT T1.`معرف_العميل`)
                    FROM `المشاريع` T1
                    JOIN `العملاء` T2 ON T1.`معرف_العميل` = T2.`id`
                    WHERE T1.`الحالة` IN ('قيد الإنجاز', 'مؤجل')
                 """)
                 result = cursor.fetchone()
                 active_clients = result[0] if result else 0
                 stats_values["عملاء لهم مشاريع نشطة"] = active_clients


            
            elif section_name == "التدريب":
                 cursor.execute("SELECT COUNT(*) FROM `التدريب` WHERE `الحالة` = 'قيد التسجيل'")
                 result = cursor.fetchone()
                 stats_values["دورات قيد التسجيل"] = result[0] if result else 0

                 cursor.execute("SELECT COUNT(*) FROM `التدريب` WHERE `الحالة` = 'جارية'")
                 result = cursor.fetchone()
                 stats_values["دورات جارية"] = result[0] if result else 0

                 cursor.execute("SELECT SUM(`المبلغ_المدفوع`) FROM `التدريب_دفعات_الطلاب`")
                 result = cursor.fetchone()
                 total_amount = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي الإيرادات"] = f"{total_amount:,.0f}  {Currency_type}" # Or your currency

                 cursor.execute("SELECT SUM(`عدد_المشاركين`) FROM `التدريب`")
                 result = cursor.fetchone()
                 total_participants = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي المشاركين"] = total_participants
            
            elif section_name == "الموردين":
                 cursor.execute("SELECT COUNT(*) FROM `الموردين`")
                 result = cursor.fetchone()
                 stats_values["إجمالي الموردين"] = result[0] if result else 0

                 cursor.execute("SELECT SUM(`المدفوع_للمورد`) FROM `الموردين`")
                 result = cursor.fetchone()
                 total_amount = result[0] if result and result[0] is not None else 0
                 stats_values["إجمالي الإيرادات"] = f"{total_amount:,.0f}  {Currency_type}" # Or your currency

                 


            # تحديث قيم البوكسات
            for title, value in stats_values.items():
                box = stat_boxes.get(title)
                if box:
                     value_label = box.findChild(QLabel, "StatValue")
                     if value_label:
                        value_label.setText(str(value))

        except mysql.connector.Error as err:
            print(f"Error loading stats for {section_name} ({year}): {err}")
            for box in stat_boxes.values():
                 value_label = box.findChild(QLabel, "StatValue")
                 if value_label:
                    value_label.setText("خطأ")
            # QMessageBox.warning(self, "خطأ في تحميل الإحصائيات",
            #                      f"حدث خطأ أثناء تحميل إحصائيات {section_name}:\n{err}")
        except Exception as e:
            print(f"Unexpected Error loading stats: {e}")
            for box in stat_boxes.values():
                 value_label = box.findChild(QLabel, "StatValue")
                 if value_label:
                    value_label.setText("خطأ")
            # QMessageBox.critical(self, "خطأ غير متوقع",
            #                      f"حدث خطأ غير متوقع أثناء تحميل الإحصائيات:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    #مساعد للحصول على اسم القسم المرئي حاليًا
    # الحصول على اسم القسم الحالي
    # احصل على اسم القسم الحالي
    # احصل على اسم القسم الحالي
    def get_current_section_name(self):
        current_page = self.main_content_area.currentWidget()
        for name, info in self.sections.items():
            if info["page"] == current_page:
                return name
        return None

    # التبديل بين عرض الجدول والبطاقات العصرية لقسم محدد مع حفظ التفضيل
    # تبديل العرض
    # تبديل العرض
    def toggle_view(self, section_name):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                print(f"القسم {section_name} غير موجود")
                return

            # معالجة خاصة للأقسام التي لا تدعم view_stack
            if section_name == "التقارير":
                
                return

            view_stack = section_info.get("view_stack")
            if not view_stack:
                print(f"view_stack غير موجود للقسم {section_name}")
                return

            # الحصول على العرض الحالي
            current_view = section_info.get("current_view", "table")
            new_view = "cards" if current_view == "table" else "table"

            # تطبيق العرض الجديد على هذا القسم فقط
            self.apply_view_to_section(section_name, new_view == "cards")

            # حفظ التفضيل الجديد
            self.set_section_view_preference(section_name, new_view)

            # إظهار رسالة تأكيد
            view_type_ar = "البطاقات" if new_view == "cards" else "الجدول"


        except Exception as e:
            print(f"خطأ في تبديل العرض للقسم {section_name}: {e}")

    # تبديل عرض القسم مع رسالة تأكيد للمستخدم
    # عرض قسم التبديل مع التأكيد
    # عرض قسم التبديل مع التأكيد
    def toggle_section_view_with_confirmation(self, section_name):
        try:
            current_view = self.sections[section_name].get("current_view", "table")
            new_view = "البطاقات" if current_view == "table" else "الجدول"

            reply = QMessageBox.question(
                self,
                "تغيير العرض",
                f"هل تريد تغيير عرض قسم {section_name} إلى {new_view}؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.toggle_view(section_name)
                QMessageBox.information(
                    self,
                    "تم التغيير",
                    f"تم تغيير عرض قسم {section_name} إلى {new_view} بنجاح"
                )
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تغيير العرض: {str(e)}")

    # تبديل عرض القسم وتحديث نص الزر
    # تبديل القسم عرض وتحديث زر التحديث
    # تبديل القسم عرض وتحديث زر التحديث
    def toggle_section_view_and_update_button(self, section_name):
        try:
            # تبديل العرض
            self.toggle_view(section_name)

            # تحديث نص الزر
            self.update_section_toggle_button(section_name)

        except Exception as e:
            print(f"خطأ في تبديل العرض وتحديث الزر للقسم {section_name}: {e}")

    # تحديث نص زر التبديل لقسم محدد
    # زر التحديث زر تبديل
    # زر التحديث زر تبديل
    def update_section_toggle_button(self, section_name):
        try:
            # معالجة خاصة للصفحة الرئيسية - لا تحتوي على زر تبديل
            if section_name == "الرئيسية":
                return
                
            section_info = self.sections.get(section_name)
            if not section_info:
                return

            view_toggle_btn = section_info.get("view_toggle_btn")
            if not view_toggle_btn:
                return

            # التحقق من أن كائن QPushButton لم يحذف قبل الوصول إليه
            try:
                # اختبار بسيط للتحقق من وجود الكائن
                if not hasattr(view_toggle_btn, 'setText'):
                    return

                current_view = section_info.get("current_view", "table")

                if current_view == "cards":
                    view_toggle_btn.setText("📊 جدول")
                    view_toggle_btn.setToolTip(f"التبديل إلى عرض الجدول لقسم {section_name}")
                else:
                    view_toggle_btn.setText("🎴 بطاقات")
                    view_toggle_btn.setToolTip(f"التبديل إلى عرض البطاقات لقسم {section_name}")
                    
            except RuntimeError as e:
                # التحقق من كون الخطأ بسبب حذف الكائن
                if "Internal C++ object" in str(e) and "already deleted" in str(e):
                    # print(f"تحذير: كائن view_toggle_btn محذوف للقسم {section_name}")
                    return  # خروج بصمت
                else:
                    raise  # إعادة رفع الخطأ إذا لم يكن بسبب حذف الكائن

        except Exception as e:
            print(f"خطأ في تحديث زر التبديل للقسم {section_name}: {e}")

    # تحديث نصوص جميع أزرار التبديل
    # قم بتحديث جميع أزرار تبديل القسم
    # قم بتحديث جميع أزرار تبديل القسم
    def update_all_section_toggle_buttons(self):
        for section_name in self.sections.keys():
            self.update_section_toggle_button(section_name)

    # معالجة حدث تغيير السنة في ComboBox للصفحة المحددة
    # تغيير سنة
    # تغيير سنة
    def change_year(self, index, section_name):
        section_info = self.sections.get(section_name)
        if not section_info:
             print(f"Section info not found for {section_name}")
             return

        selected_year = section_info["year_combo"].currentText()

        # Clear search and reset filter when year changes
        section_info["search_input"].clear()
        if "filter_combo" in section_info and section_info["filter_combo"].count() > 0:
            # تحديد النص الصحيح حسب نوع القسم
            if section_name in ["المشاريع",  "التدريب"]:
                section_info["filter_combo"].setCurrentText("كل الحالات")
            else:
                section_info["filter_combo"].setCurrentText("كل التصنيفات")

        # Reset classification filter for real estate section
        if "classification_filter_combo" in section_info and section_info["classification_filter_combo"].count() > 0:
            section_info["classification_filter_combo"].setCurrentText("كل التصنيفات")

        # Reset job filter for employees section
        if "job_filter_combo" in section_info and section_info["job_filter_combo"].count() > 0:
            section_info["job_filter_combo"].setCurrentText("كل الوظائف")

        # Reset responsible filter for projects and contracting sections
        if "responsible_filter_combo" in section_info and section_info["responsible_filter_combo"].count() > 0:
            section_info["responsible_filter_combo"].setCurrentText("كل المسؤولين")

        # إعادة تعبئة فلتر الوظيفة للسنة الجديدة
        if "job_filter_combo" in section_info and section_info["job_filter_combo"] is not None:
            job_filter_combo = section_info["job_filter_combo"]
            job_filter_combo.clear()
            self.populate_job_filter(job_filter_combo, section_name)

        # إعادة تحميل بيانات وإحصائيات القسم الحالي للسنة الجديدة
        # _load_data_from_db will now handle filtering based on the reset combo
        self._load_data_from_db(section_info["table"], section_name)
        self._update_stats(section_info["stats"], section_name, selected_year)

        # تحديث عرض البطاقات مع الفلاتر الموحدة
        if hasattr(self, 'update_cards_view'):
            self.update_cards_view(section_name)

        # تطبيق الفلاتر الموحدة بعد تغيير السنة
        self.apply_unified_filters_to_section(section_name)

    # الحصول على بيانات القسم لعرضها في البطاقات العصرية
    # احصل على بيانات القسم للبطاقات
    def get_section_data_for_cards(self, section_name):
        try:
            # الحصول على اسم الجدول من القسم
            table_name = self.get_db_table_name(section_name)
            if not table_name:
                return []
                
            # الاتصال بقاعدة البيانات
            conn = self.get_db_connection()
            if conn is None:
                return []
                
            cursor = conn.cursor(dictionary=True)
            
            # استعلام البيانات حسب نوع القسم
            if section_name == "المشاريع":
                query = """
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM المشاريع p
                    LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                    LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المشاريع'
                    ORDER BY p.تاريخ_الإضافة DESC
                """
                cursor.execute(query)
                data_list = cursor.fetchall()

            elif section_name == "المقاولات":
                query = """
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM المشاريع p
                    LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                    LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المقاولات'
                    ORDER BY p.تاريخ_الإضافة DESC
                """
                cursor.execute(query)
                data_list = cursor.fetchall()

                # حساب الوقت المتبقي لكل مشروع
                for data in data_list:
                    if data.get('تاريخ_التسليم'):
                        try:
                            from datetime import datetime
                            end_date = datetime.strptime(str(data['تاريخ_التسليم']), '%Y-%m-%d')
                            today = datetime.now()
                            remaining_days = (end_date - today).days
                            if remaining_days > 0:
                                data['الوقت_المتبقي_محسوب'] = f"{remaining_days} يوم متبقي"
                            elif remaining_days == 0:
                                data['الوقت_المتبقي_محسوب'] = "ينتهي اليوم"
                            else:
                                data['الوقت_المتبقي_محسوب'] = f"متأخر بـ {abs(remaining_days)} يوم"
                        except:
                            data['الوقت_المتبقي_محسوب'] = "غير محدد"
                    else:
                        data['الوقت_المتبقي_محسوب'] = "غير محدد"

            elif section_name == "المقاولات":
                query = """
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM المشاريع p
                    LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                    LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المقاولات'
                    ORDER BY p.تاريخ_الإضافة DESC
                """
                cursor.execute(query)
                data_list = cursor.fetchall()

                # حساب الوقت المتبقي لكل مقاولات
                for data in data_list:
                    if data.get('تاريخ_التسليم'):
                        try:
                            from datetime import datetime
                            end_date = datetime.strptime(str(data['تاريخ_التسليم']), '%Y-%m-%d')
                            today = datetime.now()
                            remaining_days = (end_date - today).days
                            if remaining_days > 0:
                                data['الوقت_المتبقي_محسوب'] = f"{remaining_days} يوم متبقي"
                            elif remaining_days == 0:
                                data['الوقت_المتبقي_محسوب'] = "ينتهي اليوم"
                            else:
                                data['الوقت_المتبقي_محسوب'] = f"متأخر بـ {abs(remaining_days)} يوم"
                        except:
                            data['الوقت_المتبقي_محسوب'] = "غير محدد"
                    else:
                        data['الوقت_المتبقي_محسوب'] = "غير محدد"
                    
            elif section_name == "العملاء":
                query = """
                    SELECT c.*,
                           COUNT(p.id) as عدد_المشاريع,
                           COALESCE(SUM(p.المبلغ), 0) as إجمالي_القيمة,
                           COALESCE(SUM(p.المدفوع), 0) as إجمالي_المدفوع,
                           COALESCE(SUM(p.الباقي), 0) as إجمالي_الباقي
                    FROM العملاء c
                    LEFT JOIN المشاريع p ON c.id = p.معرف_العميل
                    GROUP BY c.id
                    ORDER BY c.اسم_العميل
                """
                cursor.execute(query)
                data_list = cursor.fetchall()
                
            elif section_name == "الموظفين":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY اسم_الموظف")
                data_list = cursor.fetchall()
                
            elif section_name == "الحسابات":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_المصروف DESC")
                data_list = cursor.fetchall()
                
            elif section_name == "المصروفات":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_المصروف DESC")
                data_list = cursor.fetchall()
                
            
                
            elif section_name == "التدريب":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_البدء DESC")
                data_list = cursor.fetchall()
            
            elif section_name == "الموردين":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_الإنشاء DESC")
                data_list = cursor.fetchall()
                
            else:
                # للأقسام الأخرى
                cursor.execute(f"SELECT * FROM `{table_name}`")
                data_list = cursor.fetchall()
                
            cursor.close()
            conn.close()
            return data_list
            
        except Exception as e:
            print(f"خطأ في الحصول على بيانات القسم {section_name}: {e}")
            return []

    # البحث في البيانات
    # بيانات البحث
    # بيانات البحث
    def search_data(self, text, section_name):
        search_data(self, text, section_name)

    # تعبئة فلتر التصنيف تلقائياً من قاعدة البيانات
    # ملء تصفية التصنيف
    # ملء تصفية التصنيف
    def populate_classification_filter(self, combo_box, section_name):
        try:
            # معالجة خاصة لقسم التقارير المالية
            if section_name == "التقارير":
                combo_box.addItems(["كل التصنيفات", "تقارير مالية", "تقارير إدارية", "تقارير تشغيلية"])
                return

            # الحصول على السنة الحالية

            conn = self.get_db_connection()
            if conn is None:
                combo_box.addItem("كل التصنيفات")
                return

            cursor = conn.cursor()

            # جلب التصنيفات الفريدة من الجدول
            db_table_name = self.get_db_table_name(section_name)
            cursor.execute(f"SELECT DISTINCT `التصنيف` FROM `{db_table_name}` WHERE `التصنيف` IS NOT NULL AND `التصنيف` != '' ORDER BY `التصنيف`")
            classifications = cursor.fetchall()

            # إضافة الخيار الافتراضي
            combo_box.addItem("كل التصنيفات")

            # إضافة التصنيفات المجلبة من قاعدة البيانات
            for (classification,) in classifications:
                combo_box.addItem(classification)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تعبئة فلتر التصنيف: {e}")
            combo_box.addItem("كل التصنيفات")

    # تعبئة فلتر الحالة تلقائياً من قاعدة البيانات أو استخدام القيم الافتراضية
    # ملء مرشح الحالة
    # ملء مرشح الحالة
    def populate_status_filter(self, combo_box, section_name):
        try:
            if section_name == "الرئيسية":
                return

            # معالجة خاصة لقسم التقارير المالية
            if section_name == "التقارير":
                combo_box.addItems(["كل التقارير", "التقارير المالية", "تقارير المشاريع", "تقارير الموظفين"])
                return

            # الحصول على السنة الحالية

            conn = self.get_db_connection()

            if conn is not None:
                cursor = conn.cursor()

                # تحديد العامود المناسب حسب نوع القسم
                if section_name in ["المشاريع", "المقاولات", "التدريب"]:
                    column_name = "الحالة"
                    default_text = "كل الحالات"
                elif section_name == "الموظفين":
                    # للموظفين، نستخدم عمود الحالة مع القيم الافتراضية للـ ENUM
                    column_name = "الحالة"
                    default_text = "كل الحالات"
                elif section_name == "الموردين":
                    column_name = "التصنيف"
                    default_text = "كل التصنيفات"
                else:
                    column_name = "التصنيف"
                    default_text = "كل التصنيفات"

                # جلب القيم الفريدة من الجدول
                db_table_name = self.get_db_table_name(section_name)

                # للموظفين، نستخدم القيم الافتراضية للـ ENUM بدلاً من الاستعلام
                if section_name == "الموظفين":
                    combo_box.addItem(default_text)
                    # إضافة قيم ENUM للموظفين
                    status_values = ['نشط', 'غير نشط', 'إجازة', 'مستقيل', 'تم فصله']
                    for status in status_values:
                        combo_box.addItem(status)
                else:
                    cursor.execute(f"SELECT DISTINCT `{column_name}` FROM `{db_table_name}` WHERE `{column_name}` IS NOT NULL AND `{column_name}` != '' ORDER BY `{column_name}`")
                    values = cursor.fetchall()

                    # إضافة الخيار الافتراضي
                    combo_box.addItem(default_text)

                    # إضافة القيم المجلبة من قاعدة البيانات
                    for (value,) in values:
                        combo_box.addItem(value)

                cursor.close()
                conn.close()

            else:
                # في حالة عدم وجود اتصال بقاعدة البيانات، استخدم القيم الافتراضية
                self._add_default_status_items(combo_box, section_name)

        except Exception as e:
            print(f"خطأ في تعبئة فلتر الحالة: {e}")
            # في حالة حدوث خطأ، استخدم القيم الافتراضية
            self._add_default_status_items(combo_box, section_name)

    # إضافة عناصر الحالة الافتراضية
    # إضافة عناصر الحالة الافتراضية
    # إضافة عناصر الحالة الافتراضية
    def _add_default_status_items(self, combo_box, section_name):
        if section_name == "المشاريع":
            combo_box.addItems(["كل الحالات", "قيد الإنجاز", "منتهي", "غير خالص", "غير مكتمل"])
        elif section_name == "المقاولات":
            combo_box.addItems(["كل الحالات", "قيد الإنجاز", "منتهي", "غير خالص", "غير مكتمل"])
        elif section_name == "العملاء":
            combo_box.addItems(["كل التصنيفات", "شريك", "عميل"])
        elif section_name == "الحسابات":
            combo_box.addItems(["كل التصنيفات", "مصاريف", "مبيعات", "أخرى"])
        elif section_name == "الموظفين":
            # للموظفين، نستخدم قيم الحالة من ENUM
            combo_box.addItems(["كل الحالات", "نشط", "غير نشط", "إجازة", "مستقيل", "تم فصله"])
        elif section_name == "التدريب":
            combo_box.addItems(["كل الحالات", "قيد التسجيل", "جارية", "منتهية", "ملغية"])
        elif section_name == "الموردين":
            combo_box.addItems(["كل الحالات", "قيد الإنجاز", "منتهي", "غير خالص", "غير مكتمل"])
        else:
            combo_box.addItem("كل الحالات")

    # تعبئة فلتر الوظيفة تلقائياً من قاعدة البيانات
    # ملء مرشح الوظائف
    # ملء مرشح الوظائف
    def populate_job_filter(self, combo_box, section_name):
        try:
            # الحصول على السنة المختارة من الفلتر
            section_info = self.sections.get(section_name)
            
            conn = self.get_db_connection()
            if conn is None:
                combo_box.addItem("كل الوظائف")
                return

            cursor = conn.cursor()

            # جلب الوظائف المختلفة من جدول الموظفين
            if section_name == "الموظفين":
                cursor.execute("""
                    SELECT DISTINCT الوظيفة
                    FROM الموظفين
                    WHERE الوظيفة IS NOT NULL AND الوظيفة != ''
                    ORDER BY الوظيفة
                """)
                jobs = cursor.fetchall()

                # إضافة الخيار الافتراضي
                combo_box.addItem("كل الوظائف")

                # إضافة الوظائف المجلبة من قاعدة البيانات
                for (job_name,) in jobs:
                    combo_box.addItem(job_name)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تعبئة فلتر الوظيفة: {e}")
            combo_box.addItem("كل الوظائف")

    # تعبئة فلتر المسؤول تلقائياً من قاعدة البيانات
    # تملأ مرشح المسؤول
    # تملأ مرشح المسؤول
    def populate_responsible_filter(self, combo_box, section_name):
        try:
            # الحصول على السنة الحالية
            conn = self.get_db_connection()
            if conn is None:
                combo_box.addItem("كل المسؤولين")
                return

            cursor = conn.cursor()

            # جلب المهندسين المسؤولين من جدول المشاريع
            if section_name in ["المشاريع", "المقاولات"]:
                cursor.execute("""
                    SELECT DISTINCT e.اسم_الموظف
                    FROM المشاريع p
                    LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = %s AND e.اسم_الموظف IS NOT NULL AND e.اسم_الموظف != ''
                    ORDER BY e.اسم_الموظف
                """, (section_name,))
                responsible_engineers = cursor.fetchall()

                # إضافة الخيار الافتراضي
                combo_box.addItem("كل المسؤولين")

                # إضافة المهندسين المجلبين من قاعدة البيانات
                for (engineer_name,) in responsible_engineers:
                    combo_box.addItem(engineer_name)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"خطأ في تعبئة فلتر المسؤول: {e}")
            combo_box.addItem("كل المسؤولين")

    # يطبق المرشح بناءً على الحالة لأقسام محددة مع تصفية موحدة.
    # جدول المرشح
    def filter_table(self, section_name, status_text):
        section_info = self.sections.get(section_name)
        if not section_info:
            return

        current_table = section_info["table"]
        selected_year = section_info["year_combo"].currentText()

        # معالجة خاصة للأقسام التي لا تستخدم جدول تقليدي
        if current_table is None:
            print(f"⚠️ القسم '{section_name}' لا يستخدم جدول تقليدي - تخطي إعادة تحميل البيانات")
            # تطبيق الفلاتر الموحدة فقط
            self.apply_unified_filters_to_section(section_name)
            return

        # إعادة تحميل البيانات مع الفلاتر للأقسام التي تستخدم جدول
        self._load_data_from_db(current_table, section_name)

        # تطبيق البحث الحالي
        current_search_text = section_info["search_input"].text()
        self.search_data(current_search_text, section_name)

        # تطبيق الفلاتر الموحدة على البطاقات
        self.apply_unified_filters_to_section(section_name)

    # يطبق المرشح بناءً على التصنيف لأقسام محددة مع تصفية موحدة.
    # جدول المرشح عن طريق التصنيف
    def filter_table_by_classification(self, section_name, classification_text):
        section_info = self.sections.get(section_name)
        if not section_info:
            return

        current_table = section_info["table"]
        selected_year = section_info["year_combo"].currentText()

        # معالجة خاصة للأقسام التي لا تستخدم جدول تقليدي
        if current_table is None:
            print(f"⚠️ القسم '{section_name}' لا يستخدم جدول تقليدي - تخطي إعادة تحميل البيانات")
            # تطبيق الفلاتر الموحدة فقط
            self.apply_unified_filters_to_section(section_name)
            return

        # إعادة تحميل البيانات مع الفلاتر للأقسام التي تستخدم جدول
        self._load_data_from_db(current_table, section_name)

        # تطبيق البحث الحالي
        current_search_text = section_info["search_input"].text()
        self.search_data(current_search_text, section_name)

        # تطبيق الفلاتر الموحدة على البطاقات
        self.apply_unified_filters_to_section(section_name)

    # يطبق المرشح بناءً على مهندس مسؤول لأقسام محددة مع تصفية موحدة.
    # جدول التصفية عن طريق المسؤول
    def filter_table_by_responsible(self, section_name, responsible_text):
        section_info = self.sections.get(section_name)
        if not section_info:
            return

        current_table = section_info["table"]
        selected_year = section_info["year_combo"].currentText()

        # معالجة خاصة للأقسام التي لا تستخدم جدول تقليدي
        if current_table is None:
            print(f"⚠️ القسم '{section_name}' لا يستخدم جدول تقليدي - تخطي إعادة تحميل البيانات")
            # تطبيق الفلاتر الموحدة فقط
            self.apply_unified_filters_to_section(section_name)
            return

        # إعادة تحميل البيانات مع الفلاتر للأقسام التي تستخدم جدول
        self._load_data_from_db(current_table, section_name)

        # تطبيق البحث الحالي
        current_search_text = section_info["search_input"].text()
        self.search_data(current_search_text, section_name)

        # تطبيق الفلاتر الموحدة على البطاقات
        self.apply_unified_filters_to_section(section_name)

    # يطبق التصفية بناءً على قسم الوظيفة للموظفين مع تصفية موحدة.
    # جدول التصفية عن طريق الوظيفة
    def filter_table_by_job(self, section_name, job_text):
        section_info = self.sections.get(section_name)
        if not section_info:
            return

        table = section_info["table"]
        # معالجة خاصة للأقسام التي لا تستخدم جدول تقليدي
        if table is None:
            print(f"⚠️ القسم '{section_name}' لا يستخدم جدول تقليدي - تطبيق الفلاتر الموحدة فقط")
            # تطبيق الفلاتر الموحدة فقط
            self.apply_unified_filters_to_section(section_name)
            return

        # تطبيق الفلاتر الموحدة على الجدول والبطاقات للأقسام التي تستخدم جدول
        self.apply_unified_filters_to_section(section_name)

    # تطبيق الفلاتر الموحدة على القسم المحدد
    # تطبيق المرشحات الموحدة على القسم
    def apply_unified_filters_to_section(self, section_name):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                return

            current_view = section_info.get("current_view", "table")

            # جمع الفلاتر الحالية
            search_text = section_info.get("search_input", "").text() if section_info.get("search_input") else ""

            classification_filter = ""
            if section_info.get("classification_filter_combo"):
                classification_filter = section_info["classification_filter_combo"].currentText()

            status_filter = ""
            if section_info.get("filter_combo"):
                status_filter = section_info["filter_combo"].currentText()

            job_filter = ""
            if section_info.get("job_filter_combo"):
                job_filter = section_info["job_filter_combo"].currentText()

            responsible_filter = ""
            if section_info.get("responsible_filter_combo"):
                responsible_filter = section_info["responsible_filter_combo"].currentText()

            year_filter = ""
            if section_info.get("year_combo"):
                year_filter = section_info["year_combo"].currentText()

            # تطبيق الفلاتر على الجدول أولاً
            self._apply_filters_to_table(section_name, classification_filter, status_filter, job_filter, responsible_filter, search_text)

            # تطبيق الفلاتر على البطاقات إذا كانت نشطة
            if current_view == "cards":
                view_stack = section_info.get("view_stack")
                if view_stack and view_stack.count() > 1:
                    cards_view = view_stack.widget(1)
                    if hasattr(cards_view, 'apply_unified_filters'):
                        # تمرير جميع الفلاتر بما في ذلك فلتر الوظيفة
                        cards_view.apply_unified_filters(
                            search_text=search_text,
                            classification_filter=classification_filter,
                            status_filter=status_filter,
                            job_filter=job_filter,
                            year_filter=year_filter
                        )

        except Exception as e:
            print(f"خطأ في تطبيق الفلاتر الموحدة: {e}")

    # تطبيق الفلاتر على الجدول
    # تطبيق المرشحات على الجدول
    def _apply_filters_to_table(self, section_name, classification_filter, status_filter, job_filter, responsible_filter, search_text):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                return

            table = section_info["table"]
            if not table:
                return

            # إخفاء جميع الصفوف أولاً
            for row in range(table.rowCount()):
                table.setRowHidden(row, True)

            # تطبيق الفلاتر على كل صف
            for row in range(table.rowCount()):
                show_row = True

                # فلتر البحث
                if search_text:
                    row_matches_search = False
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        if item and search_text.lower() in item.text().lower():
                            row_matches_search = True
                            break
                    if not row_matches_search:
                        show_row = False

                # فلتر التصنيف
                if show_row and classification_filter and classification_filter != "كل التصنيفات":
                    classification_col = self._get_column_index(table, "التصنيف")
                    if classification_col >= 0:
                        item = table.item(row, classification_col)
                        if not item or item.text() != classification_filter:
                            show_row = False

                # فلتر الحالة
                if show_row and status_filter and status_filter != "كل الحالات":
                    status_col = self._get_column_index(table, "الحالة")
                    if status_col >= 0:
                        item = table.item(row, status_col)
                        if not item or item.text() != status_filter:
                            show_row = False

                # فلتر الوظيفة (للموظفين فقط)
                if show_row and job_filter and job_filter != "كل الوظائف" and section_name == "الموظفين":
                    job_col = self._get_column_index(table, "الوظيفة")
                    if job_col >= 0:
                        item = table.item(row, job_col)
                        if not item or item.text() != job_filter:
                            show_row = False

                # فلتر المسؤول (للمشاريع والمقاولات فقط)
                if show_row and responsible_filter and responsible_filter != "كل المسؤولين" and section_name in ["المشاريع", "المقاولات"]:
                    responsible_col = self._get_column_index(table, "المهندس المسؤول")
                    if responsible_col >= 0:
                        item = table.item(row, responsible_col)
                        if not item or item.text() != responsible_filter:
                            show_row = False

                # إظهار أو إخفاء الصف
                table.setRowHidden(row, not show_row)

        except Exception as e:
            print(f"خطأ في تطبيق الفلاتر على الجدول: {e}")

    # الحصول على فهرس العمود بالاسم
    # الحصول على فهرس العمود
    def _get_column_index(self, table, column_name):
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == column_name:
                return col
        return -1

    # مزامنة البحث عبر جميع أنماط العرض
    # Sync Search عبر طرق العرض
    def sync_search_across_views(self, section_name, search_text):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                return

            # تطبيق البحث على الجدول
            self.search_data(search_text, section_name)

            # تطبيق البحث على البطاقات
            current_view = section_info.get("current_view", "table")
            if current_view == "cards":
                view_stack = section_info.get("view_stack")
                if view_stack and view_stack.count() > 1:
                    cards_view = view_stack.widget(1)
                    if hasattr(cards_view, 'search_input'):
                        # تحديث نص البحث في البطاقات
                        cards_view.search_input.setText(search_text)
                        # تطبيق الفلتر
                        if hasattr(cards_view, 'filter_cards'):
                            cards_view.filter_cards()

        except Exception as e:
            print(f"خطأ في مزامنة البحث: {e}")

    #حفظ الاضافة
    # حفظ الدخول
    # حفظ الدخول
    def save_entry(self, section_name, data):
        save_entry(self, section_name, data)

    # تحديث الإدخال
    # تحديث الإدخال
    def update_entry(self, section_name, row_id, data):
        # الحصول على السنة الحالية
        from PySide6.QtCore import QDate
        current_year = str(QDate.currentDate().year())
        update_entry(self, section_name, current_year, row_id, data)

    # حذف الصفوف
    # حذف الصفوف المختارة
    # حذف الصفوف المختارة
    def _delete_selected_rows(self, table, section_name, year, selected_rows):
        delete_selected_rows(self, table, section_name, year, selected_rows)

    # معالج الإضافة والطباعة وحذف الأزرار المحددة للقسم الحالي.
    # التعامل مع زر الإجراء
    def handle_action_button(self, action_type, section_name, card_data=None):

        section_info = self.sections.get(section_name)
        if not section_info:
             print(f"Section info not found for {section_name} during action {action_type}")
             return

        
        current_table = section_info["table"]

        if action_type == "اضافة":
            open_add_entry_dialog(self, section_name)

        elif action_type == "تعديل":
            if card_data:
                # تعديل من البطاقة - استخدم البيانات المرسلة
              pass
            else:
                # تعديل من الجدول - استخدم الصف المحدد
                selected_rows = [item.row() for item in current_table.selectedItems()]
                if not selected_rows:
                    QMessageBox.warning(self, "لا يوجد اختيار", "الرجاء اختيار صف للتعديل.")
                    return
                # الحصول على بيانات الصف المحدد
                row_data = self.get_selected_row_data(current_table, selected_rows[0], section_name)
                if row_data:
                    pass

        elif action_type == "طباعة":
            # فتح نافذة الطباعة والتصدير المتقدمة
            try:
                open_print_export_dialog(current_table, section_name, self)
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة الطباعة والتصدير:\n{str(e)}")
                # في حالة الفشل، عرض رسالة بديلة
                QMessageBox.information(self, "طباعة", f"سيتم طباعة تقرير لـ {section_name}.")

        elif action_type == "حذف":
            if card_data:
                # حذف من البطاقة - استخدم البيانات المرسلة
                self.delete_single_item(section_name, card_data)
            else:
                # حذف من الجدول - استخدم الصفوف المحددة
                selected_rows = sorted(list(set([item.row() for item in current_table.selectedItems()])))
                if not selected_rows:
                     QMessageBox.warning(self, "لا يوجد اختيار", "الرجاء اختيار الصفوف التي تريد حذفها.")
                     return
                reply = QMessageBox.question(self, "تأكيد الحذف",
                                             f"هل أنت متأكد من حذف {len(selected_rows)} صفوف مختارة من {section_name}؟",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self._delete_selected_rows(current_table, section_name, current_year, selected_rows)
            # تحديث عرض البطاقات بعد الحذف
            if hasattr(self, 'update_cards_view'):
                self.update_cards_view(section_name)

    # الحصول على بيانات الصف المحدد من الجدول
    # احصل على بيانات صف محددة
    def get_selected_row_data(self, table, row_index, section_name):
        try:
            selected_row_values = []
            for col in range(table.columnCount()):
                item = table.item(row_index, col)
                if item:
                    selected_row_values.append(item.data(Qt.UserRole))
                else:
                    selected_row_values.append(None)

            # الحصول على أسماء الأعمدة
            column_keys = [col["key"] for col in TABLE_COLUMNS.get(section_name, [])]

            if len(column_keys) == len(selected_row_values):
                return dict(zip(column_keys, selected_row_values))
            else:
                return None
        except Exception as e:
            print(f"خطأ في الحصول على بيانات الصف: {e}")
            return None

    # حذف عنصر واحد من قاعدة البيانات
    # حذف عنصر واحد
    def delete_single_item(self, section_name, data):
        try:
            item_id = data.get('id')
            if not item_id:
                QMessageBox.warning(self, "خطأ", "معرف العنصر غير متوفر")
                return

            # تحديد نوع العنصر للرسالة
            item_type = "العنصر"
            item_name = ""
            if section_name == "العملاء":
                item_type = "العميل"
                item_name = data.get('اسم_العميل', '')
            elif section_name == "الموظفين":
                item_type = "الموظف"
                item_name = data.get('اسم_الموظف', '')
            elif section_name == "الحسابات":
                item_type = "الحساب"
                item_name = data.get('وصف_المصروف', '')
            elif section_name == "التدريب":
                item_type = "الدورة التدريبية"
                item_name = data.get('اسم_الدورة', '')
            elif section_name == "الموردين":
                item_type = "المورد"
                item_name = data.get('اسم_المورد', '')
            elif section_name in ["المشاريع", "المقاولات"]:
                item_type = "المشروع"
                item_name = data.get('اسم_المشروع', '')

            # رسالة التأكيد
            message = f"هل أنت متأكد من حذف {item_type}"
            if item_name:
                message += f":\n{item_name}"
            message += "؟\n\nهذا الإجراء لا يمكن التراجع عنه."

            reply = QMessageBox.question(
                self, "تأكيد الحذف", message,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # حذف من قاعدة البيانات
                conn = self.get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    table_name = self.get_db_table_name(section_name)

                    cursor.execute(f"DELETE FROM `{table_name}` WHERE id = %s", (item_id,))
                    conn.commit()

                    if cursor.rowcount > 0:
                        QMessageBox.information(self, "تم الحذف", f"تم حذف {item_type} بنجاح")
                        # تحديث الجدول
                        self.show_section(section_name)
                    else:
                        QMessageBox.warning(self, "خطأ", "لم يتم العثور على العنصر للحذف")

                    cursor.close()
                    conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حذف العنصر: {str(e)}")

    #توضيف ازرار الواجهات
    # يرسل الإجراءات المخصصة بناءً على القسم واسم الإجراء.
    # التعامل مع الإجراء المخصص
    def handle_custom_action(self, action_name, section_name):

        section_info = self.sections.get(section_name)
        if not section_info:
             print(f"Section info not found for {section_name} during custom action {action_name}")
             return

        current_year = section_info["year_combo"].currentText()
        current_table = section_info["table"]

        # Special handling for financial reports section which doesn't use traditional table
        if section_name == "التقارير" and current_table is None:
            self.handle_financial_reports_action(action_name, section_name)
            return

        selected_items = current_table.selectedItems()
        selected_row_data = None # Data of the first selected row (as a dict)

        if selected_items:
            # Get data from the first selected row (assuming action applies to a single row)
            first_selected_row = selected_items[0].row()

            # Check if this is the "No data" row
            if current_table.rowCount() == 1 and current_table.item(0, 0) and current_table.item(0, 0).flags() == Qt.NoItemFlags:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار صف بيانات صالح.")
                 return

            # Retrieve the data from the UserRole for the selected row
            selected_row_values = []
            for col in range(current_table.columnCount()):
                 item = current_table.item(first_selected_row, col)
                 if item:
                      selected_row_values.append(item.data(Qt.UserRole))
                 else:
                      selected_row_values.append(None) # Append None for empty cells

            # Get column names from the setup (these should match DB names)
            #column_names = TABLE_COLUMNS.get(section_name, [])
            column_keys = [col["key"] for col in TABLE_COLUMNS.get(section_name, [])]

            #if len(column_names) == len(selected_row_values):
            if len(column_keys) == len(selected_row_values):
                 #selected_row_dict = dict(zip(column_names, selected_row_values))
                 selected_row_dict = dict(zip(column_keys, selected_row_values))
                 # print(f"Selected Row Data: {selected_row_dict}")
                 selected_row_data = selected_row_dict # Store as dict
            else:
                 print(f"Warning: Column count mismatch for section {section_name}. Cannot create row dict.")
                 # Fallback: pass just the list of values
                 selected_row_data = selected_row_values

        # Dispatch based on section name and action name
        if section_name == "المشاريع":
            self.handle_project_action(action_name, section_name, current_year, current_table, selected_row_data)
        elif section_name == "المقاولات":
            self.handle_contracting_action(action_name, section_name, current_year, current_table, selected_row_data)
        elif section_name == "العملاء":
            self.handle_client_action(action_name, section_name, current_year, current_table, selected_row_data)
        elif section_name == "الموظفين":
             self.handle_employee_action(action_name, section_name, current_year, current_table, selected_row_data)
        elif section_name == "الحسابات":
             self.handle_expense_action(action_name, section_name, current_year, current_table, selected_row_data)

        
        elif section_name == "التدريب":
             self.handle_training_action(action_name, section_name, current_year, current_table, selected_row_data)

        elif section_name == "الموردين":
             self.handle_supplier_action(action_name, section_name, current_year, current_table, selected_row_data)

        elif section_name == "التقارير":
             self.handle_financial_reports_action(action_name, section_name)
        else:
            QMessageBox.information(self, "إجراء مخصص",
                                     f"الإجراء المخصص '{action_name}' في قسم {section_name} غير مطبق بعد.")

    # معالجة إجراءات قسم التقارير المالية
    # التعامل مع الإجراءات التقارير المالية
    def handle_financial_reports_action(self, action_name, section_name):
        try:
            # الأزرار المحاسبية التي تستدعي النظام المحاسبي المتكامل
            accounting_actions = [
                "شجرة_الحسابات", "القيود_المحاسبية", "ربط_المعاملات",
                "قائمة_الدخل", "الميزانية_العمومية", "التدفقات_النقدية",
                "إعدادات_النظام"
            ]

            if action_name in accounting_actions:
                # استدعاء معالج الأزرار المحاسبية المتكامل
                from معالج_أزرار_التقارير_المالية import handle_financial_custom_action
                handle_financial_custom_action(self, action_name, section_name)

            elif action_name == "إضافة":
                # فتح النافذة المتقدمة للتقارير المالية (الوظيفة القديمة)
                from التقارير_المالية import open_financial_reports_window
                window = open_financial_reports_window(self)
                if window:
                    window.show()

            elif action_name == "تحديث":
                # تحديث بيانات التقارير المالية
                section_info = self.sections.get(section_name)
                if section_info and "page" in section_info:
                    # البحث عن ويدجت التقارير المالية في الصفحة
                    page = section_info["page"]
                    for child in page.findChildren(QWidget):
                        if hasattr(child, 'refresh_data'):
                            child.refresh_data()
                            break
                QMessageBox.information(self, "تحديث", "تم تحديث بيانات التقارير المالية")

            elif action_name == "طباعة":
                # فتح نافذة الطباعة
                from PrintManager import PrintManager
                print_manager = PrintManager(self, "التقارير المالية", [], [])
                print_manager.show()

            else:
                QMessageBox.information(self, "إجراء غير مدعوم",
                                      f"الإجراء '{action_name}' غير مدعوم في قسم التقارير المالية")

        except Exception as e:
            print(f"خطأ في معالجة إجراء التقارير المالية: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تنفيذ الإجراء '{action_name}':\n{str(e)}")

    # تحديث الإحصائيات المالية
    # تحديث الإحصائيات المالية
    def update_financial_stats(self, section_info):
        try:
            from محتوى_التقارير_المالية import get_financial_stats_data
            stats_data = get_financial_stats_data()

            if "stats" in section_info and section_info["stats"]:
                stat_names = list(section_info["stats"].keys())

                for i, (title, value, color, icon) in enumerate(stats_data):
                    if i < len(stat_names):
                        stat_name = stat_names[i]
                        if stat_name in section_info["stats"]:
                            section_info["stats"][stat_name].update_value(value)

        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات المالية: {e}")

    # التعامل مع عمل المشروع
    # التعامل مع عمل المشروع
    def handle_project_action(self, action, section, year, table, selected_row_data):
        # Ensure selected_row_data is a dict before trying to get('id')
        project_id = selected_row_data.get('id') if isinstance(selected_row_data, dict) and selected_row_data else None
        project_code = selected_row_data.get('التصنيف') if isinstance(selected_row_data, dict) and selected_row_data else "N/A"

        if action == "دفعات_المشروع":
            if project_id is None:
                QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مشروع من الجدول لعرض دفعاته.")
                return
           
           
        elif action == "حالة_المشروع":
             if project_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مشروع من الجدول لتحديث حالته.")
                 return
             # فتح نافذة حالة المشروع الجديدة
             dialog = ProjectStatusDialog(self, project_id, project_code, year, selected_row_data)
             if dialog.exec() == QDialog.Accepted:
                self.show_section("المشاريع")  # تحديث عرض البيانات
                # تحديث عرض البطاقات إذا كان نشطاً
                if hasattr(self, 'update_cards_view'):
                    self.update_cards_view("المشاريع", year)

        elif action == "تقرير_الدفعات":
             self.open_project_financial_reports(project_id, project_code)

        elif action == "إدارة_المشروع":
            if project_id is None:
                QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مشروع من الجدول لإدارته.")
                return

            # فتح نافذة إدارة المشروع الجديدة
            try:
                # تحديد نوع المشروع من البيانات المحددة
                project_type = selected_row_data.get('اسم_القسم', 'المشاريع')

                # استيراد وفتح نافذة مراحل المشروع الجديدة
                #from إدارة_المشروع import open_project_phases_window
                #from المشاريع.إدارة_المشروع import open_project_phases_window
                self.project_phases_window = open_project_phases_window(
                    self, selected_row_data, project_type
                )
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المشروع: {str(e)}")
                # في حالة الفشل، استخدم النافذة القديمة كبديل
                try:
                    #from إدارة_المشروع import open_project_management_window
                    self.project_management_window = open_project_management_window(
                        self, selected_row_data, selected_row_data.get('التصنيف', 'تصميم معماري')
                    )
                except:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المشروع: {str(e)}")

        elif action == "العهد_المالية":
            pass

        elif action == "مصروفات_المشروع":
            pass
             

        elif action == "اضافة":
             self.handle_action_button("اضافة", section) # Connect to handler

        elif action == "تعديل":
             self.handle_action_button("تعديل", section) # Connect to handler

        elif action == "طباعة":
             self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "حذف":
             self.handle_action_button("حذف", section) # Connect to handler

        else:
             QMessageBox.information(self, "إجراء مخصص", f"الإجراء المخصص '{action}' في قسم {section} غير مطبق بعد.")

    # معالجة الإجراءات من البطاقات العصرية
    # التعامل مع عمل البطاقة
    def handle_card_action(self, action, card_type, data):
        try:
            # تحديد القسم من نوع البطاقة
            section_mapping = {
                "project": "المشاريع",  # يشمل المشاريع والمقاولات
                "client": "العملاء",
                "employee": "الموظفين",
                "expense": "الحسابات",
                "training": "التدريب",
                "supplier": "الموردين"

            }
            

            section_name = section_mapping.get(card_type, "غير محدد")
            current_year = self.get_current_year()

            # للمشاريع، نحتاج للتمييز بين المشاريع والمقاولات
            if card_type == "project":
                project_type = data.get('اسم_القسم', 'المشاريع')
                if project_type == 'المقاولات':
                    section_name = "المقاولات"

            # معالجة الإجراءات المختلفة
            if action == "عرض":
                self.handle_view_from_card(section_name, data)
            elif action == "تعديل":
                self.handle_edit_from_card(section_name, data)
            elif action == "حذف":
                self.handle_delete_from_card(section_name, data, current_year)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في معالجة إجراء البطاقة: {str(e)}")

    # معالجة عرض العنصر من البطاقة
    # التعامل مع العرض من البطاقة
    def handle_view_from_card(self, section_name, data):
        try:
            if section_name in ["المشاريع", "المقاولات"]:
                # فتح نافذة مراحل المشروع الجديدة في وضع العرض للمشاريع والمقاولات فقط
                try:
                    #from إدارة_المشروع import open_project_phases_window
                    project_type = data.get('اسم_القسم', 'المشاريع')
                    self.project_phases_window = open_project_phases_window(self, data, project_type)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة المشروع: {str(e)}")
                    # في حالة الفشل، استخدم النافذة القديمة كبديل
                    try:
                        #from إدارة_المشروع import open_project_management_window
                        project_type = data.get('التصنيف', 'تصميم معماري')
                        self.project_management_window = open_project_management_window(self, data, project_type)
                    except:
                        pass
            elif section_name == "الموظفين":
                # فتح نافذة إدارة الموظف
                try:
                    from إدارة_الموظفين import open_employee_management_window
                    self.employee_management_window = open_employee_management_window(self, data)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة الموظف: {str(e)}")
                    # في حالة الفشل، عرض التفاصيل العادية
                    self.show_item_details(section_name, data)
            elif section_name == "التدريب":
                # فتح نافذة إدارة التدريب
                try:
                    from إدارة_التدريب import open_training_management_window
                    self.training_management_window = open_training_management_window(self, data)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة التدريب: {str(e)}")
                    # في حالة الفشل، عرض التفاصيل العادية
                    self.show_item_details(section_name, data)

            elif section_name == "الموردين":
                # فتح نافذة إدارة المورد
                try:
                    from إدارة_الموردين import open_supplier_management_window
                    self.supplier_management_window = open_supplier_management_window(self, data)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المورد: {str(e)}")
            else:
                # للأقسام الأخرى - عرض معلومات مفصلة
                self.show_item_details(section_name, data)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في عرض العنصر: {str(e)}")

    # معالجة تعديل العنصر من البطاقة
    # تعامل من البطاقة
    def handle_edit_from_card(self, section_name, data):
        try:
            # معالجة خاصة لكل قسم
            if section_name == "الموظفين":
                # فتح نافذة إدارة الموظف للتعديل
                try:
                    from إدارة_الموظفين import open_employee_management_window
                    self.employee_management_window = open_employee_management_window(self, data)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة الموظف: {str(e)}")
                    # في حالة الفشل، استخدم النافذة العادية
                    self.handle_action_button("تعديل", section_name, data)
            elif section_name == "التدريب":
                # فتح نافذة إدارة التدريب للتعديل
                try:
                    from إدارة_التدريب import open_training_management_window
                    self.training_management_window = open_training_management_window(self, data)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة التدريب: {str(e)}")
                    # في حالة الفشل، استخدم النافذة العادية
                    self.handle_action_button("تعديل", section_name, data)
            elif section_name == "الموردين":
                # فتح نافذة إدارة المورد للتعديل
                try:
                    from إدارة_الموردين import open_supplier_management_window
                    self.supplier_management_window = open_supplier_management_window(self, data)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المورد: {str(e)}")
                    # في حالة الفشل، استخدم النافذة العادية
                    self.handle_action_button("تعديل", section_name, data)

            elif section_name in ["المشاريع", "المقاولات"]:
                # فتح نافذة إدارة المشروع للمشاريع والمقاولات
                try:
                    #from إدارة_المشروع import open_project_phases_window
                    project_type = data.get('اسم_القسم', section_name)
                    self.project_phases_window = open_project_phases_window(self, data, project_type)
                except Exception as e:
                    QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المشروع: {str(e)}")
                    # في حالة الفشل، استخدم النافذة العادية
                    self.handle_action_button("تعديل", section_name, data)
            else:
                # للأقسام الأخرى، استخدم النافذة العادية
                self.handle_action_button("تعديل", section_name, data)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تعديل العنصر: {str(e)}")

    # معالجة حذف العنصر من البطاقة
    # التعامل مع الحذف من البطاقة
    def handle_delete_from_card(self, section_name, data, year):
        try:
            # استدعاء دالة الحذف المناسبة لكل قسم
            self.handle_action_button("حذف", section_name, data)

            # تحديث عرض البطاقات بعد الحذف
            self.refresh_cards_view(section_name, year)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حذف العنصر: {str(e)}")

    # عرض تفاصيل العنصر في نافذة منفصلة
    # إظهار تفاصيل العنصر
    def show_item_details(self, section_name, data):
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QTextEdit

            dialog = QDialog(self)
            dialog.setWindowTitle(f"تفاصيل {section_name}")
            dialog.setMinimumSize(400, 300)

            layout = QVBoxLayout(dialog)

            # منطقة التمرير
            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            # عرض البيانات
            for key, value in data.items():
                if value is not None and str(value).strip():
                    label = QLabel(f"<b>{key}:</b> {value}")
                    label.setWordWrap(True)
                    label.setStyleSheet("padding: 5px; border-bottom: 1px solid #eee;")
                    scroll_layout.addWidget(label)

            scroll.setWidget(scroll_widget)
            layout.addWidget(scroll)

            dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في عرض التفاصيل: {str(e)}")

    # تحديث عرض البطاقات بعد العمليات
    # عرض بطاقات التحديث
    def refresh_cards_view(self, section_name, year):
        try:
            # تحديث البيانات وإعادة عرض البطاقات
            if hasattr(self, 'update_cards_view'):
                self.update_cards_view(section_name, year)
        except Exception as e:
            print(f"خطأ في تحديث عرض البطاقات: {e}")

    # معالجة إجراءات قسم المقاولات
    # التعامل مع الإجراءات المتعاقدة
    def handle_contracting_action(self, action, section, year, table, selected_row_data):
        # Ensure selected_row_data is a dict before trying to get('id')
        project_id = selected_row_data.get('id') if isinstance(selected_row_data, dict) and selected_row_data else None
        project_code = selected_row_data.get('التصنيف') if isinstance(selected_row_data, dict) and selected_row_data else "N/A"

        if action == "دفعات_المشروع":
            if project_id is None:
                QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مقاولات من الجدول لعرض دفعاتها.")
            return
            

        elif action == "حالة_المشروع":
             if project_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مقاولات من الجدول لتحديث حالتها.")
                 return
             # فتح نافذة حالة المشروع الجديدة
             dialog = ProjectStatusDialog(self, project_id, project_code, year, selected_row_data)
             if dialog.exec() == QDialog.Accepted:
                self.show_section("المقاولات")  # تحديث عرض البيانات
                # تحديث عرض البطاقات إذا كان نشطاً
                if hasattr(self, 'update_cards_view'):
                    self.update_cards_view("المقاولات", year)

        elif action == "تقرير_الدفعات":
             self.open_project_financial_reports(project_id, project_code)

        elif action == "إدارة_المشروع":
            if project_id is None:
                QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مقاولات من الجدول لإدارتها.")
                return

            # فتح نافذة مراحل المشروع الجديدة للمقاولات
            try:
                # تحديد نوع المشروع من البيانات المحددة
                project_type = selected_row_data.get('اسم_القسم', 'المشاريع')

                # استيراد وفتح نافذة مراحل المشروع
                #from إدارة_المشروع import open_project_phases_window
                self.project_phases_window = open_project_phases_window(
                    self, selected_row_data, project_type
                )
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة إدارة المقاولات: {str(e)}")
                # في حالة الفشل، استخدم النافذة القديمة كبديل
                try:
                    #from إدارة_المشروع import open_project_management_window
                    self.project_management_window = open_project_management_window(
                        self, selected_row_data, selected_row_data.get('التصنيف', 'مقاولات')
                    )
                except:
                    pass

        elif action == "العهد_المالية":
            pass

        elif action == "مصروفات_المشروع":
            pass

        elif action == "اضافة":
             self.handle_action_button("اضافة", section) # Connect to handler

        elif action == "تعديل":
             self.handle_action_button("تعديل", section) # Connect to handler

        elif action == "طباعة":
             self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "حذف":
             self.handle_action_button("حذف", section) # Connect to handler

        else:
             QMessageBox.information(self, "إجراء مخصص", f"الإجراء المخصص '{action}' في قسم {section} غير مطبق بعد.")

    #وظيفة مساعدة لتحديث حالة المشروع في قاعدة البيانات.
    # وظيفة المساعد لتحديث حالة المشروع في قاعدة البيانات.
    # تحديث حالة المشروع
    def update_project_status(self, project_id, new_status, year):
        if project_id is None:
             return # Cannot update without an id

        conn = None
        cursor = None
        try:
            conn = self.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"تعذر الاتصال بقاعدة البيانات لتحديث حالة المشروع.")
                return

            cursor = conn.cursor()
            db_table_name = self.get_db_table_name("المشاريع")

            # Additional updates might be needed based on status change (e.g., set delivery date to today if status becomes "تم التسليم")
            sql = f"UPDATE `{db_table_name}` SET `الحالة` = %s WHERE `id` = %s"
            params = [new_status, project_id]

            # ملاحظة: تم إزالة المنطق القديم لتحديث حالة المشروع
            # يتم الآن استخدام نافذة حالة المشروع الجديدة (ProjectStatusDialog) لهذا الغرض


            cursor.execute(sql, params)
            conn.commit()

            if cursor.rowcount > 0:
                 QMessageBox.information(self, "نجاح", f"تم تحديث حالة المشروع رقم {project_id} إلى '{new_status}'.")
                 # Reload data for the projects section to reflect the change
                 self.show_section("المشاريع")
                 # تحديث عرض البطاقات إذا كان نشطاً
                 if hasattr(self, 'update_cards_view'):
                     self.update_cards_view("المشاريع", year)
            else:
                 QMessageBox.warning(self, "لم يتم التحديث", f"لم يتم العثور على المشروع رقم {project_id} لتحديث حالته.")

        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Error updating project status for id {project_id}: {err}")
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"حدث خطأ أثناء تحديث حالة المشروع رقم {project_id}:\n{err}")
        except Exception as e:
            conn.rollback()
            print(f"Unexpected error updating project status: {e}")
            QMessageBox.critical(self, "خطأ غير متوقع", f"حدث خطأ غير متوقع أثناء تحديث حالة المشروع رقم {project_id}:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    #ازرار العملاء
    # التعامل مع عمل العميل
    # التعامل مع عمل العميل
    def handle_client_action(self, action, section, year, table, selected_row_data):
        client_id = selected_row_data.get('id') if selected_row_data else None

        if action == "اضافة":
             self.handle_action_button("اضافة", section) # Connect to handler

        elif action == "حذف":
            self.handle_action_button("حذف", section) # Connect to handler

        elif action == "طباعة":
            self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "مشاريع_العميل":
             if client_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار عميل من الجدول لعرض مشاريعه.")
                 return
             QMessageBox.information(self, "مشاريع العميل", f"سيتم عرض مشاريع العميل رقم {client_id} في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             
        elif action == "دفعات_العميل":
             if client_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار عميل من الجدول لعرض دفعاته.")
                 return
             QMessageBox.information(self, "دفعات العميل", f"سيتم عرض دفعات العميل رقم {client_id} في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             

        elif action == "الجدول_الزمني_للعميل":
             if client_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار عميل من الجدول لعرض الجدول الزمني.")
                 return
             QMessageBox.information(self, "الجدول الزمني للعميل", f"سيتم عرض الجدول الزمني للعميل رقم {client_id} في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             
        else:
             QMessageBox.information(self, "إجراء مخصص", f"الإجراء المخصص '{action}' في قسم {section} غير مطبق بعد.")

    #ازرار الموظفين
    # التعامل مع إجراء الموظف
    # التعامل مع إجراء الموظف
    def handle_employee_action(self, action, section, year, table, selected_row_data):
        employee_id = selected_row_data.get('id') if selected_row_data else None

        if action == "اضافة":
             self.handle_action_button("اضافة", section) # Connect to handler

        elif action == "حذف":
            self.handle_action_button("حذف", section) # Connect to handler

        elif action == "طباعة":
            self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "رصيد_الحساب":
             pass

        elif action == "تقرير_مالي":
            if employee_id is None:
                QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار موظف من الجدول لعرض التقارير.")
                return
            pass

        elif action == "تكليف_بمهمة":
             if employee_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار موظف من الجدول لتكليفه بمهمة.")
                 return
             QMessageBox.information(self, "تكليف بمهمة", f"سيتم تكليف الموظف رقم {employee_id} بمهمة في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")

        elif action == "الموظفين_التقييم":
             if employee_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار موظف من الجدول لتقييمه.")
                 return
             QMessageBox.information(self, "تقييم المهندسين", f"سيتم تقييم الموظف رقم {employee_id} في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")

        else:
             QMessageBox.information(self, "إجراء مخصص", f"الإجراء المخصص '{action}' في قسم {section} غير مطبق بعد.")

    #ازرار الحسابات
    # التعامل مع عمل النفقات
    # التعامل مع عمل النفقات
    def handle_expense_action(self, action, section, year, table, selected_row_data):
        expense_id = selected_row_data.get('id') if selected_row_data else None

        if action == "اضافة":
             self.handle_action_button("اضافة", section) # Connect to handler

        elif action == "حذف":
            self.handle_action_button("حذف", section) # Connect to handler

        elif action == "طباعة":
            self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "طباعة_فاتورة":
            self.print_expense_voucher()
        
        elif action == "الموردين":
            self.open_suppliers_management_window()

        elif action == "سجل_الديون":
            self.open_debts_management_window()

        elif action == "الأقساط":
            pass

        else:
             QMessageBox.information(self, "إجراء مخصص", f"الإجراء المخصص '{action}' في قسم {section} غير مطبق بعد.")

    #ازرار التدريب
    # التعامل مع العمل التدريبي
    # التعامل مع العمل التدريبي
    def handle_training_action(self, action, section, year, table, selected_row_data):
        # Ensure selected_row_data is a dict before trying to get('id')
        course_id = selected_row_data.get('id') if isinstance(selected_row_data, dict) and selected_row_data else None
        course_code = selected_row_data.get('التصنيف') if isinstance(selected_row_data, dict) and selected_row_data else "N/A"

        if action == "اضافة":
             self.handle_action_button("اضافة", section) # Connect to handler

        elif action == "حذف":
             self.handle_action_button("حذف", section) # Connect to handler

        elif action == "طباعة":
             self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "إدارة_المجموعات":
             if course_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار دورة من الجدول لإدارة مجموعاتها.")
                 return
             QMessageBox.information(self, "إدارة المجموعات", f"سيتم عرض إدارة مجموعات الدورة رقم {course_code} (id: {course_id}) في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             
        elif action == "إدارة_الطلاب":
             if course_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار دورة من الجدول لإدارة طلبتها.")
                 return
             QMessageBox.information(self, "إدارة الطلاب", f"سيتم عرض إدارة الطلاب الدورة رقم {course_code} (id: {course_id}) في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             
        elif action == "إدارة_المدربين":
             if course_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار دورة من الجدول لإدارة مدربيها.")
                 return
             QMessageBox.information(self, "إدارة المدربين", f"سيتم عرض إدارة مدربي الدورة رقم {course_code} (id: {course_id}) في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             
        elif action == "مصروفات_الدورة":
             if course_id is None:
                 QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار دورة من الجدول لعرض مصروفاتها.")
                 return
             QMessageBox.information(self, "مصروفات الدورة", f"سيتم عرض مصروفات الدورة رقم {course_code} (id: {course_id}) في قسم {section} ({year}).\n(هذا الإجراء غير مطبق بعد)")
             
        else:
             QMessageBox.information(self, "إجراء مخصص", f"الإجراء المخصص '{action}' في قسم {section} غير مطبق بعد.")

    #ازرار الموردين
    # التعامل مع العمل الموردين
    # التعامل مع العمل الموردين
    def handle_supplier_action(self, action, section, year, table, selected_row_data):
        supplier_id = selected_row_data.get('id') if selected_row_data else None    

        if action == "اضافة":
            if open_supplier_management_window(self) == QDialog.Accepted:
                self.show_section(section)

        elif action == "تعديل":
            if not selected_row_data:
                QMessageBox.warning(self, "اختيار مطلوب", "الرجاء اختيار مورد من الجدول لتعديل بياناته.")
                return
            if open_supplier_management_window(self, selected_row_data) == QDialog.Accepted:
                self.show_section(section)

        elif action == "حذف":
             self.handle_action_button("حذف", section) # Connect to handler

        elif action == "طباعة":
             self.handle_action_button("طباعة", section) # Connect to handler

        elif action == "طباعة_فاتورة":
            self.print_expense_voucher()

    #الدوال ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    #التحديثات=======================================================================================================
    # تحقق من وجود تحديثات pottom
    # تحقق من وجود تحديثات pottom
    def check_for_updates_pottom(self):
        check_for_updates_pottom(self)

    #تبديل المستخدم f12=======================================================================================================
    # keypressevent
    # keypressevent
    def keyPressEvent(self, event):
        # عند الضغط على F12
        if event.key() == Qt.Key_F9:  # التصنيف الخاص بـ F12 في PyQt
            if password!= pm_password:
                reply = GEN_MSG_BOX('تأكيد تبديل المستخدم','هل تريد تبديل المستخدم','personalization32.png','تبديل المستخدم','إلغاء',msg_box_color)
                if reply == QMessageBox.Ok:
                    restart_application()

    #تبديل المستخدم
    # فتح تسجيل الدخول
    # فتح تسجيل الدخول
    def open_login(self):
        if password!= pm_password:
            reply = GEN_MSG_BOX('تأكيد تبديل المستخدم','هل تريد تبديل المستخدم','personalization32.png','تبديل المستخدم','إلغاء',msg_box_color)
            if reply == QMessageBox.Ok:
                restart_application()

    # التحقق من بيانات الشركة  ========================================================================================
    # تحميل معلومات الشركة
    # تحميل معلومات الشركة
    def load_company_info(self):
        # التحقق مما إذا كانت الإعدادات موجودة في الرجستري
        if not settings.contains("company_name"):
            try:
                # الاتصال بقاعدة البيانات
                conn = mysql.connector.connect(host=host, user=user, password=password, database="project_manager2_user")
                cursor = conn.cursor()
                # التحقق من وجود بيانات الشركة في قاعدة البيانات
                cursor.execute("SELECT company_name, company_logo , company_logo FROM company LIMIT 1")
                result = cursor.fetchone()
                if result:
                    company_name, logo_path,Currency_type = result
                    # حفظ البيانات في الرجستري
                    settings.setValue("company_name", company_name)
                    settings.setValue("company_logo", logo_path)
                    settings.setValue("Currency_type", Currency_type)

                    self.company_name = settings.value("company_name", "منظومة المهندس")
                    self.setWindowTitle(f"{self.company_name}")
                else:
                    # إذا لم تكن هناك بيانات في قاعدة البيانات، افتح نافذة إدخال معلومات الشركة
                    self.open_company_info_dialog()
                conn.close()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}")

    #نافذة الشركة=======================================================================================================
    # فتح حوار معلومات الشركة
    # فتح حوار معلومات الشركة
    def open_company_info_dialog(self):
        CompanyInfo(self)

    #الترخيص ///////////////////////////////////////////////////////////////////////////////////////////
    # تحميل بيانات الترخيص
    # تحميل بيانات الترخيص
    def load_license_data(self):
        license_details = get_license_details(self)
        if license_details:
            self.license_type = license_details["license_type"]
            self.start_date = license_details["start_date"]
            self.end_date = license_details["end_date"]

            if self.license_type in ["trial", "annual"]:
                remaining_days = loadDemoInterface(self, self.start_date, self.end_date)
                if remaining_days is not None:
                    self.remaining_days = remaining_days
                else:
                    self.show_activation_dialog()
                    self.load_license_data()
        else:
            self.show_activation_dialog()
            self.load_license_data()

    # إظهار حوار التنشيط
    # إظهار حوار التنشيط
    def show_activation_dialog(self):
        dialog = ActivationDialog(self)
        if dialog.exec() != QDialog.Accepted:
            try:
                sys.exit()
            except ValueError:
                QMessageBox.critical(self, 'خطأ في الترخيص ', "الترخيص غير صحيح يرجى الإتصال بالمطور")

    #تغيير الترخيص
    # تغيير الحوار التنشيط
    # تغيير الحوار التنشيط
    def changing_activation_dialog(self):
        dialog = ActivationDialog(self)
        if dialog.exec() != QDialog.Accepted:
            pass
        else:
            QMessageBox.information(self, "اعادة تشغيل", "سيتم إعادة تشغيل التطبيق.")
            restart_application()

    #اعدادات الشبكة الداخلية//////////////////////////////////////////////////////////////////////////////////////////////////////
    # إعدادات الشبكة
    # إعدادات الشبكة
    def network_settings(self):
        # فتح نافذة إعدادات الشبكة
        dialog = NetworkSettingsDialog(self)
        dialog.exec()

    #تلوين حسب  الحالة //////////////////////////////////////////////////////////////////////////////////////////////////
    # تلوين الخلايا
    # تلوين الخلايا
    def colorize_cells(self, table, section_name):
        # Implement actual cell coloring logic here based on section_name
        if section_name == "المشاريع":
            # Get column indices by keys instead of hardcoded numbers
            status_col = get_column_index_by_key(table, section_name, "الحالة")
            remaining_col = get_column_index_by_key(table, section_name, "الوقت_المتبقي")
            remaining_amount_col = get_column_index_by_key(table, section_name, "الباقي")
            paid_amount_col = get_column_index_by_key(table, section_name, "المدفوع")
            total_amount_col = get_column_index_by_key(table, section_name, "المبلغ")

            # تلوين عمود الحالة
            for row in range(table.rowCount()):
                # تلوين عمود الحالة
                if status_col >= 0:
                    status_item = table.item(row, status_col)
                    if status_item:
                        status_text = status_item.text().strip()

                        if "تم الإنجاز" in status_text:
                            # تم الإنجاز - أخضر
                            status_item.setForeground(QColor("##00ad42"))  # أخضر فاتح
                            
                        elif "تم التسليم" in status_text:
                            # تم التسليم - أخضر
                            status_item.setForeground(QColor("##00ad42"))  # أخضر فاتح
                        elif "تأكيد التسليم" in status_text:
                            # تأكيد التسليم - أخضر داكن
                            status_item.setForeground(QColor("#e9ad6e"))  # أخضر ليموني
                        elif "قيد الإنجاز" in status_text:
                            # قيد الإنجاز - أصفر
                            status_item.setForeground(QColor("#C48600"))
                        elif "غير خالص" in status_text:
                            # غير خالص - أحمر
                            status_item.setForeground(QColor("#ac0707"))  # أحمر
                        elif "متوقف" in status_text:
                            # متوقف - أحمر فاتح
                            status_item.setForeground(QColor("#ac0707"))  # أحمر فاتح
                        elif "معلق" in status_text:
                            # معلق - أزرق
                            status_item.setForeground(QColor("#8EC7DD"))  # أزرق فاتح

                # تلوين عمود الوقت المتبقي
                if remaining_col >= 0:
                    remaining_item = table.item(row, remaining_col)
                    if remaining_item:
                        remaining_text = remaining_item.text().strip()

                        if "تم الإنجاز" in remaining_text:
                            # تم الإنجاز مع رقم - أخضر
                            remaining_item.setForeground(QColor("#00ad42"))  # أخضر فاتح
                        elif remaining_text == "اليوم":
                            # تم اليوم - برتقالي
                            remaining_item.setForeground(QColor("#FFA500"))  # برتقالي
                        elif "متأخر" in remaining_text:
                            # متأخر رقم يوم - أحمر
                            remaining_item.setForeground(QColor("#ac0707"))  # أحمر
                        elif remaining_text == "معلق":
                            # معلق - أزرق
                            remaining_item.setForeground(QColor("#87CEEB"))  # أزرق فاتح
                        elif remaining_text == "متوقف":
                            # متوقف - أحمر فاتح
                            remaining_item.setForeground(QColor("#ac0707"))  # أحمر فاتح
                        elif "متبقي" in remaining_text:
                            # متبقي رقم يوم - أصفر
                            remaining_item.setForeground(QColor("#F7C569"))  # أصفر فاتح

                # تلوين عمود الباقي
                if remaining_amount_col >= 0:
                    remaining_amount_item = table.item(row, remaining_amount_col)
                    if remaining_amount_item:
                        remaining_amount_text = remaining_amount_item.text().strip()

                        try:
                            if remaining_amount_text.lower() in ["خالص", "0", "0.0", "0.00"]:
                                # الباقي = 0 أو خالص - أخضر
                                remaining_amount_item.setForeground(QColor("##00ad42"))  # أخضر فاتح
                            else:
                                remaining_amount_value = float(remaining_amount_text.replace(",", ""))
                                if remaining_amount_value > 0:
                                    # الباقي أكبر من 0 - أحمر
                                    remaining_amount_item.setForeground(QColor("#ac0707"))  # أحمر
                                elif remaining_amount_value < 0:
                                    # الباقي أقل من 0 - أصفر
                                    remaining_amount_item.setForeground(QColor("#F7C569"))  # أصفر فاتح
                        except (ValueError, TypeError):
                            # في حالة عدم القدرة على تحويل النص إلى رقم
                            if remaining_amount_text.lower() == "خالص":
                                remaining_amount_item.setForeground(QColor("#cdd7b9"))  # أخضر فاتح

                # تلوين عمود المدفوع
                if paid_amount_col >= 0 and total_amount_col >= 0:
                    paid_item = table.item(row, paid_amount_col)
                    total_item = table.item(row, total_amount_col)

                    if paid_item and total_item:
                        paid_text = paid_item.text().strip()
                        total_text = total_item.text().strip()

                        try:
                            if paid_text.lower() in ["خالص"]:
                                # المدفوع = خالص - أخضر
                                paid_item.setForeground(QColor("##00ad42"))  # أخضر فاتح
                            elif paid_text in ["0", "0.0", "0.00", ""]:
                                # المدفوع = 0 أو فارغ - أحمر
                                paid_item.setForeground(QColor("#ac0707"))  # أحمر
                            else:
                                paid_value = float(paid_text.replace(",", ""))
                                total_value = float(total_text.replace(",", ""))

                                if paid_value == total_value:
                                    # المدفوع يساوي المبلغ - أخضر
                                    paid_item.setForeground(QColor("##00ad42"))  # أخضر فاتح
                                elif paid_value > 0:
                                    # المدفوع أكبر من 0 - أصفر
                                    paid_item.setForeground(QColor("#F7C569"))  # أصفر فاتح
                                else:
                                    # المدفوع = 0 - أحمر
                                    paid_item.setForeground(QColor("#ac0707"))  # أحمر
                        except (ValueError, TypeError):
                            # في حالة عدم القدرة على تحويل النص إلى رقم
                            if paid_text.lower() == "خالص":
                                paid_item.setForeground(QColor("##00ad42"))  # أخضر فاتح
                            elif paid_text in ["0", "0.0", "0.00", ""]:
                                paid_item.setForeground(QColor("#ac0707"))  # أحمر

        elif section_name == "الحسابات":
            # Get column index by key
            amount_col = get_column_index_by_key(table, section_name, "المبلغ")

            if amount_col >= 0:  # Only proceed if the column was found
                for row_idx in range(table.rowCount()):
                    item = table.item(row_idx, amount_col)
                    if item:
                        item.setForeground(QColor("#dc8484"))

        elif section_name == "الموظفين":
            # Get column indices by keys
            balance_col = get_column_index_by_key(table, section_name, "الرصيد")
            classification_col = get_column_index_by_key(table, section_name, "الالتصنيف")

            # Color the balance column
            if balance_col >= 0:  # Only proceed if the column was found
                for row_idx in range(table.rowCount()):
                    balance_item = table.item(row_idx, balance_col)
                    if balance_item:
                        balance_data = balance_item.text()
                        balance_item.setForeground(QColor("#cdd7b9"))

                        try:
                            if float(balance_data) <= 0:
                                balance_item.setForeground(QColor("#dc8484"))
                        except (ValueError, TypeError):
                            pass  # Ignore if not a valid number

            # Color the classification column based on employee type
            if classification_col >= 0:  # Only proceed if the column was found
                for row_idx in range(table.rowCount()):
                    classification_item = table.item(row_idx, classification_col)
                    if classification_item:
                        classification_text = classification_item.text().strip()

                        # Set colors based on classification
                        if "مهندس" in classification_text:
                            classification_item.setForeground(QColor("#6e989c"))  # Blue
                        elif "مقاول" in classification_text:
                            classification_item.setForeground(QColor("#eee0bd"))  # Yellow
                        elif "عامل" in classification_text:
                            classification_item.setForeground(QColor("#e9ad6e"))  # Orange
                        elif "موظف" in classification_text:
                            classification_item.setForeground(QColor("#cdd7b9"))  # Green
                        elif "متعاون" in classification_text:
                            classification_item.setForeground(QColor("#d3d3d3"))  # Gray

    #نسح احتياطي ===================================================================================
    # النسخ الاحتياطي DB
    # النسخ الاحتياطي DB
    def Backup_DB(self):
        Backup_DB(self)

    # استيراد DB
    # استيراد DB
    def import_db(self):
        import_db(self)

    # استيراد ملف اكسل ===================================================================================
    # exceltodbimporter
    # exceltodbimporter
    def ExcelToDBImporter(self):
        open_excel_to_db_dialog(self,parent=None)

    # حماية  =================================================================================
    # OpenAdduserDialog
    # OpenAdduserDialog
    def openAddUserDialog(self):
        openAddUserDialog(self)

    # CreatePassword
    # CreatePassword
    def createPassword(self):
        createPassword(self)

    # aspassword
    # AskPassword
    def askPassword(self):
        askPassword(self)

    # تغيير كلمة المرور
    # تغيير كلمة المرور
    def changePassword(self):
        changePassword(self)

    # تعطل الأمن
    # تعطل الأمن
    def disableSecurity(self):
        disableSecurity(self)

    # دوال تحميل الواجهات المختلفة
    # loadAdMinInterface
    # loadAdMinInterface
    def loadAdminInterface(self):
        try:
            account_type = settings.value("account_type", self.account_type)
            if account_type != "admin":
                self.setWindowTitle(f"{company_name} - {account_type}")
                self.User_Permissions()
                self.profits_label2.setText(f"المستخدم\n{account_type}")
        except Exception as e:
            account_type = settings.value("account_type", "admin")
            self.setWindowTitle(f"{company_name} - {account_type}")
            self.profits_label2.setText(f"المستخدم\n{account_type}")

    #صلاحيات الموظفين///////////////////////////////////////////////////////////
    # أذونات المستخدم
    # أذونات المستخدم
    def User_Permissions(self):
        User_Permissions(self)

    #تأكيد الاغلاق //////////////////////////////////////////////////////////////////////////
    # Closevent
    # Closevent
    def closeEvent(self, event):
        from الدوال_الأساسية import closeEvent as close_func
        close_func(self, event)

    #دروس تعليمية ///////////////////////////////////////////////////////////////////////////////////
    # فتح رابط البرنامج التعليمي
    # فتح رابط البرنامج التعليمي
    def open_tutorial_link(self):
        webbrowser.open("https://www.youtube.com/watch?v=wTG37oZESmw&list=PLRrETGQR_7qIGebxDJUAPiXHbvVrpaRai&ab_channel=%D8%AE%D8%A7%D9%84%D8%AF%D8%A7%D9%84%D9%86%D9%88%D9%8A%D8%B5%D8%B1%D9%8A")
        #webbrowser.open("https://www.youtube.com/playlist%slist=PLRrETGQR_7qIGebxDJUAPiXHbvVrpaRai&playnext=1&index=1")

    #ابلاغ عن مشكلة/////////////////////////////////////////////////////////////////////
    # مشكلة الإبلاغ
    # مشكلة الإبلاغ
    def report_problem(self):
        # رابط الإبلاغ عن مشكلة مع محتوى الرسالة
        url = "https://wa.me/218928198656?text=الإبلاغ%20عن%20مشكلة%20-%20منظومة%20المهندس"
        webbrowser.open(url)

    # طباعة دفعات العميل
    # مدفوعات الطباعة
    # مدفوعات الطباعة
    def print_Payments(self):
        # الحصول على القسم الحالي
        current_section = self.get_current_section_name()
        if not current_section:
            QMessageBox.warning(self, "تحذير", "لا يمكن تحديد القسم الحالي")
            return

        # الحصول على معلومات القسم
        section_info = self.sections.get(current_section)
        if not section_info:
            QMessageBox.warning(self, "تحذير", "لا يمكن العثور على معلومات القسم")
            return

        # الحصول على الجدول الحالي
        current_table = section_info["table"]

        print_table_data(
            self,
            mastr_table=current_table,
            table=self.payments_table if hasattr(self, 'payments_table') else current_table,
            title="فاتورة دفعات",
            name_column=2,
            project_column=3,
            total_column=4,
            remaining_column=9,
            paid_column=5,
            file_prefix="دفعات العميل"
        )

    #طباعة تقرير الدفعات
    # طباعة المدفوعات التقارير
    # طباعة المدفوعات التقارير
    def print_reports_Payments(self):
        print_table_report(
            self,
            table=self.reports_table,
            title_prefix="تقرير الدفعات",
            summary_data={
                "total_paid": self.total_paid
            },
            file_prefix="تقرير الدفعات"
        )

    # طباعة معاملات الموظف
    # موظف طباعة
    # موظف طباعة
    def print_Employee(self):
        # الحصول على القسم الحالي
        current_section = self.get_current_section_name()
        if not current_section:
            QMessageBox.warning(self, "تحذير", "لا يمكن تحديد القسم الحالي")
            return

        # الحصول على معلومات القسم
        section_info = self.sections.get(current_section)
        if not section_info:
            QMessageBox.warning(self, "تحذير", "لا يمكن العثور على معلومات القسم")
            return

        # الحصول على الجدول الحالي
        current_table = section_info["table"]

        print_table_data(
            self,
            mastr_table=current_table,
            table=self.tableWidget if hasattr(self, 'tableWidget') else current_table,
            title="فاتورة موظف",
            name_column=2,
            project_column=3,
            total_column=8,
            remaining_column=9,
            paid_column=5,
            file_prefix="فاتورة موظف"
        )

    #طباعة تقرير الموظفين
    # تقارير طباعة
    # تقارير طباعة
    def print_reports(self):
        print_table_report(
            self,
            table=self.reports_table,
            title_prefix="تقرير الموظفين",
            summary_data={
                "balance": self.Employee_Balance,
                "withdraw": self.Employee_Withdraw
            },
            file_prefix="تقرير الموظفين"
        )

    # طباعة سند صرف مصروفات
    # طباعة قسيمة نفقات
    # طباعة قسيمة نفقات
    def print_expense_voucher(self):
        try:
            # الحصول على القسم الحالي
            current_section = self.get_current_section_name()
            if current_section != "الحسابات":
                QMessageBox.warning(self, "تحذير", "هذه الوظيفة متاحة فقط في قسم الحسابات")
                return

            # الحصول على الجدول الحالي من sections
            section_info = self.sections.get(current_section)
            if not section_info:
                QMessageBox.warning(self, "تحذير", "لا يمكن العثور على معلومات القسم")
                return

            current_table = section_info["table"]

            # التحقق من وجود صف محدد
            current_row = current_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد مصروف من الجدول أولاً")
                return

            # الحصول على id المصروف
            معرف_item = current_table.item(current_row, 0)
            if not معرف_item:
                QMessageBox.warning(self, "تحذير", "لا يمكن العثور على id المصروف")
                return

            expense_id = معرف_item.data(Qt.UserRole) if معرف_item.data(Qt.UserRole) is not None else معرف_item.text()

            # جلب بيانات المصروف من قاعدة البيانات
            conn = self.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "فشل في الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `الحسابات` WHERE id = %s", (expense_id,))
            expense_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if not expense_data:
                QMessageBox.warning(self, "تحذير", "لا يمكن العثور على بيانات المصروف")
                return

            # فتح نافذة سند الصرف
            voucher_dialog = ExpenseVoucherDialog(expense_data, self)
            voucher_dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إنشاء سند الصرف:\n{str(e)}")
            print(f"Error in print_expense_voucher: {e}")

    # الخلفية تخصيص الالوان===============================================================
    #مود ليلي
    # تبديل موضوع
    # تبديل موضوع
    def toggle_theme(self):
        # تغيير حالة الدارك مود
        self.is_dark_mode = not self.is_dark_mode
        # حفظ حالة الدارك مود باستخدام QSettings
        settings.setValue("dark_mode", self.is_dark_mode)
        # إعادة تطبيق الأنماط بناءً على الحالة الجديدة
        self.Basic_Styles()

    # فتح نافذة إدارة التصنيفات
    # إدارة الفئات المفتوحة
    def open_categories_management(self):
        try:
            from إدارة_التصنيفات import CategoriesManagementDialog
            dialog = CategoriesManagementDialog(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل نافذة إدارة التصنيفات: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إدارة التصنيفات: {e}")

    # فتح نافذة إدارة أسعار المراحل
    # إدارة تسعير المراحل المفتوحة
    def open_phases_pricing_management(self):
        try:
            from إدارة_أسعار_المراحل import PhasePricingManagementDialog
            dialog = PhasePricingManagementDialog(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل نافذة إدارة أسعار المراحل: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إدارة أسعار المراحل: {e}")

    # فتح نافذة إدارة مواعيد العمل
    # إدارة جدول العمل المفتوح
    def open_work_schedule_management(self):
        try:
            from إدارة_مواعيد_العمل import open_work_schedule_management
            open_work_schedule_management(self)
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل نافذة إدارة مواعيد العمل: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إدارة مواعيد العمل: {e}")

    # فتح نافذة الإعدادات الموحدة
    # فتح الإعدادات الموحدة
    def open_unified_settings(self):
        try:
            from إدارة_الإعدادات_الموحدة import open_unified_settings_window
            self.unified_settings_window = open_unified_settings_window(self)
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل نافذة الإعدادات الموحدة: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة الإعدادات الموحدة: {e}")

    # فتح نافذة إدارة الموردين
    # فتح نافذة إدارة الموردين
    def open_suppliers_management_window(self):
        try:
            # إنشاء النافذة
            self.suppliers_window = SuppliersManagementWindow()

            # ربط الإشارات
            self.suppliers_window.connect_signals()

            # عرض النافذة
            self.suppliers_window.show()

            # رفع النافذة للمقدمة
            self.suppliers_window.raise_()
            self.suppliers_window.activateWindow()

        except ImportError as e:
            QMessageBox.critical(self, "خطأ", f"لم يتم العثور على وحدة إدارة الموردين: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إدارة الموردين: {e}")

    # فتح نافذة إدارة الديون
    # فتح نافذة إدارة الديون
    def open_debts_management_window(self):
        try:
            from ادارة_الديون import DebtsManagementWindow
            # إنشاء النافذة
            self.debts_window = DebtsManagementWindow()

            # ربط الإشارات
            self.debts_window.connect_signals()

            # عرض النافذة
            self.debts_window.show()

            # رفع النافذة للمقدمة
            self.debts_window.raise_()
            self.debts_window.activateWindow()

        except ImportError as e:
            QMessageBox.critical(self, "خطأ", f"لم يتم العثور على وحدة إدارة الديون: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إدارة الديون: {e}")

    # تبديل العرض العام بين البطاقات والجدول لجميع الأقسام مع حفظ فوري وموثوق
    # تبديل العرض العالمي
    def toggle_global_view(self):
        try:
            # حفظ الحالة السابقة للتراجع في حالة الفشل
            previous_view = self.is_cards_view

            # تغيير حالة العرض
            self.is_cards_view = not self.is_cards_view

            # حفظ فوري للإعداد الجديد مع التحقق من النجاح
            settings.setValue("view_mode_cards", self.is_cards_view)
            settings.sync()  # فرض الحفظ الفوري

            # التحقق من نجاح الحفظ
            saved_value = settings.value("view_mode_cards", not self.is_cards_view, type=bool)
            if saved_value != self.is_cards_view:
                # فشل في الحفظ - التراجع
                self.is_cards_view = previous_view
                QMessageBox.critical(self, "خطأ في الحفظ",
                                   "فشل في حفظ إعدادات العرض. يرجى المحاولة مرة أخرى.")
                return

            # تطبيق العرض الجديد على جميع الأقسام
            applied_sections = []
            failed_sections = []

            for section_name in self.sections.keys():
                try:
                    self.apply_view_to_section(section_name, self.is_cards_view)
                    applied_sections.append(section_name)
                except Exception as e:
                    failed_sections.append(section_name)
                    print(f"فشل في تطبيق العرض على القسم {section_name}: {e}")

            # تحديث نص القائمة
            self.update_view_menu_text()

            # إظهار رسالة تأكيد مفصلة
            view_type = "البطاقات العصرية" if self.is_cards_view else "الجدول"
            success_message = f"✅ تم تطبيق عرض {view_type} بنجاح\n\n"
            success_message += f"📊 الأقسام المطبقة: {len(applied_sections)}\n"
            success_message += f"💾 تم حفظ الإعداد تلقائياً\n"
            success_message += f"🔄 سيتم تطبيق هذا العرض عند إعادة تشغيل التطبيق"

            if failed_sections:
                success_message += f"\n\n⚠️ فشل في تطبيق العرض على: {', '.join(failed_sections)}"

            QMessageBox.information(self, "تم تغيير العرض", success_message)

        except Exception as e:
            # في حالة حدوث خطأ عام، التراجع إلى الحالة السابقة
            self.is_cards_view = previous_view if 'previous_view' in locals() else True
            QMessageBox.critical(self, "خطأ",
                               f"حدث خطأ أثناء تغيير العرض:\n{str(e)}\n\nتم التراجع إلى الإعداد السابق.")

    # تطبيق نوع العرض على قسم محدد مع معالجة شاملة للأخطاء
    # تطبيق العرض على القسم
    def apply_view_to_section(self, section_name, is_cards_view):
        try:
            # التحقق من وجود القسم
            section_info = self.sections.get(section_name)
            if not section_info:
                raise ValueError(f"القسم '{section_name}' غير موجود")

            # معالجة خاصة للأقسام التي لا تدعم view_stack (مثل التقارير المالية)
            if section_name == "التقارير":
                
                section_info["current_view"] = "financial_reports"
                return  # الخروج بنجاح دون معالجة view_stack

            # التحقق من وجود view_stack للأقسام العادية
            view_stack = section_info.get("view_stack")
            if not view_stack:
                raise ValueError(f"view_stack غير موجود للقسم '{section_name}'")

            # التحقق من وجود الويدجت المطلوب مع حماية من RuntimeError
            try:
                if is_cards_view:
                    if view_stack.count() < 2:
                        raise ValueError(f"عرض البطاقات غير متوفر للقسم '{section_name}'")
                    cards_widget = view_stack.widget(1)
                    if not cards_widget:
                        raise ValueError(f"ويدجت البطاقات غير موجود للقسم '{section_name}'")
                else:
                    if view_stack.count() < 1:
                        raise ValueError(f"عرض الجدول غير متوفر للقسم '{section_name}'")
                    table_widget = view_stack.widget(0)
                    if not table_widget:
                        raise ValueError(f"ويدجت الجدول غير موجود للقسم '{section_name}'")

                if is_cards_view:
                    # التبديل إلى عرض البطاقات
                    view_stack.setCurrentIndex(1)
                    section_info["current_view"] = "cards"

                    # تحديث البطاقات بالبيانات الحالية مع معالجة الأخطاء
                    cards_view = view_stack.widget(1)
                    if hasattr(cards_view, 'add_cards'):
                        try:
                            year_combo = section_info.get("year_combo")
                            if year_combo:
                                year = year_combo.currentText()
                                cards_data = self.get_section_data_for_cards(section_name)
                                cards_view.add_cards(cards_data if cards_data else [])
                            else:
                                print(f"تحذير: year_combo غير موجود للقسم {section_name}")
                        except Exception as e:
                            print(f"تحذير: فشل في تحديث بيانات البطاقات للقسم {section_name}: {e}")
                            # لا نرفع الخطأ هنا لأن العرض تم تطبيقه بنجاح
                else:
                    # التبديل إلى عرض الجدول
                    view_stack.setCurrentIndex(0)
                    section_info["current_view"] = "table"

                # التحقق من نجاح التطبيق
                current_index = view_stack.currentIndex()
                expected_index = 1 if is_cards_view else 0
                if current_index != expected_index:
                    raise RuntimeError(f"فشل في تطبيق العرض للقسم '{section_name}' - المؤشر الحالي: {current_index}, المتوقع: {expected_index}")
            
            except RuntimeError as e:
                # التحقق من كون الخطأ بسبب حذف الكائن
                if "Internal C++ object" in str(e) and "already deleted" in str(e):
                    print(f"تحذير: كائن view_stack محذوف للقسم {section_name}")
                    return  # خروج بصمت
                else:
                    raise  # إعادة رفع الخطأ إذا لم يكن بسبب حذف الكائن

            # تحديث زر التبديل بعد تطبيق العرض بنجاح
            self.update_section_toggle_button(section_name)

        except Exception as e:
            # إعادة رفع الخطأ مع معلومات إضافية
            raise Exception(f"فشل في تطبيق العرض على القسم '{section_name}': {str(e)}")

    # تحديث نص قائمة العرض في شريط الأدوات بطريقة محسنة
    # تحديث نص عرض القائمة
    def update_view_menu_text(self):
        try:
            # البحث عن عنصر القائمة الخاص بتبديل العرض
            view_action = None
            for action in self.draggable_toolbar.customize_menu.actions():
                action_text = action.text()
                if "التبديل إلى عرض" in action_text:
                    view_action = action
                break

            if view_action:
                # تحديث النص مباشرة دون إعادة إنشاء القائمة
                if self.is_cards_view:
                    new_text = "           التبديل إلى عرض الجدول "
                else:
                    new_text = "         التبديل إلى عرض البطاقات "

                view_action.setText(new_text)
            else:
                # في حالة عدم العثور على العنصر، إعادة إنشاء القائمة كحل احتياطي
                print("تحذير: لم يتم العثور على عنصر تبديل العرض، سيتم إعادة إنشاء القائمة")
                self.draggable_toolbar.customize_menu.clear()
                self._setup_customize_menu()

        except Exception as e:
            print(f"خطأ في تحديث نص القائمة: {e}")
            # حل احتياطي: إعادة إنشاء القائمة
            try:
                self.draggable_toolbar.customize_menu.clear()
                self._setup_customize_menu()
            except Exception as e2:
                print(f"خطأ في إعادة إنشاء القائمة: {e2}")

    # تطبيق إعدادات العرض المحفوظة عند بدء التشغيل مع التحقق من الصحة - مع دعم التفضيلات الفردية
    # تطبيق إعدادات العرض الأولية
    def apply_initial_view_settings(self):
        try:
            # التحقق من وجود الأقسام
            if not hasattr(self, 'sections') or not self.sections:
                print("تحذير: لا توجد أقسام لتطبيق إعدادات العرض عليها")
                return

            # تطبيق العرض على كل قسم حسب تفضيله المحفوظ
            applied_count = 0
            failed_count = 0

            for section_name in self.sections.keys():
                try:
                    # الحصول على تفضيل العرض لهذا القسم
                    preferred_view = self.get_section_view_preference(section_name)
                    is_cards_view = preferred_view == "cards"

                    # تطبيق العرض المفضل على القسم
                    self.apply_view_to_section(section_name, is_cards_view)
                    applied_count += 1

                    

                except Exception as e:
                    failed_count += 1
                    print(f"فشل في تطبيق العرض الأولي على القسم {section_name}: {e}")

            
            
            if failed_count > 0:
                print(f"⚠️ فشل في تطبيق العرض على {failed_count} قسم")

        except Exception as e:
            print(f"خطأ في تطبيق إعدادات العرض الأولية: {e}")
            # في حالة الفشل، تطبيق الإعدادات الافتراضية
            for section_name in self.sections.keys():
                try:
                    default_view = self.section_default_views.get(section_name, "cards")
                    is_cards_view = default_view == "cards"
                    self.apply_view_to_section(section_name, is_cards_view)
                except Exception as e2:
                    print(f"فشل في تطبيق الإعداد الافتراضي على القسم {section_name}: {e2}")

    # التحقق من ثبات إعدادات العرض وصحتها
    # تحقق
    def verify_view_settings_persistence(self):
        try:
            # قراءة الإعداد من QSettings
            saved_view = settings.value("view_mode_cards", True, type=bool)

            # التحقق من تطابق الإعداد المحفوظ مع الحالة الحالية
            if saved_view != self.is_cards_view:
                print(f"تحذير: عدم تطابق في إعدادات العرض - محفوظ: {saved_view}, حالي: {self.is_cards_view}")
                # تصحيح التطابق
                self.is_cards_view = saved_view
                return False

            # التحقق من تطبيق الإعداد على الأقسام
            mismatched_sections = []
            for section_name, section_info in self.sections.items():
                current_view = section_info.get("current_view", "table")
                expected_view = "cards" if self.is_cards_view else "table"

                if current_view != expected_view:
                    mismatched_sections.append(section_name)

            if mismatched_sections:
                print(f"تحذير: عدم تطابق العرض في الأقسام: {mismatched_sections}")
                # إعادة تطبيق الإعدادات على الأقسام غير المتطابقة
                for section_name in mismatched_sections:
                    try:
                        self.apply_view_to_section(section_name, self.is_cards_view)
                    except Exception as e:
                        print(f"فشل في تصحيح العرض للقسم {section_name}: {e}")
                return False

            return True

        except Exception as e:
            print(f"خطأ في التحقق من ثبات الإعدادات: {e}")
            return False

    # الحصول على تفضيل العرض لقسم محدد
    # الحصول على تفضيل عرض القسم
    def get_section_view_preference(self, section_name):
        # الحصول على القيمة المحفوظة أو استخدام الافتراضية
        default_view = self.section_default_views.get(section_name, "cards")
        saved_view = settings.value(f"section_view_{section_name}", default_view, type=str)
        return saved_view

    # حفظ تفضيل العرض لقسم محدد
    # تعيين تفضيل عرض القسم
    def set_section_view_preference(self, section_name, view_type):
        settings.setValue(f"section_view_{section_name}", view_type)
        settings.sync()

    # الحصول على تفضيلات العرض لجميع الأقسام
    # احصل على كل تفضيلات عرض القسم
    def get_all_section_view_preferences(self):
        preferences = {}
        for section_name in self.sections.keys():
            preferences[section_name] = self.get_section_view_preference(section_name)
        return preferences

    # فتح نافذة تخصيص عرض الأقسام
    # فتح إعدادات عرض القسم
    def open_section_view_settings(self):
        try:
            dialog = SectionViewSettingsDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                # تطبيق الإعدادات الجديدة
                self.apply_initial_view_settings()
                QMessageBox.information(self, "تم الحفظ", "تم حفظ إعدادات عرض الأقسام بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح نافذة الإعدادات: {str(e)}")

    # الحصول على حالة مفصلة لإعدادات العرض
    # احصل على حالة إعدادات العرض
    def get_view_settings_status(self):
        try:
            status = {
                "current_view": "البطاقات" if self.is_cards_view else "الجدول",
                "saved_setting": settings.value("view_mode_cards", True, type=bool),
                "sections_status": {},
                "total_sections": len(self.sections),
                "consistent": True,
                "section_preferences": self.get_all_section_view_preferences()
            }

            # فحص حالة كل قسم
            for section_name, section_info in self.sections.items():
                current_view = section_info.get("current_view", "table")
                view_stack = section_info.get("view_stack")
                current_index = view_stack.currentIndex() if view_stack else -1
                preferred_view = self.get_section_view_preference(section_name)

                status["sections_status"][section_name] = {
                    "current_view": current_view,
                    "stack_index": current_index,
                    "preferred_view": preferred_view,
                    "expected_index": 1 if preferred_view == "cards" else 0
                }

                # التحقق من الاتساق مع التفضيل المحفوظ
                expected_index = 1 if preferred_view == "cards" else 0

                if current_view != preferred_view or current_index != expected_index:
                    status["consistent"] = False

            return status

        except Exception as e:
            return {"error": str(e)}

    # الأساليب الأساسية
    # الأساليب الأساسية
    def Basic_Styles(self):
        Basic_Styles(self)

    #تغيير لون الخلفية
    # ChangeInterFaceColor
    # ChangeInterFaceColor
    def changeInterfaceColor(self):
        table_name = self.Interface_combo.currentText()
        current_color, _, _, _, _, _, _, _, _, _, _, _, _, _ = load_Styles_settings(self)

        #color_dialog = QColorDialog()
        color_dialog = QColorDialog(QColor(current_color), self)  # تعيين اللون الحالي عند الفتح

        color_dialog.setOption(QColorDialog.NoButtons, True)
        color_dialog.currentColorChanged.connect(self.updateInterfaceColor)

        reset_button = QPushButton("استعادة الافتراضيات", color_dialog)
        reset_button.clicked.connect(lambda: reset_Castom(self,table_name,None,None))

        layout = color_dialog.layout()
        layout.addWidget(reset_button)
        color_dialog.exec()

    # UpdateInterFaceColor
    # UpdateInterFaceColor
    def updateInterfaceColor(self, color):
        updateInterfaceColor(self, color)

    #لون الازرار
    # ChangeButtonscolor
    # ChangeButtonscolor
    def changeButtonsColor(self):
        _, button_color, _, _, _, _, _, _, _, _, _, _, _, _ = load_Styles_settings(self)  # الحصول على لون الأزرار
        #color_dialog = QColorDialog()
        color_dialog = QColorDialog(QColor(button_color), self)  # تعيين اللون الحالي عند الفتح

        color_dialog.setOption(QColorDialog.NoButtons, True)
        color_dialog.currentColorChanged.connect(self.updateButtonsColor)
        reset_button = QPushButton("استعادة الافتراضيات", color_dialog)
        reset_button.clicked.connect(lambda: reset_Castom(self,"لون الازرار",None,None))
        layout = color_dialog.layout()
        layout.addWidget(reset_button)
        color_dialog.exec()

    # updateButtaCholor
    # updateButtaCholor
    def updateButtonsColor(self, color):
        updateButtonsColor(self, color)

    #لون حقول الادخال
    # ChangeInputColor
    # ChangeInputColor
    def changeinputColor(self):
        _, _, input_color, _, _, _, _, _, _, _, _, _, _, _ = load_Styles_settings(self)  # الحصول على لون الإدخال
        #color_dialog = QColorDialog()
        color_dialog = QColorDialog(QColor(input_color), self)  # تعيين اللون الحالي عند الفتح

        color_dialog.setOption(QColorDialog.NoButtons, True)
        color_dialog.currentColorChanged.connect(self.updateinputColor)
        reset_button = QPushButton("استعادة الافتراضيات", color_dialog)
        reset_button.clicked.connect(lambda: reset_Castom(self,"لون الادخال",None,None))
        layout = color_dialog.layout()
        layout.addWidget(reset_button)
        color_dialog.exec()

    # updateInputColor
    # updateInputColor
    def updateinputColor(self, color):
        updateinputColor(self, color)

    #فتح نافذة تغيير لون الأيقونات SVG
    # OpenSvgColorChanger
    # OpenSvgColorChanger
    def openSvgColorChanger(self):
        
        from تخصيص_الواجهة import SvgColorChanger
        self.svg_color_changer = SvgColorChanger()
        self.svg_color_changer.show()
        self.svg_color_changer.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                font-size: 13px;
                color: #333;
                background-color: #f8f9fa;
            }
            QLineEdit, QLabel {
                background-color: #fff;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #222;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QSpinBox {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 3px;
                min-width: 60px;
            }
        """)

    #لون الجول
    # changetableColor
    # changetableColor
    def changeTableColor(self):
        _, _, _, Table_color, _, _, _, _, _, _, _, _, _, _ = load_Styles_settings(self)  # الحصول على لون الإدخال
        #color_dialog = QColorDialog()
        color_dialog = QColorDialog(QColor(Table_color), self)  # تعيين اللون الحالي عند الفتح

        color_dialog.setOption(QColorDialog.NoButtons, True)
        color_dialog.currentColorChanged.connect(self.updateTableColor)
        reset_button = QPushButton("استعادة الافتراضيات", color_dialog)
        reset_button.clicked.connect(lambda: reset_Castom(self,"لون الجدول",None,None))
        layout = color_dialog.layout()
        layout.addWidget(reset_button)
        color_dialog.exec()

    # updatetableColor
    # updatetableColor
    def updateTableColor(self, color):
        updateTableColor(self, color)

    #لون الخط العام
    # ChangeFontColor
    # ChangeFontColor
    def changefontColor(self):
        _, _, _, _, font_color, _, _, _, _, _, _, _, _, _ = load_Styles_settings(self)  # الحصول على لون الإدخال
        #color_dialog = QColorDialog()
        color_dialog = QColorDialog(QColor(font_color), self)  # تعيين اللون الحالي عند الفتح

        color_dialog.setOption(QColorDialog.NoButtons, True)
        color_dialog.currentColorChanged.connect(self.updatefontColor)
        reset_button = QPushButton("استعادة الافتراضيات", color_dialog)
        reset_button.clicked.connect(lambda: reset_Castom(self,"لون الخط العام",None,None))
        layout = color_dialog.layout()
        layout.addWidget(reset_button)
        color_dialog.exec()

    # UpdateFontColor
    # UpdateFontColor
    def updatefontColor(self, color):
        updatefontColor(self, color)

    #تغيير الخط الازرار
    # ChangeButtonsfont
    # ChangeButtonsfont
    def changeButtonsFont(self):
        changeFont(self,"نوع خط الازرار","حجم خط الازرار","وزن خط الازرار",self.updateButtonsFont)

    #تحديث الخط الازرار
    # UpdateButtonsfont
    # UpdateButtonsfont
    def updateButtonsFont(self,font):
        updateFont(self,font,"نوع خط الازرار","حجم خط الازرار","وزن خط الازرار")

    #تغيير خط الجدول
    # changetablefont
    # changetablefont
    def changeTableFont(self):
        changeTableFont(self)

    #تحديث ونوع خط الجدول
    # updatetablefont
    # updatetablefont
    def updateTableFont(self,font):
        updateFont(self,font,"نوع خط الجدول","حجم خط الجدول","وزن خط الجدول")

    #تغيير الخط العام
    # ChangeGenralfont
    # ChangeGenralfont
    def changeGenralFont(self):
        changeFont(self,"نوع الخط العام","حجم الخط العام",",وزن الخط العام",self.updateGenralFont)

    #تحديث الخط العام
    # updategenralfont
    # updategenralfont
    def updateGenralFont(self,font):
        updateFont(self,font,"نوع الخط العام","حجم الخط العام","وزن الخط العام")

    #إعادة تعيين الواجهة
    # Resettodefault
    # Resettodefault
    def resetToDefault(self):
        resetToDefault(self)

    #إعادة تعيين الواجهة
    # إعادة تعيين Castom
    # إعادة تعيين Castom
    def reset_Castom(self):
        reset_Castom(self)

    
# إعدادات الشبكة ////////////////////////////////////////////////////////////////////////////
# مربع الحوار الشبكات
# مربع الحوار الشبكات
class NetworkSettingsDialog(QDialog):
    # init
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إعدادات الشبكة")
        self.setGeometry(100, 100, 400, 300)
        self.ip_input = QLineEdit()
        saved_ip = settings.value("saved_ip", "")

        if saved_ip:
            self.ip_input.setText(str(saved_ip))
        else:
            self.ip_input.setPlaceholderText("أدخل IP الجهاز الرئيسي (اختياري)")

        # الأزرار
        self.save_ip_btn = QPushButton("حفظ ")
        self.save_ip_btn.clicked.connect(self.save_ip)

        self.delete_ip_btn = QPushButton("حذف")
        self.delete_ip_btn.clicked.connect(self.delete_ip)

        self.show_ip_btn = QPushButton("عرض IPs المتاحة")
        self.show_ip_btn.clicked.connect(self.show_ips)

        self.status_label = QLabel("")

        self.ip_display = QTextEdit()
        self.ip_display.setReadOnly(True)
        self.ip_display.setPlaceholderText("هنا يتم عرض IP الواي فاي و الإنترنت")

        layout = QVBoxLayout()
        layout1 = QHBoxLayout()

        layout.addWidget(self.ip_input)
        layout1.addWidget(self.save_ip_btn)
        layout1.addWidget(self.delete_ip_btn)
        layout1.addWidget(self.show_ip_btn)

        layout.addLayout(layout1)  # أضفنا layout1 داخل layout الرئيسي
        layout.addWidget(self.ip_display)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    # حفظ IP
    # حفظ IP
    def save_ip(self):
        ip = self.ip_input.text().strip()
        if ip:
            settings.setValue("host", ip)
            self.status_label.setText(f"✅ تم حفظ IP: {ip}")
        else:
            self.status_label.setText("❌ الرجاء إدخال IP")

    # حذف IP
    # حذف IP
    def delete_ip(self):
        settings.remove("host")
        self.ip_input.clear()
        self.ip_input.setPlaceholderText("أدخل IP الجهاز الرئيسي (اختياري)")
        self.status_label.setText("🗑️ تم حذف IP المخزن")

    # عرض IPS
    # عرض IPS
    def show_ips(self):
        ip_list = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    if "Wi-Fi" in interface:
                        ip_list.append(f" Wi-Fi:  {addr.address}")
                    elif "Ethernet" in interface:
                        ip_list.append(f" Ethernet:  {addr.address}")

        if ip_list:
            self.ip_display.setPlainText("\n\n".join(ip_list))
        else:
            self.ip_display.setPlainText("❌ لم يتم العثور على IP")

#نافذة حوار لتحديث حالة المشروع"------
# ProjectStatusDialog
# ProjectStatusDialog
class ProjectStatusDialog(QDialog):
    # init
    # init
    def __init__(self, parent, project_id, project_code, year, selected_row_data):
        super().__init__(parent)
        self.parent = parent
        self.project_id = project_id
        self.project_code = project_code
        self.year = year
        self.selected_row_data = selected_row_data

        self.setup_ui()
        self.load_project_data()

    # إعداد واجهة المستخدم
    # إعداد واجهة المستخدم
    def setup_ui(self):
        self.setWindowTitle(f"حالة المشروع - {self.project_code}")
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # عنوان النافذة
        title_label = QLabel(f"تحديث حالة المشروع رقم: {self.project_code}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # نموذج الإدخال
        form_layout = QFormLayout()

        # كومبو بوكس الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "تم الإنجاز",
            "تم التسليم",
            "في انتظار التسليم",
            "متوقف",
            "معلق"
        ])
        form_layout.addRow("الحالة الجديدة:", self.status_combo)

        # حقل التاريخ
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("التاريخ:", self.date_edit)

        layout.addLayout(form_layout)

        # أزرار العمليات
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_status)
        save_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 8px; }")

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 8px; }")

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    #تحميل بيانات المشروع الحالية"
    # تحميل بيانات المشروع
    # تحميل بيانات المشروع
    def load_project_data(self):
        
        try:
            conn = self.parent.get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()
            db_table_name = self.parent.get_db_table_name("المشاريع")

            cursor.execute(f"SELECT تاريخ_الإستلام, الباقي FROM `{db_table_name}` WHERE id = %s", (self.project_id,))
            result = cursor.fetchone()

            if result:
                self.receive_date = result[0]
                self.remaining_amount = result[1]
            else:
                self.receive_date = None
                self.remaining_amount = 0

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error loading project data: {e}")
            self.receive_date = None
            self.remaining_amount = 0
    
    #حفظ حالة المشروع الجديدة"----------------------------------
    # حفظ الحالة
    # حفظ الحالة
    def save_status(self):
        try:
            selected_status = self.status_combo.currentText()
            selected_date = self.date_edit.date().toString(Qt.ISODate)

            conn = self.parent.get_db_connection()
            if conn is None:
                QMessageBox.critical(self, "خطأ", "تعذر الاتصال بقاعدة البيانات")
                return

            cursor = conn.cursor()
            db_table_name = self.parent.get_db_table_name("المشاريع")

            # جلب البيانات الحالية للمشروع
            cursor.execute(f"SELECT تاريخ_الإستلام, الباقي, الوقت_المتبقي FROM `{db_table_name}` WHERE id = %s", (self.project_id,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على المشروع")
                return

            receive_date, remaining_amount, current_remaining_time = result

            # حساب عدد الأيام من تاريخ الاستلام إلى التاريخ المحدد
            if receive_date:
                from datetime import datetime
                receive_date_obj = datetime.strptime(str(receive_date), '%Y-%m-%d').date()
                selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                days_diff = (selected_date_obj - receive_date_obj).days
                # التأكد من أن عدد الأيام لا يكون سالباً
                days_diff = max(days_diff, 0)
            else:
                days_diff = 0

            # تحديد القيم الجديدة حسب الحالة المختارة
            new_status = ""
            new_remaining_time = ""
            update_delivery_date = True

            if selected_status == "تم الإنجاز":
                new_remaining_time = f"تم الإنجاز {days_diff} يوم"
                # تحديد الحالة حسب الباقي
                if remaining_amount == 0 or str(remaining_amount).lower() == "خالص":
                    new_status = "تأكيد التسليم"
                else:
                    new_status = "غير خالص"

            elif selected_status == "تم التسليم":
                # التحقق من وجود "تم الإنجاز" في النص الحالي
                if "تم الإنجاز" in str(current_remaining_time):
                    new_remaining_time = current_remaining_time  # الاحتفاظ بالنص الحالي
                else:
                    new_remaining_time = f"تم الإنجاز {days_diff} يوم"

                # تحديد الحالة حسب الباقي
                if remaining_amount == 0 or str(remaining_amount).lower() == "خالص":
                    new_status = "تم التسليم"
                else:
                    new_status = "غير خالص"

            elif selected_status == "في انتظار التسليم":
                new_remaining_time = f"تم الإنجاز {days_diff} يوم"
                # تحديد الحالة حسب الباقي
                if remaining_amount == 0 or str(remaining_amount).lower() == "خالص":
                    new_status = "تم الإنجاز"
                else:
                    new_status = "غير خالص"

            elif selected_status == "متوقف":
                new_status = "متوقف"
                new_remaining_time = "متوقف"
                update_delivery_date = False

            elif selected_status == "معلق":
                new_status = "معلق"
                new_remaining_time = "معلق"
                update_delivery_date = False

            # تحديث قاعدة البيانات
            if update_delivery_date:
                sql = f"UPDATE `{db_table_name}` SET `الحالة` = %s, `الوقت_المتبقي` = %s, `تاريخ_التسليم` = %s WHERE `id` = %s"
                params = [new_status, new_remaining_time, selected_date, self.project_id]
            else:
                sql = f"UPDATE `{db_table_name}` SET `الحالة` = %s, `الوقت_المتبقي` = %s WHERE `id` = %s"
                params = [new_status, new_remaining_time, self.project_id]

            cursor.execute(sql, params)
            conn.commit()

            cursor.close()
            conn.close()

            # رسالة نجاح مفصلة
            success_message = f"تم تحديث حالة المشروع #{self.project_code} بنجاح\n\n"
            success_message += f"الحالة الجديدة: {new_status}\n"
            success_message += f"الوقت المتبقي: {new_remaining_time}\n"
            if update_delivery_date:
                success_message += f"تاريخ التسليم: {selected_date}"

            QMessageBox.information(self, "نجاح", success_message)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الحالة: {str(e)}")
            print(f"Error saving status: {e}")

    # الحصول على بيانات القسم لعرضها في البطاقات العصرية
    # احصل على بيانات القسم للبطاقات
    def get_section_data_for_cards(self, section_name):
        try:
            # الحصول على اسم الجدول من القسم
            table_name = self.get_db_table_name(section_name)
            if not table_name:
                return []
                
            # الاتصال بقاعدة البيانات
            conn = self.get_db_connection()
            if conn is None:
                return []
                
            cursor = conn.cursor(dictionary=True)
            
            # استعلام البيانات حسب نوع القسم
            if section_name == "المشاريع":
                query = """
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM المشاريع p
                    LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                    LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المشاريع'
                    ORDER BY p.تاريخ_الإضافة DESC
                """
                cursor.execute(query)
                data_list = cursor.fetchall()

            elif section_name == "المقاولات":
                query = """
                    SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                    FROM المشاريع p
                    LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                    LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                    WHERE p.اسم_القسم = 'المقاولات'
                    ORDER BY p.تاريخ_الإضافة DESC
                """
                cursor.execute(query)
                data_list = cursor.fetchall()
                
                # حساب الوقت المتبقي لكل مشروع
                for data in data_list:
                    if data.get('تاريخ_التسليم'):
                        try:
                            from datetime import datetime
                            end_date = datetime.strptime(str(data['تاريخ_التسليم']), '%Y-%m-%d')
                            today = datetime.now()
                            remaining_days = (end_date - today).days
                            if remaining_days > 0:
                                data['الوقت_المتبقي_محسوب'] = f"{remaining_days} يوم متبقي"
                            elif remaining_days == 0:
                                data['الوقت_المتبقي_محسوب'] = "ينتهي اليوم"
                            else:
                                data['الوقت_المتبقي_محسوب'] = f"متأخر بـ {abs(remaining_days)} يوم"
                        except:
                            data['الوقت_المتبقي_محسوب'] = "غير محدد"
                    else:
                        data['الوقت_المتبقي_محسوب'] = "غير محدد"
                    
            elif section_name == "العملاء":
                query = """
                    SELECT c.*,
                           COUNT(p.id) as عدد_المشاريع,
                           COALESCE(SUM(p.المبلغ), 0) as إجمالي_القيمة,
                           COALESCE(SUM(p.المدفوع), 0) as إجمالي_المدفوع,
                           COALESCE(SUM(p.الباقي), 0) as إجمالي_الباقي
                    FROM العملاء c
                    LEFT JOIN المشاريع p ON c.id = p.معرف_العميل
                    GROUP BY c.id
                    ORDER BY c.اسم_العميل
                """
                cursor.execute(query)
                data_list = cursor.fetchall()
                
            elif section_name == "الموظفين":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY اسم_الموظف")
                data_list = cursor.fetchall()
                
            elif section_name == "الحسابات":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_المصروف DESC")
                data_list = cursor.fetchall()
                
            elif section_name == "المصروفات":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_المصروف DESC")
                data_list = cursor.fetchall()
            
                
            elif section_name == "التدريب":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_البدء DESC")
                data_list = cursor.fetchall()
            elif section_name == "الموردين":
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY تاريخ_الإنشاء DESC")
                data_list = cursor.fetchall()
                
                
            else:
                # للأقسام الأخرى
                cursor.execute(f"SELECT * FROM `{table_name}`")
                data_list = cursor.fetchall()
                
            cursor.close()
            conn.close()
            return data_list
            
        except Exception as e:
            print(f"خطأ في الحصول على بيانات القسم {section_name}: {e}")
            return []

    # تحديث عرض البطاقات للقسم المحدد مع تطبيق الفلاتر
    # عرض بطاقات التحديث
    def update_cards_view(self, section_name):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                return

            current_view = section_info.get("current_view", "table")
            if current_view == "cards":
                view_stack = section_info.get("view_stack")
                if view_stack and hasattr(view_stack, 'count'):
                    try:
                        if view_stack.count() > 1:
                            cards_view = view_stack.widget(1)
                            if hasattr(cards_view, 'add_cards'):
                                # الحصول على البيانات مع تطبيق الفلاتر
                                cards_data = self.get_filtered_section_data_for_cards(section_name)
                                cards_view.add_cards(cards_data if cards_data else [])

                                # تطبيق الفلاتر الحالية على البطاقات
                                self.apply_current_filters_to_cards(section_name)
                    except RuntimeError:
                        # تجاهل إذا كان الكائن محذوف
                        pass
        except Exception as e:
            print(f"خطأ في تحديث عرض البطاقات: {e}")

    # الحصول على بيانات القسم مع تطبيق الفلاتر لعرضها في البطاقات
    # احصل على بيانات القسم المرشح للبطاقات
    def get_filtered_section_data_for_cards(self, section_name):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                return []

            # الحصول على اسم الجدول من القسم
            table_name = self.get_db_table_name(section_name)
            if not table_name:
                return []

            # الاتصال بقاعدة البيانات
            conn = self.get_db_connection()
            if not conn:
                return []

            cursor = conn.cursor()

            # بناء الاستعلام الأساسي
            if section_name == "المشاريع":
                sql = f"""
                SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                FROM `{table_name}` p
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                WHERE p.اسم_القسم = 'المشاريع'
                """
            elif section_name == "المقاولات":
                sql = f"""
                SELECT p.*, c.اسم_العميل, e.اسم_الموظف as اسم_المهندس_الرئيسي
                FROM `{table_name}` p
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                LEFT JOIN الموظفين e ON p.معرف_المهندس = e.id
                WHERE p.اسم_القسم = 'المقاولات'
                """
            else:
                sql = f"SELECT * FROM `{table_name}`"

            # تطبيق الفلاتر الإضافية
            additional_conditions = []
            params = []

            # فلتر التصنيف
            classification_filter_combo = section_info.get("classification_filter_combo")
            if classification_filter_combo and classification_filter_combo.currentText() != "كل التصنيفات":
                classification_value = classification_filter_combo.currentText()
                if section_name in ["المشاريع", "المقاولات"]:
                    additional_conditions.append("p.`التصنيف` = %s")
                else:
                    additional_conditions.append("`التصنيف` = %s")
                params.append(classification_value)

            # فلتر المسؤول للمشاريع والمقاولات
            responsible_filter_combo = section_info.get("responsible_filter_combo")
            if responsible_filter_combo and responsible_filter_combo.currentText() != "كل المسؤولين":
                responsible_value = responsible_filter_combo.currentText()
                if section_name in ["المشاريع", "المقاولات"]:
                    additional_conditions.append("e.`اسم_الموظف` = %s")
                    params.append(responsible_value)

            # فلتر الحالة
            filter_combo = section_info.get("filter_combo")
            if filter_combo:
                filter_text = filter_combo.currentText()
                # للموظفين، نتحقق من فلتر الحالة
                if section_name == "الموظفين" and filter_text != "كل الحالات":
                    additional_conditions.append("`الحالة` = %s")
                    params.append(filter_text)
                # للمشاريع والمقاولات والتدريب، نتحقق من فلتر الحالة
                elif section_name in ["المشاريع", "المقاولات", "التدريب"] and filter_text != "كل الحالات":
                    if section_name in ["المشاريع", "المقاولات"]:
                        additional_conditions.append("p.`الحالة` = %s")
                    else:
                        additional_conditions.append("`الحالة` = %s")
                    params.append(filter_text)
                # للعملاء والحسابات، نتحقق من فلتر التصنيف (للتوافق مع الكود القديم)
                elif section_name in ["العملاء", "الحسابات"] and filter_text != "كل التصنيفات":
                    additional_conditions.append("`التصنيف` = %s")
                    params.append(filter_text)
                    
                elif section_name == "الموردين" and filter_text != "كل الحالات":
                    additional_conditions.append("`الحالة` = %s")
                    params.append(filter_text)

            # إضافة الشروط الإضافية
            if additional_conditions:
                if section_name in ["المشاريع", "المقاولات"]:
                    sql += " AND " + " AND ".join(additional_conditions)
                else:
                    sql += " WHERE " + " AND ".join(additional_conditions)

            # إضافة ترتيب البيانات
            if section_name == "المشاريع":
                sql += " ORDER BY p.تاريخ_الإضافة DESC"
            elif section_name == "المقاولات":
                sql += " ORDER BY p.تاريخ_الإضافة DESC"
            
            elif section_name == "التدريب":
                sql += " ORDER BY تاريخ_البدء DESC"

            elif section_name == "الموردين":
                sql += " ORDER BY تاريخ_الإنشاء DESC"

            # تنفيذ الاستعلام
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            # تحويل النتائج إلى قائمة من القواميس
            if results:
                columns = [desc[0] for desc in cursor.description]
                data_list = []
                for row in results:
                    row_dict = dict(zip(columns, row))
                    data_list.append(row_dict)
                return data_list
            else:
                return []

        except Exception as e:
            print(f"خطأ في الحصول على البيانات المفلترة للقسم {section_name}: {e}")
            return []

    # تطبيق الفلاتر الحالية على عرض البطاقات
    # تطبيق المرشحات الحالية على البطاقات
    def apply_current_filters_to_cards(self, section_name):
        try:
            section_info = self.sections.get(section_name)
            if not section_info:
                return

            current_view = section_info.get("current_view", "table")
            if current_view != "cards":
                return

            view_stack = section_info.get("view_stack")
            if not view_stack or not hasattr(view_stack, 'count'):
                return
            
            try:
                if view_stack.count() <= 1:
                    return

                cards_view = view_stack.widget(1)
            except RuntimeError:
                # تجاهل إذا كان الكائن محذوف
                return
            if not hasattr(cards_view, 'sync_filters_from_main'):
                return

            # مزامنة الفلاتر من الواجهة الرئيسية إلى البطاقات
            search_text = section_info.get("search_input", "").text() if section_info.get("search_input") else ""

            classification_filter = ""
            if section_info.get("classification_filter_combo"):
                classification_filter = section_info["classification_filter_combo"].currentText()

            status_filter = ""
            if section_info.get("filter_combo"):
                status_filter = section_info["filter_combo"].currentText()

            # تطبيق الفلاتر على البطاقات
            cards_view.sync_filters_from_main(search_text, classification_filter, status_filter)

        except Exception as e:
            print(f"خطأ في تطبيق الفلاتر على البطاقات: {e}")

# تشغيل التطبيق
#------------------------------------------------------------------------------------------
# هو المسؤول
# هو المسؤول
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# تشغيل كمسؤول
# تشغيل كمسؤول
def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# رئيسي
# رئيسي
def main():
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")  # تطبيق الستايل المخصص
    # إنشاء اختصار عام على مستوى التطبيق
    calculator_shortcut = QShortcut(QKeySequence("Alt+C"), app)  # ربط الاختصار بـ QApplication
    calculator_shortcut.activated.connect(lambda: open_calculator())

    voice_shortcut = QShortcut(QKeySequence("Alt+V"), app)
    voice_shortcut.activated.connect(lambda: start_voice_input(app.focusWidget(), None))

    shared_memory_key = 'my_unique_application_key2'
    shared_memory = QSharedMemory(shared_memory_key)
    if not shared_memory.create(1):  # محاولة إنشاء الذاكرة المشتركة
        return
    # if not is_admin():
    #     run_as_admin()
    #     return
    window = MainWindow()
    window.show()

    # التأكد من أن الاختصارات تعمل في أي نافذة نشطة
    app.focusChanged.connect(lambda _, __: (
        calculator_shortcut.setParent(app.focusWidget() or app),
        voice_shortcut.setParent(app.focusWidget() or app)
    ))

    # تعيين الخط العربي
    font = QFont(font_app, 13)
    app.setFont(font)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


