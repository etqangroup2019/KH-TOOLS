import os
import sys
from datetime import datetime, timedelta, date  # أضف date أيضًا
import json
import mysql.connector
from mysql.connector import Error, errorcode

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtPrintSupport import *
from PySide6.QtWebEngineWidgets import QWebEngineView 
from PySide6.QtCore import QUrl, QByteArray
from PySide6.QtSvgWidgets import QSvgWidget

from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from cryptography.fernet import Fernet, InvalidToken
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import openpyxl
import subprocess
import winreg as reg
import speech_recognition as sr
from bs4 import BeautifulSoup
import webbrowser
import re
import io
import shutil
import wmi
import hashlib
import ctypes
import keyring
import winreg
import win32cred
import base64
import bcrypt
import random
import string
import ntplib
import requests
import time
import zipfile
import tempfile
import atexit
import hmac
import qtawesome as qta
import socket
import psutil

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd

from decimal import Decimal
import importlib


# النسخة الحالية من البرنامج
CURRENT_VERSION = "2.0"

#proj
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
            
folder_path = os.path.join(application_path, "Project Manager")
icons_dir = os.path.join(application_path, 'icons') 
fonts_dir = os.path.join(application_path, 'fonts') 
Programs_dir = os.path.join(application_path, 'Programs') 
license_key_path = os.path.join(folder_path, "record_errors")
last_date_path = os.path.join(folder_path, "record_errors1")
Customize_json_path = os.path.join(application_path, "Customize.json")
update_folder = os.path.join(application_path, "update")

back_settings = QSettings("khaled", "EngineerSystem1")
# الحفظ في HKEY_LOCAL_MACHINE
settings = QSettings(QSettings.NativeFormat, QSettings.SystemScope, "Eng2", "Eng2")

A_CODE="a_code2"
#اصدار الترخيص
VER= "V2"
DEVICE_id="device_id2"
DIV_KEY="div_key2"
HASH="hash2"
L_TYPE="l_type2"
S_DATE="s_date2"
E_DATE="e_date2"
LAST_D="last_d2"

#خطوط===========================
msg_box_color = "#e0e0e0"
font_app = 'Janna LT'
font_app_defolt = 'Janna LT'
print_font = 'Janna LT'
font_app1 = 'Janna LT'
Table_font_size= "16px"

#ايقونات===================================================
down_up= os.path.join(icons_dir, 'down_up.png')
down_up_url = QUrl.fromLocalFile(down_up).toString()

#قاعدة البيانات===================================================
user="pme"
pm_password = "kh123456"

host = "localhost" 
user_r = "root" 
password_r = "kh123456"
#host= settings.value("host", "127.0.0.1")
#db    
backup_info = os.path.join(application_path, 'backup_path.txt')

# تفاصيل اتصال قاعدة البيانات (يمكن جلبها من إعدادات البرنامج لاحقاً)
DB_HOST = "localhost"
DEFAULT_DB_USER = "pme"
DEFAULT_DB_PASSWORD = "kh123456"
ROOT_USER = "root"
ROOT_PASSWORD = "kh123456" # كلمة مرور المستخدم root - تستخدم فقط لإنشاء DBs


# احصل على كلمة مرور المسؤول
def get_admin_password():
    try:
        conn = mysql.connector.connect(host=host, user="root",password=password_r, database='project_manager2_user')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", ("admin",))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result[0]:  # إذا كان هناك password_hash مخزن
            return result[0]  # إذا كنت تريد إرجاع الـ hash مباشرة، أو يمكنك تعديل الكود لفك التشفير
        else:
            return pm_password # القيمة الافتراضية إذا لم يكن هناك password_hash
    except mysql.connector.Error as err:
        return pm_password  # الرجوع إلى القيمة الافتراضية في حالة الخطأ

# جلب كلمة المرور من قاعدة البيانات
DEFAULT_DB_PASSWORD = get_admin_password()
password = get_admin_password()
    
#الشركة ==========================================================
أيقونة_الشعار = os.path.join(icons_dir, 'لوقو.svg')
company_name = settings.value("company_name", "منظومة المهندس")
logo_path = settings.value(f"company_logo", {أيقونة_الشعار})
documents_folder = os.path.expanduser("~\\Documents")  # الحصول على مسار المجلد في المستندات

account_type = settings.value("account_type", "admin")

Currency_type=settings.value("Currency_type") 
if Currency_type is None:
    Currency_type = "د.ل"

company_phone = settings.value("company_phone", "///")
company_address = settings.value("company_address", "///")
company_email = settings.value("company_email", "///")



#تنسيق الكمبو بوكس= ======================================================================
# فتح القائمة المنسدلة عند الضغط على النص.
def open_combo(combo_box, event):
    combo_box.showPopup()
       
# محاذاة
class AlignedItemDelegate(QStyledItemDelegate):
    # initstyleoption
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter

# محاذاة
class AlignedItemDelegate(QStyledItemDelegate):
    # initstyleoption
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter
        option.textAlignment = Qt.AlignCenter  # إضافة هذه السطر
        option.textAlignment = Qt.AlignHCenter | Qt.AlignVCenter  # محاذاة أفقية وعمودية

#بتوسيط كل العناصر (QLabel, QLineEdit, QComboBox) داخل النافذة.-------------------------
# مركز جميع الحاجيات
def center_all_widgets(widget):
    # البحث عن جميع الويدجت الفرعية داخل النافذة المُمررة
    for w in widget.findChildren(QWidget):
        if isinstance(w, QLabel):
            w.setAlignment(Qt.AlignCenter)
        elif isinstance(w, QLineEdit):
            w.setAlignment(Qt.AlignCenter)
        elif isinstance(w, QComboBox):
            w.setEditable(True)  # السماح بالتعديل لتفعيل المحاذاة
            if w.lineEdit():
                w.lineEdit().setAlignment(Qt.AlignCenter)
                w.setItemDelegate(AlignedItemDelegate(w))

#الكمبو بوكس              
# ComboBox Center Item
def ComboBox_Center_item(ComboBox):
    delegate = AlignedItemDelegate(ComboBox)
    line_edit = QtWidgets.QLineEdit()
    line_edit.setAlignment(QtCore.Qt.AlignCenter)  # Center the text
    ComboBox.setLineEdit(line_edit)
    ComboBox.setEditable(True)
    ComboBox.lineEdit().setReadOnly(True) 
    ComboBox.lineEdit().mousePressEvent = lambda event: open_combo(ComboBox, event)
    ComboBox.setItemDelegate(delegate)

#تكملة البحث في كمبو بوكس
# Combobox Completeer
def ComboBox_completer(combo_box: QComboBox):
    combo_box.setEditable(True)
    # إنشاء نموذج جديد بناءً على العناصر الموجودة في الكومبوبوكس
    model = QStandardItemModel()
    for i in range(combo_box.count()):
        item_text = combo_box.itemText(i)
        item = QStandardItem(item_text)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # محاذاة النص في النموذج
        model.appendRow(item)
    
    # تعيين النموذج للكومبوبوكس
    combo_box.setModel(model)

    # إعداد الـ completer
    completer = QCompleter(model, combo_box)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)

    # إعداد popup الخاص بالـ completer
    popup = QListView()
    popup.setFont(QFont("Janna LT", 12, QFont.Bold))
    popup.setItemDelegate(AlignedItemDelegate(popup))

    popup.setStyleSheet("""
        QListView {
            background-color: #ffffff;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 4px;
            outline: 0;
            selection-background-color: #3498db;
            selection-color: white;
        }
        QListView::item {
            height: 30px;
            padding: 5px;
            text-align: center;
        }
    """)

    completer.setPopup(popup)
    combo_box.setCompleter(completer)
    combo_box.setStyleSheet("QComboBox { text-align: center; }")


#------------اخفاء اعمدة ال id----------------------------
# إخفاء أعمدة الهوية
def hide_id_columns(table_view):
    model = table_view.model()
    if model is None:
        return

    for col in range(model.columnCount()):
        header = model.headerData(col, Qt.Horizontal)
        if header and 'id' in str(header).lower():
            table_view.setColumnHidden(col, True)
        if header and 'معرف' in str(header).lower():
            table_view.setColumnHidden(col, True)

        
#------------تنسيق الجدول----------------------------
# إعداد الجدول
def table_setting(table):
    # الجدول من اليمين إلى اليسار
    table.setLayoutDirection(Qt.RightToLeft)
    # يمنع المستخدم من تعديل محتويات الجدول يدويًا
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    # يجعل التحديد في الجدول يشمل الصف بأكمله وليس خلايا فردية
    table.setSelectionBehavior(QTableWidget.SelectRows)
    # يضبط ألوان الصفوف لتكون متناوبة (مثل لون فاتح ولون غامق)
    table.setAlternatingRowColors(True)
    # يخفي العمود الرأسي (الرؤوس العمودية) على الجانب الأيسر من الجدول
    table.verticalHeader().setHidden(True)
    #ويفعّل فرز الأعمدة عند النقر على رؤوسها (لو كان مفعلًا).
    table.setSortingEnabled(True)

    header = table.horizontalHeader()

    header.setSectionsClickable(False)  # جعل العناوين غير قابلة للنقر 
    #جعل عناوين الاعمدة في المنتصف 
    header.setDefaultAlignment(Qt.AlignCenter)

    #header.setStretchLastSection(True)  # نبدأ بإيقاف الـ stretch بشكل افتراضي
    header.setSectionResizeMode(QHeaderView.ResizeToContents)  # وضع افتراضي
    
    column_count = table.columnCount()
    if column_count == 0:
        return

    # ضبط العمود الأخير
    def adjust_last_column():
        if table.columnCount() == 0:
            return

        # العثور على العمود الأخير المرئي
        last_visible_col = -1
        for i in range(table.columnCount() - 1, -1, -1):
            if not table.isColumnHidden(i):
                last_visible_col = i
                break
        
        if last_visible_col == -1:  # إذا لم يكن هناك أعمدة مرئية
            return

        # ضبط أحجام الأعمدة المرئية بناءً على المحتوى
        for i in range(table.columnCount()):
            if not table.isColumnHidden(i):
                table.resizeColumnToContents(i)
        
        # حساب العرض الكلي للأعمدة المرئية فقط
        total_width = sum(table.columnWidth(i) for i in range(table.columnCount()) if not table.isColumnHidden(i))
        available_width = table.viewport().width()

        # ضبط العمود الأخير المرئي
        if total_width <= available_width:
            header.setSectionResizeMode(last_visible_col, QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(last_visible_col, QHeaderView.ResizeToContents)

        # ربط التعديل بحجم الجدول عند تغيير الحجم
        table.viewport().resizeEvent = lambda event: (
            QTableWidget.viewport(table).resizeEvent(event),
            adjust_last_column()
        )

    # تأخير التنفيذ حتى يتم عرض الجدول
    QTimer.singleShot(0, adjust_last_column)

    hide_id_columns(table)

    # إعداد ارتفاع الصفوف
    table.verticalHeader().setDefaultSectionSize(40)
    
    

    
#اضافة عمدة الجدول  headers
# أضف عمود الجدول
def add_table_column(table,headers):  
    table.setColumnCount(len(headers)) 
    table.setHorizontalHeaderLabels(headers) 

#مسج بوكس عام ==============================================================================
# Gen MSG Box
def GEN_MSG_BOX(Title,Text,icon,button_Ok,button_Cancel,color):
    is_dark_mode = settings.value("dark_mode", False, type=bool)
    msg_box = QMessageBox()
    QApplication.beep()
    msg_box.setWindowTitle(Title)
    msg_box.setText(Text)
    app_icon_path = os.path.join(icons_dir, "icon_app.png")
    msg_box.setWindowIcon(QIcon(app_icon_path))
    icon_path = os.path.join(icons_dir, icon)
    msg_box.setIconPixmap(QPixmap(icon_path))
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg_box.button(QMessageBox.Ok).setText(button_Ok)
    msg_box.button(QMessageBox.Cancel).setText(button_Cancel)
    msg_box.setDefaultButton(QMessageBox.Ok)
    if not is_dark_mode:
        msg_box.setStyleSheet(f"""
                QLabel {{
                    font-family: {font_app};
                    font-weight: bold; font-size: 15px;
                    background-color: {color};
                    color: black;
                }}
                QPushButton {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 16px;
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
                    background-color: #cdd7b9;
                }}
                QPushButton:pressed {{
                    font-family: {font_app};
                    font-weight: bold;
                    background-color: #849c79; /* اللون الأخضر */;
                }}
                QPushButton:focus{{
                    border: 2px solid #0078D7;
                    
                }}
                QMessageBox {{
                    background-color: {color};
                    color: black;
                }}
                QInputDialog{{
                    background-color: #e0e0e0;
                    color: black;
                }}                   
            """)
    else:
        msg_box.setStyleSheet(f"""
                QLabel {{
                    font-family: {font_app};
                    font-weight: bold; font-size: 15px;
                    background-color: #39587d;
                    color: #ffffff;
                }}
                QPushButton {{
                    font-family: {font_app};
                    font-weight: bold;
                    font-size: 16px;
                    height: 20px;
                    width:150px;
                    background-color: #7876b7;
                    border: 2px solid #8a63ff;
                    border-radius: 10px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    font-family: {font_app};
                    font-weight: bold;
                    background-color: #8a63ff;
                }}
                QPushButton:pressed {{
                    font-family: {font_app};
                    font-weight: bold;
                    background-color: #4b2ecc; /* اللون الأخضر */;
                }}
                QPushButton:focus{{
                    border: 2px solid #0078D7;
                    
                }}
                QMessageBox {{
                    background-color: #39587d;
                    color: #ffffff;
                }}
                QInputDialog{{
                    background-color: #39587d;
                    color: #ffffff;
                }}                   
            """)
    response = msg_box.exec()
    return response

#تشفير =================================================

#فك تشفير كلمة مرور المستخدمين
# تحقق من كلمة المرور
def verify_password(self,entered_password, stored_hash):
    try:
        return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())
    except Exception as e:
        QMessageBox.warning(self, "خطأ حماية المستخدم او التاريخ"," تم اكتشاف تغييرات  في الحماية اتصل بالمطور!")
        return None
        #sys.exit()

#اعدادات الويندوز=====================================
# إنشاء او تحميل مفتاح
# احصل أو إنشاء مفتاح
def get_or_create_key(SERVICE_NAME,KEY_NAME):
    key = keyring.get_password(SERVICE_NAME, KEY_NAME)
    if not key:
        key = Fernet.generate_key().decode()
        keyring.set_password(SERVICE_NAME, KEY_NAME, key)
    return key.encode()

#يحذف المفتاح القديم (إن وجد) ويحفظ مفتاح أمان مشفر جديد في نظام الويندوز.
# حفظ مفتاح الأمان
def save_security_key(service_name, key_name, key1):
    try:
        keyring.delete_password(service_name, key_name)
    except keyring.errors.PasswordDeleteError:
        pass
    keyring.set_password(service_name, key_name, key1)

#استرجاع مفتاح أمان مشفر في نظام الويندوز. الترخيص
# احصل على مفتاح الأمان
def get_security_key(service_name, key_name):
    key = keyring.get_password(service_name, key_name)
    return key


#الرجستري ======================================
# تشفير النصوص
# نص الجهاز تشفير reg
def reg_encrypt_device_text(text, key):
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()

# فك تشفير النصوص
# فك شفرة نص الجهاز
def decrypt_reg_device_text(encrypted_text, key):
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()

#تشقير الملفات  ==========================================================================================   
# تشفير ملف
# تشفير الملف
def encrypt_file(file_path, key):
    fernet = Fernet(key)
    # إرجاعه إلى ملف عادي
    ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x80)  
    with open(file_path, "rb") as file:
        file_data = file.read() 
    encrypted_data = fernet.encrypt(file_data)
    with open(file_path, "wb") as file:
        file.write(encrypted_data)
        # إعادة تعيين الخصائص إلى ملف مخفي ونظام
    ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x02 | 0x04)
    hide_folder(folder_path)

# تشفير الملفات
# أخير
def tashfer():
    key = get_or_create_key("FOLDERKEY","FOLDERKEY")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            encrypt_file(file_path, key)

# دالة فك تشفير ملف
# ملف فك التشفير
def decrypt_file(file_path, key):
    try:
        fernet = Fernet(key)
        # إرجاعه إلى ملف عادي
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x80)  
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
        # إعادة تعيين الخصائص إلى ملف مخفي ونظام
        #ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x02 | 0x04)
    except (ValueError, InvalidToken) as e:
        pass

# فك التشفير
# فاك طاشفر
def fak_tashfer():
    key = get_or_create_key("FOLDERKEY","FOLDERKEY")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            decrypt_file(file_path, key)

#اخفاء المجلد ///////////////////////////////////////////////////////////////////////
# إخفاء المجلد
def hide_folder(folder_path):
    FILE_ATTRIBUTE_HidDEN = 0x02
    try:
        ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_HidDEN)
    except Exception as e:
        pass
# إظهار المجلد
# مجلد unide
def unhide_folder(folder_path):
    FILE_ATTRIBUTE_NORMAL = 0x80
    try:
        ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_NORMAL)
    except Exception as e:
        pass

#لاوامر الصوتية ==================================
# إظهار نافذة "تحدث الآن" عند الضغط على Ctrl+M
def start_voice_input(self,voice_label):
        show_floating_label(self,voice_label,"تحدث الآن...",icon=True) 
        QTimer.singleShot(200,lambda: process_voice_input(self,voice_label))  # انتظار 1 ثانية ثم بدء التسجيل الصوتي
        
# التقاط الصوت وتحويله إلى نص
def process_voice_input(self,voice_label):
    focused_widget = QApplication.focusWidget()  # الحصول على الحقل النشط
    if isinstance(focused_widget, QLineEdit):  # التأكد من أنه QLineEdit
        text = speech_to_text()
        if text:
            focused_widget.setText(text)
            #show_floating_label(self,voice_label,text)  # عرض النص المحوّل
        else:
            show_floating_label(self,voice_label,"تعذر التعرف على الصوت.")  # عرض خطأ عند الفشل

#اوامر صوتية
# تحويل الصوت إلى نص مع تحديد الميكروفون الافتراضي
def speech_to_text():
    recognizer = sr.Recognizer()
    mic_list = sr.Microphone.list_microphone_names()
    default_mic_index = 0  # عادة يكون الميكروفون الافتراضي هو الأول في القائمة

    # إنشاء نافذة الرسالة
    with sr.Microphone(device_index=default_mic_index) as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # ضبط حساسية الميكروفون
            recognizer.pause_threshold = 1  # انتظار 3 ثوانٍ بعد آخر كلمة قبل إنهاء التسجيل
            # تسجيل الصوت مع مهلة 3 ثوانٍ إذا لم يتم سماع أي صوت
            audio = recognizer.listen(source, timeout=5)  # إزالة timeout لجعل التسجيل يستمر حتى تتوقف عن الكلام
            text = recognizer.recognize_google(audio, language="ar-AR")
            return text
        
        except sr.UnknownValueError:
            return "تعذر التعرف على الصوت."
        except sr.RequestError:
            return "لا يوجد اتصال بالإنترنت."
        except sr.WaitTimeoutError:
            return "لم يتم التقاط أي صوت."  # إذا لم يتم تسجيل صوت خلال 3 ثوانٍ
    return ""
    
# عرض نافذة صغيرة تحتوي على النص المحوّل أو رسالة في منتصف النافذة
def show_floating_label(self,voice_label, text,icon=False):
    icon_path = os.path.join(icons_dir, 'speaking.png')  # مسار الأيقونة
    if voice_label:
        voice_label.close()  # إغلاق النافذة السابقة إن وجدت
    voice_label = QWidget(self)
    voice_label.setStyleSheet("background-color: #93c47d; border-radius:10px; padding: 0px;")
    layout = QVBoxLayout(voice_label)
    if icon and os.path.exists(icon_path):  # إذا كان هناك أيقونة، أضفها
        icon_label = QLabel()
        #pixmap = QPixmap(icon_path).scaled(16, 16, Qt.KeepAspectRatio)
        #icon_label.setPixmap(pixmap)
        #icon_label.setAlignment(Qt.AlignCenter)
        #layout.addWidget(icon_label)

    text_label = QLabel(text)
    text_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
    text_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(text_label)
    voice_label.setLayout(layout)
    voice_label.setFixedSize(300, 50)
    # وضع النافذة في **منتصف** النافذة الرئيسية
    x = (self.width() - voice_label.width()) // 2
    y = (self.height() - voice_label.height()) // 2
    voice_label.move(x, y)
    voice_label.show()
    # إغلاق النافذة تلقائيًا بعد 3 ثوانٍ
    QTimer.singleShot(3000, voice_label.close)
    
# إعادة فتح التطبيق================================================================
# إعادة تشغيل التطبيق
def restart_application():
    #QApplication.quit()
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()


#حفظ آخر تاريخ تشغيل في الريجستري وفي ملف JSON
# احفظ التاريخ الأخير
def save_last_date():
    current_date = datetime.now().strftime("%Y-%m-%d")
    encrypted_date = encrypt_data(current_date)
    date_signature = sign_data(current_date)
    # حفظ في QSettings (الريجستري)
    settings.setValue(LAST_D, current_date)
    #settings.setValue(HASH, encrypted_date)
    settings.setValue(HASH, date_signature)
    # التأكد من وجود المجلد قبل إنشاء الملف
    last_date_dir = os.path.dirname(last_date_path)
    if not os.path.exists(last_date_dir):
        os.makedirs(last_date_dir)
    # حفظ في ملف JSON كنسخة احتياطية
    try:
        with open(last_date_path, "w") as file:
            json.dump({LAST_D: current_date, HASH: date_signature}, file)
    except Exception as e:
        print(f"⚠️ خطأ أثناء حفظ JSON: {e}")
    #حفظ في الويندوز
    save_security_key(LAST_D, LAST_D, date_signature)
    # جعل الملف "مخفي" و"ملف نظام"
    try:
        ctypes.windll.kernel32.SetFileAttributesW(last_date_path, 0x02 | 0x04)
    except Exception as e:
        print(f"⚠️ خطأ أثناء تعيين خصائص الملف: {e}")

#تشفير البيانات باستخدام التجزئة==============================
# تشفير البيانات باستخدام التجزئة
def encrypt_data(data):
    return hashlib.sha256(data.encode()).hexdigest()


#إنشاء توقيع رقمي للبيانات باستخدام HMAC-SHA256 ================
SECRET_KEY = b"my_secure_secret_key"
# توقيع البيانات
def sign_data(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

# التحقق من أن البيانات لم يتم العبث بها """
# تحقق من التوقيع
def verify_signature(data, signature):
    return sign_data(data) == signature

# التحقق من توفر الإنترنت """
# هل الإنترنت متاح
def is_internet_available():
    try:
        requests.get("http://www.google.com", timeout=1)
        return True
    except requests.exceptions.RequestException:
        return False
    
# تشغيل الآلة الحاسبة
# حاسبة مفتوحة
def open_calculator():
    subprocess.run("calc.exe")

#السحب والافلات =================================================   
# DragGablElabel
class DraggableLabel(QLabel):
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # تفعيل السحب والإفلات

    # حدث الناقل
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():  # التأكد أن العنصر المسحوب هو ملف
            event.acceptProposedAction()

    # دروبنت
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            image_path = files[0]  # أخذ أول ملف فقط
            self.setPixmap(QPixmap(image_path).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.parent().logo_path = image_path  # حفظ المسار للاستخدام لاحقًا

#اخفاء العمود في الجدول حسب الاسم
# إخفاء العمود بالاسم
def hide_column_by_name(table, column_name):
    for col in range(table.columnCount()):
        if table.horizontalHeaderItem(col).text() == column_name:
            table.setColumnHidden(col, True)
            break

#انتقال تلقائي للصف التالي ///////////////////////////////////////////////////
# EnterKey Focus Filter
class EnterKeyFocusFilter(QObject):
    # init
    def __init__(self, parent_widget, button_name, focus_widgets):
        super().__init__()
        self.parent_widget = parent_widget
        self.button_name = button_name
        self.focus_widgets = focus_widgets  # قائمة الحقول المحددة يدويًا

    # EventFilter
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                #print(f"Current widget: {obj.objectName() or type(obj).__name__}")
                if obj in self.focus_widgets:
                    current_index = self.focus_widgets.index(obj)
                    #print(f"Current index: {current_index}, Total widgets: {len(self.focus_widgets)}")
                    if current_index + 1 < len(self.focus_widgets):
                        next_widget = self.focus_widgets[current_index + 1]
                        #print(f"Moving focus to: {next_widget.objectName() or type(next_widget).__name__}")
                        next_widget.setFocus()
                    else:
                        button = self.parent_widget.findChild(QPushButton, self.button_name)
                        if button and button.isEnabled() and button.isVisible():
                            #print(f"Clicking button: {button.objectName()}")
                            button.click()
                    return True
        return super().eventFilter(obj, event)
    
#تنقل بين حقول الادخال
# تطبيق أدخل التركيز
def apply_enter_focus(parent_widget, button_name, focus_widgets):
    enter_filter = EnterKeyFocusFilter(parent_widget, button_name, focus_widgets)
    for widget in focus_widgets:
        widget.installEventFilter(enter_filter)
        widget.setFocusPolicy(Qt.StrongFocus)
    parent_widget._enter_filter = enter_filter
    #print("Event filter applied to:", [w.objectName() or type(w).__name__ for w in focus_widgets])


#حفظ التصنيفات ------------------
# تحميل التصنيفات المحفوظة من قاعدة البيانات
def load_saved_classifications(table_name, column_name):
    try:
        from متغيرات import host, user, password
        import mysql.connector
        
        db_name = f"project_manager_V2"
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # إنشاء الجدول إذا لم يكن موجوداً
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `{column_name}` VARCHAR(255) UNIQUE NOT NULL,
                `تاريخ_الإضافة` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        # جلب التصنيفات المحفوظة
        cursor.execute(f"SELECT `{column_name}` FROM `{table_name}` ORDER BY `{column_name}`")
        results = cursor.fetchall()
        
        return [row[0] for row in results]
        
    except Exception as e:
        print(f"خطأ في تحميل التصنيفات المحفوظة: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# جلب التصنيفات مع ألوانها من جدول التصنيفات المخصص
def get_categories_with_colors(section_name, year=None):
    if year is None:
        year = str(QDate.currentDate().year())

    categories = []
    cursor = None
    conn = None

    try:
        # محاولة الاتصال بقاعدة البيانات
        import mysql.connector
        from متغيرات import host, user, password

        conn = mysql.connector.connect(
            host=host, user=user, password=password,
            database=f"project_manager_V2"
        )
        cursor = conn.cursor()

        # جلب التصنيفات من جدول التصنيفات المخصص
        cursor.execute("""
            SELECT اسم_التصنيف, لون_التصنيف
            FROM التصنيفات
            WHERE اسم_القسم = %s AND حالة_التصنيف = 'نشط'
            ORDER BY اسم_التصنيف
        """, (section_name,))

        results = cursor.fetchall()
        categories = [(name, color) for name, color in results]

    except Exception as e:
        print(f"خطأ في جلب التصنيفات مع الألوان: {e}")
        # في حالة الفشل، جلب التصنيفات من الجدول الأصلي
        categories = [(cat, "#3498db") for cat in load_saved_classifications("", section_name, "التصنيف")]

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return categories

# حفظ التصنيف الجديد في قاعدة البيانات
def save_new_classification(inputs,text, table_name, column_name):
    if not text or text.strip() == "":
        return

    text = text.strip()

    # التحقق من أن النص ليس من التصنيفات الافتراضية الموجودة
    current_items = [inputs["classification"].itemText(i)
                    for i in range(inputs["classification"].count())]

    if text in current_items:
        return  # التصنيف موجود بالفعل

    # Initialize variables to None
    cursor = None
    conn = None
    
    try:
        from متغيرات import host, user, password
        import mysql.connector
        
        db_name = f"project_manager_V2"
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # إنشاء الجدول إذا لم يكن موجوداً
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `{column_name}` VARCHAR(255) UNIQUE NOT NULL,
                `تاريخ_الإضافة` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        # التحقق من عدم وجود التصنيف في قاعدة البيانات
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `{column_name}` = %s", (text,))
        if cursor.fetchone()[0] > 0:
            return  # التصنيف موجود بالفعل في قاعدة البيانات
        
        # إضافة التصنيف الجديد
        cursor.execute(
            f"INSERT INTO `{table_name}` (`{column_name}`) VALUES (%s)",
            (text,)
        )
        conn.commit()
        
        # إضافة التصنيف إلى القائمة المنسدلة إذا لم يكن موجوداً
        if text not in current_items:
            inputs["classification"].addItem(text)
            print(f"تم حفظ التصنيف الجديد: {text}")
        
    except mysql.connector.IntegrityError:
        # التصنيف موجود بالفعل (خطأ UNIQUE)
        pass
    except Exception as e:
        print(f"خطأ في حفظ التصنيف الجديد: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

