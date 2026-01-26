#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة إدارة الموردين
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt

from ستايل_نوافذ_الإدارة import apply_management_style

class SupplierManagementWindow(QDialog):
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.parent = parent
        self.supplier_data = supplier_data or {}
        self.supplier_id = self.supplier_data.get('id')

        self.setup_window()
        self.create_widgets()
        self.layout_widgets()
        self.populate_data()
        
        apply_management_style(self)

    def setup_window(self):
        title = "تعديل بيانات المورد" if self.supplier_id else "إضافة مورد جديد"
        self.setWindowTitle(title)
        self.setGeometry(300, 200, 500, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.main_layout = QVBoxLayout(self)

    def create_widgets(self):
        self.fields = {}
        # Based on TABLE_COLUMNS for "الموردين" in متغيرات.py
        field_labels = {
            "اسم_المورد": "اسم المورد:",
            "التصنيف": "تصنيف المورد:",
            "العنوان": "العنوان:",
            "رقم_الهاتف": "رقم الهاتف:",
            "الإيميل": "البريد الإلكتروني:"
        }

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)

        row = 0
        for key, label in field_labels.items():
            self.grid_layout.addWidget(QLabel(label), row, 0)
            if key == "التصنيف":
                field = QComboBox()
                # Populate with classifications from DB or a predefined list
                field.addItems(["مواد بناء", "أدوات كهربائية", "أثاث مكتبي", "خدمات عامة", "غير محدد"])
            else:
                field = QLineEdit()
            
            self.fields[key] = field
            self.grid_layout.addWidget(field, row, 1)
            row += 1
            
        self.save_button = QPushButton("حفظ")
        self.save_button.clicked.connect(self.save_supplier)
        
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.clicked.connect(self.reject)

    def layout_widgets(self):
        self.main_layout.addLayout(self.grid_layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(buttons_layout)

    def populate_data(self):
        if self.supplier_id:
            for key, field in self.fields.items():
                value = self.supplier_data.get(key, "")
                if isinstance(field, QLineEdit):
                    field.setText(str(value))
                elif isinstance(field, QComboBox):
                    field.setCurrentText(str(value))

    def save_supplier(self):
        connection = self.get_db_connection()
        if not connection:
            QMessageBox.critical(self, "خطأ في الاتصال", "فشل الاتصال بقاعدة البيانات.")
            return

        cursor = connection.cursor()
        data = {key: field.text() if isinstance(field, QLineEdit) else field.currentText() for key, field in self.fields.items()}

        try:
            if self.supplier_id:
                # Update existing supplier
                query = """
                    UPDATE الموردين SET
                        اسم_المورد = %s, التصنيف = %s, العنوان = %s, رقم_الهاتف = %s, الإيميل = %s
                    WHERE id = %s
                """
                values = (data['اسم_المورد'], data['التصنيف'], data['العنوان'], data['رقم_الهاتف'], data['الإيميل'], self.supplier_id)
            else:
                # Insert new supplier
                query = """
                    INSERT INTO الموردين (اسم_المورد, التصنيف, العنوان, رقم_الهاتف, الإيميل, تاريخ_الإنشاء)
                    VALUES (%s, %s, %s, %s, %s, CURDATE())
                """
                values = (data['اسم_المورد'], data['التصنيف'], data['العنوان'], data['رقم_الهاتف'], data['الإيميل'])

            cursor.execute(query, values)
            connection.commit()
            QMessageBox.information(self, "نجاح", "تم حفظ بيانات المورد بنجاح.")
            self.accept()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"حدث خطأ: {err}")
        finally:
            cursor.close()
            connection.close()

def open_supplier_management_window(parent=None, supplier_data=None):
    dialog = SupplierManagementWindow(parent, supplier_data)
    return dialog.exec() 