from الإعدادات_العامة import*


# بدء معاملة قاعدة بيانات بشكل آمن - دالة عامة
def safe_start_transaction(conn):
    try:
        conn.start_transaction()
    except Exception:
        try:
            conn.rollback()
        except:
            pass
        try:
            conn.start_transaction()
        except Exception as e:
            print(f"خطأ في بدء المعاملة: {e}")
            raise



# معالجة المرتبات المجدولة تلقائياً
def process_scheduled_salaries(main_window):
    try:
        conn = main_window.get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        today = QDate.currentDate()
        today_str = today.toString(Qt.ISODate)

        # البحث عن الموظفين الذين لديهم جدولة مرتب مفعلة وحالة نشط
        cursor.execute("""
            SELECT id, اسم_الموظف, المرتب
            FROM الموظفين
            WHERE الحالة = 'نشط'
            AND جدولة_المرتب_تلقائية = TRUE
            AND المرتب > 0
        """)

        employees = cursor.fetchall()

        if not employees:
            return

        # تجميع الموظفين حسب نوع المعالجة المطلوبة
        current_month_employees = []  # للمرتبات الحالية
        overdue_employees = []  # للمرتبات المتأخرة

        for employee in employees:
            try:
                employee_id = employee['id']
                employee_name = employee['اسم_الموظف']
                salary_amount = employee['المرتب']

                # البحث عن تاريخ آخر إضافة مرتب للموظف
                cursor.execute("""
                    SELECT التاريخ
                    FROM الموظفين_معاملات_مالية
                    WHERE معرف_الموظف = %s
                    AND نوع_المعاملة = 'إيداع مرتب'
                    ORDER BY التاريخ DESC
                    LIMIT 1
                """, (employee_id,))

                last_salary_result = cursor.fetchone()

                if last_salary_result:
                    last_salary_date = QDate.fromString(str(last_salary_result['التاريخ']), Qt.ISODate)
                else:
                    # إذا لم يكن هناك مرتب سابق، استخدم تاريخ التوظيف
                    cursor.execute("SELECT تاريخ_التوظيف FROM الموظفين WHERE id = %s", (employee_id,))
                    hiring_result = cursor.fetchone()
                    if hiring_result and hiring_result['تاريخ_التوظيف']:
                        last_salary_date = QDate.fromString(str(hiring_result['تاريخ_التوظيف']), Qt.ISODate)
                    else:
                        last_salary_date = today.addMonths(-1)  # افتراضي: شهر واحد مضى

                # حساب الفرق بالأشهر
                months_diff = calculate_months_difference(last_salary_date, today)

                if months_diff >= 1:
                    # إذا مر شهر أو أكثر، نحتاج لإدراج المرتبات
                    if months_diff > 1:
                        # إضافة للقائمة المتأخرة
                        overdue_employees.append({
                            'id': employee_id,
                            'name': employee_name,
                            'salary': salary_amount,
                            'last_date': last_salary_date,
                            'months_overdue': months_diff
                        })
                    else:
                        # إضافة للمرتبات الحالية
                        current_month_employees.append({
                            'id': employee_id,
                            'name': employee_name,
                            'salary': salary_amount,
                            'month': today.month(),
                            'year': today.year()
                        })

            except Exception as e:
                print(f"خطأ في معالجة مرتب الموظف {employee_name}: {str(e)}")

        # معالجة المرتبات الحالية مع التأكيد
        if current_month_employees:
            if confirm_current_month_salaries(main_window, current_month_employees, today):
                processed_count = process_current_month_salaries(conn, cursor, current_month_employees, today_str)
                if processed_count > 0:
                    QMessageBox.information(
                        main_window, "معالجة المرتبات الشهرية",
                        f"تم إدراج {processed_count} مرتب شهري بنجاح"
                    )

        # عرض تنبيه للمرتبات المتأخرة
        if overdue_employees:
            handle_overdue_salaries(main_window, conn, cursor, overdue_employees)

        cursor.close()
        conn.close()

    except Exception as e:
        QMessageBox.warning(main_window, "خطأ", f"فشل في معالجة المرتبات التلقائية: {str(e)}")


# حساب الفرق بالأشهر بين تاريخين
def calculate_months_difference(start_date, end_date):
    years_diff = end_date.year() - start_date.year()
    months_diff = end_date.month() - start_date.month()
    total_months = years_diff * 12 + months_diff

    # إذا كان اليوم الحالي أقل من يوم آخر مرتب، نقلل شهر واحد
    if end_date.day() < start_date.day():
        total_months -= 1

    return max(0, total_months)


# إضافة معاملة مرتب للموظف
def add_salary_transaction(conn, cursor, employee_id, salary_amount, date_str, description):
    try:
        # بدء معاملة قاعدة بيانات بشكل آمن
        safe_start_transaction(conn)

        # إدراج المعاملة
        cursor.execute("""
            INSERT INTO الموظفين_معاملات_مالية
            (معرف_الموظف, نوع_العملية, نوع_المعاملة, المبلغ, التاريخ, الوصف, المستخدم)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (employee_id, 'إيداع', 'إيداع مرتب',
              salary_amount, date_str, description, 'النظام التلقائي'))

        # تحديث رصيد الموظف
        cursor.execute("UPDATE الموظفين SET الرصيد = الرصيد + %s WHERE id = %s",
                      (salary_amount, employee_id))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"خطأ في إضافة معاملة المرتب: {str(e)}")
        return False


# معالجة المرتبات المتأخرة
def handle_overdue_salaries(main_window, conn, cursor, overdue_employees):
    try:
        # إنشاء رسالة تفصيلية للمرتبات المتأخرة
        message = "تم العثور على مرتبات متأخرة للموظفين التاليين:\n\n"

        for emp in overdue_employees:
            message += f"• {emp['name']}: {emp['months_overdue']} شهر متأخر\n"
            message += f"  آخر مرتب: {emp['last_date'].toString('dd/MM/yyyy')}\n"
            message += f"  مبلغ المرتب الشهري: {emp['salary']:,.2f}\n\n"

        message += "هل تريد إدراج جميع المرتبات المتأخرة تلقائياً؟"

        # عرض رسالة تأكيد
        reply = QMessageBox.question(
            main_window,
            "مرتبات متأخرة",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            process_overdue_salaries_automatically(conn, cursor, overdue_employees)
        else:
            # عرض نافذة تفصيلية للاختيار اليدوي
            show_overdue_salaries_dialog(main_window, conn, cursor, overdue_employees)

    except Exception as e:
        QMessageBox.warning(main_window, "خطأ", f"فشل في معالجة المرتبات المتأخرة: {str(e)}")


# معالجة المرتبات المتأخرة تلقائياً
def process_overdue_salaries_automatically(conn, cursor, overdue_employees):
    processed_count = 0
    total_amount = 0

    for emp in overdue_employees:
        try:
            # إدراج المرتبات لكل شهر متأخر
            last_date = emp['last_date']
            current_date = QDate.currentDate()

            # البدء من الشهر التالي لآخر مرتب
            process_date = last_date.addMonths(1)

            while process_date <= current_date:
                # تحديد إذا كان هذا الشهر مكتمل أم لا
                if process_date.month() == current_date.month() and process_date.year() == current_date.year():
                    # الشهر الحالي - تحقق من اليوم
                    if current_date.day() < process_date.day():
                        break

                # إنشاء وصف المعاملة مع الشهر والسنة
                month_name = get_arabic_month_name(process_date.month())
                month_number = process_date.month()
                year = process_date.year()
                description = f"مرتب شهر {month_number}/{year} ({month_name}) - {emp['name']} - {emp['salary']:,.2f} (متأخر)"

                # تاريخ المعاملة (آخر يوم في الشهر المحدد)
                transaction_date = QDate(process_date.year(), process_date.month(),
                                       process_date.daysInMonth()).toString(Qt.ISODate)

                if add_salary_transaction(conn, cursor, emp['id'],
                                        emp['salary'], transaction_date, description):
                    processed_count += 1
                    total_amount += emp['salary']

                # الانتقال للشهر التالي
                process_date = process_date.addMonths(1)

        except Exception as e:
            print(f"خطأ في معالجة المرتبات المتأخرة للموظف {emp['name']}: {str(e)}")

    if processed_count > 0:
        QMessageBox.information(
            None, "معالجة المرتبات المتأخرة",
            f"تم إدراج {processed_count} مرتب متأخر بإجمالي {total_amount:,.2f}"
        )


# الحصول على اسم الشهر بالعربية
def get_arabic_month_name(month_number):
    months = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    return months.get(month_number, str(month_number))


# عرض رسالة تأكيد للمرتبات الشهرية الحالية
def confirm_current_month_salaries(main_window, employees, today):
    try:
        current_month = get_arabic_month_name(today.month())
        current_year = today.year()

        # إنشاء رسالة تفصيلية
        message = f"تم العثور على {len(employees)} موظف مستحق لمرتب شهر {current_month} {current_year}:\n\n"

        total_amount = 0
        for emp in employees:
            message += f"• {emp['name']}: {emp['salary']:,.2f}\n"
            total_amount += emp['salary']

        message += f"\nإجمالي المبلغ: {total_amount:,.2f}\n"
        message += f"الشهر: {current_month} {current_year}\n\n"
        message += "هل تريد إدراج هذه المرتبات؟"

        # عرض رسالة تأكيد
        reply = QMessageBox.question(
            main_window,
            f"تأكيد إدراج مرتبات شهر {current_month}",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        return reply == QMessageBox.Yes

    except Exception as e:
        QMessageBox.warning(main_window, "خطأ", f"فشل في عرض رسالة التأكيد: {str(e)}")
        return False


# معالجة المرتبات الشهرية الحالية
def process_current_month_salaries(conn, cursor, employees, today_str):
    processed_count = 0

    try:
        for emp in employees:
            current_month = get_arabic_month_name(emp['month'])
            current_year = emp['year']
            description = f"مرتب شهر {emp['month']}/{current_year} ({current_month}) - {emp['name']} - {emp['salary']:,.2f}"

            if add_salary_transaction(conn, cursor, emp['id'],
                                    emp['salary'], today_str, description):
                processed_count += 1

        return processed_count

    except Exception as e:
        print(f"خطأ في معالجة المرتبات الشهرية: {str(e)}")
        return processed_count


# عرض نافذة تفصيلية لاختيار المرتبات المتأخرة
def show_overdue_salaries_dialog(main_window, conn, cursor, overdue_employees):
    try:

        dialog = QDialog(main_window)
        dialog.setWindowTitle("إدارة المرتبات المتأخرة")
        dialog.setModal(True)
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        # عنوان النافذة
        title_label = QLabel("اختر المرتبات المتأخرة التي تريد إدراجها:")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # جدول المرتبات المتأخرة
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "اختيار", "اسم الموظف", "الشهر/السنة", "مبلغ المرتب",
            "تاريخ الاستحقاق", "الوصف"
        ])

        # تحضير بيانات الجدول
        all_overdue_salaries = []
        for emp in overdue_employees:
            last_date = emp['last_date']
            current_date = QDate.currentDate()
            process_date = last_date.addMonths(1)

            while process_date <= current_date:
                if process_date.month() == current_date.month() and process_date.year() == current_date.year():
                    if current_date.day() < process_date.day():
                        break

                month_name = get_arabic_month_name(process_date.month())
                month_number = process_date.month()
                year = process_date.year()
                due_date = QDate(process_date.year(), process_date.month(),
                               process_date.daysInMonth())

                all_overdue_salaries.append({
                    'employee_id': emp['id'],
                    'employee_name': emp['name'],
                    'salary': emp['salary'],
                    'month_year': f"{month_number}/{year} ({month_name})",
                    'due_date': due_date,
                    'description': f"مرتب شهر {month_number}/{year} ({month_name}) - {emp['name']} - {emp['salary']:,.2f} (متأخر)"
                })

                process_date = process_date.addMonths(1)

        table.setRowCount(len(all_overdue_salaries))

        # ملء الجدول
        for row, salary_data in enumerate(all_overdue_salaries):
            # عمود الاختيار
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            table.setCellWidget(row, 0, checkbox)

            # باقي الأعمدة
            table.setItem(row, 1, QTableWidgetItem(salary_data['employee_name']))
            table.setItem(row, 2, QTableWidgetItem(salary_data['month_year']))
            table.setItem(row, 3, QTableWidgetItem(f"{salary_data['salary']:,.2f}"))
            table.setItem(row, 4, QTableWidgetItem(salary_data['due_date'].toString('dd/MM/yyyy')))
            table.setItem(row, 5, QTableWidgetItem(salary_data['description']))

        # تنسيق الجدول
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)

        layout.addWidget(table)

        # أزرار التحكم
        buttons_layout = QHBoxLayout()

        select_all_btn = QPushButton("تحديد الكل")
        select_all_btn.clicked.connect(lambda: select_all_checkboxes(table, True))

        deselect_all_btn = QPushButton("إلغاء تحديد الكل")
        deselect_all_btn.clicked.connect(lambda: select_all_checkboxes(table, False))

        process_btn = QPushButton("إدراج المحدد")
        process_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        process_btn.clicked.connect(lambda: process_selected_salaries(
            dialog, conn, cursor, table, all_overdue_salaries))

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)

        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(deselect_all_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(process_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        dialog.exec_()

    except Exception as e:
        QMessageBox.warning(main_window, "خطأ", f"فشل في عرض نافذة المرتبات المتأخرة: {str(e)}")


# تحديد أو إلغاء تحديد جميع الصناديق
def select_all_checkboxes(table, checked):
    for row in range(table.rowCount()):
        checkbox = table.cellWidget(row, 0)
        if checkbox:
            checkbox.setChecked(checked)


# معالجة المرتبات المحددة
def process_selected_salaries(dialog, conn, cursor, table, all_overdue_salaries):
    try:
        selected_salaries = []

        for row in range(table.rowCount()):
            checkbox = table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_salaries.append(all_overdue_salaries[row])

        if not selected_salaries:
            QMessageBox.warning(dialog, "تحذير", "لم يتم تحديد أي مرتبات للمعالجة")
            return

        # تأكيد المعالجة
        total_amount = sum(salary['salary'] for salary in selected_salaries)
        confirm_msg = f"سيتم إدراج {len(selected_salaries)} مرتب بإجمالي {total_amount:,.2f}\nهل أنت متأكد؟"

        reply = QMessageBox.question(dialog, "تأكيد الإدراج", confirm_msg,
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            processed_count = 0

            for salary_data in selected_salaries:
                transaction_date = salary_data['due_date'].toString(Qt.ISODate)

                if add_salary_transaction(conn, cursor, salary_data['employee_id'],
                                        salary_data['salary'], transaction_date, salary_data['description']):
                    processed_count += 1

            if processed_count > 0:
                QMessageBox.information(dialog, "نجح",
                                      f"تم إدراج {processed_count} مرتب متأخر بنجاح")
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "خطأ", "فشل في إدراج المرتبات")

    except Exception as e:
        QMessageBox.warning(dialog, "خطأ", f"فشل في معالجة المرتبات المحددة: {str(e)}")
