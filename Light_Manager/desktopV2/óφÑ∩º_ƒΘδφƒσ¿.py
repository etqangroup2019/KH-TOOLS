#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
توحيد_النوافذ
طبقة موحدة لنوافذ الإدارة وحواريات الإضافة/التعديل/الحذف، مع طبقة وصول عامة لقاعدة البيانات.

المزايا:
- DatabaseManager: إدارة الاتصال والاستعلامات مع MySQL.
- GenericRepository: CRUD عام لأي جدول مع حماية أسماء الأعمدة.
- BaseCrudDialog: حوار نماذج ديناميكي (إضافة/تعديل) يُبنى من تهيئة الحقول.
- UnifiedManagementWindow: نافذة إدارة موحدة مع جدول وإجراءات (إضافة/تعديل/حذف/تحديث/إغلاق).

الاستخدام النموذجي موجود أسفل الملف.
"""

from __future__ import annotations

import sys
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# محاولة التوافق بين PySide6 و PyQt6 تلقائياً
try:
    from PySide6.QtWidgets import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
        QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QPushButton,
        QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QFrame,
        QTabWidget
    )
    from PySide6.QtGui import QIcon, QFont
    from PySide6.QtCore import Qt, QDate, Signal as pyqtSignal
    USING_PYSIDE = True
except Exception:
    from PyQt6.QtWidgets import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
        QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QPushButton,
        QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QFrame,
        QTabWidget
    )
    from PyQt6.QtGui import QIcon, QFont
    from PyQt6.QtCore import Qt, QDate, pyqtSignal
    USING_PYSIDE = False

import mysql.connector

# تكامل مع إعدادات التطبيق والستايلات إن توفرت
try:
    from الإعدادات_العامة import (
        DB_HOST, DEFAULT_DB_USER, DEFAULT_DB_PASSWORD, icons_dir,
        UI_SECTION_TO_DB_TABLE_MAP, TABLE_COLUMNS, Currency_type
    )
except Exception:
    DB_HOST = "localhost"
    DEFAULT_DB_USER = "pme"
    DEFAULT_DB_PASSWORD = ""
    icons_dir = os.getcwd()
    UI_SECTION_TO_DB_TABLE_MAP = {}
    TABLE_COLUMNS = {}
    Currency_type = "د.ل"

try:
    from ستايل_نوافذ_الإدارة import apply_management_style, setup_table_style
except Exception:
    def apply_management_style(widget):
        widget.setLayoutDirection(Qt.RightToLeft)
    def setup_table_style(table):
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)


# ====================== طبقة قاعدة البيانات ======================

class DatabaseManager:
    """مدير اتصال MySQL مع دوال مساعدة للاستعلامات وإدارة الموارد."""

    def __init__(self, host: str = DB_HOST, user: str = DEFAULT_DB_USER, password: str = DEFAULT_DB_PASSWORD, database: str = "project_manager_V2"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        return mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)

    @contextmanager
    def get_cursor(self):
        conn = None
        cur = None
        try:
            conn = self.connect()
            cur = conn.cursor(dictionary=True)
            yield conn, cur
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            try:
                if cur:
                    cur.close()
                if conn and conn.is_connected():
                    conn.close()
            except Exception:
                pass

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            return cur.rowcount

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            return cur.fetchall() or []

    def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            return cur.fetchone()


# ====================== مستودع CRUD عام ======================

class GenericRepository:
    """طبقة CRUD عامة لأي جدول.

    - تتحقق من الأعمدة المسموح بها لمنع حقن SQL.
    - تدعم الفلاتر والبحث البسيط.
    """

    def __init__(self, db: DatabaseManager, table_name: str, allowed_columns: List[str], primary_key: str = "id"):
        self.db = db
        self.table_name = table_name
        self.allowed_columns = set(allowed_columns)
        self.primary_key = primary_key

    def _validate_columns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if k in self.allowed_columns}

    def list(self, filters: Optional[Dict[str, Any]] = None, limit: int = 500) -> List[Dict[str, Any]]:
        filters = filters or {}
        filters = self._validate_columns(filters)
        where = []
        params: List[Any] = []
        for k, v in filters.items():
            where.append(f"`{k}` = %s")
            params.append(v)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"SELECT * FROM `{self.table_name}`{where_sql} ORDER BY `{self.primary_key}` DESC LIMIT %s"
        params.append(limit)
        return self.db.fetch_all(sql, tuple(params))

    def get_by_id(self, row_id: Any) -> Optional[Dict[str, Any]]:
        sql = f"SELECT * FROM `{self.table_name}` WHERE `{self.primary_key}` = %s"
        return self.db.fetch_one(sql, (row_id,))

    def create(self, data: Dict[str, Any]) -> int:
        data = self._validate_columns(data)
        if not data:
            return 0
        cols = ", ".join([f"`{c}`" for c in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO `{self.table_name}` ({cols}) VALUES ({placeholders})"
        return self.db.execute(sql, tuple(data.values()))

    def update(self, row_id: Any, data: Dict[str, Any]) -> int:
        data = self._validate_columns(data)
        if not data:
            return 0
        sets = ", ".join([f"`{c}` = %s" for c in data.keys()])
        sql = f"UPDATE `{self.table_name}` SET {sets} WHERE `{self.primary_key}` = %s"
        params = list(data.values()) + [row_id]
        return self.db.execute(sql, tuple(params))

    def delete(self, row_id: Any) -> int:
        sql = f"DELETE FROM `{self.table_name}` WHERE `{self.primary_key}` = %s"
        return self.db.execute(sql, (row_id,))


# ====================== نموذج حوار CRUD عام ======================

FieldType = str  # text, textarea, number, int, date, combo

@dataclass
class FieldConfig:
    name: str
    label: str
    type: FieldType = "text"
    required: bool = False
    options: Optional[List[str]] = None  # للكومبو
    suffix: Optional[str] = None         # للوحدات/العملة


class BaseCrudDialog(QDialog):
    """حوار موحد للإضافة/التعديل يعتمد على تهيئة الحقول.

    - عند تزويد initial_data يعمل في وضع التعديل، خلاف ذلك إضافة.
    - عند الضغط على حفظ يستدعي callbacks للبناء فوقه أو يستخدم repository مباشرة إن توفر.
    """

    def __init__(
        self,
        title: str,
        fields: List[FieldConfig],
        repository: Optional[GenericRepository] = None,
        initial_data: Optional[Dict[str, Any]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.fields = fields
        self.repository = repository
        self.initial_data = initial_data or {}
        self.is_edit_mode = bool(initial_data)
        self.inputs: Dict[str, QWidget] = {}

        self._build_ui()
        apply_management_style(self)

    def _build_ui(self):
        main = QVBoxLayout(self)
        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("dialog_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(10)

        for f in self.fields:
            w: QWidget
            if f.type == "textarea":
                w = QTextEdit()
            elif f.type == "number":
                w = QDoubleSpinBox()
                w.setDecimals(2)
                w.setRange(-1_000_000_000, 1_000_000_000)
                if f.suffix:
                    w.setSuffix(f" {f.suffix}")
                else:
                    w.setSuffix(f" {Currency_type}")
            elif f.type == "int":
                w = QSpinBox()
                w.setRange(-1_000_000_000, 1_000_000_000)
            elif f.type == "date":
                w = QDateEdit()
                w.setDate(QDate.currentDate())
                w.setCalendarPopup(True)
                w.setDisplayFormat("yyyy-MM-dd")
            elif f.type == "combo":
                w = QComboBox()
                for opt in (f.options or []):
                    w.addItem(opt)
            else:
                w = QLineEdit()

            w.setObjectName("form_input")
            self.inputs[f.name] = w
            label = f.label + (" *" if f.required else "")
            form.addRow(label + ":", w)

        main.addLayout(form)

        # أزرار
        btns = QHBoxLayout()
        self.save_btn = QPushButton("حفظ")
        self.save_btn.setObjectName("save_button")
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        main.addLayout(btns)

        # تحميل بيانات التعديل
        if self.is_edit_mode:
            self._load_initial_values()

    def _load_initial_values(self):
        for f in self.fields:
            v = self.initial_data.get(f.name)
            w = self.inputs.get(f.name)
            if w is None:
                continue
            if isinstance(w, QLineEdit):
                w.setText("" if v is None else str(v))
            elif isinstance(w, QTextEdit):
                w.setPlainText("" if v is None else str(v))
            elif isinstance(w, QDoubleSpinBox):
                try:
                    w.setValue(float(v) if v is not None else 0.0)
                except Exception:
                    w.setValue(0.0)
            elif isinstance(w, QSpinBox):
                try:
                    w.setValue(int(v) if v is not None else 0)
                except Exception:
                    w.setValue(0)
            elif isinstance(w, QDateEdit):
                if v:
                    try:
                        parts = str(v).split("-")
                        y, m, d = map(int, parts[:3])
                        w.setDate(QDate(y, m, d))
                    except Exception:
                        w.setDate(QDate.currentDate())
            elif isinstance(w, QComboBox):
                if v is not None:
                    idx = w.findText(str(v))
                    if idx >= 0:
                        w.setCurrentIndex(idx)

    def _collect_values(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for f in self.fields:
            w = self.inputs[f.name]
            if isinstance(w, QLineEdit):
                data[f.name] = w.text().strip()
            elif isinstance(w, QTextEdit):
                data[f.name] = w.toPlainText().strip()
            elif isinstance(w, QDoubleSpinBox):
                data[f.name] = float(w.value())
            elif isinstance(w, QSpinBox):
                data[f.name] = int(w.value())
            elif isinstance(w, QDateEdit):
                data[f.name] = w.date().toString("yyyy-MM-dd")
            elif isinstance(w, QComboBox):
                data[f.name] = w.currentText()
        return data

    def _validate(self, data: Dict[str, Any]) -> Optional[str]:
        for f in self.fields:
            if f.required:
                v = data.get(f.name)
                if v is None or (isinstance(v, str) and v.strip() == ""):
                    return f"الحقل '{f.label}' مطلوب"
        return None

    def _on_save(self):
        data = self._collect_values()
        err = self._validate(data)
        if err:
            QMessageBox.warning(self, "تحقق", err)
            return
        try:
            if self.repository is None:
                # لا يوجد مستودع: فقط إرجاع البيانات
                self._result = data
                self.accept()
                return
            if self.is_edit_mode:
                row_id = self.initial_data.get("id") or self.initial_data.get("معرف") or self.initial_data.get("ID")
                self.repository.update(row_id, data)
            else:
                self.repository.create(data)
            self._result = data
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في الحفظ: {e}")

    def get_result(self) -> Optional[Dict[str, Any]]:
        return getattr(self, "_result", None)


# ====================== نافذة إدارة موحدة ======================

class UnifiedManagementWindow(QDialog):
    """نافذة إدارة موحدة تدير جدول وإجراءات CRUD باستخدام مستودع عام وحوار موحد."""

    data_changed = pyqtSignal()

    def __init__(
        self,
        title: str,
        repository: GenericRepository,
        table_columns: List[Dict[str, str]],  # [{'key': 'اسم_الحقل', 'label': 'العنوان في الجدول'}]
        parent: Optional[QWidget] = None,
        add_edit_fields: Optional[List[FieldConfig]] = None,
        allow_delete: bool = True,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.repo = repository
        self.table_columns = table_columns
        self.add_edit_fields = add_edit_fields or [
            FieldConfig(name=c['key'], label=c['label'], type='text') for c in table_columns if c['key'] != 'id'
        ]
        self.allow_delete = allow_delete

        self._build_ui()
        apply_management_style(self)
        self.load_data()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # رأس بسيط
        header = QHBoxLayout()
        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("main_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(title_label)
        main.addLayout(header)

        # الأزرار
        actions = QHBoxLayout()
        self.add_btn = QPushButton("إضافة")
        self.edit_btn = QPushButton("تعديل")
        self.delete_btn = QPushButton("حذف")
        self.refresh_btn = QPushButton("تحديث")
        self.close_btn = QPushButton("إغلاق")
        for b in (self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn, self.close_btn):
            actions.addWidget(b)
        actions.addStretch()
        main.addLayout(actions)

        self.add_btn.clicked.connect(self.on_add)
        self.edit_btn.clicked.connect(self.on_edit)
        self.delete_btn.clicked.connect(self.on_delete)
        self.refresh_btn.clicked.connect(self.load_data)
        self.close_btn.clicked.connect(self.close)
        if not self.allow_delete:
            self.delete_btn.setDisabled(True)

        # الجدول
        self.table = QTableWidget()
        setup_table_style(self.table)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(len(self.table_columns))
        self.table.setHorizontalHeaderLabels([c['label'] for c in self.table_columns])
        main.addWidget(self.table)

        # حدث دبل كليك = تعديل
        self.table.doubleClicked.connect(self.on_edit)

    def _current_row_id(self) -> Optional[Any]:
        row = self.table.currentRow()
        if row < 0:
            return None
        # نفترض أن عمود "id" موجود ضمن table_columns
        try:
            id_col = [i for i, c in enumerate(self.table_columns) if c['key'].lower() in ('id', 'معرف')][0]
        except IndexError:
            return None
        item = self.table.item(row, id_col)
        if not item:
            return None
        return item.text()

    def load_data(self):
        try:
            rows = self.repo.list()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, col in enumerate(self.table_columns):
                key = col['key']
                value = row.get(key, "")
                # تنسيق مبسط للمبالغ والتواريخ إن لزم
                if isinstance(value, float):
                    value = f"{value:,.2f}"
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, item)

    def on_add(self):
        dlg = BaseCrudDialog(title=f"إضافة {self.windowTitle()}", fields=self.add_edit_fields, repository=self.repo, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()

    def on_edit(self):
        row_id = self._current_row_id()
        if not row_id:
            QMessageBox.information(self, "تنبيه", "يرجى اختيار صف للتعديل")
            return
        data = self.repo.get_by_id(row_id)
        if not data:
            QMessageBox.warning(self, "تنبيه", "تعذر العثور على السجل")
            return
        dlg = BaseCrudDialog(title=f"تعديل {self.windowTitle()}", fields=self.add_edit_fields, repository=self.repo, initial_data=data, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()

    def on_delete(self):
        if not self.allow_delete:
            return
        row_id = self._current_row_id()
        if not row_id:
            QMessageBox.information(self, "تنبيه", "يرجى اختيار صف للحذف")
            return
        if QMessageBox.question(self, "تأكيد", "هل تريد حذف السجل المحدد؟") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.repo.delete(row_id)
            self.load_data()
            self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل حذف السجل: {e}")


# ====================== أدوات مساعدة للتهيئة من القواميس الموجودة ======================

def get_table_columns_for_section(section_name: str) -> List[Dict[str, str]]:
    """تحويل تعريف الأعمدة في الإعدادات إلى صيغة موحدة لهذه النافذة."""
    cols = TABLE_COLUMNS.get(section_name, [])
    # التأكد من وجود عمود id لسهولة التحديد
    has_id = any(c.get('key', '').lower() in ('id', 'معرف') for c in cols)
    if not has_id:
        cols = [{"key": "id", "label": "id"}] + cols
    return cols


def build_repository_for_section(db: DatabaseManager, section_name: str) -> Optional[GenericRepository]:
    table = UI_SECTION_TO_DB_TABLE_MAP.get(section_name)
    if not table:
        return None
    cols = get_table_columns_for_section(section_name)
    allowed = [c['key'] for c in cols if c['key'].lower() != 'id']
    return GenericRepository(db=db, table_name=table, allowed_columns=allowed, primary_key='id')


# ====================== مثال استخدام (للاختبار السريع) ======================

if __name__ == "__main__":
    # تشغيل اختبار بسيط للنافذة الموحدة لأي قسم موجود تعريفه في الإعدادات
    try:
        from PySide6.QtWidgets import QApplication
    except Exception:
        from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    section = "المشاريع"  # غيّرها لتجربة أقسام أخرى: "المشاريع"، "الموظفين"...
    columns = get_table_columns_for_section(section)
    db = DatabaseManager()
    repo = build_repository_for_section(db, section)
    if repo is None:
        QMessageBox.warning(None, "تنبيه", f"لا يوجد جدول مرتبط بالقسم: {section}")
        sys.exit(0)

    # تحويل الأعمدة إلى حقول لنموذج الإضافة/التعديل (باستثناء id)
    fields = []
    for c in columns:
        if c['key'].lower() == 'id':
            continue
        # تقدير نوع الحقل من اسمه بشكل مبسط
        key = c['key']
        ftype: FieldType = 'text'
        if 'تاريخ' in key:
            ftype = 'date'
        elif 'مبلغ' in key or key in ("المبلغ", "الباقي", "المدفوع", "المرتب", "النسبة"):
            ftype = 'number'
        fields.append(FieldConfig(name=key, label=c['label'].strip(), type=ftype))

    win = UnifiedManagementWindow(title=section, repository=repo, table_columns=columns, add_edit_fields=fields)
    win.resize(1100, 700)
    win.show()
    sys.exit(app.exec())


