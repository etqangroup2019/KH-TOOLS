from الإعدادات_العامة import*
# "حسابات المستخدمين" ///////////////////////////////////////////////////////////////////////////////
# OpenAdduserDialog
def openAddUserDialog(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("حسابات المستخدمين")
    dialog.setLayoutDirection(Qt.RightToLeft)
    dialog.resize(600, 600)
    layout = QVBoxLayout(dialog)
    # تحديد عرض ثابت لجميع الليبلات
    label_width = 120  # العرض الثابت للأعمدة
    # تخطيط أفقي لاسم المستخدم
    username_layout = QHBoxLayout()
    username_label = QLabel("اسم المستخدم:")
    username_label.setFixedWidth(label_width)  # ضبط العرض
    username_input = QLineEdit()
    username_input.setAlignment(QtCore.Qt.AlignCenter)
    username_layout.addWidget(username_label)
    username_layout.addWidget(username_input)
    layout.addLayout(username_layout)
    # تخطيط أفقي لكلمة المرور
    password_layout = QHBoxLayout()
    password_label = QLabel("كلمة المرور:")
    password_label.setFixedWidth(label_width)  # ضبط العرض
    password_input = QLineEdit()
    password_input.setAlignment(QtCore.Qt.AlignCenter)
    password_input.setEchoMode(QLineEdit.Password)
    password_layout.addWidget(password_label)
    password_layout.addWidget(password_input)
    layout.addLayout(password_layout)
    # تخطيط أفقي للصلاحيات
    permissions_layout = QHBoxLayout()
    permissions_label = QLabel("الصلاحيات:")
    permissions_label.setFixedWidth(label_width)  # ضبط العرض
    permissions_combo = QComboBox()
    permissions_combo.addItems(["مدير", "موظف"])
    permissions_layout.addWidget(permissions_label)
    permissions_layout.addWidget(permissions_combo)
    layout.addLayout(permissions_layout)
    # إضافة تنسيق لعنصر الصلاحيات
    delegate = AlignedItemDelegate(permissions_combo)
    permissions_combo.setItemDelegate(delegate)
    line_edit = QtWidgets.QLineEdit()
    line_edit.setAlignment(QtCore.Qt.AlignCenter)
    permissions_combo.setLineEdit(line_edit)
    permissions_combo.setEditable(True)
    permissions_combo.lineEdit().setReadOnly(True)
    permissions_combo.setStyleSheet(f"""
        QLabel {{
            font-family: {font_app1}; font-weight: bold; 
            font-size: 14px; background-color: #c1cbcd;
        }}
    """)
    permissions_combo.lineEdit().mousePressEvent = lambda event: open_combo(permissions_combo, event)
    # مجموعة Checkboxes لتحديد الصلاحيات
    permissions_groupbox = QGroupBox("الصلاحيات (للموظف فقط):")
    permissions_layout = QGridLayout()
    # إضافة الصلاحيات كمربعات اختيار
    permission_checkboxes = {
        "أدوات": QCheckBox("إضافة/تعديل/حذف"),
        "كشف": QCheckBox("كشف حساب"),
        "الدفعات": QCheckBox("إدارة فعات العميل"),
        "المعاملات": QCheckBox("عرض جميع الدفعات"),
        "البحث": QCheckBox("تمكين البحث"),
        "المعلومات": QCheckBox("لوحة المعلومات"),
        "الحسابات": QCheckBox("إدارة الحسابات"),
        "الموظفين": QCheckBox("إدارة الموظفين")
    }
    
    # ترتيب العناصر على صفين
    row, col = 0, 0
    for checkbox in permission_checkboxes.values():
        permissions_layout.addWidget(checkbox, row, col)
        col += 1
        if col > 3:  # عند الوصول للعمود الثالث، انتقل للصف التالي
            col = 0
            row += 1
        #permissions_layout.addWidget(checkbox)
    permissions_groupbox.setLayout(permissions_layout)
    permissions_groupbox.setVisible(False)  # إخفاء الخيارات افتراضيًا
    layout.addWidget(permissions_groupbox)
    # تغيير الرؤية بناءً على الصلاحيات
    permissions_combo.currentTextChanged.connect(
        lambda: permissions_groupbox.setVisible(permissions_combo.currentText() == "موظف")
    )
    # تخطيط الازرار (إضافة وحذف) في نفس الصف
    button_layout = QHBoxLayout()
    # زر الإضافة
    add_button = QPushButton(qta.icon('fa5s.plus', color='darkgreen'), "إضافة مستخدم ")
    button_layout.addWidget(add_button)

    edit_button = QPushButton(qta.icon('fa5s.edit', color='gray'), "تعديل المستخدم ")
    button_layout.addWidget(edit_button)
    # زر الحذف
    delete_button = QPushButton(qta.icon('fa5s.trash', color='crimson'), "حذف المستخدم ")
    button_layout.addWidget(delete_button)
    # إضافة التخطيط الأفقي الخاص بالازرار إلى التخطيط الرئيسي
    layout.addLayout(button_layout)
    # جدول عرض المستخدمين
    user_table = QTableWidget()
    user_table.setColumnCount(2)
    user_table.setHorizontalHeaderLabels(["اسم المستخدم", "الصلاحيات"])
    user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    user_table.setAlternatingRowColors(True)
    user_table.verticalHeader().setHidden(True)
    user_table.setSortingEnabled(True)
    user_table.setSelectionBehavior(QTableWidget.SelectRows)
    user_table.setEditTriggers(QTableWidget.NoEditTriggers)  # عدم السماح بالتعديل
    layout.addWidget(user_table)

    # مركز جميع الحاجيات
    def center_all_widgets():
        # البحث عن جميع الويدجت داخل النافذة
        widgets = dialog.findChildren(QWidget)

        for widget in widgets:
            # إذا كان الويدجت من نوع QLabel، QLineEdit، أو QComboBox
            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignCenter)
            elif isinstance(widget, QLineEdit):
                widget.setAlignment(Qt.AlignCenter)
            elif isinstance(widget, QComboBox):
                widget.setEditable(True)  # السماح بالتعديل لتفعيل المحاذاة
                widget.lineEdit().setAlignment(Qt.AlignCenter)  # توسيط النصوص داخل القوائم المنسدلة
    
    # adduser
    def addUser():
        username = username_input.text().strip()
        password = password_input.text().strip()
        permissions = permissions_combo.currentText()
        if not username or not password:
            QMessageBox.warning(dialog, "خطأ", "يرجى إدخال جميع الحقول!")
            return
        # جمع تفاصيل الصلاحيات إذا كان الموظف
        permissions_details = []
        if permissions == "موظف":
            permissions_details = [
                key for key, checkbox in permission_checkboxes.items() if checkbox.isChecked()
            ]
            #permissions_details = ", ".join(permissions_details)
        
        # التأكد من أن permissions_details هو نص وليس قائمة
        permissions_details = ", ".join(permissions_details) if permissions_details else ""

        try:
            conn = mysql.connector.connect(host=host, user=user_r, password=password_r, database='project_manager2_user')
            cursor = conn.cursor()
            # التحقق من وجود المستخدم
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(dialog, "خطأ", "اسم المستخدم موجود مسبقًا!")
                return
            # تشفير كلمة المرور
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # إضافة المستخدم
            cursor.execute(
                "INSERT INTO users (username, password_hash, user_permissions, permissions_details) VALUES (%s, %s, %s, %s)",
                (username, hashed_password.decode('utf-8'), permissions, permissions_details)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(dialog, "نجاح", "تمت إضافة المستخدم بنجاح!")
            loadUsers()
            #dialog.close()
        except mysql.connector.Error as e:
            QMessageBox.critical(dialog, "خطأ", f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}")

    # الحمل
    def loadUsers():
        try:
            conn = mysql.connector.connect(host=host, user=user_r, password=password_r, database='project_manager2_user')
            cursor = conn.cursor()
            # تعديل الاستعلام لاستبعاد المستخدم "admin"
            cursor.execute("SELECT username, user_permissions FROM users WHERE username != 'admin'")
            users = cursor.fetchall()
            conn.close()
            user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                username_item = QTableWidgetItem(user[0])
                permissions_item = QTableWidgetItem(user[1])
                # ضبط المحاذاة لتكون في المنتصف
                username_item.setTextAlignment(Qt.AlignCenter)
                permissions_item.setTextAlignment(Qt.AlignCenter)
                user_table.setItem(row, 0, username_item)
                user_table.setItem(row, 1, permissions_item)
        except mysql.connector.Error as e:
            QMessageBox.critical(dialog, "خطأ", f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}")

    # حذف
    def deleteUser():
        selected_row = user_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(dialog, "خطأ", "يرجى اختيار مستخدم!")
            return
        username = user_table.item(selected_row, 0).text()
        # عرض رسالة تأكيد مع اسم الموظف
        reply = QMessageBox.question(dialog, 'تأكيد الحذف',
                                    f"هل أنت متأكد من أنك تريد حذف المستخدم {username}؟",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        try:
            conn = mysql.connector.connect(host=host, user=user, password=password, database='project_manager2_user')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()
            QMessageBox.information(dialog, "نجاح", "تم حذف المستخدم بنجاح!")
            loadUsers()
        except mysql.connector.Error as e:
            QMessageBox.critical(dialog, "خطأ", f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}")
    
    # FillUserDetails
    def fillUserDetails():
        selected_items = user_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(dialog, "خطأ", "يرجى تحديد مستخدم!")
            return
        selected_row = user_table.currentRow()
        username = user_table.item(selected_row, 0).text()
        try:
            conn = mysql.connector.connect(host=host, user=user_r, password=password_r, database='project_manager2_user')
            cursor = conn.cursor()
            cursor.execute("SELECT username, user_permissions, permissions_details FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                username_input.setText(user_data[0])
                permissions_combo.setCurrentText(user_data[1])
                # إعادة تعيين مربعات الاختيار
                for checkbox in permission_checkboxes.values():
                    checkbox.setChecked(False)
                # تمكين مربعات الاختيار للصلاحيات المخزنة
                if user_data[2]:
                    saved_permissions = user_data[2].split(", ")
                    for perm in saved_permissions:
                        if perm in permission_checkboxes:
                            permission_checkboxes[perm].setChecked(True)

        except mysql.connector.Error as e:
            QMessageBox.critical(dialog, "خطأ", f"حدث خطأ أثناء استرداد بيانات المستخدم: {str(e)}")

    # UpdateUser
    def updateUser():
        username = username_input.text().strip()
        password = password_input.text().strip()
        permissions = permissions_combo.currentText()
        permissions_details = ", ".join([key for key, checkbox in permission_checkboxes.items() if checkbox.isChecked()])
        if not username:
            QMessageBox.warning(dialog, "خطأ", "يرجى إدخال اسم المستخدم!")
            return
        try:
            conn = mysql.connector.connect(host=host, user=user_r, password=password_r, database='project_manager2_user')
            cursor = conn.cursor()
            if password:  # إذا تم إدخال كلمة مرور جديدة
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "UPDATE users SET password_hash = %s, user_permissions = %s, permissions_details = %s WHERE username = %s",
                    (hashed_password.decode('utf-8'), permissions, permissions_details, username)
                )
            else:  # تحديث الصلاحيات فقط
                cursor.execute(
                    "UPDATE users SET user_permissions = %s, permissions_details = %s WHERE username = %s",
                    (permissions, permissions_details, username)
                )

            conn.commit()
            conn.close()
            QMessageBox.information(dialog, "نجاح", "تم تحديث بيانات المستخدم بنجاح!")
            loadUsers()
        except mysql.connector.Error as e:
            QMessageBox.critical(dialog, "خطأ", f"حدث خطأ أثناء تحديث بيانات المستخدم: {str(e)}")

    user_table.itemSelectionChanged.connect(fillUserDetails)
    loadUsers()
    delete_button.clicked.connect(deleteUser)
    add_button.clicked.connect(addUser)
    edit_button.clicked.connect(updateUser)
    center_all_widgets()
    dialog.exec()


#صلاحيات الموظفين///////////////////////////////////////////////////////////
# أذونات المستخدم
def User_Permissions(self):
    try:
        table_name = self.Interface_combo.currentText()
        # الحصول على اسم المستخدم المخزن في الإعدادات
        username = settings.value("account_type", None)
        if not username:
            account_type = settings.value("account_type", "admin")
            self.setWindowTitle(f"{company_name} - {account_type}")
            # QMessageBox.warning(self, "خطأ", "لم يتم العثور على اسم المستخدم.")
            # sys.exit()
        # الاتصال بقاعدة البيانات
        conn = mysql.connector.connect(host=host, user=user, password=password, database='project_manager2_user')
        cursor = conn.cursor()
        # التحقق من الصلاحيات من قاعدة البيانات
        cursor.execute("SELECT user_permissions, Permissions_details FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            account_type = settings.value("account_type", "admin")
            self.setWindowTitle(f"{company_name} - {account_type}")
            try:
                # تحديث كلمة المرور في MySQL
                conn = mysql.connector.connect(host=host, user="root", password=password_r, database='project_manager2_user')
                cursor = conn.cursor()
                # التحقق من وجود اسم المستخدم لحساب مدير
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin",))
                if cursor.fetchone()[0] == 0:
                    # إذا لم يكن موجودًا، إنشاء حساب مدير جديد
                    cursor.execute(
                        "INSERT INTO users (username, user_permissions) VALUES (%s, %s)",("admin", "مدير"))
                    conn.commit()
                conn.commit()                    
                cursor.close()
                conn.close()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث كلمة المرور: {err}")
                return
            
            # QMessageBox.warning(self, "خطأ", "لم يتم العثور على الصلاحيات لهذا المستخدم.")
            # sys.exit()

        else:
            user_permissions = result[0]  # استخراج الصلاحيات
            permissions_details = result[1]  # استخراج تفاصيل الصلاحيات
            
            # إعداد الواجهة بناءً على الصلاحيات
            if user_permissions == "موظف":

                #"إضافة/تعديل/حذف"
                if "أدوات" not in permissions_details:
                    self.add_btn.setDisabled(True)
                    self.update_btn.setDisabled(True)
                    self.delete_btn.setDisabled(True)

                #"كشف حساب"
                if "كشف" not in permissions_details:
                    self.Reports.setDisabled(True)

                #"عرض جميع الدفعات"      
                if "المعاملات" not in permissions_details:
                    #جميع المعاملات
                    self.load_button1.setDisabled(True)
                    #جميع الدفعات
                    self.button4.setDisabled(True)

                #"إدارة فعات العميل"
                if "الدفعات" not in permissions_details :
                    if table_name == "المشاريع":
                        self.button1.setDisabled(True)

                #"تمكين البحث"
                if "البحث" not in permissions_details:
                    self.search_input.setDisabled(True)
                
                if "المعلومات" not in permissions_details:
                    self.information.setVisible(False)  # إخفاء النافذة بالكامل
                
                if "الحسابات" not in permissions_details:
                    #نافذة الموظفين
                    index = self.Interface_combo.findText("الحسابات")
                    if index != -1:
                        self.Interface_combo.removeItem(index)

                if "الموظفين" not in permissions_details:
                    #نافذة الموظفين
                    index = self.Interface_combo.findText("الموظفين")
                    if index != -1:
                        self.Interface_combo.removeItem(index)
  
                # تعطيل قائمة "ملف" وقائمة "الحماية"
                self.menu_bar.setVisible(False)  # إخفاء النافذة بالكامل

                # file_menu = self.menuBar().findChild(QMenu, "ملف")
                # if file_menu:
                #     file_menu.setDisabled(True)
                    
                # file_menu1 = self.menuBar().findChild(QMenu, "الحماية")
                # if file_menu1:
                #     file_menu1.setDisabled(True)
                
                # file_menu2 = self.menuBar().findChild(QMenu, "معلومات")
                # if file_menu2:
                #     file_menu2.setDisabled(True)
            
                # لود فلتر
                self.filter_projects_by_status()
                

    except mysql.connector.Error as e:
        QMessageBox.critical(self, "خطأ", f"خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}")
        sys.exit()