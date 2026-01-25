from ستايل import*
from الإعدادات_العامة import*
import shutil



# رابط ملف JSON على GitHub
VERSION_URL = "https://raw.githubusercontent.com/etqa/engineer-system-updates/refs/heads/main/version.json"

# تحويل رابط Google Drive إلى رابط مباشر للتحميل
def convert_to_direct_download_url(url):
    if "drive.google.com" in url and "/file/d/" in url:
        file_id = url.split("/file/d/")[1].split("/view")[0]
        return f"https://drive.google.com/uc?id={file_id}&export=download"
    return url


# تحقق للحصول على التحديثات
def check_for_updates():
    if not is_internet_available():
        return None
    try:
        # تحميل ملف النسخة من الإنترنت
        response = requests.get(VERSION_URL,timeout=3)
        response.raise_for_status()
        version_info = response.json()

        # استخراج المعلومات من ملف JSON
        latest_version = version_info.get("version", "")
        download_url = version_info.get("download_url", "")
        description = version_info.get("description", "")

        # تحويل رابط التنزيل إلى رابط مباشر
        download_url = convert_to_direct_download_url(download_url)
        # مقارنة النسخة
        if latest_version > CURRENT_VERSION:

            formatted_description = "\n".join(f"{'- ' + item if item else ''}" for item in description)

            show_update_notification(latest_version,formatted_description, download_url)

    except requests.exceptions.Timeout:
        pass
        #QMessageBox.warning(self, "التحقق من وجود تحديثات", "لايوجد إتصال بالإنترنت.. تعذر البحث عن تحديثات.")
    except Exception as e:
        pass


# تحقق من وجود تحديثات pottom
def check_for_updates_pottom(self):
    if self.license_type  == "trial":
        reply = GEN_MSG_BOX("قيود النسخة التجريبية","هذه الميزة متوفرة في النسخة المدفوعة فقط.","license.png","شراء","إلغاء","#dfcab4")
        if reply != QMessageBox.Ok:
            return
        else:
            self.changing_activation_dialog()
            return
    #========================================================================
    try:
        # تحميل ملف النسخة من الإنترنت
        response = requests.get(VERSION_URL)
        response.raise_for_status()
        version_info = response.json()
        # استخراج المعلومات من ملف JSON
        latest_version = version_info.get("version", "")
        download_url = version_info.get("download_url", "")
        description = version_info.get("description", "")
        # تحويل رابط التنزيل إلى رابط مباشر
        download_url = convert_to_direct_download_url(download_url)
        # مقارنة النسخة
        if latest_version > CURRENT_VERSION:
            formatted_description = "\n".join(f"{'- ' + item if item else ''}" for item in description)
            show_update_notification(latest_version, formatted_description, download_url)
        else:
            QMessageBox.information(self, "التحقق من التحديثات", f"البرنامج محدث إلى آخر إصدار (الإصدار {CURRENT_VERSION}).")
    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"تحقق من الاتصال بالانترنت")


# def show_update_notification(latest_version, description, download_url):
#     # إنشاء الرسالة
#     msg = QMessageBox()
#     # تحميل الأيقونة المخصصة
#     icon_path = os.path.join(icons_dir, 'sync.png')
#     if os.path.exists(icon_path):
#         msg.setIconPixmap(QPixmap(icon_path))  # استخدام الأيقونة المخصصة

#     # إعدادات نافذة الرسالة
#     msg.setWindowTitle("تحديث جديد متاح")
#     msg.setWindowIcon(QIcon(icon_path))

#     # إعداد الخط المخصص
#     custom_font = QFont(font_app, 11)  # حدد نوع الخط والحجم
#     msg.setFont(custom_font)

#     # # النص الأساسي للإشعار
#     # main_text = (
#     #     f"<div style='text-align: center;'>"
#     #     f"<b>يوجد إصدار جديد للبرنامج</b><br><br>"
#     #     f"الإصدار الحالي: <b>( {CURRENT_VERSION} )</b><br>"
#     #     f"الإصدار الجديد: <b>( {latest_version} )</b>"
#     #     f"</div>"
#     # )
#     main_text = (
#         f"<div style='text-align: center;'>"
#         f"<b>يوجد إصدار جديد للبرنامج</b><br><br>"
#         f"<span style='display: inline-block; width: 150px; text-align: right;'>"
#         f"الإصدار الحالي:</span> <b>({CURRENT_VERSION})</b>"
#         f"&nbsp; | &nbsp;"
#         f"<span style='display: inline-block; width: 150px; text-align: left;'>"
#         f"الإصدار الجديد:</span> <b>({latest_version})</b>"
#         f"</div>"
#     )

#     msg.setText(main_text)

#     # النص الإضافي
#     #informative_text = f"<div style='text-align: center;'>التحديثات الجديدة:<br></div>"
#     msg.setInformativeText(f"\nالتحديثات الجديدة :\n{description}")

#     # أزرار النافذة
#     msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#     msg.button(QMessageBox.Ok).setText("تحديث الآن")
#     msg.button(QMessageBox.Cancel).setText("لاحقًا")

#     # انتظار النتيجة
#     result = msg.exec()
#     if result == QMessageBox.Ok:
#         download_update_with_progress(download_url)

# عرض إشعار التحديث
def show_update_notification(latest_version, description, download_url):
    dialog = QDialog()
    dialog.setWindowTitle("تحديث جديد متاح")

    icon_path = os.path.join(icons_dir, 'sync.png')
    if os.path.exists(icon_path):
        dialog.setWindowIcon(QIcon(icon_path))

    dialog.setMinimumSize(450, 350)
    dialog.resize(550, 600)

    layout = QVBoxLayout()

    # الأيقونة والنص الرئيسي
    if os.path.exists(icon_path):
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

    font = QFont(font_app, 11)

    main_text = (
        f"<div style='text-align: center;'>"
        f"<b>يوجد إصدار جديد للبرنامج</b><br><br>"
        f"<span style='display: inline-block; width: 150px; text-align: right;'>"
        f"الإصدار الحالي:</span> <b>({CURRENT_VERSION})</b>"
        f"&nbsp; | &nbsp;"
        f"<span style='display: inline-block; width: 150px; text-align: left;'>"
        f"الإصدار الجديد:</span> <b>({latest_version})</b>"
        f"</div>"
    )
    main_label = QLabel(main_text)
    main_label.setFont(font)
    main_label.setAlignment(Qt.AlignCenter)
    main_label.setWordWrap(True)
    layout.addWidget(main_label)

    # Scrollable description
    desc_area = QScrollArea()
    desc_area.setWidgetResizable(True)

    desc_widget = QWidget()
    desc_layout = QVBoxLayout(desc_widget)

    desc_label = QLabel(f"التحديثات الجديدة:\n{description}")
    desc_label.setFont(font)
    desc_label.setWordWrap(True)
    desc_layout.addWidget(desc_label)

    desc_area.setWidget(desc_widget)
    layout.addWidget(desc_area)

    # أزرار
    buttons_layout = QHBoxLayout()
    update_btn = QPushButton("تحديث الآن")
    later_btn = QPushButton("لاحقًا")

    buttons_layout.addWidget(update_btn)
    buttons_layout.addWidget(later_btn)
    layout.addLayout(buttons_layout)

    dialog.setLayout(layout)

    # الإجراءات
    update_btn.clicked.connect(lambda: (dialog.accept(), download_update_with_progress(download_url)))
    later_btn.clicked.connect(dialog.reject)

    dialog.exec()

# تنزيل
class DownloadThread(QThread):
    progress = Signal(int)
    speed = Signal(float)
    finished = Signal(str)
    error = Signal(str)
    # init
    def __init__(self, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.cancelled = False
    # يجري
    def run(self):
        try:
            # إنشاء مجلد التحديث إذا لم يكن موجودًا
            if not os.path.exists(update_folder):
                os.makedirs(update_folder)
            # تحديد اسم الملف ومساره
            file_name = "update_file.zip"
            file_path = os.path.join(update_folder, file_name)
            # تنزيل الملف
            with requests.get(self.download_url, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0
                start_time = time.time()
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.cancelled:
                            raise Exception("تم إلغاء التنزيل بواسطة المستخدم.")
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        # تحديث الإشارات
                        percentage = int((downloaded_size / total_size) * 100)
                        self.progress.emit(percentage)  # إرسال النسبة المئوية
                        elapsed_time = time.time() - start_time
                        speed_kbps  = downloaded_size / elapsed_time / 1024  # بالكيلوبايت/ثانية
                        self.speed.emit(speed_kbps)

                self.finished.emit(file_path)
        except Exception as e:
            self.error.emit(f"")


# تنزيل التحديث مع التقدم
def download_update_with_progress(download_url):
    dialog = DownloadDialog(download_url)
    dialog.exec()

# DownloadDialog
class DownloadDialog(QDialog):
    # init
    def __init__(self, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle("تنزيل التحديث")
        self.resize(400, 150)
        icon_path = os.path.join(icons_dir, 'icon_app.ico')
        self.setWindowIcon(QIcon(icon_path))
        # إعداد واجهة المستخدم
        self.layout = QVBoxLayout(self)
        self.label = QLabel("جاري تنزيل التحديث...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)  # تعيين الحد الأقصى إلى 100 (النسبة المئوية)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: rgba(236, 240, 241, 0.3);
                text-align: center;
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
                height: 25px;
                padding: 0px;
                margin: 0px 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.3 #2980b9,
                    stop:0.6 #16a085, stop:1 #2ecc71
                );
                border-radius: 10px;
                margin: 0px;
            }
        """)
        self.layout.addWidget(self.progress_bar)

        self.speed_label = QLabel("سرعة الإنترنت: 0 KB/s", self)
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 14px; margin-top: 5px;")
        self.layout.addWidget(self.speed_label)
        self.cancel_button = QPushButton("إلغاء التنزيل", self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 14px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.layout.addWidget(self.cancel_button)

        # تعديل حجم النافذة ليناسب المحتوى الجديد
        self.resize(450, 200)
        # بدء التحميل
        self.download_thread = DownloadThread(download_url)
        self.download_thread1 = UPDETThread(download_url)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.speed.connect(self.update_speed_label)  # تحديث عرض السرعة
        self.download_thread.finished.connect(self.handle_finished)
        self.download_thread.error.connect(self.handle_error)
        self.download_thread.start()

    #تحديث النص الخاص بسرعة الإنترنت.
    # تحديث تسمية السرعة
    def update_speed_label(self, speed):
        if speed >= 1024:  # إذا كانت السرعة أكبر من أو تساوي 1 ميجابايت/ثانية
            speed_text = f"سرعة الإنترنت: {speed / 1024:.2f} MB/s"
        else:
            speed_text = f"سرعة الإنترنت: {speed:.2f} KB/s"
        self.speed_label.setText(speed_text)

    # إلغاء التنزيل
    def cancel_download(self,download_url):
        self.download_thread.cancelled = True
        self.download_thread1.cancelled = True
        self.label.setText("تم إلغاء التنزيل.")

    # تعامل مع الانتهاء
    def handle_finished(self, file_path):
        self.extract_and_run(file_path)
        self.accept()

    #معالجة الأخطاء وإضافة خيار نسخ الرابط.
    # التعامل مع الخطأ
    def handle_error(self):
        msg_box = GEN_MSG_BOX("خطأ أثناء التنزيل",f"  خطأ أثناء التنزيل:\n"
                        f"يرجى التحقق من اتصالك بالإنترنت وإعادة المحاولة.\n","warning.png","إعادة المحاولة","إغلاق",msg_box_color)
        if msg_box != QMessageBox.Ok:
            self.reject()  # إغلاق النافذة
        else:
            self.retry_download()  # إعادة محاولة التنزيل


    # تحميل تنزيل
    def retry_download(self):
        try:
            # التأكد من إيقاف التحميل الحالي قبل البدء من جديد
            if hasattr(self, "download_thread") and self.download_thread.isRunning():
                self.download_thread.cancelled = True
                self.download_thread.quit()
                self.download_thread.wait()

            self.label.setText("جاري إعادة المحاولة...")
            self.download_thread1 = UPDETThread(self.download_url)
            self.download_thread1.progress.connect(self.progress_bar.setValue)
            self.download_thread1.speed.connect(self.update_speed_label)
            self.download_thread1.finished.connect(self.handle_finished)
            self.download_thread1.error.connect(self.handle_error)
            self.download_thread1.start()

        except RuntimeError as e:
            # إذا حدث خطأ أثناء تشغيل `QThread`، يتم إلغاء كل العمليات
            self.download_thread.cancelled = True
            self.download_thread1.cancelled = True

            QMessageBox.critical(self, "خطأ", f"فشل إعادة المحاولة: {str(e)}")

    # استخراج الملف المضغوط وتشغيل الملف الداخلي.
    def extract_and_run(self, archive_path):
        try:
            # مسار الاستخراج
            extract_path = os.path.join(update_folder, "extracted")

            # حذف مجلد extracted إذا كان موجود مسبقاً
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)

            # إنشاء مجلد extracted جديد
            os.makedirs(extract_path)
            # التحقق من نوع الملف (ZIP أو RAR)
            if archive_path.endswith(".zip"):
                # فك ضغط ملفات ZIP
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            else:
                raise Exception("الملف ليس بتنسيق ZIP أو RAR.")
            # التحقق من الملفات المستخرجة
            extracted_files = os.listdir(extract_path)
            print(f"الملفات المستخرجة: {extracted_files}")
            # البحث عن الملف التنفيذي
            for root, _, files in os.walk(extract_path):
                for file in files:
                    if file.endswith(".exe"):  # إذا كان الملف تنفيذي
                        msg_box = GEN_MSG_BOX("تثبيت التحديث",f"  تم تنزيل التحديث بنجاح \n سيتم إغلاق البرنامج لثتبيت التحديث.","sync.png","تثبيت التحديث","إغلاق التطبيق","green")
                        if msg_box != QMessageBox.Ok:
                            executable_path = os.path.join(root, file)
                            subprocess.Popen([executable_path], shell=True)
                            sys.exit()  # Exit the application
                            return
                        else:
                            executable_path = os.path.join(root, file)
                            subprocess.Popen([executable_path], shell=True)
                            sys.exit()  # Exit the application
                            return


            QMessageBox.warning(self, "خطأ", "لم يتم العثور على  ملف التثبيت.")
        except Exception as e:
            msg_box = GEN_MSG_BOX("خطأ تثبيت التحديث",f"حدث خطأ أثناء تثبيت التحديث:\nتحقق من إتصال الانترنت وأعد المحاولة","warning.png","إعادة المحاولة","إغلاق",msg_box_color)
            if msg_box != QMessageBox.Ok:
                self.reject()  # إغلاق النافذة
            else:
                self.reject()  # إغلاق النافذة
                download_update_with_progress(self.download_url)    # إعادة محاولة التنزيل

    #نسخ النص إلى الحافظة.
    # نسخ إلى الحافظة
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "نسخ الرابط", "تم نسخ الرابط إلى الحافظة.")
    
    

#كلاس اعادة المحاولة
# updetthread
class UPDETThread(QThread):
    progress = Signal(int)
    speed = Signal(float)
    finished = Signal(str)
    error = Signal(str)
    # init
    def __init__(self, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.cancelled = False

    # يجري
    def run(self):
        try:
            # إنشاء مجلد التحديث إذا لم يكن موجودًا
            if not os.path.exists(update_folder):
                os.makedirs(update_folder)
            # تحديد اسم الملف ومساره
            file_name = "update_file.zip"
            file_path = os.path.join(update_folder, file_name)
            # تحديد حجم التنزيل الذي تم
            downloaded_size = 0
            if os.path.exists(file_path):
                downloaded_size = os.path.getsize(file_path)
            # إرسال رأس التنزيل إذا كانت هناك بيانات تم تنزيلها مسبقًا
            headers = {"Range": f"bytes={downloaded_size}-"} if downloaded_size > 0 else {}
            with requests.get(self.download_url, headers=headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0)) + downloaded_size
                start_time = time.time()
                with open(file_path, "ab") as file:  # فتح الملف للإضافة
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.cancelled:
                            #return  # الخروج فورًا دون إثارة استثناء
                            raise Exception("تم إلغاء التنزيل بواسطة المستخدم.")
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        # تحديث الإشارات
                        percentage = int((downloaded_size / total_size) * 100)
                        self.progress.emit(percentage)  # إرسال النسبة المئوية
                        elapsed_time = time.time() - start_time
                        speed_kbps = downloaded_size / elapsed_time / 1024  # بالكيلوبايت/ثانية
                        self.speed.emit(speed_kbps)
                self.finished.emit(file_path)
        except Exception as e:
            self.error.emit(str(e))


# Closevent
def closeEvent(self, event):
    try:
        if hasattr(self, "download_thread") and self.download_thread.isRunning():
            self.download_thread.cancelled = True
            self.download_thread.quit()
            self.download_thread.wait()

        if hasattr(self, "download_thread1") and self.download_thread1.isRunning():
            self.download_thread1.cancelled = True
            self.download_thread1.quit()
            self.download_thread1.wait()

        event.accept()
    except Exception as e:
        QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء الإغلاق: {str(e)}")
        event.ignore()