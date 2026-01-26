from أزرار_الواجهة import*
from DB import*
from ستايل import*
from الإعدادات_العامة import*

#"ترخيص منظومة المهندس الإصدار الأول"/////////////////////////////////////////////////////////////////
# ActivationDialog
class ActivationDialog(QDialog):
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"ترخيص منظومة المهندس ( V{CURRENT_VERSION})")
        self.setFixedHeight(350)
        self.setFixedWidth(700)
        layout = QVBoxLayout()
        icon_path = os.path.join(icons_dir, 'icon_app.ico')
        self.setWindowIcon(QIcon(icon_path))
#======================================================================
        self.device_id = random_device_id()
#======================================================================
        # ComboBox for account type
        # إضافة النص إلى التخطيط الأيسر مع محاذاة في المنتصف
        label = QLabel(f"ترخيص منظومة المهندس ( V{CURRENT_VERSION})")
        label.setStyleSheet("font-size: 22px; font-weight: bold;background-color: #30738b;")  # تحسين شكل النص
        label.setAlignment(Qt.AlignCenter)  # ضبط محاذاة النص في المنتصف

        #license_label = QLabel(f"اختر نوع الترخيص :")
        self.license_type_combo = QComboBox()
        self.license_type_combo.addItems(["نسخة تجريبية (30 يومًا)", "اشتراك لمدة سنة (قابل للتجديد)", "ترخيص مدى الحياة (دائم)"])
        self.license_type_combo.currentTextChanged.connect(self.toggle_date_input)

        delegate = AlignedItemDelegate(self.license_type_combo)
        self.license_type_combo.setItemDelegate(delegate)
        line_edit = QtWidgets.QLineEdit()
        line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.license_type_combo.setLineEdit(line_edit)

        self.license_type_combo.setEditable(True)
        self.license_type_combo.lineEdit().setReadOnly(True)
        self.license_type_combo.setStyleSheet(f"""
            QLabel {{
                font-family: {font_app1}; font-weight: bold;
                font-size: 14px; background-color: #c1cbcd;
            }}
        """)
        self.license_type_combo.lineEdit().mousePressEvent = lambda event: open_combo(self.license_type_combo, event)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("ادخل تاريخ الإنتهاء")
        self.date_input.setVisible(False)  # إخفاء حقل إدخال التاريخ افتراضيًا
        self.date_input.setAlignment(Qt.AlignCenter)
        # كود الجهاز
        self.device_id_label = QLabel(f"كود الجهاز :  {self.device_id}")
        self.device_id_label.setAlignment(Qt.AlignCenter)
        self.device_id_label .setFixedHeight(60)
        # مدخل كود التفعيل
        self.activation_entryL1_input = QLineEdit()
        self.activation_entryL1_input.setPlaceholderText("ادخل كود التفعيل")
        self.activation_entryL1_input.setAlignment(Qt.AlignCenter)
        # تخطيط أفقي للأزرار
        buttons_layout = QHBoxLayout()
        # الازرار: نسخ الكود وإرسال الكود
        self.copy_device_id_button = QPushButton("إنشاء ترخيص جديد")
        self.copy_device_id_button .setFixedHeight(50)
        self.send_button = QPushButton("الحصول على التفعيل")
        self.send_button .setFixedHeight(50)
        # زر التفعيل
        self.activate_button = QPushButton("تفعيل المنظومة")
        self.activate_button .setFixedHeight(50)

        # إضافة العناصر إلى التخطيط الرئيسي
        layout.addWidget(label, alignment=Qt.AlignCenter)
        #layout.addWidget(license_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.device_id_label)
        layout.addWidget(self.license_type_combo)
        layout.addWidget(self.date_input)
        layout.addWidget(self.activation_entryL1_input)
        layout.addLayout(buttons_layout)  # إضافة تخطيط الازرار الأفقي
        buttons_layout.addWidget(self.activate_button)
        buttons_layout.addWidget(self.send_button)
        buttons_layout.addWidget(self.copy_device_id_button)
        self.setLayout(layout)
        self.copy_device_id_button.clicked.connect(self.copy_device_id)
        self.activate_button.clicked.connect(self.check_activation)
        self.send_button.clicked.connect(self.report_problem)

        self.toggle_date_input()
        Pass_Styles(self)

    #عرض التاريخ للنسخة التجريبية
    # تبديل مدخلات تاريخ
    def toggle_date_input(self):
        if self.license_type_combo.currentText() == "اشتراك لمدة سنة (قابل للتجديد)" or self.license_type_combo.currentText() == "نسخة تجريبية (30 يومًا)":
            self.date_input.setVisible(True)
        else:
            self.date_input.setVisible(False)
            self.date_input.clear()

        self.copy_device_id_button.setDisabled(False)
        self.device_id_label.setText("قم بإنشاء ترخيص جديد ثم الحصول على التفعيل \n ( تحذير: ستفقد أي ترخيص سابق إذا قمت بإنشاء ترخيص جديد )")


    # نسخ معرف الجهاز
    def copy_device_id(self):
        # إنشاء الترخيص الجديد
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle('تحذير')
        msg_box.setText("إنشاء ترخيص جديد سيؤدي إلى فقدان أي ترخيص سابق\n هل أنت متأكد من المتابعة؟")
        msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)

        # تخصيص النصوص للأزرار
        msg_box.button(QMessageBox.Ok).setText("إنشاء ترخيص")
        msg_box.button(QMessageBox.Cancel).setText("إلغاء")
        reply = msg_box.exec()
        if reply == QMessageBox.Ok:
            # التحقق من نوع الترخيص
            if self.license_type_combo.currentText() == "اشتراك لمدة سنة (قابل للتجديد)" or self.license_type_combo.currentText() == "نسخة تجريبية (30 يومًا)":
                # إذا وافق المستخدم على الإنشاء
                self.device_id = random_device_id()
                self.encryption_key = get_or_create_key(DIV_KEY, DIV_KEY)
                encrypted_device_id = reg_encrypt_device_text(self.device_id, self.encryption_key)
                settings.setValue(DEVICE_id, encrypted_device_id)
            else:
                self.device_id = get_device_id()
                self.encryption_key = get_or_create_key(DIV_KEY, DIV_KEY)
                encrypted_device_id = reg_encrypt_device_text(self.device_id, self.encryption_key)
                settings.setValue(DEVICE_id, encrypted_device_id)


            self.copy_device_id_button.setDisabled(True)
            self.send_button.setFocus()
            clipboard = QApplication.clipboard()
            clipboard.setText(self.device_id)
            self.device_id_label.setText("تم نسخ كود الجهاز قم بإرسال الكود الى المطور للحصول على التفعيل.")

            # عرض رسالة تأكيد بعد نسخ الكود
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle('تأكيد')
            msg_box.setText("تم نسخ كود الجهاز بنجاح. قم بإرسال الكود إلى المطور للحصول على التفعيل.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        else:
            # إذا اختار المستخدم الإلغاء
            return

    # ارسال كود الجهاز
    # مشكلة الإبلاغ
    def report_problem(self):
        url = f"https://wa.me/218928198656?text={self.device_id}"
        webbrowser.open(url)


    # حفظ الكود JSON
    # حفظ التنشيط
    def save_activation(self, activation_code, license_type,start_date,end_date):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            #tashfer()
        # تحويل كائنات datetime إلى نصوص
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')

        # كتابة كود التفعيل ونوع الترخيص في ملف JSON
        license_data = {
            "activation_code": activation_code,
            "license_type": license_type,  # إضافة نوع الترخيص
            "start_date": start_date,  # إضافة نوع الترخيص
            "end_date": end_date  # إضافة نوع الترخيص
        }
        fak_tashfer()
        with open(license_key_path, "w", encoding="utf-8") as f:
            json.dump(license_data, f, ensure_ascii=False, indent=4)

        # تشفير البيانات
        # تحويل التواريخ إلى نصوص
        #start_date_str = start_date.strftime('%Y-%m-%d')


        # hashed_a_code = bcrypt.hashpw(activation_code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # hashed_l_type = bcrypt.hashpw(license_type.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # hashed_s_date = bcrypt.hashpw(start_date.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') #if end_date != "permanent" else "permanent"
        # hashed_e_date = bcrypt.hashpw(end_date.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        hashed_a_code = sign_data(activation_code)
        hashed_l_type = sign_data(license_type)
        hashed_s_date = sign_data(start_date)
        hashed_e_date = sign_data(end_date)

        settings.setValue(A_CODE, hashed_a_code)
        settings.setValue(L_TYPE, hashed_l_type)
        settings.setValue(S_DATE, hashed_s_date)
        settings.setValue(E_DATE, hashed_e_date)

        # حفظ مفتاح الأمان في إعدادات ويندوز باستخدام keyring
        save_security_key(A_CODE, A_CODE, activation_code)
        save_security_key(L_TYPE, L_TYPE, license_type)
        save_security_key(S_DATE, S_DATE, start_date)
        save_security_key(E_DATE, E_DATE, end_date)

        #حفظ تاريخ اخر فتح للمنظومة
        save_last_date()


    # تحقق من التنشيط
    def check_activation(self):
        self.device_id_label.setText("قم بإنشاء ترخيص جديد ثم الحصول على التفعيل \n ( تحذير: ستفقد أي ترخيص سابق إذا قمت بإنشاء ترخيص جديد )")

        activation_code = self.activation_entryL1_input.text()
        date_input=self.date_input.text()
        start_date = datetime.now()
        compo_box=self.license_type_combo.currentText()

        annual= start_date + timedelta(days=365)
        trial= start_date + timedelta(days=30)

        # التحقق من كود التفعيل
        if verify_activation_code(self.device_id, activation_code, license_type=date_input) and compo_box=="نسخة تجريبية (30 يومًا)"and trial.strftime('%Y-%m-%d')== date_input:
            end_date = date_input
            DB_license_status(self,"trial",end_date, start_date)
            self.save_activation(activation_code, "trial",start_date,end_date)
            QMessageBox.information(self, "نجاح", f"تم تفعيل النسخة التجريبية حتى: {end_date}!")
            self.accept()

        elif verify_activation_code(self.device_id, activation_code, license_type=date_input )and compo_box=="اشتراك لمدة سنة (قابل للتجديد)" and annual.strftime('%Y-%m-%d')== date_input:
            end_date = date_input
            DB_license_status(self,"annual",end_date,start_date)
            self.save_activation(activation_code, "annual",start_date,end_date)
            QMessageBox.information(self, "نجاح", f"تم تفعيل ترخيص الإشتراك السنوي حتى: {end_date}!")
            self.accept()

        elif verify_activation_code(self.device_id, activation_code, license_type="permanent")and compo_box=="ترخيص مدى الحياة (دائم)":
            end_date="permanent"
            DB_license_status(self,"permanent",end_date,start_date)
            self.save_activation(activation_code, "permanent",start_date,end_date)
            QMessageBox.information(self, "نجاح", "تم تفعيل الترخيص الدائم!")
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "كود التفعيل غير صحيح!")

        self.copy_device_id_button.setDisabled(False)



# id الجهاز=======================================================================================
# معرف الجهاز العشوائي
def random_device_id():
    c = wmi.WMI()
    motherboard = c.Win32_BaseBoard()[0].SerialNumber
    #processor = c.Win32_Processor()[0].Processorid
    hard_drive = c.Win32_DiskDrive()[0].SerialNumber

    hardware_info = motherboard + hard_drive #+ processor
    device_id = hashlib.sha256(hardware_info.encode()).hexdigest()
    # توليد رقم عشوائي ليضاف إلى الكود ، ولكنه لا يؤثر على الid الفعلي
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return random_suffix + device_id + random_suffix + VER

# احصل على معرف الجهاز
def get_device_id():
    c = wmi.WMI()
    motherboard = c.Win32_BaseBoard()[0].SerialNumber
    #processor = c.Win32_Processor()[0].Processorid
    hard_drive = c.Win32_DiskDrive()[0].SerialNumber

    hardware_info = motherboard + hard_drive #+ processor
    device_id = hashlib.sha256(hardware_info.encode()).hexdigest()
    return device_id+ VER

#استرجاع كود الجهاز المخزن
# Reg GET أو CRAET معرف الجهاز
def REG_get_or_craet_device_id():
    encryption_key = get_or_create_key(DIV_KEY,DIV_KEY)
    device_id = settings.value(DEVICE_id, "")
    try:
        device_id = decrypt_reg_device_text(device_id, encryption_key)
        return device_id
    except (InvalidToken, ValueError):
        return None

#التحقق من أكواد التفعيل
# تحقق من رمز التنشيط
def verify_activation_code(device_id, code, license_type):
    expected_code = hashlib.sha256(f"{device_id}:{license_type}".encode()).hexdigest()
    return code == expected_code

#التحقق من الترخيص=================================================================
# احصل على تفاصيل الترخيص
def get_license_details(self):
    Check_computer_deta(self)
    try:
        db_name = "project_manager2_user"
        conn = mysql.connector.connect(host=host, user=user_r, password=password_r, database=db_name)
        cursor = conn.cursor()
        # التحقق من وجود جدول الترخيص
        cursor.execute("SHOW TABLES LIKE 'License_Status'")
        if not cursor.fetchone():
            return None
        # جلب البيانات من قاعدة البيانات
        cursor.execute("SELECT license_type, start_date, end_date FROM License_Status ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if not result:
            tashfer()
            response=GEN_MSG_BOX("التحقق من الترخيص","(DB) لم يتم العثور على أي بيانات ترخيص.","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()
        DB_license_type, DB_start_date, DB_end_date = result

        #JSON
        try:
            with open(license_key_path, "r", encoding="utf-8") as f:
                license_data = json.load(f)
                JSON_activation_code = license_data.get("activation_code", "")
                JSON_license_type = license_data.get("license_type", "")
                JSON_start_date = license_data.get("start_date", "")
                JSON_end_date = license_data.get("end_date", "")
        except Exception:
            tashfer()
            response=GEN_MSG_BOX("التحقق من الترخيص","(JS)ملف الترخيص مفقود!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        #كود التفعيل
        try:
            if JSON_license_type == "trial" or JSON_license_type == "annual":
                activation_license_type= JSON_end_date
            else:
                activation_license_type= JSON_license_type
            device_id=REG_get_or_craet_device_id()
            if not verify_activation_code(device_id, JSON_activation_code, activation_license_type):
                tashfer()
                response=GEN_MSG_BOX("التحقق من التفعيل","(JS) كود التفعيل غير صحيح!","license.png","ترخيص جديد","خروج","#d9534f")
                if response == QMessageBox.Ok:
                    return None
                else:
                    sys.exit()
                return None
        except Exception:
            tashfer()
            response=GEN_MSG_BOX("التحقق من التفعيل","(JS) كود التفعيل غير صحيح!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        # قراءة بيانات الترخيص من السجل
        REG_activation_code = settings.value(A_CODE, "")
        REG_license_type = settings.value(L_TYPE, "")
        REG_start_date = settings.value(S_DATE, "")
        REG_end_date = settings.value(E_DATE, "")
        if not REG_activation_code or not REG_license_type or not REG_start_date or not REG_end_date:
            tashfer()
            response=GEN_MSG_BOX("التحقق من الترخيص","هناك بيانات ترخيص مفقودة في النظام (REG)!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        # قراءة بيانات الترخيص من النظام
        WIN_activation_code = get_security_key(A_CODE, A_CODE)
        WIN_license_type = get_security_key(L_TYPE, L_TYPE)
        WIN_start_date = get_security_key(S_DATE, S_DATE)
        WIN_end_date = get_security_key(E_DATE, E_DATE)

        if not WIN_activation_code  or not WIN_license_type or not WIN_start_date or not WIN_end_date:
            tashfer()
            response=GEN_MSG_BOX("التحقق من الترخيص","هناك بيانات ترخيص مفقودة (WIN)!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        # نوع تطابق الترخيص التحقق من صحة البيانات
        if verify_password(self, "trial", DB_license_type) and \
           verify_signature("trial", REG_license_type) and \
           JSON_license_type == "trial" and WIN_license_type == "trial":
            license_type = "trial"
        elif verify_password(self, "annual", DB_license_type) and \
             verify_signature("annual", REG_license_type) and \
             JSON_license_type == "annual" and WIN_license_type == "annual":
            license_type = "annual"
        elif verify_password(self, "permanent", DB_license_type) and \
             verify_signature("permanent", REG_license_type) and \
             JSON_license_type == "permanent" and WIN_license_type == "permanent":
            license_type = "permanent"

            #verify_password(self, "permanent", REG_license_type) and \

        else:
            tashfer()
            response=GEN_MSG_BOX("التحقق من تطابق الترخيص","تم اكتشاف تغيير في بيانات الترخيص!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        #التحقق من تاريخ البداية
        if verify_password(self, JSON_start_date, DB_start_date) and \
           verify_signature(JSON_start_date, REG_start_date) and \
           JSON_start_date == WIN_start_date:
            start_date = JSON_start_date
        else:
            tashfer()
            response=GEN_MSG_BOX("التحقق من تاريخ البدء","تاريخ بدء الترخيص غير مطابق!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        #التحقق من تاريخ النهاية
        if verify_password(self, JSON_end_date, DB_end_date) and \
           verify_signature(JSON_end_date, REG_end_date) and \
           JSON_end_date == WIN_end_date:
            end_date = JSON_end_date
        else:
            tashfer()
            response=GEN_MSG_BOX("التحقق من تاريخ الانتهاء","تاريخ انتهاء الترخيص غير مطابق!","license.png","ترخيص جديد","خروج","#d9534f")
            if response == QMessageBox.Ok:
                return None
            else:
                sys.exit()

        return {"license_type": license_type, "start_date": start_date, "end_date": end_date}

    except mysql.connector.Error as e:
        #print(f"خطأ أثناء الاتصال بقاعدة البيانات: {e}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# حماية=============================================================================================
#تحويل باسوورد الى باس
# تحقق ونسخ كلمة المرور
def check_and_copy_password():
    if back_settings.contains("password"):
        try:
            # محاولة الاتصال بقاعدة البيانات
            conn = mysql.connector.connect(
                host=host,
                user=user_r,
                password="123456"  # الباسورد القديم المخزن
            )
            cursor = conn.cursor()
            # تحديث الباسورد
            cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{password_r}'")
            conn.commit()
            cursor.close()
            conn.close()
            back_settings.remove("password")

        except Error as e:
            # عرض رسالة تأكيد
            response = GEN_MSG_BOX("وجود كلمة مرور غير صالحة",f"فشل الاتصال بقاعدة البيانات. يبدو أن كلمة المرور القديمة لم تعد صالحة.\nهل تريد حذفها من الإعدادات؟","license.png","حذف كلمة المرور","خروج","#d9534f")
            if response == QMessageBox.Ok:
                back_settings.remove("password")
            else:
                sys.exit()
                return False



# PasswordSetUpdialog
class PasswordSetupDialog(QDialog):
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تأمين التطبيق")
        # تعيين اتجاه التخطيط العام من اليمين إلى اليسار
        self.setLayoutDirection(Qt.RightToLeft)
        # تغيير لون الخلفية إلى الأخضر
        #self.setStyleSheet("background-color: green;")
        # تثبيت أبعاد النافذة
        self.setFixedSize(550, 300)
        self.setup_ui()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(15)

        # إضافة عنوان (Header) للنافذة في المنتصف
        titleLabel = QLabel("إنشاء كلمة مرور جديدة")
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-size: 18pt; font-weight: bold;")
        mainLayout.addWidget(titleLabel)

        # إنشاء تخطيط الفورم للإدخالات مع توحيد عرض الليبلات
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignCenter)
        labelWidth = 170  # عرض ثابت لليبلات

        # ليبل وحقل كلمة المرور
        lblPassword = QLabel("أدخل كلمة مرور جديدة :")
        lblPassword.setFixedWidth(labelWidth)
        self.passwordLineEdit = QLineEdit(self)
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.setAlignment(Qt.AlignCenter)
        self.passwordLineEdit.setPlaceholderText("أدخل كلمة المرور")
        self.passwordLineEdit.setMinimumWidth(200)
        formLayout.addRow(lblPassword, self.passwordLineEdit)

        # ليبل وحقل إعادة إدخال كلمة المرور
        lblConfirm = QLabel("أعد إدخال كلمة المرور :")
        lblConfirm.setFixedWidth(labelWidth)
        self.confirmPasswordLineEdit = QLineEdit(self)
        self.confirmPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.confirmPasswordLineEdit.setAlignment(Qt.AlignCenter)
        self.confirmPasswordLineEdit.setPlaceholderText("أعد إدخال كلمة المرور")
        self.confirmPasswordLineEdit.setMinimumWidth(200)
        formLayout.addRow(lblConfirm, self.confirmPasswordLineEdit)

        # ليبل وحقل اسم المدرسة
        lblSchool = QLabel("اسم مدرستك الابتدائية:")
        lblSchool.setFixedWidth(labelWidth)
        self.schoolNameLineEdit = QLineEdit(self)
        self.schoolNameLineEdit.setAlignment(Qt.AlignCenter)
        self.schoolNameLineEdit.setPlaceholderText("أدخل اسم مدرستك الابتدائية")
        self.schoolNameLineEdit.setMinimumWidth(200)
        formLayout.addRow(lblSchool, self.schoolNameLineEdit)

        mainLayout.addLayout(formLayout)

        lblPassword.setAlignment(Qt.AlignCenter)
        lblConfirm.setAlignment(Qt.AlignCenter)
        lblSchool.setAlignment(Qt.AlignCenter)

        # إنشاء أزرار "إنشاء" و"إلغاء"
        self.buttonBox = QDialogButtonBox(self)
        # لضمان ترتيب الأزرار كما نريد (إنشاء على اليسار) نقوم بتعيين اتجاه تخطيط خاص للأزرار إلى LeftToRight

        # إنشاء تخطيط أفقي للأزرار بحيث تمتد بعرض النافذة
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setSpacing(10)

        # زر "إلغاء"
        self.cancelButton = QPushButton("إلغاء")
        self.cancelButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # زر "إنشاء" على اليسار
        self.createButton = QPushButton("إنشاء كلمة مرور")
        self.createButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.createButton)
        mainLayout.addLayout(buttonsLayout)

        # ربط الأزرار بالإجراءات
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        # تعيين زر "إنشاء" كالزر الافتراضي وإعطاؤه التركيز
        self.createButton.setDefault(True)  # يجعل الزر الافتراضي يتم تنشيطه بـ Enter
        #self.createButton.setFocus()        # يعطي التركيز لزر "إنشاء" عند فتح النافذة

# نافذة مخصصة لتغيير كلمة المرور
# ChangePasswordDialog
class ChangePasswordDialog(QDialog):
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تغيير كلمة المرور")
        # تعيين اتجاه التخطيط من اليمين إلى اليسار
        self.setLayoutDirection(Qt.RightToLeft)
        # تغيير لون الخلفية إلى الأخضر وتثبيت أبعاد النافذة
        #self.setStyleSheet("background-color: green;")
        self.setFixedSize(500, 300)
        self.setup_ui()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(15)

        # عنوان النافذة في المنتصف
        titleLabel = QLabel("تغيير كلمة المرور")
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-size: 18pt; font-weight: bold;")
        mainLayout.addWidget(titleLabel)

        # تخطيط الفورم لإدخال الحقول مع توحيد عرض الليبل
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignRight)
        labelWidth = 180  # عرض ثابت لليبل

        # حقل إدخال كلمة السر الحالية
        lblOldPassword = QLabel("أدخل كلمة السر الحالية:")
        lblOldPassword.setFixedWidth(labelWidth)
        self.oldPasswordLineEdit = QLineEdit(self)
        self.oldPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.oldPasswordLineEdit.setAlignment(Qt.AlignCenter)
        self.oldPasswordLineEdit.setPlaceholderText("أدخل كلمة السر الحالية")
        self.oldPasswordLineEdit.setMinimumWidth(250)
        formLayout.addRow(lblOldPassword, self.oldPasswordLineEdit)

        # حقل إدخال الكلمة الجديدة
        lblNewPassword = QLabel("أدخل كلمة السر الجديدة:")
        lblNewPassword.setFixedWidth(labelWidth)
        self.newPasswordLineEdit = QLineEdit(self)
        self.newPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.newPasswordLineEdit.setAlignment(Qt.AlignCenter)
        self.newPasswordLineEdit.setPlaceholderText("أدخل كلمة السر الجديدة")
        self.newPasswordLineEdit.setMinimumWidth(250)
        formLayout.addRow(lblNewPassword, self.newPasswordLineEdit)

        # حقل إعادة إدخال الكلمة الجديدة للتأكيد
        lblConfirmPassword = QLabel("أعد إدخال كلمة السر الجديدة:")
        lblConfirmPassword.setFixedWidth(labelWidth)
        self.confirmPasswordLineEdit = QLineEdit(self)
        self.confirmPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.confirmPasswordLineEdit.setAlignment(Qt.AlignCenter)
        self.confirmPasswordLineEdit.setPlaceholderText("أعد إدخال كلمة السر الجديدة")
        self.confirmPasswordLineEdit.setMinimumWidth(250)
        formLayout.addRow(lblConfirmPassword, self.confirmPasswordLineEdit)

        mainLayout.addLayout(formLayout)

        # تخطيط أفقي للأزرار بحيث تمتد بعرض النافذة
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setSpacing(10)
        # زر "تغيير كلمة المرور" على اليسار
        self.changeButton = QPushButton("تغيير كلمة المرور")
        self.changeButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # زر "الغاء"
        self.cancelButton = QPushButton("الغاء")
        self.cancelButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.changeButton)
        mainLayout.addLayout(buttonsLayout)

        # ربط الأزرار بالإجراءات المناسبة
        self.changeButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        # تعيين زر "إنشاء" كالزر الافتراضي وإعطاؤه التركيز
        self.changeButton.setDefault(True)  # يجعل الزر الافتراضي يتم تنشيطه بـ Enter
        #self.changeButton.setFocus()        # يعطي التركيز لزر "إنشاء" عند فتح النافذة

# إنشاء كلمة المرور
# CreatePassword
def createPassword(self):
    if self.license_type == "trial":
        reply = GEN_MSG_BOX("قيود النسخة التجريبية","هذه الميزة متوفرة في النسخة المدفوعة فقط.","license.png", "شراء", "إلغاء", "#dfcab4")
        if reply != QMessageBox.Ok:
            return
        else:
            self.changing_activation_dialog()
            return

    while True:
        dialog = PasswordSetupDialog(self)
        if dialog.exec() == QDialog.Accepted:
            password1 = dialog.passwordLineEdit.text().strip()
            password2 = dialog.confirmPasswordLineEdit.text().strip()
            school_name = dialog.schoolNameLineEdit.text().strip()

            if not password1:
                QMessageBox.warning(self, "خطأ", "يجب إدخال كلمة مرور صالحة.")
                continue
            if password1 != password2:
                reply = QMessageBox.question(self, "خطأ في تأكيد كلمة المرور","كلمة المرور غير متطابقة. هل ترغب في المحاولة مرة أخرى؟",QMessageBox.Retry | QMessageBox.Close)
                if reply == QMessageBox.Close:
                    break
                continue
            if not school_name:
                QMessageBox.warning(self, "خطأ", "لم يتم إدخال اسم مدرسة صالح.")
                continue

            try:
                hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                new_school_name = bcrypt.hashpw(school_name.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                conn = mysql.connector.connect(host=host, user="root",password=password_r, database='project_manager2_user')
                cursor = conn.cursor()
                # التحقق من وجود حساب المدير
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin",))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO users (username, password_hash, user_permissions, Security_question) ""VALUES (%s, %s, %s, %s)",("admin", hashed_password, "مدير", new_school_name))
                    cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{hashed_password}'")
                else:
                    cursor.execute("UPDATE users SET password_hash = %s, Security_question = %s WHERE username = %s",(hashed_password, new_school_name, "admin"))
                    cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{hashed_password}'")

                conn.commit()
                cursor.close()
                conn.close()

                QMessageBox.information(self, "إعادة تشغيل", "سيتم إعادة تشغيل التطبيق لتحديث الإعدادات.")
                restart_application()
                break

            except mysql.connector.Error as err:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث كلمة المرور: {err}")
                return
        else:
            break

# تغيير كلمة المرور
# تغيير كلمة المرور
def changePassword(self):
    while True:
        dialog = ChangePasswordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            current_password = dialog.oldPasswordLineEdit.text().strip()
            new_password = dialog.newPasswordLineEdit.text().strip()
            confirm_password = dialog.confirmPasswordLineEdit.text().strip()

            try:
                conn = mysql.connector.connect(host=host, user="root",password=password_r, database='project_manager2_user')
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE username = %s", ("admin",))
                result = cursor.fetchone()

                if not result or not bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
                    reply = QMessageBox.question(self, "خطأ في كلمة السر الحالية","كلمة السر الحالية غير صحيحة. هل تريد إعادة المحاولة؟",QMessageBox.Retry | QMessageBox.Close)
                    if reply == QMessageBox.Close:
                        return
                    continue

                if not new_password:
                    reply = QMessageBox.question(self, "خطأ","يجب إدخال كلمة مرور جديدة صالحة. هل تريد إعادة المحاولة؟",QMessageBox.Retry | QMessageBox.Close)
                    if reply == QMessageBox.Close:
                        return
                    continue

                if new_password != confirm_password:
                    reply = QMessageBox.question(self, "خطأ في تأكيد كلمة المرور الجديدة","كلمة المرور الجديدة غير متطابقة. هل ترغب في المحاولة مرة أخرى؟",QMessageBox.Retry | QMessageBox.Close)
                    if reply == QMessageBox.Close:
                        return
                    continue
                # تحديث كلمة المرور في قاعدة البيانات
                new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s",(new_hashed_password, "admin"))
                cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{new_hashed_password}'")
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "تم تغيير كلمة السر", "تم تغيير كلمة السر بنجاح\nسيتم إعادة تشغيل التطبيق.")
                restart_application()
                return
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث كلمة المرور: {err}")
                return
        else:
            return

# حذف كلمة المرور
# تعطل الأمن
def disableSecurity(self):
    current_password, okPressed = QInputDialog.getText(self, "إلغاء التأمين","أدخل كلمة السر الحالية لإلغاء التأمين:",QLineEdit.Password)
    if not okPressed:
        return
    try:
        conn = mysql.connector.connect(host=host, user="root",password=password_r, database='project_manager2_user')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", ("admin",))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
            reply = QMessageBox.question(self, "إلغاء التأمين","هل أنت متأكد من رغبتك في إلغاء التأمين؟ سيتم حذف كلمة السر.",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{pm_password}'")
                cursor.execute("UPDATE users SET password_hash = NULL, Security_question = NULL WHERE username = %s",("admin",))
                conn.commit()
                QMessageBox.information(self, "اعادة تشغيل", "تم إلغاء التأمين سيتم إعادة تشغيل التطبيق")
                restart_application()
        else:
            QMessageBox.warning(self, "خطأ في كلمة السر الحالية", "كلمة السر الحالية غير صحيحة.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث كلمة المرور: {err}")

# التحقق من كلمة المرور عند تسجيل الدخول
# AskPassword
def askPassword(self):
    Pass_Styles(self)
    self.setWindowTitle("1 منظومة المهندس")
    icon_path = os.path.join(icons_dir, 'icon_app.ico')
    self.setWindowIcon(QIcon(icon_path))

    # إنشاء نافذة الإدخال (Dialog)
    dialog = QDialog(self)
    dialog.setWindowTitle("تسجيل دخول")
    dialog.resize(600, 0)
    dialog.setFixedHeight(280)
    dialog.setFixedWidth(600)
    main_layout = QHBoxLayout(dialog)
    left_layout = QVBoxLayout()
    # إضافة النص إلى التخطيط الأيسر مع محاذاة في المنتصف
    label = QLabel(f"منظومة المهندس ( V{CURRENT_VERSION})", dialog)
    label.setStyleSheet("font-size: 20px; font-weight: bold;")  # تحسين شكل النص
    label.setAlignment(Qt.AlignCenter)  # ضبط محاذاة النص في المنتصف
    label.setFixedHeight(25)
    left_layout.addWidget(label, alignment=Qt.AlignCenter)
    left_layout.addWidget(QLabel(" اسم المستخدم : ", dialog))
    self.pass_comboBox = QComboBox(dialog)
    left_layout.addWidget(self.pass_comboBox)

    try:
        db_name = "project_manager2_user"
        conn = mysql.connector.connect(host=host, user=user_r, password=password_r, database=db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        accounts = [row[0] for row in cursor.fetchall()]
        self.pass_comboBox.addItems(accounts)
        conn.close()
    except mysql.connector.Error as e:
        pass

    delegate = AlignedItemDelegate(self.pass_comboBox)
    self.pass_comboBox.setItemDelegate(delegate)

    line_edit = QtWidgets.QLineEdit()
    line_edit.setAlignment(QtCore.Qt.AlignCenter)
    self.pass_comboBox.setLineEdit(line_edit)

    self.pass_comboBox.setEditable(True)
    self.pass_comboBox.lineEdit().setReadOnly(True)
    self.pass_comboBox.setStyleSheet(f"""
        QLabel {{
            font-family: {font_app1}; font-weight: bold;
            font-size: 15px; background-color: #c1cbcd;
        }}
    """)
    self.pass_comboBox.lineEdit().mousePressEvent = lambda event: open_combo(self.pass_comboBox, event)

    # حقل إدخال كلمة المرور
    password_input = QLineEdit(dialog)
    password_input.setEchoMode(QLineEdit.Password)
    password_input.setAlignment(Qt.AlignCenter)
    password_input.setFocus()
    left_layout.addWidget(QLabel("  أدخل كلمة المرور : ", dialog))
    left_layout.addWidget(password_input)

    # زر "دخول" يمين الصفر
    enter_button = QPushButton("دخول", dialog)
    enter_button.setFixedHeight(60)  # تعيين الارتفاع الكلي إلى 120 (60 الأصلي + 60 إضافي)
    #enter_button.setFixedSize(60, 60)
    enter_button.setStyleSheet("""
        QPushButton {
            background-color: #70abc2;
            font-weight: bold;
            font-size: 20px;
        }
        QPushButton:hover {
            background-color: #c3d7d3;
        }
        QPushButton:pressed {
            background-color: #a8c4bc;
        }
    """)
    enter_button.clicked.connect(dialog.accept)
    left_layout.addWidget(enter_button)
    # إضافة التخطيط الأيسر إلى التخطيط الرئيسي
    main_layout.addLayout(left_layout)
    # القسم الأيمن (لوحة الأرقام)
    number_pad_layout = QVBoxLayout()
    # أزرار الأرقام
    grمعرف_layout = QGridLayout()
    buttons = {}

    for i in range(10):
        buttons[i] = QPushButton(str(i), dialog)
        buttons[i].setFixedSize(60, 60)
        buttons[i].setStyleSheet("font-size: 18px;")
        row, col = divmod(i - 1, 3) if i != 0 else (3, 1)  # تحديد الصفوف والأعمدة
        grمعرف_layout.addWidget(buttons[i], row, col)
        buttons[i].clicked.connect(lambda _, b=i: password_input.insert(str(b)))

    # زر "C" يسار الصفر
    clear_button = QPushButton("C", dialog)
    clear_button.setFixedSize(60, 60)
    clear_button.setStyleSheet("""
        QPushButton {
            background-color: #76a5af;;
            font-weight: bold;
            font-size: 20px;
        }
        QPushButton:hover {
            background-color: #c3d7d3;
        }
        QPushButton:pressed {
            background-color: #a8c4bc;
        }
    """)

    clear_button.clicked.connect(lambda: password_input.clear())
    grمعرف_layout.addWidget(clear_button, 3, 0)  # الصف الثالث، العمود الأول

    # زر "دخول" يمين الصفر
    reject_button = QPushButton("خروج", dialog)
    reject_button.setFixedSize(60, 60)

    reject_button.setStyleSheet("""
        QPushButton {
            background-color: #ea9999;
            font-weight: bold;
            font-size: 20px;
        }
        QPushButton:hover {
            background-color: #c3d7d3;
        }
        QPushButton:pressed {
            background-color: #a8c4bc;
        }
    """)
    reject_button.clicked.connect(dialog.reject)
    grمعرف_layout.addWidget(reject_button, 3, 2)  # الصف الثالث، العمود الثالث
    # إضافة شبكة الازرار إلى التخطيط
    number_pad_layout.addLayout(grمعرف_layout)
    # إضافة لوحة الأرقام إلى التخطيط الرئيسي
    main_layout.addLayout(number_pad_layout)

    while True:
        if dialog.exec() == QDialog.Accepted:
            selected_user = self.pass_comboBox.currentText()
            entered_password = password_input.text().strip()

            try:
                conn = mysql.connector.connect(host=host, user="root",
                                             password=password_r, database='project_manager2_user')
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE username = %s", (selected_user,))
                result = cursor.fetchone()
                conn.close()

                if result and result[0] and bcrypt.checkpw(entered_password.encode('utf-8'), result[0].encode('utf-8')):
                    settings.setValue("account_type", selected_user)
                    break
                else:
                    if selected_user=="admin":
                        msg = QMessageBox(self)
                        msg.setWindowTitle("خطأ في كلمة المرور")
                        msg.setText("كلمة المرور غير صحيحة. هل ترغب في المحاولة مرة أخرى؟")
                        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close | QMessageBox.Help)
                        retry_button = msg.button(QMessageBox.Retry)
                        close_button = msg.button(QMessageBox.Close)
                        help_button = msg.button(QMessageBox.Help)
                        retry_button.setText("إعادة المحاولة")
                        close_button.setText("إغلاق")
                        help_button.setText("حذف كلمة المرور")
                        reply = msg.exec()

                        if reply == QMessageBox.Close:
                            sys.exit()
                        elif reply == QMessageBox.Help:
                            handle_activation_and_password_recovery(self)
                        elif reply == QMessageBox.Retry:
                            continue
                    else:
                        # إنشاء مربع رسالة مخصص
                        msg = QMessageBox(self)
                        msg.setWindowTitle("خطأ في كلمة المرور")
                        msg.setText("كلمة المرور غير صحيحة. هل ترغب في المحاولة مرة أخرى؟")
                        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
                        # تخصيص النصوص
                        retry_button = msg.button(QMessageBox.Retry)
                        close_button = msg.button(QMessageBox.Close)

                        retry_button.setText("إعادة المحاولة")
                        close_button.setText("إغلاق")
                        # انتظار استجابة المستخدم
                        reply = msg.exec()
                        if reply == QMessageBox.Close:
                            sys.exit()  # Exit the application
                        elif reply == QMessageBox.Retry:
                            continue

            except mysql.connector.Error as err:
                QMessageBox.critical(self, "خطأ", f"خطأ أثناء التحقق من كلمة المرور: {str(err)}")
        else:
            sys.exit()

# كلاس لنافذة استعادة كلمة المرور المخصصة
# PasswordRecoveryDialog
class PasswordRecoveryDialog(QDialog):
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("حذف كلمة المرور")
        self.setFixedSize(400, 250)

        # إعداد التخطيط
        layout = QVBoxLayout(self)

        # حقل إدخال كود التفعيل
        self.activation_label = QLabel("أدخل كود تفعيل المنظومة:")
        self.activation_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.activation_label)

        self.activation_input = QLineEdit(self)
        self.activation_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.activation_input)

        # حقل إدخال اسم المدرسة
        self.school_label = QLabel("أدخل اسم مدرستك الابتدائية:")
        self.school_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.school_label)

        self.school_input = QLineEdit(self)
        self.school_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.school_input)

        # زر التأكيد
        self.confirm_button = QPushButton(qta.icon('fa5s.check-circle', color='green'), "تأكيد", self)
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #bbcfb2;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c3d7d3;
            }
            QPushButton:pressed {
                background-color: #a8c4bc;
            }
        """)
        layout.addWidget(self.confirm_button)

        # زر الإلغاء
        self.cancel_button = QPushButton("إلغاء", self)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ea9999;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c3d7d3;
            }
            QPushButton:pressed {
                background-color: #a8c4bc;
            }
        """)
        layout.addWidget(self.cancel_button)

# التعامل مع التنشيط واستعادة كلمة المرور
def handle_activation_and_password_recovery(self):
    dialog = PasswordRecoveryDialog(self)
    if dialog.exec() == QDialog.Accepted:
        activation_code = dialog.activation_input.text().strip()
        s_nam = dialog.school_input.text().strip()
        if not activation_code or not s_nam:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال كود التفعيل واسم المدرسة.")
            return

        stored_hashed_code = settings.value(A_CODE, "")
        input_hashed_code = sign_data(activation_code)
        if stored_hashed_code and input_hashed_code == stored_hashed_code:
            try:
                conn = mysql.connector.connect(host=host, user="root", password=password_r, database='project_manager2_user')
                cursor = conn.cursor()
                # جلب اسم المدرسة المشفر من قاعدة البيانات
                cursor.execute("SELECT Security_question FROM users WHERE username = %s", ("admin",))
                result = cursor.fetchone()

                if result and result[0]:
                    stored_encrypted_school = result[0]
                    # التحقق من تطابق اسم المدرسة باستخدام bcrypt
                    if bcrypt.checkpw(s_nam.encode('utf-8'), stored_encrypted_school.encode('utf-8')):
                        cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{pm_password}'")
                        cursor.execute("UPDATE users SET password_hash = NULL, Security_question = NULL WHERE username = %s", ("admin",))
                        conn.commit()
                        QMessageBox.information(self, "تم التحقق", "تم حذف كلمة المرور بنجاح.")
                        restart_application()
                    else:
                        QMessageBox.warning(self, "خطأ", "اسم المدرسة غير صحيح.")
                else:
                    QMessageBox.warning(self, "خطأ", "لا توجد بيانات أمان مخزنة.")

                cursor.close()
                conn.close()

            except mysql.connector.Error as err:
                QMessageBox.critical(self, "خطأ", f"خطأ أثناء الاسترداد: {str(err)}")
        else:
            QMessageBox.warning(self, "خطأ", "كود التفعيل غير صحيح.")

#اغلاق البرنامج ================================================================================
# Closevent
def closeEvent(self, event):
    # إغلاق نافذة الطباعة إذا كانت مفتوحة
    try:
        if hasattr(self, 'print_export_dialog') and self.print_export_dialog is not None:
            print("إغلاق نافذة الطباعة المفتوحة...")
            try:
                self.print_export_dialog.close()
                self.print_export_dialog = None
            except Exception as e:
                print(f"خطأ في إغلاق نافذة الطباعة: {e}")
    except Exception as e:
        print(f"خطأ في التحقق من نافذة الطباعة: {e}")

     # إعداد الرسالة المنبثقة مع أسماء الأزرار المتغيرة
    # عرض الحوار التأكيد
    def show_confirmation_dialog(message, icon_path, button, Cancel):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('إغلاق البرنامج')
        msg_box.setText(message)
        msg_box.setIconPixmap(QPixmap(icon_path))
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.button(QMessageBox.Ok).setText(button)
        msg_box.button(QMessageBox.Cancel).setText(Cancel)
        # تحديد الزر الافتراضي
        msg_box.setDefaultButton(QMessageBox.Ok)
        # تنفيذ النافذة والحصول على الزر الذي تم الضغط عليه
        response = msg_box.exec()
        return response

    if self.license_type  == "trial":
        icon_path = os.path.join(icons_dir, 'Exit.png')
        response = show_confirmation_dialog('هل أنت متأكد أنك تريد إغلاق البرنامج؟', icon_path,'إغلاق', 'إلغاء')
        if response == QMessageBox.Ok:
            event.accept()
            return
        else:
            event.ignore()
        return

    if os.path.exists(backup_info):
        icon_path = os.path.join(icons_dir, 'database.png')
        icon_path1 = os.path.join(icons_dir, 'Exit.png')
        icon = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        response = show_confirmation_dialog('هل أنت متأكد أنك تريد إغلاق البرنامج؟', icon_path1,'إغلاق', 'إلغاء')
        if response == QMessageBox.Ok:
            event.accept()
            #return
        else:
            event.ignore()
            return

        response = show_confirmation_dialog('هل تريد تحديث النسخة الاحتياطية؟', icon, 'نعم، قم بالتحديث', 'لا، لاحقًا')
        if response == QMessageBox.Ok:
            Auto_Backup_DB(self)
            event.accept()
        else:
            event.accept()
    else:
        #QMessageBox.warning(self, 'النسخ الإحتياطي التلقائي', 'قم بتحديد مسار حفظ النسخة الإحتياطي لقاعدة البيانات.')
        reply = GEN_MSG_BOX('النسخ الإحتياطي التلقائي','قم بتحديد مسار حفظ النسخة الإحتياطي لقاعدة البيانات.','warning.png','إضافة','خروج',msg_box_color)
        if reply != QMessageBox.Ok:
            return
        Backup_DB(self)
        event.accept()

    if not os.path.exists(backup_info):
        icon_path = os.path.join(icons_dir, 'Exit.png')
        response = show_confirmation_dialog('هل أنت متأكد أنك تريد إغلاق البرنامج؟', icon_path,"إغلاق", "إلغاء")
        if response == QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()


#اسم الشركة والشعار////////////////////////////////////////////////////////////////////
# CompanyInfo
def CompanyInfo(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("إعدادات الشركة")
    dialog.setLayoutDirection(Qt.RightToLeft)
    dialog.resize(550, 250)

    main_layout = QVBoxLayout(dialog)

    # الصف الأول: اسم الشركة
    name_layout = QVBoxLayout()
    company_name_label = QLabel("اسم الشركة:")
    company_name_label.setAlignment(Qt.AlignCenter)
    company_name_input = QLineEdit()
    company_name_input.setAlignment(Qt.AlignCenter)
    name_layout.addWidget(company_name_label)
    name_layout.addWidget(company_name_input)
    main_layout.addLayout(name_layout)

    # الصف الثاني: رقم الهاتف + عنوان الشركة
    second_row_layout = QHBoxLayout()

    phone_layout = QVBoxLayout()
    phone_label = QLabel("رقم الهاتف:")
    phone_label.setAlignment(Qt.AlignCenter)
    phone_input = QLineEdit()
    phone_input.setAlignment(Qt.AlignCenter)
    phone_layout.addWidget(phone_label)
    phone_layout.addWidget(phone_input)

    address_layout = QVBoxLayout()
    address_label = QLabel("عنوان الشركة:")
    address_label.setAlignment(Qt.AlignCenter)
    address_input = QLineEdit()
    address_input.setAlignment(Qt.AlignCenter)
    address_layout.addWidget(address_label)
    address_layout.addWidget(address_input)

    second_row_layout.addLayout(phone_layout)
    second_row_layout.addLayout(address_layout)
    main_layout.addLayout(second_row_layout)

    # الصف الثالث: نوع العملة + إيميل الشركة
    third_row_layout = QHBoxLayout()

    currency_layout = QVBoxLayout()
    currency_label = QLabel("نوع العملة:")
    currency_label.setAlignment(Qt.AlignCenter)
    currency_input = QLineEdit()
    currency_input.setAlignment(Qt.AlignCenter)
    currency_layout.addWidget(currency_label)
    currency_layout.addWidget(currency_input)

    email_layout = QVBoxLayout()
    email_label = QLabel("إيميل الشركة:")
    email_label.setAlignment(Qt.AlignCenter)
    email_input = QLineEdit()
    email_input.setAlignment(Qt.AlignCenter)
    email_layout.addWidget(email_label)
    email_layout.addWidget(email_input)

    third_row_layout.addLayout(currency_layout)
    third_row_layout.addLayout(email_layout)
    main_layout.addLayout(third_row_layout)

    # شعار الشركة
    logo_label = QLabel("شعار الشركة:")
    logo_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(logo_label)

    # تخطيط أفقي: عرض الشعار + أزرار تحت بعض
    logo_row_layout = QHBoxLayout()

    # DraggableLabel لعرض الشعار
    logo_display = DraggableLabel()
    logo_display.setFixedSize(250, 250)
    logo_display.setStyleSheet("border: 1px solid #ccc;")
    logo_display.setAlignment(Qt.AlignCenter)

    # أزرار تحميل الشعار وحذفه (عموديًا)
    logo_buttons_col = QVBoxLayout()
    upload_button = QPushButton(qta.icon('fa5s.plus', color='white'), "تحميل الشعار ")
    upload_button.setFixedSize(300, 60)
    upload_button.setStyleSheet("""
    QPushButton {
        background-color:#2889a6;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #31b0d5;
    }
""")
    delete_logo_button = QPushButton(qta.icon('fa5s.trash', color='white'), "حذف الشعار ")
    delete_logo_button.setFixedSize(300, 60)
    delete_logo_button.setStyleSheet("""
    QPushButton {
        background-color: #d15460;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #c82333;
    }
""")
    save_button = QPushButton(qta.icon('fa5s.save', color='white'), "حفظ الإعدادات ")
    save_button.setFixedSize(300, 120)
    save_button.setStyleSheet("""
    QPushButton {
        background-color: #4aa860;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #218838;
    }
""")

    logo_buttons_col.addWidget(upload_button)
    logo_buttons_col.addWidget(delete_logo_button)
    logo_buttons_col.addWidget(save_button)
    logo_row_layout.addLayout(logo_buttons_col)
    logo_row_layout.addWidget(logo_display)
    main_layout.addLayout(logo_row_layout)

    # متغير لتخزين مسار الشعار
    self.logo_path = ""

    # وظيفة لتحميل معلومات الشركة من الإعدادات
    # تحميل معلومات الشركة
    def load_company_info():
        company_name = settings.value("company_name", "")
        self.logo_path = settings.value("company_logo", "")
        Currency_type = settings.value("Currency_type", "")

        phone_number = settings.value("company_phone", "")
        address = settings.value("company_address", "")
        email = settings.value("company_email", "")

        if company_name:
            company_name_input.setText(company_name)

        if Currency_type:
            currency_input.setText(Currency_type)
        else:
            currency_input.setText(" {Currency_type}")

        if phone_number:
            phone_input.setText(phone_number)
        if address:
            address_input.setText(address)
        if email:
            email_input.setText(email)

        if self.logo_path:
            pixmap = QPixmap(self.logo_path)
            logo_display.setPixmap(pixmap.scaled(logo_display.size()))

    # وظيفة لتحميل الشعار
    # تحميل شعار
    def upload_logo():
        file_path, _ = QFileDialog.getOpenFileName(dialog, "اختر شعار الشركة", "", "Images (*.png *.jpg *.jpeg *.bmp *.ico)")
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            logo_display.setPixmap(pixmap.scaled(logo_display.size()))

    # حذف الشعار
    def delete_logo():
        # حذف الشعار من الإعدادات وإعادة تعيين المسار
        logo_path = ""
        logo_display.clear()  # مسح الشعار المعروض في واجهة المستخدم

        settings.remove("company_logo")  # حذف الشعار من الإعدادات
        load_company_info()

    # حفظ المعلومات
    def save_info():
        company_name = company_name_input.text().strip()
        Currency_type = currency_input.text().strip()

        phone_number = phone_input.text().strip()
        address = address_input.text().strip()
        email = email_input.text().strip()

        if company_name:  # التحقق من وجود اسم الشركة والشعار
            #try:
                # الاتصال بقاعدة البيانات
                db_name = "project_manager2_user"  # تأكد من تطابق اسم قاعدة البيانات
                conn = mysql.connector.connect(host=host, user=user, password=password, database=db_name)
                cursor = conn.cursor()
                # التحقق مما إذا كانت بيانات الشركة موجودة مسبقًا
                cursor.execute("SELECT COUNT(*) FROM company")
                result = cursor.fetchone()
                if result[0] > 0:  # إذا كانت البيانات موجودة، نقوم بالتحديث
                    cursor.execute(
                        "UPDATE company SET company_name = %s, company_logo = %s, Currency_type = %s, phone_number = %s, address = %s, email = %s WHERE id = 1",
                        (company_name, self.logo_path, Currency_type, phone_number, address, email)
                    )
                else:  # إذا لم تكن البيانات موجودة، نقوم بالإدخال
                    cursor.execute(
                        "INSERT INTO company (company_name, company_logo, Currency_type, phone_number, address, email) VALUES (%s, %s, %s, %s, %s, %s)",
                        (company_name, self.logo_path, Currency_type, phone_number, address, email)
                    )

                conn.commit()
                conn.close()
                # حفظ البيانات في QSettings
                settings.setValue("company_name", company_name)
                settings.setValue("company_phone", phone_number)
                settings.setValue("company_address", address)
                settings.setValue("company_email", email)
                # إذا لم يتم تحميل الشعار، نقوم بحذفه من الإعدادات
                if self.logo_path:
                    settings.setValue("company_logo", self.logo_path)
                else:
                    settings.remove("company_logo")  # حذف الشعار من الإعدادات

                # إذا لم يتم تحميل الشعار، نقوم بحذفه من الإعدادات
                if Currency_type:
                    settings.setValue("Currency_type", Currency_type)
                else:
                    settings.setValue("Currency_type", " {Currency_type}") # حذف الشعار من الإعدادات

                QMessageBox.information(self, "إعادة تشغيل", "سيتم إعادة تشغيل التطبيق لتحديث الإعدادات.")
                restart_application()

            # except mysql.connector.Error as e:
            #     QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}")
        else:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الشركة وتحميل الشعار.")

    upload_button.clicked.connect(upload_logo)
    delete_logo_button.clicked.connect(delete_logo)
    save_button.clicked.connect(save_info)
    load_company_info()
    dialog.exec()

#التحقق من تاريخ الكمبيوتر =====================================================================
# تحقق من الكمبيوتر deta
def Check_computer_deta(self):
    if not is_internet_available():
        return None
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        server_time = datetime.utcfromtimestamp(response.tx_time)
        local_time = datetime.utcnow()
        time_difference = abs((local_time - server_time).total_seconds())
        formatted_local_time = local_time.strftime('%Y-%m-%d')  # الوقت المحلي بدون ثوانٍ('%Y-%m-%d %H:%M')
        formatted_server_time = server_time.strftime('%Y-%m-%d')  # وقت الخادم بدون ثوانٍ
        if time_difference > 240 :
            tashfer()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setWindowTitle("تحذير منظومة المهندس")
            msg.setText(f"<center><b>التاريخ في جهازك غير صحيح</b><br>"
                        f"<b>قم بتعديل وقت وتاريخ الجهاز!</b><br><br>"
                        f"<b>التاريخ الحالي: {formatted_local_time}</b><br>"
                        f"<b>التاريخ الصحيح: {formatted_server_time}</b></center>")

            # إضافة ستايل مخصص
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #ffcccc;  /* لون الخلفية أحمر فاتح */
                    border: 2px solid #d9534f; /* إطار أحمر غامق */
                    border-radius: 10px;
                    font-family: 'Segoe UI';
                    font-size: 18px;  /* تكبير الخط */
                    padding: 20px;  /* تكبير حجم الرسالة */
                }
                QMessageBox QLabel {
                    color: #a94442;  /* لون النص أحمر غامق */
                    font-size: 18px;  /* تكبير حجم النص */
                }
                QMessageBox QPushButton {
                    background-color: #d9534f;  /* زر باللون الأحمر الغامق */
                    color: white;
                    font-size: 16px;
                    padding: 10px 20px;  /* تكبير حجم الازرار */
                    border-radius: 5px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #c9302c;  /* لون أغمق عند التمرير */
                }
                QMessageBox QPushButton:pressed {
                    background-color: #ac2925;  /* لون أغمق عند الضغط */
                }
            """)

            msg.exec()
            sys.exit()
    except Exception as e:
        pass



