import sys
import os
from lxml import etree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog,
    QColorDialog, QSpinBox, QCheckBox, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QPalette, QIcon
import re
import traceback

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
# >>>>>>>>>>>>> القيمة الثابتة لـ viewBox <<<<<<<<<<<<<<<<
FIXED_VIEWBOX_VALUE = "0 0 24 24"
# يمكنك تغيير هذه القيمة إذا كانت أيقوناتك مصممة على شبكة أخرى، مثلاً "0 0 16 16" أو "0 0 32 32"
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# احصل على مسار التطبيق
def get_application_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

# Svgmanipulator
class SvgManipulator(QWidget):
    # init
    def __init__(self):
        super().__init__()
        self.setWindowTitle("محرر SVG")
        self.setGeometry(100, 100, 550, 600) # زيادة الارتفاع قليلاً لاستيعاب الخيار الجديد

        self.selected_color = None
        # لم نعد بحاجة لـ current_svg_original_width/height لأننا سنفرض viewBox
        self.default_output_size = 256 # الحجم الذي ستظهر به الصورة بعد المعالجة (افتراضي)

        self.init_ui()
        self.set_default_folder()

    # init
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Folder Selection
        folder_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("اسحب مجلد SVG إلى هنا أو انقر على 'تصفح'")
        browse_folder_button = QPushButton("تصفح المجلد...")
        browse_folder_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(browse_folder_button)
        main_layout.addLayout(folder_layout)

        # Color Selection
        color_section_label = QLabel("<b>1. تغيير لون التعبئة (Fill):</b>")
        main_layout.addWidget(color_section_label)
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("اختر لون التعبئة")
        self.color_button.clicked.connect(self.select_color)
        self.color_preview_label = QLabel("لم يتم اختيار لون")
        self.color_preview_label.setFixedSize(120, 25)
        self.color_preview_label.setAutoFillBackground(True)
        self.update_color_preview(None)
        self.no_color_checkbox = QCheckBox("إزالة لون التعبئة (شفاف)")
        self.no_color_checkbox.stateChanged.connect(self.toggle_color_selection)
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview_label)
        color_layout.addWidget(self.no_color_checkbox)
        main_layout.addLayout(color_layout)

        # Size Adjustment (هذه الآن تتحكم في width/height الخارجية فقط)
        size_section_label = QLabel(f"<b>2. تحديد أبعاد الإخراج (width/height الخارجية):</b>")
        main_layout.addWidget(size_section_label)
        size_layout = QHBoxLayout()
        self.width_input = QSpinBox()
        self.width_input.setPrefix("العرض: ")
        self.width_input.setSuffix(" px")
        self.width_input.setRange(1, 10000) # يجب أن يكون أكبر من 0
        self.width_input.setValue(self.default_output_size)

        self.height_input = QSpinBox()
        self.height_input.setPrefix("الارتفاع: ")
        self.height_input.setSuffix(" px")
        self.height_input.setRange(1, 10000) # يجب أن يكون أكبر من 0
        self.height_input.setValue(self.default_output_size)
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(self.height_input)
        main_layout.addLayout(size_layout)

        # ViewBox Control Section
        viewbox_section_label = QLabel(f"<b>3. تحكم في viewBox:</b>")
        main_layout.addWidget(viewbox_section_label)
        viewbox_layout = QHBoxLayout()
        self.change_viewbox_checkbox = QCheckBox(f"تغيير viewBox إلى {FIXED_VIEWBOX_VALUE}")
        self.change_viewbox_checkbox.setChecked(False)  # افتراضياً غير مفعل
        viewbox_layout.addWidget(self.change_viewbox_checkbox)
        main_layout.addLayout(viewbox_layout)

        # Process Button
        self.process_button = QPushButton("معالجة SVG")
        self.process_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-weight: bold;")
        self.process_button.clicked.connect(self.confirm_and_process_svgs)
        main_layout.addWidget(self.process_button)

        # Status Area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText("ستظهر حالة المعالجة هنا...")
        main_layout.addWidget(self.status_text)

        self.setLayout(main_layout)
        self.setAcceptDrops(True)

    # تعيين المجلد الافتراضي
    def set_default_folder(self):
        base_path = get_application_path()
        icons_path = os.path.join(base_path, 'icons')
        if os.path.isdir(icons_path):
            self.folder_path_edit.setText(icons_path)
            self.status_text.append(f"تم تحديد المجلد الافتراضي: {icons_path}")
        else:
            self.status_text.append(f"المجلد الافتراضي 'icons' غير موجود بجانب السكربت ({icons_path}).")

    # تحديث معاينة اللون
    def update_color_preview(self, color):
        palette = self.color_preview_label.palette()
        if color:
            palette.setColor(QPalette.ColorRole.Window, color)
            self.color_preview_label.setText(color.name())
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
            self.color_preview_label.setText("لم يتم الاختيار")
        self.color_preview_label.setPalette(palette)

    # تبديل اختيار اللون
    def toggle_color_selection(self, state):
        is_checked = self.no_color_checkbox.isChecked()
        if is_checked:
            self.color_button.setEnabled(False)
            self._previous_selected_color_before_none = self.selected_color
            self.selected_color = "none"
            palette = self.color_preview_label.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#e0e0e0"))
            self.color_preview_label.setPalette(palette)
            self.color_preview_label.setText("تعبئة شفافة")
        else:
            self.color_button.setEnabled(True)
            if hasattr(self, '_previous_selected_color_before_none') and isinstance(self._previous_selected_color_before_none, QColor):
                self.selected_color = self._previous_selected_color_before_none
            else:
                self.selected_color = None
            self.update_color_preview(self.selected_color)

    # حدث الناقل
    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            if url.isLocalFile() and os.path.isdir(url.toLocalFile()):
                event.acceptProposedAction()
                return
        event.ignore()

    # دروبنت
    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            if url.isLocalFile():
                folder_path = url.toLocalFile()
                if os.path.isdir(folder_path):
                    self.folder_path_edit.setText(folder_path)
                    self.status_text.append(f"تم تحديد المجلد: {folder_path}")
                    return
        event.ignore()

    # مجلد تصفح
    def browse_folder(self):
        current_path = self.folder_path_edit.text() or get_application_path()
        folder_path = QFileDialog.getExistingDirectory(self, "اختر مجلد SVG", current_path)
        if folder_path:
            self.folder_path_edit.setText(folder_path)
            self.status_text.append(f"تم تحديد المجلد: {folder_path}")

    # حدد اللون
    def select_color(self):
        current_color = self.selected_color if isinstance(self.selected_color, QColor) else Qt.GlobalColor.white
        color = QColorDialog.getColor(current_color, self, "اختر لون التعبئة")
        if color.isValid():
            self.selected_color = color
            self.update_color_preview(color)
            self.status_text.append(f"تم اختيار اللون: {color.name()}")
            if self.no_color_checkbox.isChecked():
                self.no_color_checkbox.setChecked(False)

    # تأكيد ومعالجة SVGs
    def confirm_and_process_svgs(self):
        folder_path = self.folder_path_edit.text()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى تحديد مجلد يحتوي على ملفات SVG أولاً.")
            return

        # تحديد رسالة التحذير بناءً على حالة checkbox
        if self.change_viewbox_checkbox.isChecked():
            warning_message = (f"<b>تحذير:</b> سيتم تعديل ملفات SVG مباشرة في المجلد المحدد.\n"
                             f"سيتم تعيين <b>viewBox</b> لجميع الملفات إلى <b>{FIXED_VIEWBOX_VALUE}</b>.\n"
                             "هل أنت متأكد أنك تريد المتابعة؟\n\n"
                             "<i>يوصى بشدة بأخذ نسخة احتياطية من المجلد قبل المتابعة.</i>")
        else:
            warning_message = ("<b>تحذير:</b> سيتم تعديل ملفات SVG مباشرة في المجلد المحدد.\n"
                             "سيتم تعديل الألوان والأبعاد فقط (viewBox لن يتم تغييره).\n"
                             "هل أنت متأكد أنك تريد المتابعة؟\n\n"
                             "<i>يوصى بشدة بأخذ نسخة احتياطية من المجلد قبل المتابعة.</i>")

        reply = QMessageBox.warning(self, 'تأكيد الكتابة فوق الملفات',
                                     warning_message,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.process_svgs(folder_path)
        else:
            self.status_text.append("تم إلغاء عملية المعالجة من قبل المستخدم.")

    # تطبيق اللون على العنصر
    def _apply_color_to_element(self, elem, color_str):
        style_attr = elem.get('style')
        color_applied = False
        if style_attr:
            styles = [s.strip() for s in style_attr.split(';') if s.strip()]
            new_styles = []
            style_fill_found = False
            for style_item in styles:
                if style_item.lower().startswith('fill:'):
                    if color_str:
                        new_styles.append(f'fill:{color_str}')
                    style_fill_found = True
                else:
                    new_styles.append(style_item)
            if not style_fill_found and color_str:
                new_styles.append(f'fill:{color_str}')

            if new_styles:
                elem.set('style', '; '.join(new_styles).strip())
                color_applied = True
            elif 'style' in elem.attrib: # إذا كانت new_styles فارغة بسبب color_str=None
                del elem.attrib['style']
        elif color_str: # لا يوجد style، استخدم fill مباشرة
            if color_str.lower() == 'none':
                if 'fill' in elem.attrib:
                    del elem.attrib['fill']
            else:
                elem.set('fill', color_str)
            color_applied = True
        return color_applied

    # عملية SVGs
    def process_svgs(self, folder_path):
        output_w = self.width_input.value() # هذا هو width الخارجي
        output_h = self.height_input.value() # هذا هو height الخارجي

        self.status_text.append(f"\n--- بدء المعالجة (viewBox ثابت: {FIXED_VIEWBOX_VALUE}) ---")
        processed_count = 0
        failed_count = 0

        parser = ET.XMLParser(recover=True, strip_cdata=False, resolve_entities=False, remove_blank_text=True)
        target_tags_local_names = ["path", "rect", "circle", "ellipse", "polygon", "polyline", "text", "g"]

        for filename in os.listdir(folder_path):
            if not filename.lower().endswith(".svg"):
                continue

            svg_file_path = os.path.join(folder_path, filename)
            self.status_text.append(f"معالجة: {filename}...")

            try:
                with open(svg_file_path, 'rb') as f:
                    content_bytes = f.read()

                cleaned_content_str = content_bytes.decode('utf-8', errors='replace')
                cleaned_content_str = re.sub(r'/>/\s*fill="currentColor"\s*>', '/>', cleaned_content_str, flags=re.IGNORECASE)
                cleaned_content_str = re.sub(r'/>\s*/\s*>', '/>', cleaned_content_str, flags=re.IGNORECASE)
                content_bytes_for_parser = cleaned_content_str.encode('utf-8')

                tree_root = ET.fromstring(content_bytes_for_parser, parser=parser)
                if tree_root is None:
                    self.status_text.append(f"  فشل: لا يمكن تحليل بنية XML لـ {filename} حتى بعد التنظيف.")
                    failed_count += 1
                    continue

                xml_tree = tree_root.getroottree()
                svg_root = xml_tree.getroot()

                qname_svg = ET.QName(svg_root.tag)
                if not (qname_svg.localname == 'svg' and qname_svg.namespace == SVG_NAMESPACE):
                    self.status_text.append(f"  فشل: الملف {filename} ليس ملف SVG صالح (الجذر ليس <svg>).")
                    failed_count += 1
                    continue

                # 1. تعديل اللون
                color_to_set = None
                if self.no_color_checkbox.isChecked():
                    color_to_set = "none"
                elif self.selected_color and isinstance(self.selected_color, QColor):
                    color_to_set = self.selected_color.name()

                if color_to_set:
                    elements_colored_count = 0
                    for elem in svg_root.xpath(".//*", namespaces={'svg': SVG_NAMESPACE}):
                        q_elem_name = ET.QName(elem.tag)
                        if q_elem_name.namespace == SVG_NAMESPACE and q_elem_name.localname in target_tags_local_names:
                            if self._apply_color_to_element(elem, color_to_set):
                                elements_colored_count +=1

                    if elements_colored_count == 0 and color_to_set != "none": # حاول على الجذر إذا لم يتم تلوين أي شيء
                        self._apply_color_to_element(svg_root, color_to_set)
                    self.status_text.append(f"  اللون: تم تطبيق '{color_to_set}' (تأثر: {elements_colored_count} عنصر)")


                # 2. تطبيق الأبعاد الخارجية و viewBox الثابت
                svg_root.set('width', f"{output_w}px")
                svg_root.set('height', f"{output_h}px")

                if self.change_viewbox_checkbox.isChecked():
                    svg_root.set('viewBox', FIXED_VIEWBOX_VALUE)
                    svg_root.set('preserveAspectRatio', 'xMidYMid meet') # مهم للتحجيم الصحيح
                    self.status_text.append(f"  الحجم: تم تعيين width={output_w}px, height={output_h}px, viewBox='{FIXED_VIEWBOX_VALUE}'")
                else:
                    self.status_text.append(f"  الحجم: تم تعيين width={output_w}px, height={output_h}px (viewBox لم يتم تغييره)")

                # كتابة الملف
                with open(svg_file_path, 'wb') as f_out:
                    f_out.write(ET.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))
                processed_count += 1
                # self.status_text.append(f"  نجاح: تم تعديل {filename}") # تم تضمينها في رسالة الحجم

            except Exception as e:
                failed_count += 1
                self.status_text.append(f"  فشل: خطأ أثناء معالجة {filename}: {type(e).__name__} - {e}")
                self.status_text.append(f"    {traceback.format_exc().splitlines()[-1]}") # آخر سطر من تتبع الخطأ

        self.status_text.append(f"\n--- اكتملت المعالجة ---")
        self.status_text.append(f"ملفات تم تعديلها بنجاح: {processed_count}")
        self.status_text.append(f"ملفات فشلت معالجتها: {failed_count}")

        if processed_count > 0 or failed_count > 0:
            QMessageBox.information(self, "اكتملت المعالجة",
                                    f"تمت معالجة الملفات.\n"
                                    f"الناجحة: {processed_count}\n"
                                    f"الفاشلة: {failed_count}\n\n"
                                    f"تم تعديل الملفات في نفس المجلد.")
        else:
            QMessageBox.information(self, "لا توجد ملفات", "لم يتم العثور على ملفات SVG في المجلد المحدد أو لم يتم إجراء أي تغييرات.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = SvgManipulator()
    editor.show()
    sys.exit(app.exec())