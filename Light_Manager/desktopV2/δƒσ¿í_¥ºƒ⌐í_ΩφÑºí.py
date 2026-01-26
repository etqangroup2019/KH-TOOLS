# cSpell:disable
"""
نافذة إدارة موحدة قابلة للتخصيص
يتم استخدامها كقاعدة لجميع نوافذ الإدارة في التطبيق
"""
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime, date
import json

# استيراد الستايل والمتغيرات
try:
    from ستايل import apply_unified_window_style, apply_table_style, get_color
    from متغيرات import Currency_type
    from الدوال_الأساسية import get_database_connection
except ImportError:
    # قيم افتراضية في حالة عدم توفر الملفات
    Currency_type = "ريال"
    def apply_unified_window_style(widget): pass
    def apply_table_style(widget): pass
    def get_color(name): return "#4CAF50"
    def get_database_connection(): return None

class BaseManagementWindow(QDialog):
    """
    كلاس أساسي موحد لنوافذ الإدارة
    يوفر الهيكل الأساسي والتابات المشتركة
    """
    
    # إشارات مخصصة
    data_updated = pyqtSignal()
    tab_changed = pyqtSignal(int)
    action_requested = pyqtSignal(str, dict)  # نوع العملية، البيانات
    
    def __init__(self, parent=None, main_data=None, window_config=None):
        super().__init__(parent)
        
        # البيانات الأساسية
        self.parent_window = parent
        self.main_data = main_data or {}
        self.config = window_config or {}
        
        # معرف العنصر الرئيسي (مشروع، موظف، عميل، إلخ)
        self.main_id = self.main_data.get('id')
        
        # التكوين الافتراضي
        self.default_config = {
            'window_title': 'نافذة إدارة',
            'entity_name': 'العنصر',
            'icon': 'icons/management.png',
            'size': (1400, 900),
            'tabs_config': [],
            'enable_print': True,
            'enable_export': True,
            'enable_refresh': True,
            'info_tab_fields': [],
            'statistics_cards': [],
            'action_buttons': []
        }
        
        # دمج التكوين مع الافتراضي
        self.config = {**self.default_config, **self.config}
        
        # متغيرات التابات والبيانات
        self.tabs = {}
        self.tables = {}
        self.stat_cards = {}
        self.filters = {}
        self.current_tab_index = 0
        
        # إعداد النافذة
        self.setup_window()
        self.create_main_layout()
        self.create_tabs()
        self.load_initial_data()
        self.connect_signals()
        
    def setup_window(self):
        """إعداد النافذة الأساسية"""
        # حجم ووضعية النافذة
        self.resize(*self.config['size'])
        self.setWindowTitle(self.config['window_title'])
        
        # أيقونة النافذة
        if self.config.get('icon'):
            try:
                self.setWindowIcon(QIcon(self.config['icon']))
            except:
                pass
        
        # تطبيق الستايل
        apply_unified_window_style(self)
        
        # جعل النافذة في المركز
        self.center_window()
        
    def center_window(self):
        """وضع النافذة في وسط الشاشة"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def create_main_layout(self):
        """إنشاء التخطيط الرئيسي"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # شريط العنوان والأزرار العلوية
        self.create_header_section(main_layout)
        
        # التابات الرئيسية
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # شريط الحالة والأزرار السفلية
        self.create_footer_section(main_layout)
        
    def create_header_section(self, parent_layout):
        """إنشاء قسم الرأس (العنوان والأزرار)"""
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QHBoxLayout(header_frame)
        
        # معلومات العنصر الأساسية
        info_section = QHBoxLayout()
        
        # أيقونة العنصر
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setScaledContents(True)
        if self.config.get('icon'):
            try:
                icon_label.setPixmap(QIcon(self.config['icon']).pixmap(48, 48))
            except:
                pass
        info_section.addWidget(icon_label)
        
        # معلومات نصية
        text_info = QVBoxLayout()
        
        # العنوان الرئيسي
        self.main_title_label = QLabel(self.config['window_title'])
        self.main_title_label.setObjectName("main_title")
        text_info.addWidget(self.main_title_label)
        
        # العنوان الفرعي
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subtitle")
        text_info.addWidget(self.subtitle_label)
        
        info_section.addLayout(text_info)
        info_section.addStretch()
        
        header_layout.addLayout(info_section)
        
        # أزرار الإجراءات السريعة
        self.create_action_buttons(header_layout)
        
        parent_layout.addWidget(header_frame)
        
    def create_action_buttons(self, parent_layout):
        """إنشاء أزرار الإجراءات السريعة"""
        buttons_layout = QHBoxLayout()
        
        # أزرار افتراضية
        default_buttons = [
            ('refresh', 'تحديث', 'icons/refresh.png', self.refresh_all_data),
            ('print', 'طباعة', 'icons/print.png', self.print_current_tab),
            ('export', 'تصدير', 'icons/export.png', self.export_current_tab),
        ]
        
        # إضافة الأزرار الافتراضية
        for button_id, text, icon, callback in default_buttons:
            if self.config.get(f'enable_{button_id}', True):
                btn = self.create_action_button(text, icon, callback)
                btn.setObjectName(f"{button_id}_btn")
                buttons_layout.addWidget(btn)
                
        # إضافة أزرار مخصصة من التكوين
        for button_config in self.config.get('action_buttons', []):
            btn = self.create_action_button(
                button_config.get('text', ''),
                button_config.get('icon', ''),
                lambda: self.action_requested.emit(button_config.get('action', ''), {})
            )
            buttons_layout.addWidget(btn)
            
        parent_layout.addLayout(buttons_layout)
        
    def create_action_button(self, text, icon_path, callback):
        """إنشاء زر إجراء"""
        btn = QPushButton(text)
        btn.setFixedHeight(35)
        btn.setMinimumWidth(100)
        
        if icon_path:
            try:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(20, 20))
            except:
                pass
                
        btn.clicked.connect(callback)
        return btn
        
    def create_footer_section(self, parent_layout):
        """إنشاء قسم التذييل"""
        footer_frame = QFrame()
        footer_frame.setObjectName("footer_frame")
        footer_layout = QHBoxLayout(footer_frame)
        
        # شريط الحالة
        self.status_label = QLabel("جاهز")
        self.status_label.setObjectName("status_label")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        # أزرار الإغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.setFixedHeight(35)
        close_btn.clicked.connect(self.close)
        footer_layout.addWidget(close_btn)
        
        parent_layout.addWidget(footer_frame)
        
    def create_tabs(self):
        """إنشاء التابات بناءً على التكوين"""
        # تاب المعلومات الأساسية (دائماً موجود)
        self.create_info_tab()
        
        # التابات المخصصة من التكوين
        for tab_config in self.config.get('tabs_config', []):
            self.create_custom_tab(tab_config)
            
    def create_info_tab(self):
        """إنشاء تاب المعلومات الأساسية"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # إنشاء scroll area للمحتوى
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # القسم العلوي - المعلومات والإحصائيات
        self.create_info_top_section(content_layout)
        
        # القسم السفلي - الجداول والبيانات التفصيلية
        self.create_info_bottom_section(content_layout)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # إضافة التاب
        tab_index = self.tab_widget.addTab(tab, "المعلومات الأساسية")
        self.tabs['info'] = {'widget': tab, 'index': tab_index}
        
    def create_info_top_section(self, parent_layout):
        """إنشاء القسم العلوي لتاب المعلومات"""
        # تخطيط أفقي للحاويات
        top_layout = QHBoxLayout()
        
        # حاوية المعلومات الأساسية
        self.create_basic_info_container(top_layout)
        
        # حاوية المعلومات المالية
        self.create_financial_info_container(top_layout)
        
        # حاوية المعلومات الإضافية
        self.create_additional_info_container(top_layout)
        
        parent_layout.addLayout(top_layout)
        
        # بطاقات الإحصائيات
        self.create_statistics_cards(parent_layout)
        
    def create_basic_info_container(self, parent_layout):
        """إنشاء حاوية المعلومات الأساسية"""
        container = self.create_info_container("المعلومات الأساسية", "#2196F3")
        layout = container.layout()
        
        # الحقول الأساسية من التكوين
        basic_fields = self.config.get('info_tab_fields', {}).get('basic', [])
        
        for field_config in basic_fields:
            label = QLabel(field_config.get('label', ''))
            value_label = QLabel()
            value_label.setObjectName(f"{field_config.get('key', '')}_label")
            
            # تخطيط الحقل
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addStretch()
            field_layout.addWidget(value_label)
            
            layout.addLayout(field_layout)
            
        parent_layout.addWidget(container)
        
    def create_financial_info_container(self, parent_layout):
        """إنشاء حاوية المعلومات المالية"""
        container = self.create_info_container("المعلومات المالية", "#4CAF50")
        layout = container.layout()
        
        # الحقول المالية من التكوين
        financial_fields = self.config.get('info_tab_fields', {}).get('financial', [])
        
        for field_config in financial_fields:
            label = QLabel(field_config.get('label', ''))
            value_label = QLabel()
            value_label.setObjectName(f"{field_config.get('key', '')}_label")
            
            # تخطيط الحقل
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addStretch()
            field_layout.addWidget(value_label)
            
            layout.addLayout(field_layout)
            
        parent_layout.addWidget(container)
        
    def create_additional_info_container(self, parent_layout):
        """إنشاء حاوية المعلومات الإضافية"""
        container = self.create_info_container("معلومات إضافية", "#FF9800")
        layout = container.layout()
        
        # الحقول الإضافية من التكوين
        additional_fields = self.config.get('info_tab_fields', {}).get('additional', [])
        
        for field_config in additional_fields:
            label = QLabel(field_config.get('label', ''))
            value_label = QLabel()
            value_label.setObjectName(f"{field_config.get('key', '')}_label")
            
            # تخطيط الحقل
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addStretch()
            field_layout.addWidget(value_label)
            
            layout.addLayout(field_layout)
            
        parent_layout.addWidget(container)
        
    def create_info_container(self, title, color):
        """إنشاء حاوية معلومات مع عنوان وستايل موحد"""
        group_box = QGroupBox(title)
        group_box.setObjectName("info_container")
        
        layout = QVBoxLayout(group_box)
        layout.setSpacing(10)
        
        # تطبيق ستايل مخصص
        group_box.setStyleSheet(f"""
            QGroupBox#info_container {{
                font-weight: bold;
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 5px;
            }}
            QGroupBox#info_container::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {color};
            }}
        """)
        
        return group_box
        
    def create_statistics_cards(self, parent_layout):
        """إنشاء بطاقات الإحصائيات"""
        cards_frame = QFrame()
        cards_layout = QHBoxLayout(cards_frame)
        
        # إنشاء البطاقات من التكوين
        for card_config in self.config.get('statistics_cards', []):
            card = self.create_stat_card(
                card_config.get('title', ''),
                card_config.get('value', '0'),
                card_config.get('color', '#4CAF50'),
                card_config.get('key', '')
            )
            cards_layout.addWidget(card)
            
        cards_layout.addStretch()
        parent_layout.addWidget(cards_frame)
        
    def create_stat_card(self, title, value, color, key):
        """إنشاء بطاقة إحصائية"""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedHeight(100)
        card.setMinimumWidth(200)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # العنوان
        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # القيمة
        value_label = QLabel(str(value))
        value_label.setObjectName("card_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # حفظ مرجع البطاقة
        if key:
            self.stat_cards[key] = value_label
            
        # تطبيق الستايل
        card.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: {color};
                border-radius: 8px;
                margin: 5px;
            }}
            QLabel#card_title {{
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            QLabel#card_value {{
                color: white;
                font-weight: bold;
                font-size: 18px;
            }}
        """)
        
        return card
        
    def create_info_bottom_section(self, parent_layout):
        """إنشاء القسم السفلي لتاب المعلومات"""
        # يمكن تخصيصه في الكلاسات الفرعية
        pass
        
    def create_custom_tab(self, tab_config):
        """إنشاء تاب مخصص بناءً على التكوين"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # شريط الفلاتر والبحث
        if tab_config.get('enable_filters', True):
            self.create_tab_filters(layout, tab_config)
            
        # بطاقات الإحصائيات للتاب
        if tab_config.get('statistics_cards'):
            self.create_tab_statistics_cards(layout, tab_config)
            
        # الجدول الرئيسي
        if tab_config.get('table_config'):
            table = self.create_tab_table(layout, tab_config)
            self.tables[tab_config['key']] = table
            
        # أزرار الإجراءات
        if tab_config.get('action_buttons'):
            self.create_tab_action_buttons(layout, tab_config)
            
        # إضافة التاب
        tab_index = self.tab_widget.addTab(tab, tab_config.get('title', 'تاب'))
        self.tabs[tab_config['key']] = {
            'widget': tab, 
            'index': tab_index, 
            'config': tab_config
        }
        
    def create_tab_filters(self, parent_layout, tab_config):
        """إنشاء شريط الفلاتر للتاب"""
        filters_frame = QFrame()
        filters_frame.setObjectName("filters_frame")
        filters_layout = QHBoxLayout(filters_frame)
        
        # حقل البحث
        search_input = QLineEdit()
        search_input.setPlaceholderText("البحث...")
        search_input.setFixedWidth(200)
        filters_layout.addWidget(QLabel("البحث:"))
        filters_layout.addWidget(search_input)
        
        # فلاتر مخصصة من التكوين
        for filter_config in tab_config.get('filters', []):
            filter_widget = self.create_filter_widget(filter_config)
            filters_layout.addWidget(QLabel(filter_config.get('label', '')))
            filters_layout.addWidget(filter_widget)
            
        filters_layout.addStretch()
        
        # زر تطبيق الفلتر
        apply_filter_btn = QPushButton("تطبيق الفلتر")
        apply_filter_btn.clicked.connect(
            lambda: self.apply_tab_filter(tab_config['key'])
        )
        filters_layout.addWidget(apply_filter_btn)
        
        parent_layout.addWidget(filters_frame)
        
    def create_filter_widget(self, filter_config):
        """إنشاء أداة فلتر بناءً على النوع"""
        filter_type = filter_config.get('type', 'text')
        
        if filter_type == 'text':
            widget = QLineEdit()
            widget.setPlaceholderText(filter_config.get('placeholder', ''))
        elif filter_type == 'combo':
            widget = QComboBox()
            widget.addItems(filter_config.get('options', []))
        elif filter_type == 'date':
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
        elif filter_type == 'daterange':
            widget = QFrame()
            layout = QHBoxLayout(widget)
            start_date = QDateEdit()
            end_date = QDateEdit()
            layout.addWidget(start_date)
            layout.addWidget(QLabel("إلى"))
            layout.addWidget(end_date)
        else:
            widget = QLineEdit()
            
        return widget
        
    def create_tab_statistics_cards(self, parent_layout, tab_config):
        """إنشاء بطاقات إحصائيات للتاب"""
        cards_frame = QFrame()
        cards_layout = QHBoxLayout(cards_frame)
        
        for card_config in tab_config.get('statistics_cards', []):
            card = self.create_stat_card(
                card_config.get('title', ''),
                card_config.get('value', '0'),
                card_config.get('color', '#4CAF50'),
                f"{tab_config['key']}_{card_config.get('key', '')}"
            )
            cards_layout.addWidget(card)
            
        cards_layout.addStretch()
        parent_layout.addWidget(cards_frame)
        
    def create_tab_table(self, parent_layout, tab_config):
        """إنشاء جدول للتاب"""
        table = QTableWidget()
        apply_table_style(table)
        
        # إعداد الجدول من التكوين
        table_config = tab_config.get('table_config', {})
        
        # الأعمدة
        columns = table_config.get('columns', [])
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels([col.get('title', '') for col in columns])
        
        # خصائص الجدول
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        
        # الأحداث
        table.doubleClicked.connect(
            lambda: self.on_table_double_click(tab_config['key'])
        )
        
        parent_layout.addWidget(table)
        return table
        
    def create_tab_action_buttons(self, parent_layout, tab_config):
        """إنشاء أزرار الإجراءات للتاب"""
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        for button_config in tab_config.get('action_buttons', []):
            btn = QPushButton(button_config.get('text', ''))
            
            if button_config.get('icon'):
                try:
                    btn.setIcon(QIcon(button_config['icon']))
                except:
                    pass
                    
            btn.clicked.connect(
                lambda checked, action=button_config.get('action'): 
                self.action_requested.emit(action, {'tab': tab_config['key']})
            )
            
            buttons_layout.addWidget(btn)
            
        buttons_layout.addStretch()
        parent_layout.addWidget(buttons_frame)
        
    def load_initial_data(self):
        """تحميل البيانات الأولية"""
        self.update_window_title()
        self.load_info_data()
        self.update_statistics()
        
    def update_window_title(self):
        """تحديث عنوان النافذة"""
        if self.main_data:
            entity_name = self.main_data.get('name', self.config['entity_name'])
            title = f"{self.config['window_title']} - {entity_name}"
            self.setWindowTitle(title)
            self.main_title_label.setText(title)
            
    def load_info_data(self):
        """تحميل بيانات تاب المعلومات"""
        # يتم تخصيصها في الكلاسات الفرعية
        pass
        
    def update_statistics(self):
        """تحديث الإحصائيات"""
        # يتم تخصيصها في الكلاسات الفرعية
        pass
        
    def update_stat_card(self, key, value):
        """تحديث قيمة بطاقة إحصائية"""
        if key in self.stat_cards:
            self.stat_cards[key].setText(str(value))
            
    def load_tab_data(self, tab_key):
        """تحميل بيانات تاب معين"""
        # يتم تخصيصها في الكلاسات الفرعية
        pass
        
    def apply_tab_filter(self, tab_key):
        """تطبيق فلتر على تاب معين"""
        # يتم تخصيصها في الكلاسات الفرعية
        pass
        
    def refresh_all_data(self):
        """تحديث جميع البيانات"""
        self.load_info_data()
        self.update_statistics()
        
        for tab_key in self.tabs.keys():
            if tab_key != 'info':
                self.load_tab_data(tab_key)
                
        self.status_label.setText("تم تحديث البيانات")
        
    def print_current_tab(self):
        """طباعة التاب الحالي"""
        current_index = self.tab_widget.currentIndex()
        tab_key = None
        
        for key, tab_info in self.tabs.items():
            if tab_info['index'] == current_index:
                tab_key = key
                break
                
        if tab_key:
            self.action_requested.emit('print', {'tab': tab_key})
            
    def export_current_tab(self):
        """تصدير التاب الحالي"""
        current_index = self.tab_widget.currentIndex()
        tab_key = None
        
        for key, tab_info in self.tabs.items():
            if tab_info['index'] == current_index:
                tab_key = key
                break
                
        if tab_key:
            self.action_requested.emit('export', {'tab': tab_key})
            
    def on_tab_changed(self, index):
        """معالج تغيير التاب"""
        self.current_tab_index = index
        
        # تحميل بيانات التاب المحدد
        for tab_key, tab_info in self.tabs.items():
            if tab_info['index'] == index:
                self.load_tab_data(tab_key)
                break
                
        self.tab_changed.emit(index)
        
    def on_table_double_click(self, tab_key):
        """معالج النقر المزدوج على الجدول"""
        table = self.tables.get(tab_key)
        if table and table.currentRow() >= 0:
            row_data = self.get_table_row_data(table, table.currentRow())
            self.action_requested.emit('edit', {
                'tab': tab_key,
                'row_data': row_data
            })
            
    def get_table_row_data(self, table, row):
        """الحصول على بيانات صف من الجدول"""
        data = {}
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col)
            if header:
                item = table.item(row, col)
                data[header.text()] = item.text() if item else ""
        return data
        
    def connect_signals(self):
        """ربط الإشارات"""
        self.action_requested.connect(self.handle_action_request)
        
    def handle_action_request(self, action, data):
        """معالج طلبات الإجراءات"""
        # يتم تخصيصها في الكلاسات الفرعية
        print(f"Action requested: {action} with data: {data}")
        
    def show_message(self, title, message, msg_type="info"):
        """عرض رسالة للمستخدم"""
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "question":
            return QMessageBox.question(self, title, message) == QMessageBox.StandardButton.Yes
            
    def set_status(self, message):
        """تعيين رسالة الحالة"""
        self.status_label.setText(message)
        
    def get_database_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        try:
            return get_database_connection()
        except:
            return None


# مثال على الاستخدام
class ProjectManagementWindow(BaseManagementWindow):
    """مثال لاستخدام النافذة الموحدة لإدارة المشاريع"""
    
    def __init__(self, parent=None, project_data=None):
        # تكوين خاص بنافذة المشاريع
        config = {
            'window_title': 'إدارة المشروع',
            'entity_name': 'المشروع',
            'icon': 'icons/project.png',
            'info_tab_fields': {
                'basic': [
                    {'key': 'project_name', 'label': 'اسم المشروع'},
                    {'key': 'client_name', 'label': 'اسم العميل'},
                    {'key': 'start_date', 'label': 'تاريخ البداية'},
                    {'key': 'end_date', 'label': 'تاريخ النهاية'},
                ],
                'financial': [
                    {'key': 'total_amount', 'label': 'المبلغ الإجمالي'},
                    {'key': 'paid_amount', 'label': 'المبلغ المدفوع'},
                    {'key': 'remaining_amount', 'label': 'المبلغ المتبقي'},
                ],
                'additional': [
                    {'key': 'status', 'label': 'الحالة'},
                    {'key': 'completion_percentage', 'label': 'نسبة الإنجاز'},
                ]
            },
            'statistics_cards': [
                {'key': 'phases', 'title': 'المراحل', 'value': '0', 'color': '#2196F3'},
                {'key': 'tasks', 'title': 'المهام', 'value': '0', 'color': '#4CAF50'},
                {'key': 'payments', 'title': 'الدفعات', 'value': '0', 'color': '#FF9800'},
            ],
            'tabs_config': [
                {
                    'key': 'phases',
                    'title': 'مراحل المشروع',
                    'table_config': {
                        'columns': [
                            {'key': 'name', 'title': 'اسم المرحلة'},
                            {'key': 'amount', 'title': 'المبلغ'},
                            {'key': 'status', 'title': 'الحالة'},
                        ]
                    },
                    'action_buttons': [
                        {'text': 'إضافة مرحلة', 'action': 'add_phase', 'icon': 'icons/add.png'},
                        {'text': 'تعديل مرحلة', 'action': 'edit_phase', 'icon': 'icons/edit.png'},
                    ]
                }
            ]
        }
        
        super().__init__(parent, project_data, config)
        
    def load_info_data(self):
        """تحميل بيانات المشروع"""
        if self.main_data:
            # تحديث الحقول من البيانات
            for field_group in self.config['info_tab_fields'].values():
                for field in field_group:
                    label = self.findChild(QLabel, f"{field['key']}_label")
                    if label and field['key'] in self.main_data:
                        label.setText(str(self.main_data[field['key']]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # بيانات تجريبية
    project_data = {
        'id': 1,
        'name': 'مشروع تجريبي',
        'project_name': 'مشروع تصميم فيلا',
        'client_name': 'أحمد محمد',
        'total_amount': '150000',
        'paid_amount': '75000',
        'remaining_amount': '75000',
        'status': 'قيد التنفيذ',
        'completion_percentage': '50%'
    }
    
    window = ProjectManagementWindow(project_data=project_data)
    window.show()
    
    sys.exit(app.exec()) 