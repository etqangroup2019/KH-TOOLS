from الدوال_الأساسية import*
from الإعدادات_العامة import*
# استرجاع آخر تاريخ تشغيل والتحقق من سلامته
# تحميل التاريخ الأخير
def load_last_date():
    # محاولة جلب القيم من الريجستري
    stored_date = settings.value(LAST_D, "")
    stored_hash = settings.value(HASH, "")
    # محاولة جلب القيم من الويندوز
    WIN_hash = get_security_key(LAST_D,LAST_D)
    # محاولة جلب القيم من ملف JSON
    json_date, json_hash = None, None
    if os.path.exists(last_date_path):
        try:
            with open(last_date_path, "r") as file:
                data = json.load(file)
                json_date = data.get(LAST_D, "")
                #json_hash = data.get(HASH, "")
                json_hash = data.get(HASH, "")
        except (json.JSONDecodeError, KeyError):
            return None
    # التحقق من أن كل القيم متاحة
    if not stored_date or not stored_hash or not WIN_hash or not json_date or not json_hash:
        return None
    # التحقق من تطابق التشفير
    if verify_signature(stored_date, stored_hash) and verify_signature(json_date, json_hash) and WIN_hash == stored_hash:
        return datetime.strptime(stored_date, "%Y-%m-%d")
    return None

# التحقق من التلاعب بالتاريخ   
# تحقق من الترخيص
def check_license(self):
    last_date = load_last_date()
    current_date = datetime.now()
    if last_date is None:
        tashfer()
        response = GEN_MSG_BOX(" خطأ في التاريخ",f"معلومات التاريخ غير مطابقة.","license.png","ترخيص جديد","خروج","#d9534f")
        if response == QMessageBox.Ok:
            self.show_activation_dialog()
            return False 
        else:
            sys.exit()
            return False
    elif last_date and current_date < last_date:
        tashfer()
        response = GEN_MSG_BOX(" تحذير خطأ في التاريخ",f"⚠ تم اكتشاف تلاعب في التاريخ! سيتم إيقاف النظام.","license.png","ترخيص جديد","خروج","#d9534f")
        if response == QMessageBox.Ok:
            self.show_activation_dialog()
            return False 
        else:
            sys.exit()
            return False
    # حفظ التاريخ الجديد إذا كان كل شيء طبيعي
    save_last_date()


# تحميل الواجهة التجريبية =====================================================================================
# loadDemoInterface
def loadDemoInterface(self, start_date, end_date):
    try:
        # التأكد من عدم التلاعب بالتاريخ أولًا
        check_license(self)  
        # تحويل التواريخ النصية إلى كائنات datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")  # أو استخدم التنسيق المناسب لتاريخك
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        # الحصول على التاريخ الحالي
        today_date = datetime.now()
        if start_date and end_date:
            # إذا كان التاريخ الحالي قبل تاريخ بداية النسخة التجريبية 
            if today_date < start_date:
                tashfer()
                response = GEN_MSG_BOX("التحقق من تاريخ بداية الترخيص","التاريخ الحالي غير صالح. يرجى تصحيح التاريخ في إعدادات النظام.\n يجب الاتصال بالانترنت ثم اضغط (التحقق) لidة التاريخ الصحيح","flexible.png","تحقق","خروج","#d9534f")
                if response == QMessageBox.Ok:
                    Check_computer_deta(self)
                    return None
                else:
                    sys.exit()

            # إذا كان التاريخ الحالي بين تاريخ البداية وتاريخ النهاية
            elif start_date <= today_date <= end_date:
                remaining_days = (end_date - today_date).days
                if remaining_days <= 3:
                    QMessageBox.warning(self, "انتهاء صلاحية الترخيص", f"متبقي {remaining_days} يوم على انتهاء صلاحية الترخيص.")
                return remaining_days  # إرجاع False إذا تم تجاوز الحد الأقصى
            
            # إذا كان التاريخ الحالي بعد تاريخ انتهائها
            elif today_date > end_date:
                tashfer()
                response = GEN_MSG_BOX("انتهاء مدة الترخيص","تم انتهاء الصلاحية الترخيص . يرجى ترقية الحساب.","license.png","ترخيص جديد","خروج","#d9534f")
                if response == QMessageBox.Ok:
                    self.show_activation_dialog()
                    return False 
                else:
                    sys.exit()
            else:
                tashfer()
                QMessageBox.critical(self, "خطأ", "التاريخ الحالي غير صالح. يرجى تصحيح التاريخ في إعدادات النظام.")
                sys.exit()
        else:
            QMessageBox.critical(self, "خطأ", "لا يوجد تاريخ صالح للفترة التجريبية.")
            return None  # إرجاع False إذا تم تجاوز الحد الأقصى
    except ValueError as e:
        tashfer()
        QMessageBox.critical(self, "خطأ", f"خطأ في تنسيق التواريخ: {str(e)}")
        sys.exit()

#وصول محدود ===================================================================================================
# الاتصال بقاعدة البيانات
# الاتصال بقاعدة البيانات
def connect_to_database(selected_year):
    selected_year = selected_year
    db_name = f"project_manager_V2"
    try:
        connection = mysql.connector.connect(host=host,user=user,password=password,database=db_name)
        return connection
    except mysql.connector.Error as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None
 
 
# تحقق وإضافة صف
def check_and_add_row(self,table_name, selected_year):
    connection = connect_to_database(selected_year)
    if not connection:
        return False  # إرجاع False إذا لم يتم الاتصال
    try:
        cursor = connection.cursor()
        # تحديد الحد الأقصى لكل جدول
        if table_name == "المشاريع":
            cursor.execute("SELECT COUNT(*) FROM المشاريع")
            max_rows = 10
        elif table_name == "الحسابات":
            cursor.execute("SELECT COUNT(*) FROM الحسابات")
            max_rows = 10
        elif table_name == "الموظفين":
            cursor.execute("SELECT COUNT(*) FROM الموظفين")
            max_rows = 2
        else:
            return False  # إرجاع False إذا لم يكن الجدول معروفاً
        
        count = cursor.fetchone()[0]  # الحصول على عدد الصفوف الحالي
        if count >= max_rows: 
            reply = GEN_MSG_BOX("قيود النسخة التجريبية",f"غير مسموح بإضافة المزيد من الصفوف\n الحد الأقصى للنسخة التجريبية هو {max_rows} معاملات.","license.png","شراء","إلغاء","#dfcab4")
            if reply != QMessageBox.Ok:
                return
            else:
                self.changing_activation_dialog()
                return          
        return True  # إرجاع True إذا كان من الممكن الإضافة
    except mysql.connector.Error as e:
        print(f"خطأ في تنفيذ العملية: {e}")
        return False
    finally:
        cursor.close()
        connection.close()
        


        

