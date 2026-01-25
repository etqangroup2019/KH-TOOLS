#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نوافذ الحوار لإدارة الموردين
تحتوي على نوافذ إضافة وتعديل الفواتير والمدفوعات
"""

import sys
import os
from datetime import datetime, date
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from متغيرات import *

# إعدادات قاعدة البيانات
db_config = {
    'host': host,
    'user': user,
    'password': password,
    'database': f"project_manager_V2"
}

# نافذة إضافة/تعديل فاتورة مورد
class InvoiceDialog(QDialog):
    
    # init
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.is_edit_mode = invoice_data is not None
        self.setup_ui()
        self.apply_dialog_styles()
        
        if self.is_edit_mode:
            self.load_invoice_data()
    
    # إعداد واجهة النافذة
    def setup_ui(self):
        title = "تعديل فاتورة" if self.is_edit_mode else "إضافة فاتورة جديدة"
        self.setWindowTitle(title)
        self.setFixedSize(500, 450)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان
        title_label = QLabel(title)
        title_label.setObjectName("dialog_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # النموذج
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # المورد
        self.supplier_combo = QComboBox()
        self.supplier_combo.setObjectName("form_input")
        self.load_suppliers()
        form_layout.addRow("المورد:", self.supplier_combo)
        
        # رقم الفاتورة
        self.invoice_number_input = QLineEdit()
        self.invoice_number_input.setObjectName("form_input")
        form_layout.addRow("رقم الفاتورة:", self.invoice_number_input)
        
        # وصف الفاتورة
        self.description_input = QLineEdit()
        self.description_input.setObjectName("form_input")
        form_layout.addRow("وصف الفاتورة:", self.description_input)
        
        # المبلغ
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setObjectName("form_input")
        self.amount_input.setRange(0, 999999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(f" {Currency_type}")
        form_layout.addRow("المبلغ:", self.amount_input)
        
        # التاريخ
        self.date_input = QDateEdit()
        self.date_input.setObjectName("form_input")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("التاريخ:", self.date_input)
        
        # الملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("form_input")
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("حفظ")
        self.save_btn.setObjectName("save_button")
        self.save_btn.clicked.connect(self.save_invoice)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)
    
    # تحميل قائمة الموردين
    def load_suppliers(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, اسم_المورد FROM الموردين ORDER BY اسم_المورد")
            suppliers = cursor.fetchall()
            
            self.supplier_combo.addItem("اختر المورد", None)
            for supplier_id, supplier_name in suppliers:
                self.supplier_combo.addItem(supplier_name, supplier_id)
            
            conn.close()
            
        except Exception as e:
            print(f"خطأ في تحميل الموردين: {e}")
    
    # تحميل بيانات الفاتورة للتعديل
    def load_invoice_data(self):
        if self.invoice_data:
            # البحث عن المورد في الكومبو بوكس
            supplier_name = self.invoice_data.get('المورد', '')
            for i in range(self.supplier_combo.count()):
                if self.supplier_combo.itemText(i) == supplier_name:
                    self.supplier_combo.setCurrentIndex(i)
                    break
            
            self.invoice_number_input.setText(str(self.invoice_data.get('رقم_الفاتورة', '')))
            self.description_input.setText(str(self.invoice_data.get('وصف_الفاتورة', '')))
            
            # تنظيف المبلغ من العملة
            amount_text = str(self.invoice_data.get('المبلغ', '0'))
            amount_text = amount_text.replace(Currency_type, '').replace(',', '').strip()
            try:
                amount = float(amount_text)
                self.amount_input.setValue(amount)
            except:
                self.amount_input.setValue(0)
            
            # التاريخ
            date_str = str(self.invoice_data.get('التاريخ', ''))
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.date_input.setDate(QDate(date_obj))
                except:
                    self.date_input.setDate(QDate.currentDate())
            
            self.notes_input.setPlainText(str(self.invoice_data.get('ملاحظات', '')))
    
    # حفظ بيانات الفاتورة
    def save_invoice(self):
        # التحقق من صحة البيانات
        if self.supplier_combo.currentData() is None:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار المورد")
            return
        
        if not self.description_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال وصف الفاتورة")
            return
        
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")
            return
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            supplier_id = self.supplier_combo.currentData()
            invoice_number = self.invoice_number_input.text().strip()
            description = self.description_input.text().strip()
            amount = self.amount_input.value()
            invoice_date = self.date_input.date().toPython()
            notes = self.notes_input.toPlainText().strip()
            
            if self.is_edit_mode:
                # تعديل فاتورة موجودة
                invoice_id = self.invoice_data.get('المعرف')
                
                # الحصول على معرف المورد القديم
                cursor.execute("SELECT معرف_المورد FROM الحسابات_فواتير_الموردين WHERE id = %s", (invoice_id,))
                old_supplier_result = cursor.fetchone()
                old_supplier_id = old_supplier_result[0] if old_supplier_result else None
                
                cursor.execute("""
                    UPDATE الحسابات_فواتير_الموردين 
                    SET معرف_المورد = %s, رقم_الفاتورة = %s, وصف_الفاتورة = %s, 
                        المبلغ = %s, التاريخ = %s, ملاحظات = %s
                    WHERE id = %s
                """, (supplier_id, invoice_number, description, amount, invoice_date, notes, invoice_id))
                
                # تحديث إجماليات المورد القديم والجديد
                if old_supplier_id:
                    self.update_supplier_totals(cursor, old_supplier_id)
                if supplier_id != old_supplier_id:
                    self.update_supplier_totals(cursor, supplier_id)
                
                message = "تم تعديل الفاتورة بنجاح"
            else:
                # إضافة فاتورة جديدة
                cursor.execute("""
                    INSERT INTO الحسابات_فواتير_الموردين 
                    (معرف_المورد, رقم_الفاتورة, وصف_الفاتورة, المبلغ, التاريخ, ملاحظات)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (supplier_id, invoice_number, description, amount, invoice_date, notes))
                
                # تحديث إجماليات المورد
                self.update_supplier_totals(cursor, supplier_id)
                
                message = "تم إضافة الفاتورة بنجاح"
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "نجح", message)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الفاتورة: {str(e)}")
    
    # تحديث إجماليات المورد
    def update_supplier_totals(self, cursor, supplier_id):
        try:
            # حساب إجمالي التوريد من الفواتير
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM الحسابات_فواتير_الموردين 
                WHERE معرف_المورد = %s
            """, (supplier_id,))
            total_supply = cursor.fetchone()[0] or 0
            
            # حساب إجمالي المدفوع من الدفعات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM الحسابات_دفعات_الموردين 
                WHERE معرف_المورد = %s
            """, (supplier_id,))
            total_paid = cursor.fetchone()[0] or 0
            
            # تحديث جدول الموردين
            cursor.execute("""
                UPDATE الموردين 
                SET اجمالي_التوريد = %s, المدفوع_للمورد = %s
                WHERE id = %s
            """, (total_supply, total_paid, supplier_id))
            
        except Exception as e:
            print(f"خطأ في تحديث إجماليات المورد: {e}")
    
    # تطبيق أنماط النافذة
    def apply_dialog_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Janna LT';
            }
            
            QLabel[objectName="dialog_title"] {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
            }
            
            QLineEdit[objectName="form_input"], 
            QComboBox[objectName="form_input"],
            QTextEdit[objectName="form_input"],
            QDoubleSpinBox[objectName="form_input"],
            QDateEdit[objectName="form_input"] {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            
            QLineEdit[objectName="form_input"]:focus,
            QComboBox[objectName="form_input"]:focus,
            QTextEdit[objectName="form_input"]:focus,
            QDoubleSpinBox[objectName="form_input"]:focus,
            QDateEdit[objectName="form_input"]:focus {
                border-color: #3498db;
            }
            
            QPushButton[objectName="save_button"] {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            
            QPushButton[objectName="save_button"]:hover {
                background-color: #229954;
            }
            
            QPushButton[objectName="cancel_button"] {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            
            QPushButton[objectName="cancel_button"]:hover {
                background-color: #c0392b;
            }
            
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
        """)

# نافذة إضافة/تعديل دفعة مورد
class PaymentDialog(QDialog):

    # init
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.is_edit_mode = payment_data is not None
        self.setup_ui()
        self.apply_dialog_styles()

        if self.is_edit_mode:
            self.load_payment_data()

    # إعداد واجهة النافذة
    def setup_ui(self):
        title = "تعديل دفعة" if self.is_edit_mode else "إضافة دفعة جديدة"
        self.setWindowTitle(title)
        self.setFixedSize(500, 500)
        self.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # العنوان
        title_label = QLabel(title)
        title_label.setObjectName("dialog_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # النموذج
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # المورد
        self.supplier_combo = QComboBox()
        self.supplier_combo.setObjectName("form_input")
        self.load_suppliers()
        form_layout.addRow("المورد:", self.supplier_combo)

        # وصف الدفعة
        self.description_input = QLineEdit()
        self.description_input.setObjectName("form_input")
        form_layout.addRow("وصف الدفعة:", self.description_input)

        # المبلغ
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setObjectName("form_input")
        self.amount_input.setRange(0, 999999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(f" {Currency_type}")
        form_layout.addRow("المبلغ:", self.amount_input)

        # تاريخ الدفعة
        self.date_input = QDateEdit()
        self.date_input.setObjectName("form_input")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("تاريخ الدفعة:", self.date_input)

        # طريقة الدفع
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setObjectName("form_input")
        self.payment_method_combo.addItems(["نقدي", "شيك", "تحويل بنكي"])
        form_layout.addRow("طريقة الدفع:", self.payment_method_combo)

        # المستلم
        self.receiver_input = QLineEdit()
        self.receiver_input.setObjectName("form_input")
        form_layout.addRow("المستلم:", self.receiver_input)

        # الملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("form_input")
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_input)

        layout.addLayout(form_layout)

        # الأزرار
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("حفظ")
        self.save_btn.setObjectName("save_button")
        self.save_btn.clicked.connect(self.save_payment)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل قائمة الموردين
    def load_suppliers(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT id, اسم_المورد FROM الموردين ORDER BY اسم_المورد")
            suppliers = cursor.fetchall()

            self.supplier_combo.addItem("اختر المورد", None)
            for supplier_id, supplier_name in suppliers:
                self.supplier_combo.addItem(supplier_name, supplier_id)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل الموردين: {e}")

    # تحميل بيانات الدفعة للتعديل
    def load_payment_data(self):
        if self.payment_data:
            # البحث عن المورد في الكومبو بوكس
            supplier_name = self.payment_data.get('المورد', '')
            for i in range(self.supplier_combo.count()):
                if self.supplier_combo.itemText(i) == supplier_name:
                    self.supplier_combo.setCurrentIndex(i)
                    break

            self.description_input.setText(str(self.payment_data.get('وصف_الدفعة', '')))

            # تنظيف المبلغ من العملة
            amount_text = str(self.payment_data.get('المبلغ', '0'))
            amount_text = amount_text.replace(Currency_type, '').replace(',', '').strip()
            try:
                amount = float(amount_text)
                self.amount_input.setValue(amount)
            except:
                self.amount_input.setValue(0)

            # تاريخ الدفعة
            date_str = str(self.payment_data.get('تاريخ_الدفعة', ''))
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.date_input.setDate(QDate(date_obj))
                except:
                    self.date_input.setDate(QDate.currentDate())

            # طريقة الدفع
            payment_method = str(self.payment_data.get('طريقة_الدفع', 'نقدي'))
            index = self.payment_method_combo.findText(payment_method)
            if index >= 0:
                self.payment_method_combo.setCurrentIndex(index)

            self.receiver_input.setText(str(self.payment_data.get('المستلم', '')))
            self.notes_input.setPlainText(str(self.payment_data.get('ملاحظات', '')))

    # حفظ بيانات الدفعة
    def save_payment(self):
        # التحقق من صحة البيانات
        if self.supplier_combo.currentData() is None:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار المورد")
            return

        if not self.description_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال وصف الدفعة")
            return

        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            supplier_id = self.supplier_combo.currentData()
            description = self.description_input.text().strip()
            amount = self.amount_input.value()
            payment_date = self.date_input.date().toPython()
            payment_method = self.payment_method_combo.currentText()
            receiver = self.receiver_input.text().strip()
            notes = self.notes_input.toPlainText().strip()

            if self.is_edit_mode:
                # تعديل دفعة موجودة
                payment_id = self.payment_data.get('المعرف')

                # الحصول على معرف المورد القديم
                cursor.execute("SELECT معرف_المورد FROM الحسابات_دفعات_الموردين WHERE id = %s", (payment_id,))
                old_supplier_result = cursor.fetchone()
                old_supplier_id = old_supplier_result[0] if old_supplier_result else None

                cursor.execute("""
                    UPDATE الحسابات_دفعات_الموردين
                    SET معرف_المورد = %s, وصف_الدفعة = %s, المبلغ = %s,
                        تاريخ_الدفعة = %s, طريقة_الدفع = %s, المستلم = %s, ملاحظات = %s
                    WHERE id = %s
                """, (supplier_id, description, amount, payment_date, payment_method, receiver, notes, payment_id))

                # تحديث إجماليات المورد القديم والجديد
                if old_supplier_id:
                    self.update_supplier_totals(cursor, old_supplier_id)
                if supplier_id != old_supplier_id:
                    self.update_supplier_totals(cursor, supplier_id)

                message = "تم تعديل الدفعة بنجاح"
            else:
                # إضافة دفعة جديدة
                cursor.execute("""
                    INSERT INTO الحسابات_دفعات_الموردين
                    (معرف_المورد, وصف_الدفعة, المبلغ, تاريخ_الدفعة, طريقة_الدفع, المستلم, ملاحظات)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (supplier_id, description, amount, payment_date, payment_method, receiver, notes))

                # تحديث إجماليات المورد
                self.update_supplier_totals(cursor, supplier_id)

                message = "تم إضافة الدفعة بنجاح"

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", message)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الدفعة: {str(e)}")

    # تحديث إجماليات المورد
    def update_supplier_totals(self, cursor, supplier_id):
        try:
            # حساب إجمالي التوريد من الفواتير
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات_فواتير_الموردين
                WHERE معرف_المورد = %s
            """, (supplier_id,))
            total_supply = cursor.fetchone()[0] or 0

            # حساب إجمالي المدفوع من الدفعات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات_دفعات_الموردين
                WHERE معرف_المورد = %s
            """, (supplier_id,))
            total_paid = cursor.fetchone()[0] or 0

            # تحديث جدول الموردين
            cursor.execute("""
                UPDATE الموردين
                SET اجمالي_التوريد = %s, المدفوع_للمورد = %s
                WHERE id = %s
            """, (total_supply, total_paid, supplier_id))

        except Exception as e:
            print(f"خطأ في تحديث إجماليات المورد: {e}")

    # تطبيق أنماط النافذة
    def apply_dialog_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Janna LT';
            }

            QLabel[objectName="dialog_title"] {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #bdc3c7;
            }

            QLineEdit[objectName="form_input"],
            QComboBox[objectName="form_input"],
            QTextEdit[objectName="form_input"],
            QDoubleSpinBox[objectName="form_input"],
            QDateEdit[objectName="form_input"] {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }

            QLineEdit[objectName="form_input"]:focus,
            QComboBox[objectName="form_input"]:focus,
            QTextEdit[objectName="form_input"]:focus,
            QDoubleSpinBox[objectName="form_input"]:focus,
            QDateEdit[objectName="form_input"]:focus {
                border-color: #3498db;
            }

            QPushButton[objectName="save_button"] {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }

            QPushButton[objectName="save_button"]:hover {
                background-color: #229954;
            }

            QPushButton[objectName="cancel_button"] {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }

            QPushButton[objectName="cancel_button"]:hover {
                background-color: #c0392b;
            }

            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
        """)
