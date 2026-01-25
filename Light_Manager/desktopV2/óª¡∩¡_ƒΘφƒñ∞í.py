from الإعدادات_العامة import*

#تثبيت الخطوط ===================================================================================================
# تثبيت جميع الخطوط
def install_all_fonts(self,fonts_dir):
    # مسارات مجلدات الخطوط
    local_fonts_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Windows", "Fonts")
    system_fonts_dir = r"C:\Windows\Fonts"
    # التأكد من أن المجلدات موجودة
    os.makedirs(local_fonts_dir, exist_ok=True)
    # التأكد من أن مجلد الخطوط الأصلي موجود
    if not os.path.isdir(fonts_dir):
        QMessageBox.information(self, "مشكلة في تثبيت الخطوط", "مجلد الخطوط غير موجود.")
        return False
    # البحث عن جميع الخطوط في المجلد
    font_files = [f for f in os.listdir(fonts_dir) if f.lower().endswith(('.ttf', '.otf'))]
    if not font_files:
        QMessageBox.information(self, "مشكلة في تثبيت الخطوط", "لا توجد ملفات خطوط في المجلد.")
        return False

    FR_PRIVATE = 0x10
    installed_count = 0
    for font_file in font_files:
        source_font_path = os.path.join(fonts_dir, font_file)
        local_target_path = os.path.join(local_fonts_dir, font_file)
        system_target_path = os.path.join(system_fonts_dir, font_file)
        # التحقق من وجود الخط مسبقًا في مجلدات الخطوط
        if not os.path.exists(local_target_path):
            try:
                shutil.copy(source_font_path, local_target_path)
            except Exception as e:
                QMessageBox.information(self, "خطأ في نسخ الخط", f"تعذر نسخ الخط {font_file} إلى مجلد AppData.\n{str(e)}")

        if not os.path.exists(system_target_path):
            try:
                shutil.copy(source_font_path, system_target_path)
                add_font_to_registry(self,font_file)  # إضافة الخط إلى الريجستري
            except Exception as e:
                QMessageBox.information(self, "خطأ في نسخ الخط", f"تعذر نسخ الخط {font_file} إلى C:\\Windows\\Fonts.\n{str(e)}")

        # تثبيت الخط في النظام
        result = ctypes.windll.gdi32.AddFontResourceExW(system_target_path, FR_PRIVATE, 0)
        if result > 0:
            installed_count += 1

    if installed_count > 0:
        # إرسال رسالة إلى النظام لتحديث قائمة الخطوط
        ctypes.windll.user32.PostMessageW(0xFFFF, 0x1D, 0, 0)
        #QMessageBox.information(self, "تثبيت الخطوط", f"تم تثبيت {installed_count} خط/خطوط بنجاح.")
        return True
    else:
        QMessageBox.information(self, "مشكلة في تثبيت الخطوط", "لم يتم تثبيت أي خط.")
        return False

# إضافة الخط إلى الريجستري لجعله متاحًا دائمًا في النظام
def add_font_to_registry(self,font_name):
    font_registry_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    font_extension = os.path.splitext(font_name)[1].lower()
    
    if font_extension == ".ttf":
        font_type = font_name + " (TrueType)"
    elif font_extension == ".otf":
        font_type = font_name + " (OpenType)"
    else:
        return
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, font_registry_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, font_type, 0, winreg.REG_SZ, font_name)
    except Exception as e:
        QMessageBox.information(self, "خطأ في الريجستري", f"تعذر إضافة الخط {font_name} إلى الريجستري.\n{str(e)}")


#انشاء ملف التخصيص============================================
# إنشاء تخصيص JSON
def create_customization_json():
    os.makedirs(application_path, exist_ok=True)
    if not os.path.exists(Customize_json_path):
        with open(Customize_json_path, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)

# #استيراد الاعدادات ////////////////////////////////////////////////////////////////////////// 
#تحديث لون الخلفية
# UpdateInterFaceColor
def updateInterfaceColor(self, color):
    if color.isValid():
        table_name = self.Interface_combo.currentText()
        color_code = color.name()
        # التأكد من وجود المجلد
        os.makedirs(folder_path, exist_ok=True)
        # تحميل البيانات الحالية من JSON (إذا كان الملف موجودًا)
        if os.path.exists(Customize_json_path):
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                try:
                    settings_data = json.load(f)
                except json.JSONDecodeError:
                    settings_data = {}  # في حال كان هناك خطأ، استخدم قاموس فارغ
        else:
            settings_data = {}  # إذا لم يكن الملف موجودًا، أنشئ قاموس فارغ
        # تحديث الإعدادات في `QSettings`
        # تحديث أو إضافة اللون الجديد في JSON
        settings_data[table_name] = color_code
        # حفظ التعديلات في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
        # تطبيق اللون على الواجهة
        self.Basic_Styles()

#لون الازرار ======================================================================
# تغيير لون الازرار وحفظ القيمة في ملف JSON
def updateButtonsColor(self, color):
    # فتح نافذة لاختيار اللون
    if color.isValid():  # التأكد من أن المستخدم لم يغلق النافذة بدون اختيار لون
        button_color = color.name()  # الحصول على كود اللون (Hex)
        # التأكد من وجود المجلد
        os.makedirs(folder_path, exist_ok=True)
        # تحميل البيانات الحالية من JSON (إذا كان الملف موجودًا)
        if os.path.exists(Customize_json_path):
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                try:
                    settings_data = json.load(f)
                except json.JSONDecodeError:
                    settings_data = {}  # في حال كان هناك خطأ، استخدم قاموس فارغ
        else:
            settings_data = {}  # إذا لم يكن الملف موجودًا، أنشئ قاموس فارغ
        # تحديث قيمة لون الازرار في JSON
        settings_data["لون الازرار"] = button_color
        # حفظ التعديلات في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
            
    self.Basic_Styles()

#لون الادخال ======================================================================
# تغيير لون الادخال وحفظ القيمة في ملف JSON
def updateinputColor(self, color):
    # فتح نافذة لاختيار اللون
    if color.isValid():  # التأكد من أن المستخدم لم يغلق النافذة بدون اختيار لون
        button_color = color.name()  # الحصول على كود اللون (Hex)
        # التأكد من وجود المجلد
        os.makedirs(folder_path, exist_ok=True)
        # تحميل البيانات الحالية من JSON (إذا كان الملف موجودًا)
        if os.path.exists(Customize_json_path):
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                try:
                    settings_data = json.load(f)
                except json.JSONDecodeError:
                    settings_data = {}  # في حال كان هناك خطأ، استخدم قاموس فارغ
        else:
            settings_data = {}  # إذا لم يكن الملف موجودًا، أنشئ قاموس فارغ
        # تحديث قيمة لون الازرار في JSON
        settings_data["لون الادخال"] = button_color
        # حفظ التعديلات في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
            
    self.Basic_Styles()

#لون الجدول ======================================================================
# تغيير لون الادخال وحفظ القيمة في ملف JSON
def updateTableColor(self, color):
    # فتح نافذة لاختيار اللون
    if color.isValid():  # التأكد من أن المستخدم لم يغلق النافذة بدون اختيار لون
        button_color = color.name()  # الحصول على كود اللون (Hex)
        # التأكد من وجود المجلد
        os.makedirs(folder_path, exist_ok=True)
        # تحميل البيانات الحالية من JSON (إذا كان الملف موجودًا)
        if os.path.exists(Customize_json_path):
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                try:
                    settings_data = json.load(f)
                except json.JSONDecodeError:
                    settings_data = {}  # في حال كان هناك خطأ، استخدم قاموس فارغ
        else:
            settings_data = {}  # إذا لم يكن الملف موجودًا، أنشئ قاموس فارغ
        # تحديث قيمة لون الازرار في JSON
        settings_data["لون الجدول"] = button_color
        # حفظ التعديلات في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
            
    self.Basic_Styles()

#لون الخط العام ======================================================================
# تغيير لون الادخال وحفظ القيمة في ملف JSON
def updatefontColor(self, color):
    # فتح نافذة لاختيار اللون
    if color.isValid():  # التأكد من أن المستخدم لم يغلق النافذة بدون اختيار لون
        button_color = color.name()  # الحصول على كود اللون (Hex)
        # التأكد من وجود المجلد
        os.makedirs(folder_path, exist_ok=True)
        # تحميل البيانات الحالية من JSON (إذا كان الملف موجودًا)
        if os.path.exists(Customize_json_path):
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                try:
                    settings_data = json.load(f)
                except json.JSONDecodeError:
                    settings_data = {}  # في حال كان هناك خطأ، استخدم قاموس فارغ
        else:
            settings_data = {}  # إذا لم يكن الملف موجودًا، أنشئ قاموس فارغ
        # تحديث قيمة لون الازرار في JSON
        settings_data["لون الخط العام"] = button_color
        # حفظ التعديلات في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
            
    self.Basic_Styles()

#تغيير خط الجدول================================================================================
# changetablefont
def changeTableFont(self):      
    font_family = "Janna LT"  # القيمة الافتراضية لنوع الخط
    font_size = 16 # القيمة الافتراضية لحجم الخط
    font_weight = QFont.Normal
    # التأكد من وجود ملف JSON وقراءة الإعدادات منه
    if os.path.exists(Customize_json_path):
        with open(Customize_json_path, "r", encoding="utf-8") as f:
            try:
                settings_data = json.load(f)
                font_family = settings_data.get("نوع خط الجدول", font_family)
                font_size_str  = settings_data.get("حجم خط الجدول", font_size)
                font_weight = int(settings_data.get("وزن خط الجدول", font_weight))  # تحويل الوزن إلى int
                if 'px' in str(font_size_str):
                    font_size_str = font_size_str.replace('px', '')  # إزالة px
                font_size = int(font_size_str)  # تحويل الحجم إلى عدد صحيح
            except json.JSONDecodeError:
                pass  # في حالة وجود خطأ في قراءة البيانات
    # تعيين الخط والحجم في نافذة QFontDialog
    initial_font = QFont(font_family, int(font_size),font_weight)  # التأكد من أن الحجم هو عدد صحيح
    TableFontDialog = QFontDialog(initial_font, self)
    TableFontDialog.currentFontChanged.connect(self.updateTableFont)  # تحديث الخط مباشرة

    # إضافة زر لاستعادة الافتراضيات
    reset_button = QPushButton("استعادة الافتراضيات", TableFontDialog)
    reset_button.clicked.connect(lambda: reset_Castom(self,"نوع خط الجدول","حجم خط الجدول","وزن خط الجدول"))

    layout = TableFontDialog.layout()
    layout.addWidget(reset_button)  # إضافة الزر إلى النافذة

    # يمكنك إضافة إعدادات النافذة هنا حسب الحاجة
    TableFontDialog.setOption(QFontDialog.NoButtons)  # إخفاء الازرار إذا أردت
    TableFontDialog.exec()  # عرض النافذة بشكل حواري (معطل)

#تغيير الخط ==========================================================================
# Changefont
def changeFont(self,name,size,weight_key,fanc):     
    font_family = "Janna LT"  # القيمة الافتراضية لنوع الخط
    font_size = 16 # القيمة الافتراضية لحجم الخط
    font_weight = QFont.Normal  # القيمة الافتراضية لوزن الخط
    # التأكد من وجود ملف JSON وقراءة الإعدادات منه
    if os.path.exists(Customize_json_path):
        with open(Customize_json_path, "r", encoding="utf-8") as f:
            try:
                settings_data = json.load(f)
                font_family = settings_data.get(name, font_family)
                font_size_str  = settings_data.get(size, font_size)
                font_weight = int(settings_data.get(weight_key, font_weight))  # استرجاع الوزن
                if 'px' in str(font_size_str):
                    font_size_str = font_size_str.replace('px', '')  # إزالة px
                font_size = int(font_size_str)  # تحويل الحجم إلى عدد صحيح
            except json.JSONDecodeError:
                pass  # في حالة وجود خطأ في قراءة البيانات
    # تعيين الخط والحجم في نافذة QFontDialog
    initial_font = QFont(font_family, int(font_size),font_weight)  # التأكد من أن الحجم هو عدد صحيح
  
    TableFontDialog = QFontDialog(initial_font, self)
    TableFontDialog.currentFontChanged.connect(fanc)  # تحديث الخط مباشرة

    # إضافة زر لاستعادة الافتراضيات
    reset_button = QPushButton("استعادة الافتراضيات")
    reset_button.clicked.connect(lambda: reset_Castom(self,name,size,weight_key))

    layout = self.findChild(QFontDialog).layout()
    layout.addWidget(reset_button)

    # يمكنك إضافة إعدادات النافذة هنا حسب الحاجة
    TableFontDialog.setOption(QFontDialog.NoButtons)  # إخفاء الازرار إذا أردت
    TableFontDialog.exec()  # عرض النافذة بشكل حواري (معطل)

#تحديث الخط
# UpdateFont
def updateFont(self,font,name,size, weight_key):
    if font:   # إذا ضغط المستخدم على "موافق"
        font_family = font.family()  # نوع الخط
        font_size = font.pointSize()  # حجم الخط
        font_weight = font.weight()  # وزن الخط
        # التأكد من وجود المجلد
        os.makedirs(folder_path, exist_ok=True)
        # تحميل البيانات الحالية من JSON (إذا كان الملف موجودًا)
        if os.path.exists(Customize_json_path):
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                try:
                    settings_data = json.load(f)
                except json.JSONDecodeError:
                    settings_data = {}  # في حال كان هناك خطأ، استخدم قاموس فارغ
        else:
            settings_data = {}  # إذا لم يكن الملف موجودًا، أنشئ قاموس فارغ
        # تحديث القيم في JSON
        settings_data[name] = font_family
        settings_data[size] = str(font_size)+"px"
        settings_data[weight_key] = str(font_weight)  # تخزين وزن الخط
        # حفظ التعديلات في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)        
        self.Basic_Styles()


#إعادة تعيين الواجهة ===============================================================
# Resettodefault
def resetToDefault(self):
    reply = QMessageBox.question(None,
        "استعادة تنسيق الواجهة",
        "هل تريد استعادة تنسيق الواجهة؟",
        QMessageBox.Yes | QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        """إعادة تعيين جميع الإعدادات إلى القيم الافتراضية"""
        default_settings = {}
        
        # حفظ القيم الافتراضية في ملف JSON
        with open(Customize_json_path, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=4)

        # إعادة تحميل الإعدادات المحدثة في الواجهة
        self.Basic_Styles()
        QMessageBox.information(self, "تم الاستعادة", "تمت استعادة تنسيق الواجهة بنجاح.")
    else:
        pass

# إعادة تعيين Castom
def reset_Castom(self,delet,size,weight):
    reply = QMessageBox.question(None,
        "استعادة تنسيق الواجهة",
        "هل تريد استعادة تنسيق الواجهة؟",
        QMessageBox.Yes | QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        try:
            # تحميل البيانات من الملف
            with open(Customize_json_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            if delet in settings:
                del settings[delet]

                if size in settings:
                    del settings[size]

                elif weight in settings:
                    del settings[weight]

                # إعادة حفظ البيانات بعد الحذف
                with open(Customize_json_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)

                
            else:
                print("المفتاح 'لون الازرار' غير موجود في الملف.")

        except FileNotFoundError:
            print("الملف غير موجود.")
        except json.JSONDecodeError:
            print("خطأ في قراءة ملف JSON.")
        # إعادة تحميل الإعدادات المحدثة في الواجهة
        self.Basic_Styles()
        QMessageBox.information(self, "تم الاستعادة", "تمت استعادة تنسيق الواجهة بنجاح.")
    else:
        pass

#تلوين الايقونات----------------------------------------------------

import os
import sys
import re

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QColorDialog, QMessageBox, QSpinBox
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QColor
from PySide6.QtCore import Qt, QFileSystemWatcher


# يغير لون fill وأبعاد (width, height) داخل ملفات SVG.
def fix_nested_svg_elements(content):
    """
    إصلاح عناصر SVG المتداخلة في المحتوى
    """
    # البحث عن عناصر svg متداخلة
    nested_svg_pattern = re.compile(r'<svg[^>]*>.*?<svg[^>]*>', re.DOTALL)
    
    # إذا وجدت عناصر متداخلة، قم بإزالة العناصر الداخلية
    if nested_svg_pattern.search(content):
        # إزالة جميع عناصر svg الداخلية عدا الأول
        svg_count = content.count('<svg')
        if svg_count > 1:
            # الاحتفاظ بأول عنصر svg والمحتوى الداخلي
            content = re.sub(r'<svg[^>]*>(?=.*<svg)', '', content, flags=re.DOTALL)
            content = re.sub(r'</svg>(?=.*</svg>)', '', content, flags=re.DOTALL)
            
    return content

def change_svg_fill_color_and_size(folder_path, color, width, height):
    hex_color = color.name()
    count = 0
    fill_pattern = re.compile(r'fill="[^"]*"')
    size_pattern = re.compile(r'(width|height)="[^"]*"')

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.svg'):
            full_path = os.path.join(folder_path, filename)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # إصلاح عناصر SVG المتداخلة
                content = fix_nested_svg_elements(content)

                # تغيير اللون
                content = fill_pattern.sub(f'fill="{hex_color}"', content)

                # تغيير الأبعاد (width و height)
                # نستبدل قيم width و height كلها مباشرة
                # أولاً نتاكد أن هناك width و height موجودين
                if 'width="' in content and 'height="' in content:
                    content = re.sub(r'width="[^"]*"', f'width="{width}"', content)
                    content = re.sub(r'height="[^"]*"', f'height="{height}"', content)
                else:
                    # لو ما موجودين، نضيفهم بعد <svg
                    content = re.sub(r'<svg([^>]*)', f'<svg\\1 width="{width}" height="{height}"', content, 1)

                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                count += 1
            except Exception as e:
                print(f"فشل تعديل {filename}: {e}")

    return count


# svgcolorchanger
class SvgColorChanger(QWidget):
    # init
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مغير لون وحجم ملفات SVG")
        self.resize(700, 200)

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        self.folder_path = os.path.join(application_path, 'icons')
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.selected_color = QColor("#000000")
        self.width = 256
        self.height = 256

        self.setAcceptDrops(True)
        self.init_ui()
        self.init_watcher()

    # init
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # مسار المجلد
        folder_layout = QHBoxLayout()
        self.folder_edit = QLabel(self.folder_path)
        browse_btn = QPushButton("اختر مجلد")
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(QLabel("مسار المجلد:"))
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)

        # اختيار اللون
        color_layout = QHBoxLayout()
        self.color_display = QLabel()
        self.color_display.setFixedSize(50, 25)
        self.color_display.setStyleSheet(f"background-color: {self.selected_color.name()}; border: 1px solid #666;")
        choose_color_btn = QPushButton("اختر لون")
        choose_color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(QLabel("اللون:"))
        color_layout.addWidget(self.color_display)
        color_layout.addWidget(choose_color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # تغيير الحجم (العرض والارتفاع)
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("العرض (px):"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 1000)
        self.width_spin.setValue(self.width)
        size_layout.addWidget(self.width_spin)

        size_layout.addWidget(QLabel("الارتفاع (px):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 1000)
        self.height_spin.setValue(self.height)
        size_layout.addWidget(self.height_spin)

        size_layout.addStretch()
        layout.addLayout(size_layout)

        # زر التنفيذ
        self.start_btn = QPushButton("غير لون وحجم جميع ملفات SVG")
        self.start_btn.clicked.connect(self.start_conversion)
        layout.addWidget(self.start_btn)

        # زر إصلاح ملفات SVG
        self.fix_svg_btn = QPushButton("إصلاح ملفات SVG (إزالة العناصر المتداخلة)")
        self.fix_svg_btn.clicked.connect(self.fix_svg_files)
        layout.addWidget(self.fix_svg_btn)

        # عداد الملفات
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # ربط التغير في spinbox بالتحديث التلقائي
        self.width_spin.valueChanged.connect(self.on_size_changed)
        self.height_spin.valueChanged.connect(self.on_size_changed)

        self.update_status_label()

    # مراقب init
    def init_watcher(self):
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.folder_path)
        self.watcher.directoryChanged.connect(self.on_directory_changed)

    # على الدليل تغيرت
    def on_directory_changed(self, path):
        self.update_status_label()

    # تحديث تسمية الحالة
    def update_status_label(self):
        try:
            files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.svg')]
            self.status_label.setText(f"عدد ملفات SVG في المجلد: {len(files)} | حجم الصور: {self.width}x{self.height} px")
        except Exception:
            self.status_label.setText("المجلد غير صالح أو لا يمكن الوصول إليه.")

    # مجلد تصفح
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد")
        if folder:
            self.folder_path = folder
            self.folder_edit.setText(folder)
            self.watcher.removePaths(self.watcher.directories())
            self.watcher.addPath(folder)
            self.update_status_label()

    # اختر اللون
    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self, "اختر لون")
        if color.isValid():
            self.selected_color = color
            self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #666;")

    # على الحجم تغيرت
    def on_size_changed(self):
        self.width = self.width_spin.value()
        self.height = self.height_spin.value()
        self.update_status_label()
        # لو حابب تحدث تلقائياً لما تغير الحجم فقط، شيل التعليق تحت:
        # self.start_conversion()

    # ابدأ التحويل
    def start_conversion(self):
        if not os.path.exists(self.folder_path):
            QMessageBox.warning(self, "خطأ", "المجلد غير موجود أو لا يمكن الوصول إليه.")
            return

        count = change_svg_fill_color_and_size(self.folder_path, self.selected_color, self.width, self.height)
        QMessageBox.information(self, "انتهى", f"تم تغيير لون وحجم {count} ملف SVG.")
        self.update_status_label()
        QMessageBox.information(self, "اعادة تشغيل", "تم إلغاء التأمين سيتم إعادة تشغيل التطبيق")
        restart_application()

    # إصلاح ملفات SVG
    def fix_svg_files(self):
        if not os.path.exists(self.folder_path):
            QMessageBox.warning(self, "خطأ", "المجلد غير موجود أو لا يمكن الوصول إليه.")
            return

        reply = QMessageBox.question(self, "تأكيد", 
                                   "هل تريد إصلاح جميع ملفات SVG وإزالة العناصر المتداخلة؟\n"
                                   "هذا قد يغير بنية بعض الملفات.",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            count = self.fix_nested_svg_elements()
            QMessageBox.information(self, "انتهى", f"تم إصلاح {count} ملف SVG.")
            self.update_status_label()

    # إصلاح عناصر SVG المتداخلة
    def fix_nested_svg_elements(self):
        count = 0
        import re
        
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith('.svg'):
                full_path = os.path.join(self.folder_path, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # إصلاح العناصر المتداخلة
                    original_content = content
                    content = fix_nested_svg_elements(content)
                    
                    # حفظ الملف إذا تم تعديله
                    if content != original_content:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        count += 1
                        
                except Exception as e:
                    print(f"فشل إصلاح {filename}: {e}")
        
        return count

    # دعم السحب والإفلات
    # حدث الناقل
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and os.path.isdir(urls[0].toLocalFile()):
                event.acceptProposedAction()
        else:
            event.ignore()

    # دروبنت
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if len(urls) == 1:
            folder = urls[0].toLocalFile()
            if os.path.isdir(folder):
                self.folder_path = folder
                self.folder_edit.setText(folder)
                self.watcher.removePaths(self.watcher.directories())
                self.watcher.addPath(folder)
                self.update_status_label()

    


