from الإعدادات_العامة import*
from ستايل import*

# المعاينة
class PreviewDialog(QDialog):
    # init
    def __init__(self, html_file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("معاينة الطباعة")
        self.resize(1000, 600)
        self.html_file_path = html_file_path

        # إعداد التخطيط
        layout = QVBoxLayout()
        
        # إضافة QWebEngineView لعرض ملف HTML
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl.fromLocalFile(html_file_path))
        layout.addWidget(self.web_view)

        # إضافة زر الطباعة
        print_button = QPushButton(qta.icon('fa5s.print', color='navy'), "طباعة ")
        print_button.clicked.connect(self.print_document)
        layout.addWidget(print_button)

        self.setLayout(layout)

    # وثيقة طباعة
    def print_document(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setPageOrientation(QPageLayout.Landscape)

        # مسار ملف PDF المؤقت
        temp_pdf_path = os.path.join(documents_folder, "Reports", "temp_print.pdf")

        # رد الاتصال عند اكتمال إنشاء PDF
        # انتهى PDF
        def pdf_finished(path, success):
            if success:
                # الانتظار للتأكد من اكتمال كتابة الملف
                for _ in range(10):  # محاولة لمدة 5 ثوانٍ
                    if os.path.exists(temp_pdf_path) and os.path.getsize(temp_pdf_path) > 0:
                        try:
                            dialog = QPrintDialog(printer, self)
                            if dialog.exec() == QPrintDialog.Accepted:
                                if os.name == 'nt':  # Windows
                                    open_file_and_print(temp_pdf_path) # فتح نافذة الطباعة لملف PDF
                                elif os.name == 'posix':  # Linux/Mac
                                    os.system(f"lp {temp_pdf_path}")  # ضبط الأمر حسب النظام
                                self.accept()  # إغلاق النافذة بعد بدء الطباعة
                            break
                        except OSError as e:
                            QMessageBox.warning(self, "خطأ", f"فشل في فتح ملف PDF للطباعة: {e}\nيمكنك فتح الملف يدويًا من: {temp_pdf_path}")
                            os.startfile(temp_pdf_path)  # فتح الملف للمعاينة فقط إذا فشل الطباعة
                            self.accept()
                            break
                    time.sleep(0.5)  # الانتظار 0.5 ثانية بين المحاولات
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إنشاء ملف PDF أو الوصول إليه.")
            else:
                QMessageBox.critical(self, "خطأ", "فشل في إنشاء ملف PDF.")

        # تصدير HTML إلى PDF مع الحفاظ على التنسيق
        self.web_view.page().printToPdf(temp_pdf_path)
        self.web_view.page().pdfPrintingFinished.connect(pdf_finished)

# طباعة الجداول ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////  
# إدخالات طباعة
def print_entries(self):
    selected_year = self.year_combo.currentText()
    table_name = self.Interface_combo.currentText()
    user_text = self.profits_label2.text().replace("المستخدم", "").strip(" :")

    if table_name == "المشاريع":
        title = f"المشاريع {selected_year}"
        totel= self.profits_combo.text()#اجمالي المدفوع
        totel1= self.remaining_combo.text()#اجمالي الباقي
    elif table_name == "الحسابات":
        title = f"المصروفات {selected_year}"
        totel= self.profits_combo.text()#اجمالي المصروفات 
    elif table_name == "الموظفين":
        title = f"الموظفين {selected_year}"
        totel= self.Monthly_combo.text()#اجمالي الرصيد
        totel1= self.profits_combo.text()#اجمالي السحب

    # الحصول على تاريخ ووقت الطباعة الحالي
    current_time = datetime.now().strftime("%Y-%m-%d")

    html_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{title}</title>
        <style>
            @media print {{
                @page {{
                    margin: 15mm 10mm 15mm 10mm; /* هوامش متطابقة */
                    size: A4 landscape;  /* تخطيط الصفحة أفقياً */
                    @bottom-center {{
                        content: "" counter(page) " - " counter(pages);
                    }}
                }}
                body {{
                    -webkit-print-color-adjust: exact; /* فرض طباعة الألوان والخلفيات */
                    print-color-adjust: exact;
                }}
            }}

            body {{
                font-family: {print_font}, sans-serif;
                direction: rtl;
                text-align: center;
                margin: 15mm 10mm;
                padding: 0;

            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 2px;  /* بدل 10px */
                margin-top: 15px;
            }}
            .print-info {{
                font-size: 14px;
                color: #7f8c8d;
                margin-top: 0px;
                margin-bottom: 0px;  /* بدل 10px */
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 5px 0px;
                font-weight: bold;
                font-size: 14px;
                page-break-inside: auto; /* السماح بتقسيم الجدول عبر الصفحات */                       
                                
            }}
            th, td {{
                border: 1px solid black;  /* تغيير اللون إلى أسود */
                text-align: center;
                padding: 3px 3px;  /* تقليل الحشو العمودي */
            }}
            th {{
                background-color: #E4E0E1;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            thead {{
                display: table-header-group; /* تثبيت رؤوس الأعمدة عند تقسيم الجدول */
            }}
            tfoot {{
                display: table-footer-group;
            }}
            .page-break {{
                page-break-after: always; /* فصل كل جدول في صفحة جديدة */
            }}
            .footer-spacer td {{
                padding: 0;
                margin: 0;
                border: none;
            }}

        </style>
        <script>
            window.onload = function() {{
                window.print();  /* فتح نافذة الطباعة تلقائيًا عند تحميل الصفحة */
                window.onafterprint = function() {{
                    window.close();  /* إغلاق النافذة بعد الطباعة */
                }};
            }}
        </script>
    </head>    
    <body>
        <div class="company-info" style="display: flex; justify-content: flex-start; align-items: center; direction: rtl; width: 100%;">
            {f"<img src='" + logo_path + "' class='company-logo' alt='شعار الشركة' style='max-width: 5cm; max-height: 3cm; margin-left: 10px;'>" if logo_path else ""}
            <div class="company-name" style="font-size: 24px; font-family: {print_font}, Times, serif; font-weight: bold; color: #2c3e50; position: absolute; left: 50%; transform: translateX(-50%);">
                {company_name}
            </div>
        </div>
        
        <h1>{title}</h1>
        <p class="print-info">{current_time}</p>
        <tr class="footer-spacer"><td colspan="100">&nbsp;</td></tr>
        <table>
            <tr>
        
        <footer style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 20px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            border-top: 2px solid black;
            padding: 3px;
            background-color: white;">
            <span style="float: right; margin-right: 20px;">📍العنوان: {company_address}</span>
            <span style="float: left; margin-left: 20px; color: #7f8c8d;">🖨️{user_text}</span>
            <span style="float: left; margin-left: 20px;">📞 الهاتف:  {company_phone}</span>
            <span style="float: left; margin-left: 20px;">✉ إيميل:  {company_email}</span>
            
        </footer>

    </body>
    """
    search_text = self.search_input.text().strip()
    search_suffix = f"  ({search_text})" if search_text else ""

    # if table_name == "المشاريع":
    #     html_content += f"<p style='margin-top: 0px;'>( إجمالي المدفوع: {totel} {Currency_type} - إجمالي الباقي: {totel1} {Currency_type} )</p>"
    # elif table_name == "الحسابات":
    #     html_content += f"<p style='margin-top: 0px;'>إجمالي المصروفات: {totel} {Currency_type}</p>"
    # elif table_name == "الموظفين":
    #     html_content += f"<p style='margin-top: 0px;'>( إجمالي الرصيد: {totel} {Currency_type} - إجمالي السحب: {totel1} {Currency_type} )</p>"
    
    if table_name == "المشاريع":
        html_content += f"<p style='margin-top: 0px;'>( إجمالي المدفوع: {totel} {Currency_type} - إجمالي الباقي: {totel1} {Currency_type} ){search_suffix}</p>"
    elif table_name == "الحسابات":
        html_content += f"<p style='margin-top: 0px;'>إجمالي المصروفات: {totel} {Currency_type}{search_suffix}</p>"
    elif table_name == "الموظفين":
        html_content += f"<p style='margin-top: 0px;'>إجمالي الرصيد: {totel} {Currency_type}{search_suffix}</p>"
  


    # تحديد الأعمدة المراد تجاهلها
    ignored_columns = []
    if table_name == "المشاريع":
       # ignored_columns = [self.table.columnCount() - 1]  # العمود الأخير
        # البحث عن عمود "مدة الإنجاز"
        for column in range(self.table.columnCount()):
            if self.table.horizontalHeaderItem(column).text() == ' مدة الإنجاز  ':
                ignored_columns.append(column)

    html_content += "<thead><tr>"
    for column in range(1, self.table.columnCount()):  # بدءًا من العمود الأول
        if column not in ignored_columns:  # تخطي الأعمدة المخفية
            html_content += f"<th>{self.table.horizontalHeaderItem(column).text()}</th>"
    html_content += "</tr></thead><tbody>"

    # إنشاء الصفوف مع تجاهل الأعمدة المخفية
    for row in range(self.table.rowCount()):
        if not self.table.isRowHidden(row):
            html_content += "<tr>"
            for column in range(1, self.table.columnCount()):  # بدءًا من العمود الأول
                if column not in ignored_columns:  # تخطي الأعمدة المخفية
                    item = self.table.item(row, column)
                    if item is not None:
                        cell_text = item.text()
                        cell_text = item.text().strip()
                        
                        # التعديل المطلوب: إذا كان الجدول هو "المشاريع" واستلمنا "تم التسليم"، نحولها إلى "منتهي"
                        if table_name == "المشاريع" and cell_text.strip() == "تم التسليم":
                            cell_text = "منتهي"
                            html_content += f"<td style='background-color: #c8e6c9;'>{cell_text}</td>"
                        
                        
                        elif table_name == "المشاريع" and cell_text.strip() == "قيد الإنجاز":
                            cell_text = "مستمر"
                            html_content += f'<td style="background-color: #eee0bd; color: black;">{cell_text}</td>'

                        elif table_name == "المشاريع" and cell_text.strip() == "غير خالص":
                            cell_text = "معلق"
                            html_content += f'<td style="background-color: #dc8484; color: black;">{cell_text}</td>'
                        else:
                            html_content += f"<td>{cell_text}</td>"

                    else:
                        html_content += "<td></td>"
            html_content += "</tr>"
            
    #html_content += "</tbody></table><div class=\"page-break\"></div>"

    html_content += """
        </tbody>
        <tfoot>
            <tr class="footer-spacer"><td colspan="100" style="height: 15px;">&nbsp;</td></tr>
        </tfoot>
    </table>
    <div style="height: 15px;"></div>
    <div class="page-break"></div>
    """

    
    # تحديد المسار للمجلد في المستندات
    project_folder_path = os.path.join(documents_folder, "Reports")
    # إنشاء المجلد إذا لم يكن موجودًا
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)
    # تحديد مسار الملف بناءً على نوع الجدول
    if table_name == "المشاريع":
        html_file_path = os.path.join(project_folder_path, f"المشاريع{selected_year}.html")
    elif table_name == "الحسابات":
        html_file_path = os.path.join(project_folder_path, f"المصروفات{selected_year}.html")
    elif table_name == "الموظفين":
        html_file_path = os.path.join(project_folder_path, f"الموظفين{selected_year}.html")

    # كتابة المحتوى إلى الملف
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    # #فتح الملف في المتصفح الافتراضي
    # #webbrowser.open(f"file://{html_file_path}")
    create_window(self,html_file_path)

    # # فتح نافذة المعاينة مع ملف HTML
    # preview_dialog = PreviewDialog(html_file_path, self)
    # preview_dialog.exec()

#----------------فاتورة عميل + موظف---------------------------------
# بيانات جدول الطباعة
def print_table_data(self, mastr_table,table, title, name_column, project_column, total_column, remaining_column, paid_column, file_prefix):
    selected_year = self.year_combo.currentText()
    selected_row = mastr_table.currentRow()

    # التحقق من وجود صف محدد
    if selected_row < 0:
        QMessageBox.warning(self, "تحذير", "يرجى تحديد صف من الجدول أولاً")
        return

    # استخراج البيانات من الجدول
    name = mastr_table.item(selected_row, name_column).text()  # اسم العميل/الموظف
    project_name = mastr_table.item(selected_row, project_column).text()  # اسم المشروع/الوظيفة
    total_amount = mastr_table.item(selected_row, total_column).text()  # إجمالي المبلغ
    remaining_amount = mastr_table.item(selected_row, remaining_column).text()  # إجمالي الباقي
    paid_amount = mastr_table.item(selected_row, paid_column).text()  # المبلغ المدفوع
    current_datetime = datetime.now().strftime("%Y-%m-%d")  # تاريخ اليوم
    user_text = self.profits_label2.text().replace("المستخدم", "").strip(" :")

    # التحقق من قيمة إجمالي الباقي
    remaining_display = remaining_amount if remaining_amount == "خالص" else f"{remaining_amount} {Currency_type}"

    # حساب إجمالي الدفعات من الجدول
    total_payments = 0
    for row in range(table.rowCount()):
        if not table.isRowHidden(row):
            # البحث عن عمود المبلغ المدفوع
            for col in range(table.columnCount()):
                header = table.horizontalHeaderItem(col)
                if header and "المبلغ" in header.text() and "المدفوع" in header.text():
                    item = table.item(row, col)
                    if item and item.text().isdigit():
                        total_payments += int(item.text())
                    break

    # إنشاء محتوى HTML محسن
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset='UTF-8'>
        <title>{title} {name} {selected_year}</title>
        <style>
            @media print {{
                @page {{
                    size: A4 portrait;
                    margin: 15mm 10mm 15mm 10mm;
                    @bottom-center {{
                        content: "صفحة " counter(page) " من " counter(pages);
                    }}
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
            }}

            body {{
                direction: rtl;
                font-family: {print_font}, Arial, sans-serif;
                text-align: center;
                margin: 15mm 10mm;
                padding: 0;
                line-height: 1.6;
                color: #333;
            }}

            .company-info {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
                text-align: center;
            }}

            .company-logo {{
                width: 80px;
                height: 60px;
                object-fit: contain;
                margin-bottom: 10px;
            }}

            .company-name {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}

            .header {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px solid #2c3e50;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                
            }}

            .header h1 {{
                margin: 0 0 15px 0;
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }}

            .header .date {{
                font-size: 14px;
                font-weight: bold;
                color: #6c757d;
                text-align: center;
                margin-bottom: 15px;
            }}

            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 15px;
            }}

            .info-item {{
                background-color: #fff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
                text-align: right;
            }}

            .info-label {{
                font-weight: bold;
                color: #495057;
                font-size: 14px;
                margin-bottom: 5px;
            }}

            .info-value {{
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }}

            .summary-section {{
                background-color: #e3f2fd;
                border: 2px solid #1976d2;
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                text-align: center;
            }}

            .summary-title {{
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                margin-bottom: 10px;
            }}

            .summary-amount {{
                font-size: 22px;
                font-weight: bold;
                color: #d32f2f;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 14px;
                
                border-radius: 10px;
                overflow: hidden;
            }}

            th {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                font-weight: bold;
                padding: 12px 8px;
                text-align: center;
                font-size: 14px;
                border: none;
            }}

            td {{
                border: 1px solid #dee2e6;
                text-align: center;
                padding: 10px 8px;
                background-color: #fff;
            }}

            tr:nth-child(even) td {{
                background-color: #f8f9fa;
            }}

            tr:hover td {{
                background-color: #e3f2fd;
            }}

            thead {{
                display: table-header-group;
            }}

            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                height: 60px;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 20px;
                font-size: 12px;
                border-top: 3px solid #1976d2;
            }}

            .footer-section {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}

            .footer-item {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
        </style>
        <script>
            window.onload = function() {{
                window.print();
                window.onafterprint = function() {{
                    window.close();
                }};
            }}
        </script>
    </head>
    <body>
        <div class="company-info">
            {f'<img src="{logo_path}" class="company-logo" alt="شعار الشركة">' if logo_path else ''}
            {f'<div class="company-name">{company_name}</div>' if company_name else ''}
        </div>

        <div class="header">
            <h1>{title}</h1>
            <div class="date">تاريخ الطباعة: {current_datetime}</div>

            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">{'اسم الموظف' if 'موظف' in title else 'اسم العميل'}:</div>
                    <div class="info-value">{name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">إجمالي المبلغ:</div>
                    <div class="info-value">{total_amount} {Currency_type}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">{'الوظيفة' if 'موظف' in title else 'اسم المشروع'}:</div>
                    <div class="info-value">{project_name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">إجمالي الباقي:</div>
                    <div class="info-value">{remaining_display}</div>
                </div>
            </div>
        </div>

        <div class="summary-section">
            <div class="summary-title">إجمالي الدفعات المسجلة</div>
            <div class="summary-amount">{total_payments} {Currency_type}</div>
        </div>

        <table>

        <div class="footer">
            <div class="footer-section">
                <div class="footer-item">📍 {company_address}</div>
            </div>
            <div class="footer-section">
                <div class="footer-item">🖨️ {user_text}</div>
                <div class="footer-item">📞 {company_phone}</div>
                <div class="footer-item">✉ {company_email}</div>
            </div>
        </div>
    """

    # إضافة رأس الجدول
    html_content += "<thead><tr>"
    for column in range(table.columnCount()):
        if not table.isColumnHidden(column):
            html_content += f"<th>{table.horizontalHeaderItem(column).text()}</th>"
    html_content += "</tr></thead><tbody>"

    # إضافة الصفوف (معكوسة)
    for row in reversed(range(table.rowCount())):
        if not table.isRowHidden(row):
            html_content += "<tr>"
            for column in range(table.columnCount()):
                if not table.isColumnHidden(column):
                    item = table.item(row, column)
                    html_content += f"<td>{item.text() if item else ''}</td>"
            html_content += "</tr>"

    html_content += "</tbody></table>"

    # إضافة سكربت الطباعة
    html_content += """
    <script type="text/javascript">
        window.onload = function() {
            window.print();
            window.onafterprint = function() {
                window.close();
            };
        }
    </script>
    </body>
    </html>
    """

    # حفظ الملف
    project_folder_path = os.path.join(documents_folder, "Reports")
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)
    
    html_file_path = os.path.join(project_folder_path, f"{file_prefix} {selected_year}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    # فتح النافذة
    create_window(self, html_file_path)


#----------------تقارير الدفعات + تقارير موظفين---------------------------------
# تقرير جدول الطباعة
def print_table_report(self, table, title_prefix, summary_data=None, file_prefix=None):
    selected_year = self.year_combo1.currentText()
    title = f"{title_prefix} {selected_year}"
    current_time = datetime.now().strftime("%Y-%m-%d")
    user_text = self.profits_label2.text().replace("المستخدم", "").strip(" :")
    
    # تحديد اسم الملف إذا لم يتم تمريره
    file_prefix = file_prefix or title_prefix
    
    # إنشاء محتوى HTML
    html_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{title}</title>
        <style>
            @media print {{
                @page {{
                    size: A4 landscape;
                    margin: 15mm 10mm 15mm 10mm;
                    @bottom-center {{
                        content: "صفحة " counter(page) " من " counter(pages);
                    }}
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
            }}
            body {{
                font-family: {print_font}, sans-serif;
                direction: rtl;
                text-align: center;
                margin: 15mm 10mm;
                padding: 0;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .print-info {{
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 10px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 5px 0;
                font-weight: bold;
                font-size: 16px;
                page-break-inside: auto;
            }}
            th, td {{
                border: 1px solid black;
                text-align: center;
                padding: 5px;
            }}
            th {{
                background-color: #E4E0E1;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            thead {{
                display: table-header-group;
            }}
            tfoot {{
                display: table-footer-group;
            }}
            .page-break {{
                page-break-after: always;
            }}
            .footer-spacer td {{
                padding: 0;
                margin: 0;
                border: none;
            }}
        </style>
        <script>
            window.onload = function() {{
                window.print();
                window.onafterprint = function() {{
                    window.close();
                }};
            }}
        </script>
    </head>
    <body>
        <div class="company-info" style="display: flex; justify-content: flex-start; align-items: center; direction: rtl; width: 100%;">
            {f"<img src='{logo_path}' class='company-logo' alt='شعار الشركة' style='max-width: 5cm; max-height: 3cm; margin-left: 10px;'>" if logo_path else ""}
            <div class="company-name" style="font-size: 24px; font-family: {print_font}, Times, serif; font-weight: bold; color: #2c3e50; position: absolute; left: 50%; transform: translateX(-50%);">
                {company_name}
            </div>
        </div>
        <h1>{title}</h1>
        <p class="print-info">{current_time}</p>
        <table>
        <footer style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 20px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            border-top: 2px solid black;
            padding: 3px;
            background-color: white;">
            <span style="float: right; margin-right: 20px;">📍العنوان: {company_address}</span>
            <span style="float: left; margin-left: 20px; color: #7f8c8d;">🖨️{user_text}</span>
            <span style="float: left; margin-left: 20px;">📞 الهاتف: {company_phone}</span>
            <span style="float: left; margin-left: 20px;">✉ إيميل: {company_email}</span>
        </footer>
    </body>
    """

    # إضافة بيانات الملخص (إن وجدت)
    search_text = self.search_lineEdit.text().strip()
    search_suffix = f" ({search_text})" if search_text else ""
    
    if summary_data:
        if "balance" in summary_data:
            html_content += f"<p>إجمالي الرصيد: {summary_data['balance']} {Currency_type}{search_suffix}</p>"
        elif "total_paid" in summary_data:
            summary_title = f"إجمالي الدفعات: {summary_data['total_paid']} {Currency_type}{search_suffix}"
            html_content += f"<h2 style='text-align: center;'>{summary_title}</h2>"

    # جمع الأعمدة الظاهرة فقط
    visible_columns = [col for col in range(table.columnCount()) if not table.isColumnHidden(col)]

    # رأس الجدول
    html_content += "<thead><tr>"
    for column in visible_columns:
        header_item = table.horizontalHeaderItem(column)
        html_content += f"<th>{header_item.text()}</th>" if header_item else "<th></th>"
    html_content += "</tr></thead><tbody>"

    # البيانات
    for row in reversed(range(table.rowCount())):
        if not table.isRowHidden(row):
            html_content += "<tr>"
            for column in visible_columns:
                item = table.item(row, column)
                html_content += f"<td>{item.text() if item else ''}</td>"
            html_content += "</tr>"

    html_content += """
        </tbody>
        <tfoot>
            <tr class="footer-spacer"><td colspan="100" style="height: 15px;">&nbsp;</td></tr>
        </tfoot>
    </table>
    <div style="height: 15px;"></div>
    <div class="page-break"></div>
    </body>
    </html>
    """

    # حفظ الملف
    project_folder_path = os.path.join(documents_folder, "Reports")
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)
    
    html_file_path = os.path.join(project_folder_path, f"{file_prefix}{selected_year}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    # فتح النافذة
    create_window(self, html_file_path)


# طباعة فاتورة مصروفات /////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 
# طباعة فاتورة نفقات
def print_expense_invoice(self):
    # الحصول على بيانات الفاتورة
    expense_description = self.expense_edit.text()  # استبدال "المصروف" بـ "وصف المصروف"
    code = self.code_edit.text()
    paid_amount = self.amount_edit.text()  # استبدال "المبلغ" بـ "المبلغ المدفوع"
    receipt_date = self.date_edit.text()  # استبدال "التاريخ" بـ "تاريخ الاستلام"
    recipient_name = self.recipient_edit.text()  # استبدال "المستلم" بـ "اسم المستلم"
    invoice_number = self.invoice_number_edit.text()
    phone = self.phone_edit.text()  # رقم الهاتف
    notes = self.notes_edit.text()

    # الحصول على تاريخ ووقت الطباعة الحالي
    print_time = datetime.now().strftime("%Y-%m-%d")  # تاريخ الطباعة
    user_text = self.profits_label2.text().replace("المستخدم", "").strip(" :")

    # تنسيق البيانات في HTML مع تصميم احترافي للفاتورة
    html_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>فاتورة مصروفات</title>
        <style>
            @media print {{
                @page {{
                    margin: 15mm 10mm 15mm 10mm; /* هوامش متطابقة */
                    size: A4 portrait;  /* تخطيط الصفحة بالطول */
                }}
                body {{
                    -webkit-print-color-adjust: exact; /* فرض طباعة الألوان والخلفيات */
                    print-color-adjust: exact;
                }}
            }}
            body {{
                font-family: {print_font}, sans-serif;
                direction: rtl;
                margin: 15mm 10mm;
                padding: 0;
                font-size: 22px;  /* تكبير الخط */
            }}
            .invoice-container {{
                width: 80%;
                margin: 0 auto;
                border: 2px solid #333;
                padding: 30px;
                border-radius: 10px;
                
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 30px;
                text-align: center;
                font-weight: bold;
            }}
            .invoice-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
            }}
            .invoice-header .logo {{
                font-size: 22px;
                font-weight: bold;
                color: #34495e;
            }}
            .invoice-header .date {{
                font-size: 18px;
                color: #7f8c8d;
                font-weight: bold;
            }}
            .invoice-body {{
                margin-top: 30px;
                text-align: right;
            }}
            .invoice-body .row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
                align-items: center;
                border-bottom: 1px solid #ccc;  /* إضافة خط أفقي بين الصفوف */
                padding-bottom: 15px;
            }}
            .invoice-body .label {{
                font-weight: bold;
                width: 20%;
                text-align: right;  /* محاذاة من اليمين */
                font-size: 18px;  /* تكبير خط العناوين */
            }}
            .invoice-body .field {{
                flex: 1;
                text-align: center;  /* محاذاة البيانات في المنتصف */
                font-size: 18px;  /* تكبير خط البيانات */
            }}
            .invoice-body .row > div {{
                flex: 1;
                text-align: center;
            }}
            .invoice-footer {{
                margin-top: 40px;
                text-align: left;
                font-size: 18px;
                color: #7f8c8d;
            }}
            .footer-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 40px;
            }}
            .footer-row .signature {{
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                width: 45%;
            }}
            .footer-row .notes {{
                font-size: 18px;
                text-align: center;
                width: 45%;
            }}
        </style>
        <script>
            window.onload = function() {{
                window.print();  /* فتح نافذة الطباعة تلقائيًا عند تحميل الصفحة */
                window.onafterprint = function() {{
                    window.close();  /* إغلاق النافذة بعد الطباعة */
                }};
            }}
        </script>
    </head>
    <footer style="
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 20px;
        width: 100%;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        border-top: 2px solid black;
        padding: 3px;
        background-color: white;">
        <span style="float: right; margin-right: 20px;">📍العنوان: {company_address}</span>
        <span style="float: left; margin-left: 20px; color: #7f8c8d;">🖨️{user_text}</span>
        <span style="float: left; margin-left: 20px;">📞 الهاتف:  {company_phone}</span>
        <span style="float: left; margin-left: 20px;">✉ إيميل:  {company_email}</span>
    </footer>

    <body>
        <div class="invoice-container">
            <div class="invoice-header">
                <div class="logo">
                    {company_name}
                </div>
                <div class="date">
                    {print_time}
                </div>
            </div>
            <h1>فاتورة مصروفات رقم: {invoice_number}</h1>
            
            <div class="invoice-body">
                <!-- وصف المصروف والمبلغ المدفوع في نفس الصف -->
                <div class="row">
                    <div class="label">المصروف:</div>
                    <div class="field">{expense_description}</div>
                    <div class="label">المبلغ:</div>
                    <div class="field">{paid_amount} {Currency_type}</div>
                </div>

                <!-- اسم المستلم ورقم الهاتف في صف جديد -->
                <div class="row">
                    <div class="label">المستلم:</div>
                    <div class="field">{recipient_name}</div>
                    <div class="label">الهاتف:</div>
                    <div class="field">{phone}</div>
                </div>

                <!-- التصنيف في المنظومة وتاريخ الاستلام في نفس الصف -->
                <div class="row">
                    <div class="label">كود المنظومة:</div>
                    <div class="field">{code}</div>
                    <div class="label">تاريخ الاستلام:</div>
                    <div class="field">{receipt_date}</div>
                </div>
            </div>

            <!-- ملاحظات والتوقيع في نفس الصف -->
            <div class="footer-row">
                <div class="notes">الملاحظات: {notes}</div>
                <div class="signature">التوقيع: _____________</div>
            </div>

        </div>
    </body>
    </html>
    """

    # تحديد المسار لحفظ الفاتورة
    report_folder_path = os.path.join(documents_folder, "Reports")
    if not os.path.exists(report_folder_path):
        os.makedirs(report_folder_path)

    # حفظ المحتوى إلى ملف HTML
    html_file_path = os.path.join(report_folder_path, f"فاتورة_{invoice_number}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    # فتح الملف في المتصفح الافتراضي للطباعة
    #webbrowser.open(f"file://{html_file_path}")
    create_window(self,html_file_path)


#طباعة كشف حساب عام ////////////////////////////////////////////////////////
# طباعة kshf
def print_KSHF(self):
    selected_year = self.year_combo2.currentText()  # الحصول على السنة المختارة
    current_time = datetime.now().strftime("%Y-%m-%d")  # التاريخ والوقت الحالي
    # تحويل AM/PM إلى "ص" أو "م"
    current_time = current_time.replace("AM", "ص").replace("PM", "م")

    html_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{selected_year} كشف حساب عام</title>
        <style>
            @media print {{
                @page {{
                size: A4 landscape;  /* تخطيط الصفحة أفقي */
                margin: 15mm 10mm 15mm 10mm;         /* هوامش متطابقة */
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                    /* تقليل حجم المحتوى لتلاؤمه مع صفحة واحدة */
                    transform: scale(1);
                    transform-origin: top left;
                }}
                /* تعطيل أي فواصل صفحات مفروضة */
                .page-break {{
                    display: none;
                }}
                /* محاولة منع تقسيم الحاويات الكبيرة */
                .container, table {{
                    page-break-inside: avoid;
                }}
            }}

            body {{
                font-family: {print_font}, sans-serif;
                direction: rtl;
                margin: 15mm 10mm;
                padding: 0;
            }}
            .container {{
                width: 100%;
                overflow: hidden;
            }}
            .header {{
                text-align: center;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;  /* تنزيل العنوان قليلاً */
                margin-bottom: 5px;
                color: #333;
            }}
            .subheader {{
                text-align: center;
                font-size: 14px;
                color: #555;
                margin-bottom: 10px;
            }}
            .row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }}
            .column {{
                flex: 1;
                margin-right: 20px;
                min-width: 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                direction: rtl;
                margin-bottom: 0;
                font-weight: bold;
                font-size: 18px;
                page-break-inside: auto;
            }}
            th, td {{
                border: 1px solid #ddd;
                text-align: center;
                padding: 5px; /* تقليل ارتفاع صفوف العناوين والخلايا */
                font-size: 15px;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .title {{
                text-align: center;
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 15px;
            }}
            
        </style>
        <script>
            window.onload = function() {{
                window.print();  /* فتح نافذة الطباعة مباشرة بعد تحميل الصفحة */
                window.onafterprint = function() {{
                    window.close();  /* إغلاق النافذة بعد الطباعة */
                }};
            }};
        </script>
    </head>
    <body>
    <div class="header">كشف حساب {selected_year}</div>
    <div class="subheader">{current_time}</div>
    """

    for i, table in enumerate(self.tables):
        if hasattr(table, 'findChild'):
            reports_table = table.findChild(QTableWidget)
            if reports_table:
                if i % 3 == 0:
                    if i != 0:
                        html_content += "</div>"  # إغلاق الصف السابق
                    html_content += "<div class='row'>"  # بدء صف جديد

                month_title = f"شهر {i + 1}" if i < 12 else ""  # تعيين عنوان الشهر أو عنوان الجدول النهائي
                if i >= 12:  # لمعالجة الجداول الأخيرة
                    titles = ["إجمالي السنة", "رصيد الموظفين", "إجمالي الأرباح"]
                    month_title = titles[i - 12]

                html_content += "<div class='column'><div class='title'>{}</div><table>".format(month_title)
                html_content += "<tr>"
                for column in range(reports_table.columnCount()):
                    html_content += f"<th>{reports_table.horizontalHeaderItem(column).text()}</th>"
                html_content += "</tr>"

                for row in range(reports_table.rowCount()):
                    if not reports_table.isRowHidden(row):
                        html_content += "<tr>"
                        for column in range(reports_table.columnCount()):
                            item = reports_table.item(row, column)
                            if item is not None:
                                html_content += f"<td>{item.text()}</td>"
                            else:
                                html_content += "<td></td>"
                        html_content += "</tr>"

                html_content += "</table></div>"
    
    # تحديد المسار للمجلد في المستندات
    project_folder_path = os.path.join(documents_folder, "Reports")
    # إنشاء المجلد إذا لم يكن موجودًا
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)

    html_content += "</div></body></html>"
    html_file_path = os.path.join(project_folder_path, f"كشف حساب {selected_year}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    #webbrowser.open(f"file://{html_file_path}")
    create_window(self,html_file_path)
    

#طباعة كشف حساب تفصيلي/////////////////////////////////////////////////////////////////////////////////
# تُتوقف طباعة
def print_deteles(self):
    # الحصول على التواريخ من عناصر QDateEdit
    start_date = self.start_date_edit.date().toString('yyyy-MM-dd')
    end_date = self.end_date_edit.date().toString('yyyy-MM-dd')
    # الحصول على التواريخ من عناصر QDateEdit
    start_date1 = self.start_date_edit.date().toString('yyyy-MM-dd')
    end_date1 = self.end_date_edit.date().toString('yyyy-MM-dd')
    
    # إعداد العنوان العلوي للطباعة
    report_title = f"كشف حساب من {start_date} إلى {end_date}"
    report_title1 = f"كشف حساب من {start_date1} إلى {end_date1}"

    selected_year = self.start_date_edit.date()  # الحصول على السنة المختارة
    current_time = datetime.now().strftime("%Y-%m-%d")  # التاريخ والوقت الحالي
    current_time = current_time.replace("AM", "ص").replace("PM", "م")  # تحويل AM/PM إلى "ص" أو "م"
    selected_table_name = self.table_selector.currentText()  # اسم الجدول المحدد

    # اختيار الجدول المناسب بناءً على الاختيار
    table_widget = None
    if selected_table_name == "المشاريع":
        table_widget = self.table_projects
        total_label=self.total_remaining
    elif selected_table_name == "دفعات المشاريع":
        table_widget = self.table_payments
        total_label=self.total_paid
    elif selected_table_name == "المصروفات":
        table_widget = self.table_expenses
        total_label=self.total_expenses
    elif selected_table_name == "معاملات الموظفين":
        table_widget = self.table_reports
        total_label=self.Employee_Balance
        total_label1=self.Employee_Withdraw
    
    elif selected_table_name == "جميع المعاملات":
        # جميع الجداول للطباعة
        all_tables = {
            "المشاريع": (self.table_projects, f"إجمالي الباقي {self.total_remaining} {Currency_type}"),
            "دفعات المشاريع": (self.table_payments, f"إجمالي الدفعات {self.total_paid} {Currency_type}"),
            "المصروفات": (self.table_expenses, f"إجمالي المصروفات {self.total_expenses} {Currency_type}"),
            "معاملات الموظفين": (self.table_reports, f"رصيد الموظفين {self.Employee_Balance} {Currency_type}", f"سحب الموظفين {self.Employee_Withdraw} {Currency_type}"),
        }
    else:  # "جميع المعاملات" أو أي قيمة افتراضية
        table_widget = None
    
    
    # بناء محتوى HTML
    html_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{report_title} كشف الحساب</title>
        <style>
            @media print {{
                @page {{
                    size: A4 landscape;  /* تخطيط الصفحة أفقياً */
                    margin: 15mm 10mm 15mm 10mm;/* هوامش متطابقة */
                    @bottom-center {{
                        content: "" counter(page) " - " counter(pages);
                    }}
                }}
                body {{
                    -webkit-print-color-adjust: exact; /* فرض طباعة الألوان والخلفيات */
                    print-color-adjust: exact;
                    /* تقليل حجم المحتوى لتلاؤمه مع صفحة واحدة */
                    transform: scale(1);
                    transform-origin: center;  /* تحديد نقطة الأصل للتحجيم */


                }}
            }}
            body {{
                font-family: {print_font}, sans-serif;
                direction: rtl;
                text-align: center;
                margin: 15mm 10mm;
                padding: 0;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .print-info {{
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 10px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 5px 0;
                font-weight: bold;
                font-size: 14px;
                page-break-inside: auto; /* السماح بتقسيم الجدول عبر الصفحات */
                table-layout: auto; /* القيمة الافتراضية */
            }}
            th, td {{
                border: 2px solid black;  /* تغيير اللون إلى أسود */
                text-align: center;
                padding: 5px 5px;  /* تقليل الحشو العمودي */
            }}
            th {{
                background-color: #E4E0E1;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            thead {{
                display: table-header-group; /* تثبيت رؤوس الأعمدة عند تقسيم الجدول */
            }}
            tfoot {{
                display: table-footer-group;
            }}
            .page-break {{
                page-break-after: always; /* فصل كل جدول في صفحة جديدة */
            }}
            
            .table-title {{
                background: linear-gradient(90deg, #8494a4, #bec2c7);
                color: white;
                padding: 15px;
                margin: 20px 0;
                border-radius: 10px;
                
                text-align: center;
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #697785;
            }}

            .footer-spacer td {{
                padding: 0;
                margin: 0;
                border: none;
            }}
        
        </style>
        <script>
            window.onload = function() {{
                window.print();  /* فتح نافذة الطباعة تلقائيًا عند تحميل الصفحة */
                window.onafterprint = function() {{
                    window.close();  /* إغلاق النافذة بعد الطباعة */
                }};
            }}
        </script>
    </head>
    <body>
        <h2 style="text-align: center;">{report_title}</h2>
        <h2 style="text-align: center;">{selected_table_name}</h2>
        <h4 style="text-align: center;">{current_time}</h4>
        <table>
            <tr>    
    """
    # يجب أن تستبعد
    def should_exclude(column_name):
        return column_name in ['id', 'معرف_العميل',"معرف_الموظف","مدة_الإنجاز","الوقت_المتبقي"]

    if selected_table_name == "جميع المعاملات":
        for table_name, (table_widget, *labels) in all_tables.items():
            if table_widget.rowCount() > 0:
                labels_text = " - ".join(labels)
                html_content += f"<div class='table-title'>{table_name}: ({labels_text})</div><table><thead><tr>"
                for column in range(table_widget.columnCount()):
                    header_item = table_widget.horizontalHeaderItem(column)
                    column_name = header_item.text() if header_item else ''
                    if not should_exclude(column_name):
                        html_content += f"<th>{column_name}</th>"
                html_content += "</tr></thead><tbody>"
                for row in range(table_widget.rowCount()):
                    if not table_widget.isRowHidden(row):
                        html_content += "<tr>"
                        for column in range(table_widget.columnCount()):
                            header_item = table_widget.horizontalHeaderItem(column)
                            column_name = header_item.text() if header_item else ''
                            if not should_exclude(column_name):
                                item = table_widget.item(row, column)
                                html_content += f"<td>{item.text() if item else ''}</td>"
                        html_content += "</tr>"
                html_content += "</tbody></table><div class='page-break'></div>"
    
    elif table_widget and table_widget.rowCount() > 0:
        if selected_table_name == "المشاريع":
            html_content += f"<div class='table-title'>{selected_table_name}: (إجمالي الباقي {total_label} {Currency_type}) </div><table><thead><tr>"
        if selected_table_name == "المصروفات":
            html_content += f"<div class='table-title'>{selected_table_name}: (إجمالي المصروفات {total_label} {Currency_type}) </div><table><thead><tr>"
        if selected_table_name == "دفعات المشاريع":
            html_content += f"<div class='table-title'>{selected_table_name}: (إجمالي الدفعات {total_label} {Currency_type}) </div><table><thead><tr>"
        if selected_table_name == "معاملات الموظفين":
            html_content += f"<div class='table-title'>{selected_table_name}: ( رصيد الموظفين {total_label} {Currency_type}) ( سحب الموظفين {total_label1} {Currency_type}) </div><table><thead><tr>"
        for column in range(table_widget.columnCount()):
            header_item = table_widget.horizontalHeaderItem(column)
            column_name = header_item.text() if header_item else ''
            if not should_exclude(column_name):
                html_content += f"<th>{column_name}</th>"
        html_content += "</tr></thead><tbody>"

        for row in range(table_widget.rowCount()):
            if not table_widget.isRowHidden(row):
                html_content += "<tr>"
                for column in range(table_widget.columnCount()):
                    header_item = table_widget.horizontalHeaderItem(column)
                    column_name = header_item.text() if header_item else ''
                    if not should_exclude(column_name):
                        item = table_widget.item(row, column)
                        html_content += f"<td>{item.text() if item else ''}</td>"
                html_content += "</tr>"

        html_content += "</tbody></table>"
        
    # التحقق من وجود بيانات في الجدول المحدد
    else:
        if table_widget is None  or table_widget.rowCount() == 0:
            QMessageBox.warning(self, "تنبيه", "لم يتم العثور على أي بيانات مطابقة للفترة المحددة.")
            return

    html_content += "</body></html>"

    # حفظ الملف وفتحه
    project_folder_path = os.path.join(documents_folder, "Reports")
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)

    html_file_path = os.path.join(project_folder_path, f"{report_title1} {selected_table_name}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    #webbrowser.open(f"file://{html_file_path}")
    create_window(self,html_file_path)


#طباعة التقارير المالية للمشاريع \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# طباعة التقارير المالية للمشاريع
def print_project_financial_report(self, table, title, project_info, summary_data=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_text = getattr(self, 'profits_label2', None)
    if user_text and hasattr(user_text, 'text'):
        user_text = user_text.text().replace("المستخدم", "").strip(" :")
    else:
        user_text = "المستخدم"

    # بناء محتوى HTML
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            @page {{
                size: A4;
                margin: 15mm;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #ffffff;
                color: #333;
                line-height: 1.4;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 2px solid #0078d4;
                padding-bottom: 15px;
            }}
            .header h1 {{
                color: #0078d4;
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }}
            .header .subtitle {{
                color: #666;
                font-size: 14px;
                margin-top: 5px;
            }}
            .project-info {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #0078d4;
            }}
            .project-info h3 {{
                margin: 0 0 10px 0;
                color: #0078d4;
                font-size: 16px;
            }}
            .project-info p {{
                margin: 5px 0;
                font-size: 14px;
            }}
            .summary-section {{
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .summary-section h3 {{
                margin: 0 0 15px 0;
                color: #1976d2;
                font-size: 16px;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
            }}
            .summary-item {{
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
                text-align: center;
            }}
            .summary-item .label {{
                font-weight: bold;
                color: #666;
                font-size: 12px;
            }}
            .summary-item .value {{
                font-size: 16px;
                color: #1976d2;
                font-weight: bold;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                background-color: white;
                
            }}
            th {{
                background-color: #0078d4;
                color: white;
                padding: 12px 8px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #0066cc;
            }}
            td {{
                padding: 10px 8px;
                text-align: center;
                border: 1px solid #ddd;
                font-size: 11px;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            tr:hover {{
                background-color: #e3f2fd;
            }}
            .amount {{
                font-weight: bold;
                color: #2e7d32;
            }}
            .expense {{
                color: #d32f2f;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 12px;
                color: #666;
            }}
            .footer .left {{
                text-align: left;
            }}
            .footer .right {{
                text-align: right;
            }}
            @media print {{
                body {{
                    background-color: white;
                }}
                .no-print {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">تاريخ الطباعة: {current_time}</div>
        </div>

        <div class="project-info">
            <h3>معلومات المشروع</h3>
            <p>{project_info}</p>
        </div>
    """

    # إضافة قسم الملخص إذا توفرت البيانات
    if summary_data:
        html_content += """
        <div class="summary-section">
            <h3>ملخص التقرير</h3>
            <div class="summary-grid">
        """

        for key, value in summary_data.items():
            label = key.replace("_", " ").replace("total", "إجمالي").replace("count", "العدد")
            label = label.replace("project amount", "مبلغ المشروع")
            label = label.replace("project paid", "المدفوع")
            label = label.replace("project remaining", "الباقي")
            label = label.replace("custody", "العهد")
            label = label.replace("expenses", "المصروفات")
            label = label.replace("remaining", "المتبقي")

            html_content += f"""
                <div class="summary-item">
                    <div class="label">{label}</div>
                    <div class="value">{value}</div>
                </div>
            """

        html_content += """
            </div>
        </div>
        """

    # إضافة الجدول
    html_content += """
        <table>
            <thead>
                <tr>
    """

    # إضافة عناوين الأعمدة
    for col in range(table.columnCount()):
        if not table.isColumnHidden(col):
            header_item = table.horizontalHeaderItem(col)
            header_text = header_item.text() if header_item else f"عمود {col + 1}"
            html_content += f"<th>{header_text}</th>"

    html_content += """
                </tr>
            </thead>
            <tbody>
    """

    # إضافة بيانات الجدول
    for row in range(table.rowCount()):
        html_content += "<tr>"
        for col in range(table.columnCount()):
            if not table.isColumnHidden(col):
                item = table.item(row, col)
                cell_text = item.text() if item else ""

                # تطبيق تنسيق خاص للمبالغ
                css_class = ""
                if "مبلغ" in (table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else ""):
                    if "مصروف" in cell_text.lower() or "سحب" in cell_text.lower():
                        css_class = "expense"
                    else:
                        css_class = "amount"

                html_content += f'<td class="{css_class}">{cell_text}</td>'
        html_content += "</tr>"

    html_content += """
            </tbody>
        </table>

        <div class="footer">
            <div class="left">
                <div>المستخدم: """ + user_text + """</div>
                <div>تاريخ الطباعة: """ + current_time + """</div>
            </div>
            <div class="right">
                <div>التوقيع: _________________</div>
            </div>
        </div>
    </body>
    </html>
    """

    # حفظ الملف وفتحه
    project_folder_path = os.path.join(documents_folder, "Reports")
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)

    # تنظيف اسم الملف
    safe_title = title.replace("/", "_").replace("\\", "_").replace(":", "_")
    html_file_path = os.path.join(project_folder_path, f"{safe_title}_{current_time.replace(':', '-')}.html")

    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    create_window(self, html_file_path)


#طباعة سجل الديون \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# تقرير الديون المطبوعة
def print_debts_report(self, table,title,totel):
    current_time = datetime.now().strftime("%Y-%m-%d")
    title = f"{title}"
    user_text = self.profits_label2.text().replace("المستخدم", "").strip(" :")
    
    html_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{title}</title>
        <style>
            @media print {{
                @page {{
                    size: A4 landscape;
                    margin: 15mm 10mm 15mm 10mm; /* هوامش متطابقة */
                    @bottom-center {{
                        content: "" counter(page) " - " counter(pages);
                    }}
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
            }}
            body {{
                font-family: {print_font}, sans-serif;
                direction: rtl;
                text-align: center;
                margin: 15mm 10mm;
                padding: 0;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .print-info {{
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 10px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-weight: bold;
                font-size: 14px;
                page-break-inside: auto;
            }}
            th, td {{
                border: 1px solid black;
                text-align: center;
                padding: 5px;
            }}
            th {{
                background-color: #E4E0E1;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            thead {{
                display: table-header-group;
            }}
            tfoot {{
                display: table-footer-group;
            }}
            .page-break {{
                page-break-after: always; /* فصل كل جدول في صفحة جديدة */
            }}
            .footer-spacer td {{
                padding: 0;
                margin: 0;
                border: none;
            }}
        </style>
        <script>
            window.onload = function() {{
                window.print();
                window.onafterprint = function() {{
                    window.close();
                }};
            }}
        </script>
    </head>
    <body>
        <div class="company-info" style="display: flex; justify-content: flex-start; align-items: center; direction: rtl; width: 100%;">
            {f"<img src='" + logo_path + "' class='company-logo' alt='شعار الشركة' style='max-width: 6cm; max-height: 3cm; margin-left: 10px;'>" if logo_path else ""}
            <div class="company-name" style="font-size: 24px; font-family: {print_font}, Times, serif; font-weight: bold; color: #2c3e50; position: absolute; left: 50%; transform: translateX(-50%);">
                {company_name}
            </div>
        </div>

        <h1>{title}</h1>
        <p class="print-info">{current_time}</p>
        <table>
            <tr>
        
        <footer style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 20px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            border-top: 2px solid black;
            padding: 3px;
            background-color: white;">
            <span style="float: right; margin-right: 20px;">📍العنوان: {company_address}</span>
            <span style="float: left; margin-left: 20px; color: #7f8c8d;">🖨️{user_text}</span>
            <span style="float: left; margin-left: 20px;">📞 الهاتف:  {company_phone}</span>
            <span style="float: left; margin-left: 20px;">✉ إيميل:  {company_email}</span>
        </footer>
    </body>
    """
    #مجموع الحسابات
    html_content += totel
       

    html_content += "<thead><tr>"
    for col in range(table.columnCount()):
        html_content += f"<th>{table.horizontalHeaderItem(col).text()}</th>"
    html_content += "</tr></thead><tbody>"

    for row in range(table.rowCount()):
        html_content += "<tr>"
        for col in range(table.columnCount()):
            item = table.item(row, col)
            html_content += f"<td>{item.text() if item else ''}</td>"
        html_content += "</tr>"

    html_content += """
        </tbody>
        <tfoot>
            <tr class="footer-spacer"><td colspan="100" style="height: 15px;">&nbsp;</td></tr>
        </tfoot>
    </table>
    <div style="height: 15px;"></div>
    <div class="page-break"></div>
    """

    project_folder_path = os.path.join(documents_folder, "Reports")
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)
    html_file_path = os.path.join(project_folder_path, f"تقرير سجل الديون.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    create_window(self, html_file_path)  
    
#معاينة وطباعة================================================================================
# printdialog
class PrintDialog(QDialog):
    # init
    def __init__(self, parent, file_path1):
        super().__init__(parent)
        self.setWindowTitle("خيارات الطباعة")
        self.setFixedSize(300, 250)
        icon_path = os.path.join(icons_dir, 'printer.png')
        self.setWindowIcon(QIcon(icon_path))
        self.is_dark_mode = settings.value("dark_mode", False, type=bool)

        self.file_path1 = file_path1

        # إنشاء WebEngineView ككائن برمجي فقط (لن يتم عرضه)
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl.fromLocalFile(file_path1))

        # إنشاء الازرار
        print_button = QPushButton(qta.icon('fa5s.print', color='navy'), "طباعة مباشرة ")
        print_button.clicked.connect(self.print_to_html)

        pdf_print_button = QPushButton(qta.icon('fa5s.eye', color='orange'), "معاينة قبل الطباعة ")
        pdf_print_button.clicked.connect(self.load_html_file)

        pdf_button = QPushButton(qta.icon('fa5s.file-pdf', color='red'), "PDF تصدير إلى")
        pdf_button.clicked.connect(self.export_to_pdf)

        export_button = QPushButton(qta.icon('fa5s.file-excel', color='green'), "Excel تصدير إلى")
        export_button.clicked.connect(self.export_to_excel)

        # إضافة الازرار إلى التخطيط
        layout = QVBoxLayout()
        self.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(print_button)
        layout.addWidget(pdf_print_button)
        layout.addWidget(pdf_button)
        layout.addWidget(export_button)
        Basic_Styles(self) 
        self.setLayout(layout)
        

    # تحميل ملف HTML في WebEngineView
    def load_html_file(self):
        if self.file_path1:
            self.web_view.load(QUrl.fromLocalFile(self.file_path1))
            self.web_view.loadFinished.connect(self.on_load_finished)

    # عند انتهاء تحميل الصفحة
    def on_load_finished(self, success):
        if success:
            QTimer.singleShot(500, self.print_to_pdf)  # تأخير الطباعة قليلاً

    
    # حفظ الصفحة إلى PDF في نفس مسار ملف HTML
    def print_to_pdf(self):
        if self.file_path1:
            # تغيير امتداد الملف إلى .pdf بنفس المسار
            pdf_file_path = os.path.splitext(self.file_path1)[0] + ".pdf"

            # التعامل مع PDF المحفوظة
            def handle_pdf_saved(data: QByteArray):
                if data:
                    try:
                        with open(pdf_file_path, "wb") as pdf_file:
                            pdf_file.write(data)
                        open_file_and_print(pdf_file_path)  # تأكد من أن هذه الدالة idة لديك
                    except Exception as e:
                        QMessageBox.critical(self, "خطأ", f"فشل في حفظ الملف كـ PDF:\n{e}")
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إنشاء محتوى PDF.")

            self.web_view.page().printToPdf(handle_pdf_saved)
        else:
            print("لم يتم تحديد ملف HTML!")
            QMessageBox.critical(self, "خطأ", "لم يتم تحديد ملف HTML للطباعة.")
    
    # فتح ملف HTML في المتصفح الافتراضي
    def print_to_html(self):
        webbrowser.open(f"file://{self.file_path1}")

    # حفظ الصفحة إلى PDF
    def export_to_pdf(self):
        # file_path,_=self.file_path1
        # if not file_path:
        file_path, _ = QFileDialog.getSaveFileName(self, "حفظ كملف PDF", "", "PDF Files (*.pdf)")

        if file_path:
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"

            # التعامل مع PDF المحفوظة
            def handle_pdf_saved(data: QByteArray):
                if data:
                    try:
                        with open(file_path, "wb") as pdf_file:
                            pdf_file.write(data)
                        QMessageBox.information(self, "تم التصدير", f"تم حفظ الملف كـ PDF:\n{file_path}")
                        
                        #open_file(file_path)
                        
                        open_file_and_print(file_path)
                    except Exception as e:
                        QMessageBox.critical(self, "خطأ", f"فشل في حفظ الملف كـ PDF:\n{e}")
                else:
                    print("فشل في إنشاء محتوى PDF.")

            self.web_view.page().printToPdf(handle_pdf_saved)

    # تصدير HTML إلى Excel
    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "حفظ كملف Excel", "", "Excel Files (*.xlsx)")
        if file_path:
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            self.web_view.page().toHtml(lambda html: process_html(self,html, file_path))


# تحليل HTML وتحويله إلى Excel
def process_html(self,html, file_path):
    soup = BeautifulSoup(html, "html.parser")
    wb = Workbook()
    ws = wb.active
    ws.title = "HTML Data"
    ws.sheet_view.rightToLeft = True

    # إعداد الأنماط
    bold_font = Font(bold=True, color="FFFFFF", size=14)
    right_alignment = Alignment(horizontal='center', vertical='center')
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))
    header_fill = PatternFill(start_color="4CAF50", fill_type="solid")

    row_index = 1  # بداية الكتابة في الصف الأول

    for element in soup.body.children:
        if element.name == "table":
            headers = [th.text.strip() for th in element.find_all("th")]
            rows = [[td.text.strip() for td in row.find_all("td")] for row in element.find_all("tr")]

            if headers:
                for col_index, header in enumerate(headers, start=1):
                    cell = ws.cell(row=row_index, column=col_index, value=header)
                    cell.font = bold_font
                    cell.alignment = right_alignment
                    cell.border = thin_border
                    cell.fill = header_fill
                row_index += 1

            for row_data in rows:
                if any(row_data):
                    for col_index, cell_value in enumerate(row_data, start=1):
                        cell = ws.cell(row=row_index, column=col_index, value=cell_value)
                        cell.alignment = right_alignment
                        cell.border = thin_border
                    row_index += 1

            row_index += 1  # إضافة صف فارغ بعد الجدول

    for col in range(1, ws.max_column + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = max([len(str(cell.value)) for cell in ws[column_letter] if cell.value] or [10]) + 2

    wb.save(file_path)
    QMessageBox.information(self, "تم التصدير", f"تم تصدير البيانات إلى Excel\n{file_path}")
    open_file(self,file_path)


# فتج برنامج PDF افتراضي
# افتح الملف والطباعة
def open_file_and_print(file_path):
    try:
        if os.path.exists(file_path):
            try:
                custom_pdf_reader_path = os.path.join(Programs_dir, "PDF.exe")  # مسار PDF.exe في نفس مكان التطبيق
                # تحقق من وجود PDF.exe
                if os.path.exists(custom_pdf_reader_path):
                    # استخدم PDF.exe لفتح الملف
                    subprocess.run([custom_pdf_reader_path, file_path], check=True)
                else:
                    # افتح الملف باستخدام البرنامج الافتراضي
                    os.startfile(file_path)  # يعمل على Windows فقط
            except Exception as e:
                print(f"فشل في فتح الملف باستخدام PDF.exe: {e}")

    except Exception as e:
        print(f"فشل في فتح الملف: {e}")

# فتح ملف باستخدام التطبيق الافتراضي
def open_file(self,file_path):
    try:
        if os.path.exists(file_path):
            os.startfile(file_path)  # يعمل على Windows فقط
        else:
            QMessageBox.warning(self, "تحذير", f"الملف غير موجود: {file_path}")
    except Exception as e:
        QMessageBox.warning(self, "تحذير", f"حدث خطأ أثناء محاولة فتح الملف:\n{str(e)}")


# إنشاء نافذة
def create_window(parent, html_file_path):
    dialog = PrintDialog(parent, html_file_path)
    dialog.exec()


