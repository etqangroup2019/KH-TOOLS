
# cSpell:disable
from أزرار_الواجهة import*
from ستايل import*
from الإعدادات_العامة import*
from datetime import datetime

#-------------------------قاعدة البيانات الرئيسية- ----------------------
# إنشاء قاعدة بيانات إذا لم تكن موجودة
def create_database_if_not_exists(self):
        db_name = f"project_manager_V2"
        conn = None
        cursor = None
        try:
            conn = self.get_root_connection()
            if conn is None:
                return False
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{db_name}`")

            # إنشاء فهرس إن لم يكن موجودًا
            def create_index_if_not_exists(cursor, index_name, table_name, column_name):
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if not cursor.fetchone():
                    print(f"Table {table_name} does not exist. Skipping index creation.")
                    return # الجدول غير موجود، لا يمكن إنشاء الفهرس

                # Check if index exists using information_schema
                try:
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM INFORMATION_SCHEMA.STATISTICS
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s
                    """, (db_name, table_name, index_name))
                    if cursor.fetchone()[0] == 0:
                        try:
                            cursor.execute(f"CREATE INDEX `{index_name}` ON `{table_name}`(`{column_name}`)")
                            print(f"Index {index_name} created on {table_name}({column_name}).")
                        except mysql.connector.Error as e:
                             print(f"Warning: Could not create index {index_name} on {table_name}({column_name}): {e}")
                    # else:
                    #      print(f"Index {index_name} already exists on {table_name}. Skipping.")
                except mysql.connector.Error as e:
                     print(f"Warning: Could not check for index {index_name} existence: {e}")

            # إنشاء جدول السنوات المالية
            def انشاء_جداول_النظام(self):
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `إعدادات_الشركة` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `اسم_الشركة` VARCHAR(255) NOT NULL,
                        `1رقم_الهاتف` VARCHAR(50),
                        `2رقم_الهاتف` VARCHAR(50),
                        `العنوان` TEXT,
                        `الايميل` VARCHAR(255),
                        `نوع_العملة` VARCHAR(10) DEFAULT 'د.ل',
                        `اللوقو` LONGTEXT COMMENT 'مسار أو بيانات اللوقو',
                        `اللغة_الافتراضية` ENUM('العربية', 'English') DEFAULT 'العربية',
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `السنوات_المالية` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `السنة` INT NOT NULL UNIQUE,
                        `تاريخ_البداية` DATE NOT NULL,
                        `تاريخ_النهاية` DATE NOT NULL,
                        `حالة_السنة` ENUM('مفتوحة', 'مغلقة', 'مؤرشفة') NOT NULL DEFAULT 'مفتوحة',
                        `هي_السنة_الحالية` BOOLEAN NOT NULL DEFAULT FALSE,
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
                 
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الاقسام` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `اسم_القسم` VARCHAR(100) NOT NULL,
                    `وصف_القسم` VARCHAR(100) NOT NULL,

                    `حالة_التصنيف` ENUM('نشط', 'غير نشط') DEFAULT 'نشط',
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                             
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # جدول التصنيفات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `التصنيفات` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_القسم` VARCHAR(100) NOT NULL,
                    `اسم_التصنيف` VARCHAR(100) NOT NULL,
                    `لون_التصنيف` VARCHAR(20) DEFAULT '#3498db',
                    `الأيقونة` VARCHAR(50),
                    `وصف_التصنيف` TEXT, 
                    `حالة_التصنيف` ENUM('نشط', 'غير نشط') DEFAULT 'نشط',
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          
                    UNIQUE KEY `unique_section_category` (`اسم_القسم`, `اسم_التصنيف`),
                   
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS انواع_العمليات_المالية ( 
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    `معرف_القسم` INT DEFAULT NULL,
                    `نوع_العملية` ENUM('ايرادات','مصروفات') NOT NULL,
                    `اسم_العملية` VARCHAR(255) NOT NULL,
                    `الحالة` ENUM('نشط', 'غير نشط') DEFAULT 'نشط',
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (معرف_القسم) REFERENCES التصنيفات_المالية(id) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # جدول أسعار المراحل
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `اسعار_المراحل` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `اسم_القسم` ENUM('المشاريع', 'المقاولات') NOT NULL,
                    `معرف_التصنيف` INT NOT NULL,
                    `اسم_المرحلة` VARCHAR(250) NOT NULL,
                    `وصف_المرحلة` TEXT,
                    `الوحدة` VARCHAR(50) DEFAULT 'متر مربع',
                    `السعر` DECIMAL(10,2) NOT NULL DEFAULT 0,
                    `نشط` BOOLEAN DEFAULT TRUE,
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                    UNIQUE KEY `unique_phase_details` (`اسم_القسم`, `معرف_التصنيف`, `اسم_المرحلة`),
                    
                    FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
            
                # جدول مواعيد العمل للشركة
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `مواعيد_العمل` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `نوع_النظام` ENUM('فترة_واحدة', 'فترتين') DEFAULT 'فترة_واحدة',
                        -- الفترة الصباحية
                        `وقت_حضور_صباحي` TIME NOT NULL DEFAULT '08:00:00',
                        `وقت_انصراف_صباحي` TIME NOT NULL DEFAULT '17:00:00',

                        -- الفترة المسائية (اختيارية)
                        `وقت_حضور_مسائي` TIME DEFAULT NULL,
                        `وقت_انصراف_مسائي` TIME DEFAULT NULL,
                               
                        -- أيام العمل
                        `أيام_العمل` JSON DEFAULT '{"الأحد": true, "الاثنين": true, "الثلاثاء": true, "الأربعاء": true, "الخميس": true, "الجمعة": false, "السبت": false}',
                               
                        -- فترة التأخير المسموحة (بالدقائق)
                        `فترة_التأخير_المسموحة` INT DEFAULT 15,
                        `فترة_المغادرة_المبكرة` INT DEFAULT 0,        
                        `ساعات_العمل_اليومية` DECIMAL(4,2) DEFAULT 8.0,
                               
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
                
                # جدول حسابات البنوك
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حسابات_البنوك` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `اسم_البنك` VARCHAR(100) NOT NULL,
                        `رقم_الحساب` VARCHAR(50) NOT NULL,
                        `حساب_رئيسي`BOOLEAN DEFAULT FALSE,
                        `معرف_الحساب_الرئيسي`BOOLEAN DEFAULT FALSE,
                        `الرصيد_الافتتاحي` DECIMAL(10,2) DEFAULT 0,
                        `الحالة` ENUM('نشط', 'غير نشط') DEFAULT 'نشط',
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY `unique_bank_account` (`اسم_البنك`, `رقم_الحساب`)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)


            def انشاء_جداول_الأشخاص(self):
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الأشخاص` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `نوع_الحساب` ENUM('موظف','مورد','متدرب','عميل','ديون','أخرى') NOT NULL,
                        `معرف_التصنيف` INT NOT NULL,
                        `الاسم` VARCHAR(255) NOT NULL,
                        `العنوان` VARCHAR(255),
                        `رقم_الهاتف` VARCHAR(50),
                        `الايميل` VARCHAR(100),
                        `تاريخ_الإنشاء` DATE,
                        `ملاحظات` VARCHAR(255),                  
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,         
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,       
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)

                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حسابات_العملاء` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الشخص`INT PRIMARY KEY,                     
                        `عدد_المشاريع` INT DEFAULT 0,
                        `اجمالي_المبلغ` DECIMAL(10,2) DEFAULT 0,
                        `اجمالي_المدفوعات` DECIMAL(10,2) DEFAULT 0,
                        `إجمالي_الباقي` DECIMAL(10,2) GENERATED ALWAYS AS (`اجمالي_المبلغ` - `اجمالي_المدفوعات`) STORED,
                        `الحالة` ENUM('نشط','غير نشط') DEFAULT 'نشط',
                
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,         
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,  

                        FOREIGN KEY (معرف_الشخص) REFERENCES الأشخاص(id) ON DELETE CASCADE     
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)

                

                        
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حسابات_الديون` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الشخص`INT PRIMARY KEY,
                                    
                        `اجمالي_الدين` DECIMAL(10,2) DEFAULT 0,
                        `الرصيد_الحالي` DECIMAL(10,2) DEFAULT 0,
                        `الحالة` ENUM('نشط','غير نشط') DEFAULT 'نشط',
                                                                                 
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,        
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,  
                        FOREIGN KEY (معرف_الشخص) REFERENCES الأشخاص(id) ON DELETE CASCADE     
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                      
            def انشاء_جداول_الموظفين(self):

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حسابات_الموظفين` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الشخص`INT PRIMARY KEY,
                        `الوظيفة` VARCHAR(255),
                        `المرتب` DECIMAL(10,2),
                        `النسبة` DECIMAL(5,2),
                        `الرصيد` DECIMAL(10,2) DEFAULT 0,
                        `الحالة` ENUM('مستقيل', 'تم فصله','إجازة', 'غير نشط', 'نشط') NOT NULL DEFAULT 'نشط',
                        `جدولة_المرتب_تلقائية` BOOLEAN DEFAULT FALSE,
                        `خاضع_لنظام_الحضور_والانصراف` BOOLEAN DEFAULT TRUE,
                                             
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,         
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,  

                        FOREIGN KEY (معرف_الشخص) REFERENCES الأشخاص(id) ON DELETE CASCADE     
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)

                # تقييم الموظفين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الموظفين_التقييم` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الموظف` INT,
                        `معرف_المهمة` INT, 
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإضافة`)) STORED,
                        
                        CONSTRAINT `fk_الموظفين_التقييم_معرف_المهندس`
                        FOREIGN KEY (`معرف_الموظف`)
                        REFERENCES `الموظفين`(`id`)
                        ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # جدول حضور وانصراف الموظفين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الموظفين_الحضور_والانصراف` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الموظف` INT NOT NULL,
                        `التاريخ` DATE NOT NULL,
                        `وقت_الحضور` TIME,
                        `حالة_الحضور` VARCHAR(255) DEFAULT NULL,
                        `وقت_الانصراف` TIME,
                        `حالة_الانصراف` VARCHAR(255) DEFAULT NULL,                          
                        `ملاحظات` TEXT,
        
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,   

                        CONSTRAINT `fk_الحضور_والانصراف_الموظف`
                        FOREIGN KEY (`معرف_الموظف`)
                        REFERENCES `الموظفين`(`id`)
                        ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

            def انشاء_جداول_المشاريع(self):
                # المشاريع------------------------------------------
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `المشاريع` (
                        `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                        `اسم_القسم` ENUM('المشاريع', 'المقاولات') DEFAULT 'المشاريع',
                        `التصنيف` VARCHAR(255),
                        `معرف_العميل` INT,
                        `معرف_المهندس` INT DEFAULT NULL,

                        `اسم_المشروع` VARCHAR(255),
                        `وصف_المشروع` TEXT,
                        `المساحة` VARCHAR(255),

                        `المبلغ` DECIMAL(10,2),
                        `المدفوع` DECIMAL(10,2) DEFAULT 0,
                        `الباقي` DECIMAL(10,2) GENERATED ALWAYS AS (`المبلغ` - `المدفوع`) STORED,

                        `تاريخ_الإستلام` DATE,
                        `تاريخ_التسليم` DATE,
                        `الوقت_المتبقي` VARCHAR(255),
                        `الحالة` ENUM('معلق ', 'منتهي', 'تم التسليم', 'متوقف', 'إنتظار التسليم', 'قيد الإنجاز') NOT NULL DEFAULT 'قيد الإنجاز',
                        `ملاحظات` TEXT,

                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التسليم`)) STORED,

                        CONSTRAINT fk_العميل FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE CASCADE

                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
                         
                # مراحل المشروع
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `المشاريع_المراحل` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_المشروع` INT,
                        `اسم_المرحلة` VARCHAR(255),
                        `وصف_المرحلة` VARCHAR(255),
                        `الوحدة` VARCHAR(255),
                        `الكمية` INT,
                        `السعر` DECIMAL(10,2),
                        `الإجمالي` DECIMAL(10,2) GENERATED ALWAYS AS (`الكمية` * `السعر`) STORED,
                        `حالة_المبلغ` ENUM('غير مدرج', 'تم الإدراج') NOT NULL DEFAULT 'غير مدرج',
                        `ملاحظات` TEXT,

                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإضافة`)) STORED,

                        CONSTRAINT `fk_مرحلة_معرف_المشروع`
                        FOREIGN KEY (`معرف_المشروع`)
                        REFERENCES `المشاريع`(`id`)
                        ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # جدول الربط مشاريع_مراحل_مهندسين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `المشاريع_مهام_الفريق` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الموظف` INT NOT NULL,
                        `نوع_المهمة` ENUM('مهمة عامة','مهمة تدريب','مهمة مشروع','مهمة مقاولات') NOT NULL DEFAULT 'مهمة عامة',
                        `معرف_القسم` INT NULL,                     
                        `نوع_دور_المهمة` ENUM('ربط_بمرحلة', 'دور_عام') DEFAULT 'دور_عام',               
                        `معرف_المرحلة` INT NULL,                    
                        `عنوان_المهمة` VARCHAR(255) NULL,
                        `وصف_المهمة` TEXT, 

                        -- ===== Financial Information (for project/contract tasks) =====
                        `نسبة_الموظف` DECIMAL(5,2) DEFAULT NULL,
                        `مبلغ_الموظف` DECIMAL(10,2) DEFAULT NULL,
                        `حالة_مبلغ_الموظف` ENUM('غير مدرج', 'تم الإدراج') DEFAULT 'غير مدرج',

                        -- ===== Task Scheduling =====
                        `تاريخ_البدء` DATE,
                        `تاريخ_الانتهاء` DATE,
                        `الحالة` ENUM('قيد التنفيذ', 'مكتملة', 'ملغاة', 'متأخرة','لم يبدأ', 'متوقف') NOT NULL DEFAULT 'لم يبدأ',

                        `ملاحظات` TEXT,

                        -- ===== System Fields =====
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(COALESCE(`تاريخ_البدء`, `تاريخ_الإضافة`))) STORED,

                        -- ===== Foreign Key Constraints =====
                        CONSTRAINT `fk_مهام_موحدة_معرف_الموظف`
                            FOREIGN KEY (`معرف_الموظف`)
                            REFERENCES `الموظفين`(`id`)
                            ON DELETE CASCADE,

                        CONSTRAINT `fk_مهام_موحدة_ممعرف_القسم`
                            FOREIGN KEY (`معرف_القسم`)
                            REFERENCES `المشاريع`(`id`)
                            ON DELETE CASCADE,

                        CONSTRAINT `fk_مهام_موحدة_معرف_المرحلة`
                            FOREIGN KEY (`معرف_المرحلة`)
                            REFERENCES `المشاريع_المراحل`(`id`)
                            ON DELETE CASCADE

                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                # العهد المالية المقاولات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `المقاولات_العهد` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_المشروع` INT NOT NULL,    
                        `رقم_العهدة` VARCHAR(50),       
                        `وصف_العهدة` VARCHAR(50),
                        `مبلغ_العهدة` DECIMAL(15,2) NOT NULL,
                        `نسبة_المكتب` DECIMAL(5,2) DEFAULT 0,
                        `تاريخ_الإستلام` DATE NOT NULL,
                        `حالة_العهدة` ENUM('مفتوحة', 'مغلقة', 'مرحلة') DEFAULT 'مفتوحة',
                        `ملاحظات` TEXT,
                                                
                        `مبلغ_نسبة_المكتب` DECIMAL(15,2) GENERATED ALWAYS AS (`مبلغ_العهدة` * `نسبة_المكتب` / 100) STORED,
                    
                        `المصروف` DECIMAL(15,2) DEFAULT 0,
                        `مبلغ_المكتب_من_المصروف` DECIMAL(15,2) GENERATED ALWAYS AS (`المصروف` * `نسبة_المكتب` / 100) STORED,
                        `مبلغ_نسبة_المكتب_من_المصروف` DECIMAL(15,2) GENERATED ALWAYS AS (
                            CASE 
                                WHEN `المصروف` = 0 THEN `مبلغ_نسبة_المكتب`
                                ELSE (`المصروف` * `نسبة_المكتب` / 100)
                            END
                        ) STORED,

                        `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`مبلغ_العهدة` - `مبلغ_المكتب_من_المصروف`-`المصروف`) STORED,
                            
                        `تاريخ_الإغلاق` DATE NULL,                           
                        `معرف_العهدة_السابقة` INT NULL,
                        `مبلغ_مرحل_من_السابقة` DECIMAL(15,2) DEFAULT 0,
        
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT,

                        CONSTRAINT `fk_العهد_المالية_معرف_المقاولات`
                        FOREIGN KEY (`معرف_المشروع`)
                        REFERENCES `المشاريع`(`id`)
                        ON DELETE CASCADE,

                        CONSTRAINT `fk_العهد_المالية_معرف_العهدة_السابقة`
                        FOREIGN KEY (`معرف_العهدة_السابقة`)
                        REFERENCES `المقاولات_العهد`(`id`)
                        ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
                
                # جدول مرفقات وملفات المشروع
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `المشاريع_مرفقات` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_المشروع` INT NOT NULL,
                        `اسم_الملف` VARCHAR(255) NOT NULL,
                        `نوع_الملف` VARCHAR(50) NOT NULL,
                        `الوصف` TEXT NULL,
                        `المسار` VARCHAR(500) NOT NULL,
                        `حجم_الملف` BIGINT NOT NULL DEFAULT 0,
                        `المستخدم` VARCHAR(50),
    
                        CONSTRAINT `fk_مرفقات_المشاريع_معرف_المشروع`
                        FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

            def انشاء_جداول_الموردين(self):

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حسابات_الموردين` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الشخص`INT PRIMARY KEY,
                        `اجمالي_التوريد` DECIMAL(10,2) DEFAULT 0,
                        `الرصيد` DECIMAL(10,2) DEFAULT 0,
                        `الحالة` ENUM('غير نشط', 'نشط') NOT NULL DEFAULT 'نشط',
                                             
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,         
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,   

                        FOREIGN KEY (معرف_الشخص) REFERENCES الأشخاص(id) ON DELETE CASCADE    
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `فواتير_الموردين` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الشخص` INT,
                        `رقم_الفاتورة` VARCHAR(255) ,
                        `وصف_الفاتورة` VARCHAR(255),      
                        `المبلغ` DECIMAL(10,2),
                        `التاريخ` DATE,
                        `ملاحظات` TEXT,
                            
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)


            def انشاء_جداول_الديون(self):
                # سجل الديون
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الحسابات_سجل_الديون` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الحساب` INT,
                        `وصف _الدين` VARCHAR(255),
                        `تاريخ _الدين` DATE,
                        `المبلغ` DECIMAL(10,2),
                        `تاريخ_السداد` DATE,
                        `تذكير_بموعد_السداد` ENUM('نعم', 'لا') DEFAULT 'لا',
                        `حالة_الدين` ENUM("معلق", "غير مسدد", "مسدد") NOT NULL DEFAULT 'معلق',
                        `ملاحظات` TEXT
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                
            def انشاء_جداول_التدريب(self):
                #التدريب-------------------------------------
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `التدريب` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `التصنيف` VARCHAR(255),
                        `عنوان_الدورة` VARCHAR(255),
                        `التكلفة` DECIMAL(10,2),
                        `معرف_المدرب` INT,
                        `عدد_المشتركين_المطلوب` INT DEFAULT 0,
                        `اجمالي_المدفوعات` DECIMAL(10,2) DEFAULT 0,
                        `إجمالي_الباقي` DECIMAL(10,2),
                        `تاريخ_البدء` DATE,
                        `تاريخ_الإنتهاء` DATE,
                        `الحالة` ENUM('معلق ', 'ملغاه', 'منتهية','جارية', 'قيد التسجيل') NOT NULL DEFAULT 'قيد التسجيل',
                        `ملاحظات` TEXT,
                            
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإنتهاء`)) STORED,
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # المجموعات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `التدريب_المجموعات` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الدورة` INT,
                        `اسم المجموعه` VARCHAR(255),
                        `التوقيت` VARCHAR(255),
                        `العدد_المطلوب` INT,
                        `عدد_المشتركين` INT,
                        `الحالة` ENUM('مكتمل', 'غير مكتمل') NOT NULL DEFAULT 'غير مكتمل',
                        `ملاحظات` TEXT
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
 
            def انشاء_جداول_العمليات_المالية (self):
                cursor.execute("""          
                    CREATE TABLE IF NOT EXISTS `الايرادات` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,   
                        `معرف_القسم` INT NOT NULL COMMENT 'المشاريع مقاولات، تدريب، موظفين، موردين، الديون ، إلخ',
                        `معرف_الحساب` INT NULL COMMENT 'العهدة,الموظف,المورد,المتدرب,العهدة,العميل,المشروع,الدورة',
                        `معرف_العملية` INT NULL COMMENT 'دفعة مشروع', 'دفعة مقاولات', 'دفعة عهدة مالية', 'دفعة متدرب, 'خصم موظف', 'مردودات مورد', '',
                                             
                        `المبلغ` DECIMAL(15,2) NOT NULL,
                        `الوصف` TEXT NOT NULL COMMENT 'وصف تفصيلي للمعاملة، مثل: استلام دفعة من مشروع X',
                        `تاريخ_المعاملة` DATE NOT NULL,
                        `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل بنكي') DEFAULT 'نقدي',
                        `خصم` DECIMAL(10,2),
                               
                        `رقم_المرجع_الخارجي` VARCHAR(100) NULL COMMENT 'رقم الفاتورة أو الإيصال أو الشيك',
                        `معرف_البنك` INT NULL COMMENT 'البنك',
                        `المسؤول` VARCHAR(255) NULL,
                        `ملاحظات` TEXT,
                               
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المعاملة`)) STORED,

                        FOREIGN KEY (`معرف_الالتزام`) REFERENCES `الالتزامات_المالية`(`id`) ON DELETE SET NULL,
                        FOREIGN KEY (`معرف_الشخص`) REFERENCES `الأشخاص`(`id`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                cursor.execute("""          
                    CREATE TABLE IF NOT EXISTS `المصروفات` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,  
                        `معرف_القسم` INT NOT NULL COMMENT 'مشاريع، مقاولات، تدريب، موظفين، موردين، إدارة، إلخ',
                        `معرف_الحساب` INT NULL COMMENT 'معرف الشخص',
                        `معرف_الجهة` INT NULL COMMENT 'معرف المصدر المرتبط بالعملية (مثل معرف_المشروع)',
                        `معرف_العملية` INT NULL COMMENT 'دفعة مشروع', 'دفعة مقاولات', 'دفعة عهدة مالية', 'دفعة متدرب','مصروف عام', 'مبلغ موظف','رواتب', 'مصاريف مشاريع', 'مصاريف تدريب',
                                                       
                        `المبلغ` DECIMAL(15,2) NOT NULL,
                        `الوصف` TEXT NOT NULL COMMENT 'وصف تفصيلي للمعاملة، مثل: استلام دفعة من مشروع X',
                        `تاريخ_المعاملة` DATE NOT NULL,
                        `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل بنكي') DEFAULT 'نقدي',
                        `خصم` DECIMAL(10,2),
                               
                        `رقم_المرجع_الخارجي` VARCHAR(100) NULL COMMENT 'رقم الفاتورة أو الإيصال أو الشيك',
                        `معرف_البنك` INT NULL COMMENT 'البنك',
                        `المسؤول` VARCHAR(255) NULL,
                        `ملاحظات` TEXT,
                               
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المعاملة`)) STORED,

                        FOREIGN KEY (`معرف_الالتزام`) REFERENCES `الالتزامات_المالية`(`id`) ON DELETE SET NULL,
                        FOREIGN KEY (`معرف_الشخص`) REFERENCES `الأشخاص`(`id`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
                
                # جدول مصروفات المشروع
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `المقاولات_مصروفات_العهد` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_المشروع` INT NOT NULL,
                        `نوع_المصروف` ENUM('مرتبط_بعهدة', 'غير_مرتبط_بعهدة','خسائر','مردودات') NOT NULL DEFAULT 'غير_مرتبط_بعهدة',
                        `معرف_العهدة` INT NULL,                        
                        `المورد` VARCHAR(255),
                        -- حقول جديدة للخسائر والمردودات
                        `متحمل_الخسائر` ENUM('الشركة', 'مهندس', 'مقاول', 'عامل', 'موظف') NULL,
                        `معرف_المتحمل` INT NULL COMMENT 'معرف الموظف المتحمل للخسائر',
                        `معرف_العهدة_المردودة` INT NULL COMMENT 'معرف العهدة للمردودات',
                """)

                # معاملات مالية الموظفين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الموظفين_معاملات_مالية` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الموظف` INT,  
                        `نوع_العملية` ENUM('إيداع','سحب','خصم' ) NOT NULL,   
                        `نوع_المعاملة` ENUM('إيداع مرتب','إيداع مبلغ','إيداع نسبة%','سحب مبلغ','خصم مبلغ','خصم نسبة%') NOT NULL,     
                        `النسبة` DECIMAL(10,2) DEFAULT 0,  
                """)
                

            def انشاء_جداول_الاتزامات (self):

                # 3. جدول الالتزامات المالية والديون (معدل)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الالتزامات_المالية` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                               
                        `نوع_الالتزام` ENUM('التزام على الشركة', 'التزام للشركة') NOT NULL,

                        `معرف_القسم` INT NOT NULL COMMENT 'مشاريع، مقاولات، تدريب، موظفين، موردين، إدارة، إلخ',
                        `معرف_الحساب` INT NULL COMMENT 'العهدة، الموظف، المورد، المتدرب، العميل، المشروع',
                        `معرف_الجهة` INT NULL COMMENT 'لو مرتبط بمشروع أو جهة معينة',
                        `معرف_العملية` INT NULL COMMENT ''دين على الشركة', 'دين للشركة', 'التزام مالي', 'عهدة مالية','راتب موظف','مبلغ موظف','التزام لمورد'',

                        `الوصف` TEXT NOT NULL COMMENT 'تفاصيل الالتزام مثل: دين لمورد X أو عهدة لموظف Y',
                        `مبلغ_الالتزام` DECIMAL(15,2) NOT NULL,

                        `تاريخ_الالتزام` DATE NOT NULL,
                        `تاريخ_الاستحقاق` DATE NULL,
                        `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل بنكي') DEFAULT 'نقدي',
                        `رقم_المرجع_الخارجي` VARCHAR(100) NULL COMMENT 'رقم فاتورة، شيك، أو حوالة',
                        `معرف_البنك` INT NULL COMMENT 'البنك',

                        `حالة_الالتزام` ENUM('معلق','غير مسدد','مسدد','متأخر','مسدد جزئي') DEFAULT 'معلق',
                        `المسؤول` VARCHAR(255) NULL,
                        `ملاحظات` TEXT,

                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الالتزام`)) STORED,

                        FOREIGN KEY (`معرف_الحساب`) REFERENCES `الأشخاص`(`id`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)


                # 3. جدول الالتزامات المالية والديون
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الالتزامات_المالية` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `نوع_الالتزام` ENUM('دين على الشركة', 'دين للشركة', 'التزام مالي', 'عهدة مالية','راتب موظف','مبلغ موظف','التزام لمورد') NOT NULL,
                        `معرف_الشخص` INT NULL,
                        `معرف_مرجع` INT NULL, -- لو مرتبط بمشروع معين
                        `الوصف` TEXT NOT NULL,
                        `المبلغ_الأصلي` DECIMAL(15,2) NOT NULL,
                        `المدفوع` DECIMAL(15,2) DEFAULT 0,
                        `الباقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ_الأصلي` - `المدفوع`) STORED,
                        `تاريخ_الالتزام` DATE NOT NULL,
                        `تاريخ_الاستحقاق` DATE NULL,
                        `حالة_الالتزام` ENUM('معلق','غير مسدد','مسدد','متأخر','مسدد جزئي') DEFAULT 'معلق',
                        `ملاحظات` TEXT,
                               
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الالتزام`)) STORED,
                               
                        FOREIGN KEY (`معرف_الشخص`) REFERENCES `الأشخاص`(`id`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # سداد الديون
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `الحسابات_سجل_سداد_الديون` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الحساب` INT,
                        `نوع_السداد` ENUM('سداد عام', 'مرتبط بسجل دين') NOT NULL DEFAULT 'سداد عام',
                        `معرف_سجل_الدين` INT DEFAULT NULL,
                        
                """)

                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حسابات_المتدربين` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الشخص`INT PRIMARY KEY,

                        `معرف_الدورة` INT NOT NULL,
                        `معرف_المجموعة` INT DEFAULT NULL,

                        
                        `الخصم` DECIMAL(10,2) DEFAULT 0,
                        `اجمالي_المدفوعات` DECIMAL(10,2) DEFAULT 0,
                        `إجمالي_الباقي` DECIMAL(10,2) GENERATED ALWAYS AS (`اجمالي_المبلغ` - `اجمالي_المدفوعات` - `الخصم`) STORED,
                        `الحالة` ENUM('مسجل', 'منسحب', 'مكتمل') DEFAULT 'مسجل',
            
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,       
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED, 

                        FOREIGN KEY (معرف_الشخص) REFERENCES الأشخاص(id) ON DELETE CASCADE      
                        
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
            def انشاء_جداول_المحاسبة (self):
                #جداول المحاسبة-------------------------------------
                # إنشاء جدول القيود المحاسبية
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `القيود_المحاسبية` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `رقم_القيد` VARCHAR(50) NOT NULL,
                        `التاريخ` DATE NOT NULL,
                        `البيان` VARCHAR(255) NOT NULL,
                        `الحساب_المدين` VARCHAR(10) NOT NULL,
                        `الحساب_الدائن` VARCHAR(10) NOT NULL,
                        `المبلغ` DECIMAL(15,2) NOT NULL,
                        `نوع_القيد` ENUM('يدوي', 'تلقائي', 'تسوية') DEFAULT 'تلقائي',
                        `نوع_المعاملة` VARCHAR(50),
                        `معرف_المعاملة` INT,
                        `المرجع` VARCHAR(100),
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # إنشاء جدول شجرة الحسابات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `شجرة_الحسابات` (
                        `معرف_الحساب` VARCHAR(10) PRIMARY KEY,
                        `اسم_الحساب` VARCHAR(255) NOT NULL,
                        `نوع_الحساب` ENUM('أصول', 'خصوم', 'حقوق الملكية', 'إيرادات', 'مصروفات') NOT NULL,
                        `الحساب_الأب` VARCHAR(10) NULL,
                        `مستوى_الحساب` TINYINT NOT NULL DEFAULT 1 CHECK (`مستوى_الحساب` BETWEEN 1 AND 5),
                        `حالة_الحساب` ENUM('نشط', 'غير نشط') NOT NULL DEFAULT 'نشط',
                        `وصف_الحساب` TEXT,
                        `رقم_الترتيب` INT DEFAULT 0,
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (`الحساب_الأب`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # إنشاء جدول أرصدة الحسابات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `أرصدة_الحسابات` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الحساب` VARCHAR(10) NOT NULL,
                        `الرصيد_المدين` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                        `الرصيد_الدائن` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                        `صافي_الرصيد` DECIMAL(15,2) GENERATED ALWAYS AS (`الرصيد_المدين` - `الرصيد_الدائن`) STORED,
                        `السنة_المالية` INT NOT NULL,
                        `تاريخ_آخر_تحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY `unique_account_year` (`معرف_الحساب`, `السنة_المالية`),
                        
                        FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # إنشاء جدول حركات الحسابات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `حركات_الحسابات` (
                        `معرف_الحركة` INT PRIMARY KEY AUTO_INCREMENT,
                        `معرف_الحساب` VARCHAR(10) NOT NULL,
                        `تاريخ_الحركة` DATE NOT NULL,
                        `وصف_الحركة` VARCHAR(255) NOT NULL,
                        `المبلغ_المدين` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                        `المبلغ_الدائن` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                        `رقم_المرجع` VARCHAR(100),
                        `نوع_الحركة` ENUM('قيد افتتاحي', 'قيد يومي', 'قيد تسوية', 'قيد إقفال') NOT NULL DEFAULT 'قيد يومي',
                        `معرف_القيد` INT,
                        `مركز_التكلفة` VARCHAR(10),
                        `ملاحظات` TEXT,
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الحركة`)) STORED,
                        
                        FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE CASCADE,
                        FOREIGN KEY (`معرف_القيد`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)

                # إنشاء جدول مراكز التكلفة
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `مراكز_التكلفة` (
                        `معرف_مركز_التكلفة` VARCHAR(10) PRIMARY KEY,
                        `اسم_مركز_التكلفة` VARCHAR(255) NOT NULL,
                        `وصف_مركز_التكلفة` TEXT,
                        `حالة_المركز` ENUM('نشط', 'غير نشط') NOT NULL DEFAULT 'نشط',
                        `نوع_المركز` ENUM('إنتاجي', 'خدمي', 'إداري') NOT NULL DEFAULT 'إنتاجي',
                        `المركز_الأب` VARCHAR(10) NULL,
                        `رقم_الترتيب` INT DEFAULT 0,
                        `المستخدم` VARCHAR(50),
                        `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                        `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (`المركز_الأب`) REFERENCES `مراكز_التكلفة`(`معرف_مركز_التكلفة`) ON DELETE SET NULL
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)


            # ========================
            # إنشاء الفهارس (بعد إنشاء الجداول)
            create_index_if_not_exists(cursor, 'idx_المشاريع_التصنيف', 'المشاريع', 'التصنيف')

            # إدراج بعض التصنيفات الافتراضية
            default_categories = [
                # تصنيفات المشاريع
                ("المشاريع", "تصميم معماري", "#3498db", "تصميم المباني والمنشآت المعمارية"),
                ("المشاريع", "تصميم داخلي", "#9b59b6", "تصميم الديكور والتصميم الداخلي"),
                ("المشاريع", "تحوير خريطة", "#8b4513", "أعمال المقاولات والتنفيذ"),
                ("المشاريع", "إعداد مقايسات", "#e67e22", "إعداد المقايسات والتكاليف"),
                

                # تصنيفات العملاء
                ("العملاء", "مواطن", "#27ae60", "عملاء أفراد"),
                ("العملاء", "شركة خاصة", "#2980b9", "شركات خاصة"),
                ("العملاء", "مؤسسة حكومية", "#6d3d8a", "مؤسسات حكومية"),
                ("العملاء", "مكتب هندسي", "#16a085", "مكاتب هندسية"),
                ("العملاء", "مهندس", "#1d1599", "مهندسين أفراد"),

                # تصنيفات الحسابات
                ("الحسابات", "مصاريف إدارية", "#e74c3c", "المصاريف الإدارية العامة"),
                ("الحسابات", "مصاريف تشغيلية", "#f39c12", "مصاريف التشغيل اليومي"),
                ("الحسابات", "مصاريف مشاريع", "#3498db", "مصاريف خاصة بالمشاريع"),
                ("الحسابات", "مصاريف تسويق", "#9b59b6", "مصاريف التسويق والإعلان"),
                ("الحسابات", "مصاريف صيانة", "#73b659", "مصاريف صيانة وتطوير"),

                # تصنيفات الموظفين
                ("الموظفين", "مدير", "#19b7d3", "مدير قسم او عام في الشركة"),
                ("الموظفين", "موظف", "#1d77b3", "موظف عام في الشركة"),
                ("الموظفين", "مهندس", "#27ae60", "مهندس متخصص"),
                ("الموظفين", "مقاول", "#f39c12", "مقاول أعمال"),
                ("الموظفين", "عامل", "#bba55b", "عامل تنفيذ"),
                ("الموظفين", "مدرب", "#9b59b6", "مدرب قسم الدورات"),
                ("الموظفين", "متعاون", "#e74c3c", "متعاون خارجي"),

                
                # تصنيفات التدريب
                ("التدريب", "دورة هندسية", "#3498db", "دورات تدريبية هندسية"),
                ("التدريب", "دورة تقنية", "#e67e22", "دورات تقنية متخصصة"),
                ("التدريب", "ورشة عمل", "#9b59b6", "ورش عمل تطبيقية"),

                # تصنيفات المقاولات
                ("المقاولات", "تأسيس وتشطيب", "#3498db", "أعمال التنفيذ والبناء العامة"),
                ("المقاولات", "بناء عظم", "#73b659", "أعمال البناء والهيكل الأساسي"),
                ("المقاولات", "تشطيب", "#9b59b6", "أعمال التشطيب والديكور"),
                ("المقاولات", "إشراف هندسي", "#f39c12", "الإشراف الهندسي على المقاولات"),
                ("المقاولات", "مقاولات عامة", "#bba55b", "مقاولات عامة متنوعة"),
                ("المقاولات", "صيانة وترميم", "#e74c3c", "أعمال الصيانة والترميم"),
            ]

            for section, category, color, description in default_categories:
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO التصنيفات
                        (اسم_القسم, اسم_التصنيف, لون_التصنيف, وصف_التصنيف)
                        VALUES (%s, %s, %s, %s)
                    """, (section, category, color, description))
                except Exception as e:
                    print(f"تحذير: لم يتم إدراج التصنيف {category}: {e}")

            # إدراج أسعار المراحل الافتراضية
            # default_phases = [
            #     # مراحل المشاريع المعمارية
            #     ("المشاريع", "تصميم معماري", "رسم المخططات المعمارية", "متر مربع", 50.00),
            #     ("المشاريع", "تصميم معماري", "إعداد الواجهات", "متر مربع", 30.00),
            #     ("المشاريع", "تصميم معماري", "إعداد المقاطع", "مقطع", 200.00),
            #     ("المشاريع", "تصميم إنشائي", "حساب الأحمال", "متر مربع", 25.00),
            #     ("المشاريع", "تصميم إنشائي", "تصميم الأساسات", "متر مربع", 40.00),
            #     ("المشاريع", "تصميم إنشائي", "تصميم الأعمدة والجسور", "عنصر", 150.00),

            #     # مراحل المقاولات
            #     ("المقاولات", "تأسيس وتشطيب", "أعمال الحفر", "متر مكعب", 15.00),
            #     ("المقاولات", "تأسيس وتشطيب", "صب الخرسانة", "متر مكعب", 120.00),
            #     ("المقاولات", "تأسيس وتشطيب", "أعمال البناء", "متر مربع", 80.00),
            #     ("المقاولات", "بناء عظم", "أعمال الطوب", "متر مربع", 45.00),
            #     ("المقاولات", "بناء عظم", "أعمال الحديد", "طن", 800.00),
            #     ("المقاولات", "تشطيب", "أعمال الدهان", "متر مربع", 25.00),
            #     ("المقاولات", "تشطيب", "أعمال البلاط", "متر مربع", 35.00),
            # ]

            # for section, project_type, phase_name, unit, price in default_phases:
            #     try:
            #         cursor.execute("""
            #             INSERT IGNORE INTO أسعار_المراحل
            #             (القسم, معرف_التصنيف, اسم_المرحلة, الوحدة, السعر)
            #             VALUES (%s, %s, %s, %s, %s)
            #         """, (section, project_type, phase_name, unit, price))
            #     except Exception as e:
            #         print(f"تحذير: لم يتم إدراج المرحلة {phase_name}: {e}")

            # إدراج مواعيد العمل الافتراضية إذا لم تكن موجودة
            cursor.execute("SELECT COUNT(*) FROM مواعيد_العمل")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO مواعيد_العمل
                    (نوع_النظام, وقت_حضور_صباحي, وقت_انصراف_صباحي,
                     الأحد, الاثنين, الثلاثاء, الأربعاء, الخميس, الجمعة, السبت,
                     فترة_التأخير_المسموحة, نشط, ملاحظات)
                    VALUES
                    ('فترة_واحدة', '08:00:00', '17:00:00',
                     TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE,
                     15, TRUE, 'مواعيد العمل الافتراضية للشركة')
                """)

            # إدراج البيانات الافتراضية للجداول المحاسبية

            # إدراج السنة المالية الحالية
            current_year = datetime.now().year
            cursor.execute("""
                INSERT IGNORE INTO السنوات_المالية
                (السنة, تاريخ_البداية, تاريخ_النهاية, حالة_السنة, هي_السنة_الحالية, ملاحظات, المستخدم)
                VALUES (%s, %s, %s, 'مفتوحة', TRUE, 'السنة المالية الحالية', 'النظام')
            """, (current_year, f"{current_year}-01-01", f"{current_year}-12-31"))

            # إدراج شجرة الحسابات الافتراضية
            default_accounts = [
                # الحسابات الرئيسية - المستوى الأول
                ("1", "الأصول", "أصول", None, 1, "نشط", "جميع أصول الشركة"),
                ("2", "الخصوم", "خصوم", None, 1, "نشط", "جميع خصوم الشركة"),
                ("3", "حقوق الملكية", "حقوق الملكية", None, 1, "نشط", "حقوق ملكية الشركة"),
                ("4", "الإيرادات", "إيرادات", None, 1, "نشط", "جميع إيرادات الشركة"),
                ("5", "المصروفات", "مصروفات", None, 1, "نشط", "جميع مصروفات الشركة"),

                # الأصول - المستوى الثاني
                ("11", "الأصول المتداولة", "أصول", "1", 2, "نشط", "الأصول قصيرة الأجل"),
                ("12", "الأصول الثابتة", "أصول", "1", 2, "نشط", "الأصول طويلة الأجل"),
                ("13", "الأصول غير الملموسة", "أصول", "1", 2, "نشط", "الأصول غير الملموسة"),

                # الأصول المتداولة - المستوى الثالث
                ("111", "النقدية والبنوك", "أصول", "11", 3, "نشط", "النقدية والحسابات البنكية"),
                ("112", "العملاء والذمم المدينة", "أصول", "11", 3, "نشط", "مستحقات العملاء"),
                ("113", "المخزون", "أصول", "11", 3, "نشط", "مخزون المواد والبضائع"),
                ("114", "المصروفات المدفوعة مقدماً", "أصول", "11", 3, "نشط", "المصروفات المدفوعة مسبقاً"),

                # النقدية والبنوك - المستوى الرابع
                ("1111", "الصندوق", "أصول", "111", 4, "نشط", "النقدية في الصندوق"),
                ("1112", "البنك الأهلي", "أصول", "111", 4, "نشط", "حساب البنك الأهلي"),
                ("1113", "بنك الراجحي", "أصول", "111", 4, "نشط", "حساب بنك الراجحي"),

                # الأصول الثابتة - المستوى الثالث
                ("121", "الأراضي والمباني", "أصول", "12", 3, "نشط", "الأراضي والمباني المملوكة"),
                ("122", "المعدات والآلات", "أصول", "12", 3, "نشط", "المعدات والآلات"),
                ("123", "الأثاث والتجهيزات", "أصول", "12", 3, "نشط", "الأثاث والتجهيزات المكتبية"),
                ("124", "وسائل النقل", "أصول", "12", 3, "نشط", "السيارات ووسائل النقل"),

                # الخصوم - المستوى الثاني
                ("21", "الخصوم المتداولة", "خصوم", "2", 2, "نشط", "الخصوم قصيرة الأجل"),
                ("22", "الخصوم طويلة الأجل", "خصوم", "2", 2, "نشط", "الخصوم طويلة الأجل"),

                # الخصوم المتداولة - المستوى الثالث
                ("211", "الموردين والذمم الدائنة", "خصوم", "21", 3, "نشط", "مستحقات الموردين"),
                ("212", "المصروفات المستحقة", "خصوم", "21", 3, "نشط", "المصروفات المستحقة الدفع"),
                ("213", "القروض قصيرة الأجل", "خصوم", "21", 3, "نشط", "القروض قصيرة الأجل"),

                # حقوق الملكية - المستوى الثاني
                ("31", "رأس المال", "حقوق الملكية", "3", 2, "نشط", "رأس مال الشركة"),
                ("32", "الأرباح المحتجزة", "حقوق الملكية", "3", 2, "نشط", "الأرباح المحتجزة"),
                ("33", "الاحتياطيات", "حقوق الملكية", "3", 2, "نشط", "الاحتياطيات المختلفة"),

                # الإيرادات - المستوى الثاني
                ("41", "إيرادات التشغيل", "إيرادات", "4", 2, "نشط", "إيرادات الأنشطة الرئيسية"),
                ("42", "إيرادات أخرى", "إيرادات", "4", 2, "نشط", "الإيرادات الأخرى"),

                # إيرادات التشغيل - المستوى الثالث
                ("411", "إيرادات المشاريع", "إيرادات", "41", 3, "نشط", "إيرادات المشاريع الهندسية"),
                ("412", "إيرادات المقاولات", "إيرادات", "41", 3, "نشط", "إيرادات أعمال المقاولات"),
                ("413", "إيرادات التدريب", "إيرادات", "41", 3, "نشط", "إيرادات الدورات التدريبية"),
                ("414", "إيرادات الاستشارات", "إيرادات", "41", 3, "نشط", "إيرادات الاستشارات الهندسية"),

                # المصروفات - المستوى الثاني
                ("51", "مصروفات التشغيل", "مصروفات", "5", 2, "نشط", "مصروفات الأنشطة الرئيسية"),
                ("52", "المصروفات الإدارية", "مصروفات", "5", 2, "نشط", "المصروفات الإدارية والعمومية"),
                ("53", "المصروفات المالية", "مصروفات", "5", 2, "نشط", "المصروفات المالية"),

                # مصروفات التشغيل - المستوى الثالث
                ("511", "مصروفات المشاريع", "مصروفات", "51", 3, "نشط", "مصروفات تنفيذ المشاريع"),
                ("512", "مصروفات الموظفين", "مصروفات", "51", 3, "نشط", "رواتب ومكافآت الموظفين"),
                ("513", "مصروفات المواد", "مصروفات", "51", 3, "نشط", "تكلفة المواد والمستلزمات"),

                # المصروفات الإدارية - المستوى الثالث
                ("521", "مصروفات إدارية عامة", "مصروفات", "52", 3, "نشط", "المصروفات الإدارية العامة"),
                ("522", "مصروفات التسويق", "مصروفات", "52", 3, "نشط", "مصروفات التسويق والإعلان"),
                ("523", "مصروفات الصيانة", "مصروفات", "52", 3, "نشط", "مصروفات الصيانة والإصلاح"),
            ]

            for account_id, account_name, account_type, parent_id, level, status, description in default_accounts:
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO شجرة_الحسابات
                        (معرف_الحساب, اسم_الحساب, نوع_الحساب, الحساب_الأب, مستوى_الحساب, حالة_الحساب, وصف_الحساب, المستخدم)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'النظام')
                    """, (account_id, account_name, account_type, parent_id, level, status, description))
                except Exception as e:
                    print(f"تحذير: لم يتم إدراج الحساب {account_name}: {e}")

            # إدراج مراكز التكلفة الافتراضية
            default_cost_centers = [
                ("CC001", "المشاريع الهندسية", "مركز تكلفة المشاريع الهندسية", "نشط", "إنتاجي", None),
                ("CC002", "أعمال المقاولات", "مركز تكلفة أعمال المقاولات", "نشط", "إنتاجي", None),
                ("CC003", "التدريب والتطوير", "مركز تكلفة الدورات التدريبية", "نشط", "إنتاجي", None),
                ("CC004", "الإدارة العامة", "مركز تكلفة الإدارة العامة", "نشط", "إداري", None),
                ("CC005", "التسويق والمبيعات", "مركز تكلفة التسويق والمبيعات", "نشط", "خدمي", None),
            ]

            for cc_id, cc_name, cc_desc, status, cc_type, parent in default_cost_centers:
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO مراكز_التكلفة
                        (معرف_مركز_التكلفة, اسم_مركز_التكلفة, وصف_مركز_التكلفة, حالة_المركز, نوع_المركز, المركز_الأب, المستخدم)
                        VALUES (%s, %s, %s, %s, %s, %s, 'النظام')
                    """, (cc_id, cc_name, cc_desc, status, cc_type, parent))
                except Exception as e:
                    print(f"تحذير: لم يتم إدراج مركز التكلفة {cc_name}: {e}")

            # إدراج أرصدة افتتاحية للحسابات الرئيسية
            for account_id, _, _, _, _, _, _ in default_accounts:
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO أرصدة_الحسابات
                        (معرف_الحساب, الرصيد_المدين, الرصيد_الدائن, السنة_المالية, المستخدم)
                        VALUES (%s, 0.00, 0.00, %s, 'النظام')
                    """, (account_id, current_year))
                except Exception as e:
                    print(f"تحذير: لم يتم إدراج رصيد الحساب {account_id}: {e}")

            create_index_if_not_exists(cursor, 'idx_المشاريع_المدفوعات_معرف_المشروع', 'المشاريع_المدفوعات', 'معرف_المشروع')
            create_index_if_not_exists(cursor, 'idx_المشاريع_المدفوعات_تاريخ_الدفع', 'المشاريع_المدفوعات', 'تاريخ_الدفع')

            create_index_if_not_exists(cursor, 'idx_العملاء_اسم_العميل', 'العملاء', 'اسم_العميل')

            create_index_if_not_exists(cursor, 'idx_المصروفات_التاريخ', 'الحسابات', 'تاريخ_المصروف')
            create_index_if_not_exists(cursor, 'idx_المصروفات_رقم_الفاتورة', 'الحسابات', 'رقم_الفاتورة')

            create_index_if_not_exists(cursor, 'idx_الموظفين_التصنيف', 'الموظفين', 'التصنيف')
            create_index_if_not_exists(cursor, 'idx_الموظفين_اسم_الموظف', 'الموظفين', 'اسم_الموظف')
            create_index_if_not_exists(cursor, 'idx_الموظفين_معاملات_مالية_معرف_الموظف', 'الموظفين_معاملات_مالية', 'معرف_الموظف')
            create_index_if_not_exists(cursor, 'idx_الموظفين_معاملات_مالية_التاريخ', 'الموظفين_معاملات_مالية', 'التاريخ')

            create_index_if_not_exists(cursor, 'idx_المشاريع_المراحل_معرف_المشروع', 'المشاريع_المراحل', 'معرف_المشروع')
            

            create_index_if_not_exists(cursor, 'idx_الموظفين_التقييم_معرف_المهندس', 'الموظفين_التقييم', 'معرف_الموظف')

            create_index_if_not_exists(cursor, 'idx_دورات_تدريبية_التصنيف', 'التدريب', 'التصنيف')
            create_index_if_not_exists(cursor, 'idx_دورات_تدريبية_تاريخ_البدء', 'التدريب', 'تاريخ_البدء')
            
            create_index_if_not_exists(cursor, 'idx_مصروفات_المشروع_معرف_المشروع', 'المقاولات_مصروفات_العهد', 'معرف_المشروع')
            create_index_if_not_exists(cursor, 'idx_مصروفات_المشروع_نوع_المصروف', 'المقاولات_مصروفات_العهد', 'نوع_المصروف')
            create_index_if_not_exists(cursor, 'idx_مصروفات_المشروع_تاريخ_المصروف', 'المقاولات_مصروفات_العهد', 'تاريخ_المصروف')
            create_index_if_not_exists(cursor, 'idx_مصروفات_مباشرة_المشروع_معرف_المشروع', 'المقاولات_مصروفات_العهد', 'معرف_المشروع')
            create_index_if_not_exists(cursor, 'idx_مصروفات_مباشرة_المشروع_تاريخ_المصروف', 'المقاولات_مصروفات_العهد', 'تاريخ_المصروف')



            # إنشاء التريغرات
            # Note: MySQL triggers are schema-specific. These will be created in project_manager2_YYYY database
            triggers = [
                ("update_project_paid_insert", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_project_paid_insert`
                    AFTER INSERT ON `المشاريع_المدفوعات`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `المشاريع`
                        SET `المدفوع` = `المدفوع` + NEW.`المبلغ_المدفوع`
                        WHERE `id` = NEW.`معرف_المشروع`;
                    END;
                """),
                ("update_project_paid_update", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_project_paid_update`
                    AFTER UPDATE ON `المشاريع_المدفوعات`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `المشاريع`
                        SET `المدفوع` = `المدفوع` - OLD.`المبلغ_المدفوع` + NEW.`المبلغ_المدفوع`
                        WHERE `id` = NEW.`معرف_المشروع`;
                    END;
                """),
                ("update_project_paid_delete", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_project_paid_delete`
                    AFTER DELETE ON `المشاريع_المدفوعات`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `المشاريع`
                        SET `المدفوع` = `المدفوع` - OLD.`المبلغ_المدفوع`
                        WHERE `id` = OLD.`معرف_المشروع`;
                    END;
                """),

                # ("update_employee_balance_insert", f"""
                #     CREATE TRIGGER IF NOT EXISTS `update_employee_balance_insert`
                #     AFTER INSERT ON `الموظفين_معاملات_مالية`
                #     FOR EACH ROW
                #     BEGIN
                #         UPDATE `الموظفين`
                #         SET `الرصيد` = `الرصيد` + NEW.`المبلغ`
                #         WHERE `id` = NEW.`معرف_الموظف`;
                #     END;
                # """),
                #  ("update_employee_balance_update", f"""
                #     CREATE TRIGGER IF NOT EXISTS `update_employee_balance_update`
                #     AFTER UPDATE ON `الموظفين_معاملات_مالية`
                #     FOR EACH ROW
                #     BEGIN
                #         UPDATE `الموظفين`
                #         SET `الرصيد` = `الرصيد` - OLD.`المبلغ` + NEW.`المبلغ`
                #         WHERE `id` = NEW.`معرف_الموظف`;
                #     END;
                # """),
                #  ("update_employee_balance_delete", f"""
                #     CREATE TRIGGER IF NOT EXISTS `update_employee_balance_delete`
                #     AFTER DELETE ON `الموظفين_معاملات_مالية`
                #     FOR EACH ROW
                #     BEGIN
                #         UPDATE `الموظفين`
                #         SET `الرصيد` = `الرصيد` - OLD.`المبلغ`
                #         WHERE `id` = OLD.`معرف_الموظف`;
                #     END;
                # """),

                
                # تم حذف تريغر تحديث_التصميم لأن الأعمدة المطلوبة غير موجودة في جدول المشاريع_المراحل
                

                # تريغرات العهد المالية
                # ("update_custody_expenses_insert", f"""
                #     CREATE TRIGGER IF NOT EXISTS `update_custody_expenses_insert`
                #     AFTER INSERT ON `المقاولات_مصروفات_العهد`
                #     FOR EACH ROW
                #     BEGIN
                #         UPDATE `المقاولات_العهد`
                #         SET `المصروف` = `المصروف` + NEW.`المبلغ`
                #         WHERE `id` = NEW.`معرف_العهدة`;
                #     END;
                # """),
                # ("update_custody_expenses_update", f"""
                #     CREATE TRIGGER IF NOT EXISTS `update_custody_expenses_update`
                #     AFTER UPDATE ON `المقاولات_مصروفات_العهد`
                #     FOR EACH ROW
                #     BEGIN
                #         UPDATE `المقاولات_العهد`
                #         SET `المصروف` = `المصروف` - OLD.`المبلغ` + NEW.`المبلغ`
                #         WHERE `id` = NEW.`معرف_العهدة`;
                #     END;
                # """),
                # ("update_custody_expenses_delete", f"""
                #     CREATE TRIGGER IF NOT EXISTS `update_custody_expenses_delete`
                #     AFTER DELETE ON `المقاولات_مصروفات_العهد`
                #     FOR EACH ROW
                #     BEGIN
                #         UPDATE `المقاولات_العهد`
                #         SET `المصروف` = `المصروف` - OLD.`المبلغ`
                #         WHERE `id` = OLD.`معرف_العهدة`;
                #     END;
                # """),
                # تم حذف تريغر update_custody_project_info لأن الأعمدة المطلوبة غير موجودة في جدول المقاولات_العهد

                # تريغرات دفعات العهد المالية لتحديث مبلغ_العهدة تلقائياً
                ("update_custody_amount_insert", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_custody_amount_insert`
                    AFTER INSERT ON `المقاولات_دفعات_العهد`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `المقاولات_العهد`
                        SET `مبلغ_العهدة` = `مبلغ_العهدة` + NEW.`المبلغ`
                        WHERE `id` = NEW.`معرف_العهدة`;
                    END;
                """),
                ("update_custody_amount_update", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_custody_amount_update`
                    AFTER UPDATE ON `المقاولات_دفعات_العهد`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `المقاولات_العهد`
                        SET `مبلغ_العهدة` = `مبلغ_العهدة` - OLD.`المبلغ` + NEW.`المبلغ`
                        WHERE `id` = NEW.`معرف_العهدة`;
                    END;
                """),
                ("update_custody_amount_delete", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_custody_amount_delete`
                    AFTER DELETE ON `المقاولات_دفعات_العهد`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `المقاولات_العهد`
                        SET `مبلغ_العهدة` = `مبلغ_العهدة` - OLD.`المبلغ`
                        WHERE `id` = OLD.`معرف_العهدة`;
                    END;
                """),

                # تريغرات مصروفات المشروع
                ("update_project_expenses_insert", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_project_expenses_insert`
                    AFTER INSERT ON `المقاولات_مصروفات_العهد`
                    FOR EACH ROW
                    BEGIN
                        -- إذا كان المصروف مرتبط بعهدة، قم بتحديث العهدة أيضاً
                        IF NEW.`نوع_المصروف` = 'مرتبط_بعهدة' AND NEW.`معرف_العهدة` IS NOT NULL THEN
                            UPDATE `المقاولات_العهد`
                            SET `المصروف` = `المصروف` + NEW.`المبلغ`
                            WHERE `id` = NEW.`معرف_العهدة`;
                        END IF;
                    END;
                """),
                ("update_project_expenses_update", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_project_expenses_update`
                    AFTER UPDATE ON `المقاولات_مصروفات_العهد`
                    FOR EACH ROW
                    BEGIN
                        -- إذا كان المصروف القديم مرتبط بعهدة، قم بطرح المبلغ القديم
                        IF OLD.`نوع_المصروف` = 'مرتبط_بعهدة' AND OLD.`معرف_العهدة` IS NOT NULL THEN
                            UPDATE `المقاولات_العهد`
                            SET `المصروف` = `المصروف` - OLD.`المبلغ`
                            WHERE `id` = OLD.`معرف_العهدة`;
                        END IF;
                        
                        -- إذا كان المصروف الجديد مرتبط بعهدة، قم بإضافة المبلغ الجديد
                        IF NEW.`نوع_المصروف` = 'مرتبط_بعهدة' AND NEW.`معرف_العهدة` IS NOT NULL THEN
                            UPDATE `المقاولات_العهد`
                            SET `المصروف` = `المصروف` + NEW.`المبلغ`
                            WHERE `id` = NEW.`معرف_العهدة`;
                        END IF;
                    END;
                """),
                ("update_project_expenses_delete", f"""
                    CREATE TRIGGER IF NOT EXISTS `update_project_expenses_delete`
                    AFTER DELETE ON `المقاولات_مصروفات_العهد`
                    FOR EACH ROW
                    BEGIN
                        -- إذا كان المصروف مرتبط بعهدة، قم بطرح المبلغ من العهدة
                        IF OLD.`نوع_المصروف` = 'مرتبط_بعهدة' AND OLD.`معرف_العهدة` IS NOT NULL THEN
                            UPDATE `المقاولات_العهد`
                            SET `المصروف` = `المصروف` - OLD.`المبلغ`
                            WHERE `id` = OLD.`معرف_العهدة`;
                        END IF;
                    END;
                """)
            ]

            for trigger_name, trigger_sql in triggers:
                try:
                    trigger_exists = False
                    try:
                        cursor.execute("""
                            SELECT COUNT(*)
                            FROM INFORMATION_SCHEMA.TRIGGERS
                            WHERE TRIGGER_SCHEMA = %s AND TRIGGER_NAME = %s
                        """, (db_name, trigger_name))
                        if cursor.fetchone()[0] > 0:
                            trigger_exists = True
                    except mysql.connector.Error as check_err:
                         print(f"Warning: Could not check for trigger {trigger_name} existence: {check_err}")

                    if not trigger_exists:
                        try:
                            cursor.execute(trigger_sql)
                            print(f"Trigger {trigger_name} ensured.")
                        except mysql.connector.Error as err:
                            if err.errno == 1359: # Trigger already exists error number (common)
                                print(f"Trigger {trigger_name} already exists. Skipping creation (from error code).")
                            else:
                                print(f"Error creating trigger {trigger_name}: {err}")
                                # Decide if this should be a fatal error or just a warning
                                # raise # Uncomment to make trigger creation errors fatal
                    # else:
                    #      print(f"Trigger {trigger_name} already exists. Skipping creation.")

                except Exception as e:
                     print(f"Unexpected error processing trigger {trigger_name}: {e}")

            conn.commit()
            conn.commit()
            return True

        except mysql.connector.Error as err:
            print(f"Database Creation/Setup Error: {err}")
            QMessageBox.critical(self, "خطأ في إعداد قاعدة البيانات",
                                 f"حدث خطأ أثناء إنشاء أو تحديث قاعدة البيانات  :\n{err}")
            return False
        except Exception as e:
            print(f"Unexpected Error during DB setup: {e}")
            QMessageBox.critical(self, "خطأ غير متوقع",
                                 f"حدث خطأ غير متوقع أثناء إعداد قاعدة البيانات:\n{e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# إنشاء قاعدة بيانات إذا لم تكن موجودة


# متغير يخزن آخر مجلد تم فيه النسخ الاحتياطي---------------------------------------------------------------
last_backup_folder = None

#بروسس بار للنسخ الاحتياطي
# ProgressDialog
class ProgressDialog(QDialog):
    # init
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(450, 150)

        layout = QVBoxLayout()

        # تحسين شكل الرسالة
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.label)

        # تحسين شكل البروغرس بار
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
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
                margin: 10px 10px;
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
        layout.addWidget(self.progress_bar)

        # إضافة هامش في الأسفل
        layout.addSpacing(10)

        self.setLayout(layout)

#==========# دالة النسخ الاحتياطي اليدوي============================================================================================
# النسخ الاحتياطي DB
def Backup_DB(self):
    global last_backup_folder

    if self.license_type == "trial":
        reply = GEN_MSG_BOX("قيود النسخة التجريبية", "هذه الميزة متوفرة في النسخة المدفوعة فقط.", "license.png", "شراء", "إلغاء", "#dfcab4")
        if reply != QMessageBox.Ok:
            return
        else:
            self.changing_activation_dialog()
            return

    # اختيار مجلد الحفظ
    source_folder = QFileDialog.getExistingDirectory(None, "اختر مجلد حفظ النسخ الاحتياطية")
    if source_folder:
        # حفظ المسار
        with open(backup_info, 'w', encoding='utf-8') as file:
            file.write(source_folder)

        main_backup_folder = os.path.join(source_folder, "Backup folders")
        os.makedirs(main_backup_folder, exist_ok=True)

        today_date = datetime.now().strftime("%d-%m-%Y")
        backup_folder_name = f"Backup_DB V{CURRENT_VERSION} {today_date}"
        project_manager = os.path.join(main_backup_folder, backup_folder_name)

        try:
            # إنشاء شريط التقدم
            progress = QProgressDialog("جارٍ إنشاء النسخ الاحتياطية...", "إلغاء", 0, 100, self)
            progress.setWindowTitle("النسخ الاحتياطي")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            # حذف المجلد إذا كان موجودًا
            if os.path.exists(project_manager):
                shutil.rmtree(project_manager)

            # نسخ الملفات (50% من التقدم)
            total_files = sum(len(files) for _, _, files in os.walk(folder_path))
            if total_files == 0:
                progress.close()
                QMessageBox.warning(self, "تحذير", "لم يتم العثور على ملفات للنسخ.")
                return

            copied_files = 0

            # نسخ مع التقدم
            def copy_with_progress(src, dst):
                nonlocal copied_files
                os.makedirs(dst, exist_ok=True)
                for item in os.listdir(src):
                    if progress.wasCanceled():
                        return False
                    s = os.path.join(src, item)
                    d = os.path.join(dst, item)
                    if os.path.isdir(s):
                        copy_with_progress(s, d)
                    else:
                        shutil.copy2(s, d)
                        copied_files += 1
                        progress_value = int((copied_files / total_files) * 50)  # 50% للملفات
                        progress.setValue(progress_value)
                        progress.setLabelText(f"جارٍ نسخ الملفات: {copied_files}/{total_files}")
                        QApplication.processEvents()
                return True

            # نسخ الملفات
            if not copy_with_progress(folder_path, project_manager):
                progress.close()
                QMessageBox.information(self, "إلغاء", "تم إلغاء عملية النسخ الاحتياطي.")
                return

            # نسخ قواعد البيانات (50% المتبقية)
            progress.setLabelText("جارٍ نسخ قاعدة البيانات...")
            if not backup_databases(source_folder, project_manager, progress, start_progress=50, end_progress=100):
                progress.close()
                QMessageBox.information(self, "إلغاء", "تم إلغاء عملية النسخ الاحتياطي.")
                return

            # إكمال التقدم
            progress.setValue(100)
            progress.close()

            # حذف النسخ القديمة
            remove_old_backup_folders(self, main_backup_folder)

            QMessageBox.information(self, "النسخ الاحتياطية", "تم إنشاء النسخ الاحتياطية لجميع قواعد البيانات بنجاح.")
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "نسخ إحتياطي يدوي", f"فشل في إنشاء النسخة الاحتياطية: {e}")
    else:
        QMessageBox.warning(self, "تحذير", "لم يتم اختيار أي مجلد.")



# إنشاء ملف إعداد mysql مؤقت
# إنشاء ملف تكوين MySQL
def create_mysql_config_file():
    user_home = os.path.expanduser("~")
    config_path = os.path.join(user_home, "temp_mysql.cnf")

    config_content = """
[client]
user=root
password=kh123456
host=localhost
"""

    try:
        with open(config_path, 'w') as f:
            f.write(config_content.strip())

        # إخفاء الملف في ويندوز
        subprocess.run(["attrib", "+h", config_path], shell=True)
        return config_path
    except Exception as e:
        QMessageBox.critical(None, "خطأ", f"فشل في إنشاء ملف إعداد الاتصال: {e}")
        return None

# دالة تنفيذ النسخ الاحتياطي
# قواعد بيانات النسخ الاحتياطي
def backup_databases(folder, project_manager, progress_dialog=None, start_progress=50, end_progress=100):
    if not folder:
        return

    if not os.path.exists(project_manager):
        os.makedirs(project_manager)

    mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
    mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe"

    # جلب قائمة قواعد البيانات
    list_command = [
        mysql_path,
        f"--host={host}",
        f"--user={user_r}",
        f"--password={password_r}",
        "--batch",
        "--skip-column-names",
        "-e",
        "SHOW DATABASES LIKE 'project_manager%';"
    ]
    result = subprocess.run(list_command, capture_output=True, text=True, check=True)
    db_list = result.stdout.splitlines()
    total_dbs = len(db_list)

    if total_dbs == 0:
        return

    # حساب التقدم لكل قاعدة بيانات
    progress_per_db = (end_progress - start_progress) / total_dbs if total_dbs > 0 else 0
    current_progress = start_progress

    for i, db_name in enumerate(db_list):
        if progress_dialog and progress_dialog.wasCanceled():
            return False  # إلغاء العملية

        backup_filename = f"{db_name}_backup.sql"
        backup_path = os.path.join(project_manager, backup_filename)
        dump_command = [
            mysqldump_path,
            f"--host={host}",
            f"--user={user_r}",
            f"--password={password_r}",
            db_name,
            "-r",
            backup_path
        ]
        subprocess.run(dump_command, check=True)

        # تحديث شريط التقدم
        if progress_dialog:
            current_progress += progress_per_db
            progress_dialog.setValue(int(current_progress))
            progress_dialog.setLabelText(f"جارٍ نسخ قاعدة البيانات: {i + 1}/{total_dbs}")
            QApplication.processEvents()

    return True

# دالة تنفيذ النسخ الاحتياطي
# قواعد بيانات النسخ الاحتياطي
def backup_databases(folder, project_manager, progress_dialog=None, start_progress=50, end_progress=100):
    if not folder:
        return

    if not os.path.exists(project_manager):
        os.makedirs(project_manager)

    # إنشاء ملف إعداد الاتصال
    config_path = create_mysql_config_file()
    if not config_path:
        return False

    mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
    mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe"

    try:
        # جلب قائمة قواعد البيانات
        list_command = [
            mysql_path,
            f"--defaults-file={config_path}",
            "--batch",
            "--skip-column-names",
            "-e",
            "SHOW DATABASES LIKE 'project_manager%';"
        ]
        result = subprocess.run(list_command, capture_output=True, text=True, check=True)
        db_list = result.stdout.splitlines()
        total_dbs = len(db_list)

        if total_dbs == 0:
            return

        # حساب التقدم لكل قاعدة بيانات
        progress_per_db = (end_progress - start_progress) / total_dbs if total_dbs > 0 else 0
        current_progress = start_progress

        for i, db_name in enumerate(db_list):
            if progress_dialog and progress_dialog.wasCanceled():
                return False  # إلغاء العملية

            backup_filename = f"{db_name}_backup.sql"
            backup_path = os.path.join(project_manager, backup_filename)
            dump_command = [
                mysqldump_path,
                f"--defaults-file={config_path}",
                db_name,
                "-r",
                backup_path
            ]
            subprocess.run(dump_command, check=True)

            # تحديث شريط التقدم
            if progress_dialog:
                current_progress += progress_per_db
                progress_dialog.setValue(int(current_progress))
                progress_dialog.setLabelText(f"جارٍ نسخ قاعدة البيانات: {i + 1}/{total_dbs}")
                QApplication.processEvents()

    finally:
        # حذف ملف الإعداد المؤقت بعد الانتهاء
        try:
            if os.path.exists(config_path):
                os.remove(config_path)
        except Exception as e:
            print(f"تنبيه: لم يتم حذف ملف الاتصال المؤقت: {e}")

    return True

#=========#نسخ تلقائي للقاعدة=============================================================================================
# نسخة احتياطية السيارات
def Auto_Backup_DB(self):
    global last_backup_folder
    try:
        with open(backup_info, 'r', encoding='utf-8') as file:
            dest_folder_path = file.read().strip()

        if os.path.exists(dest_folder_path):
            today_date = datetime.now().strftime("%d-%m-%Y")
            dest_folder_backup_path = os.path.join(dest_folder_path, "Backup folders", f"Backup_DB V{CURRENT_VERSION} {today_date}")

            # إنشاء شريط التقدم
            progress = QProgressDialog("جارٍ إنشاء النسخ الاحتياطية التلقائية...", "إلغاء", 0, 100, self)
            progress.setWindowTitle("النسخ الاحتياطي التلقائي")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            # حذف المجلد إذا كان موجودًا
            if os.path.exists(dest_folder_backup_path):
                shutil.rmtree(dest_folder_backup_path)

            # نسخ الملفات (50% من التقدم)
            total_files = sum(len(files) for _, _, files in os.walk(folder_path))
            if total_files == 0:
                progress.close()
                QMessageBox.warning(self, "تحذير", "لم يتم العثور على ملفات للنسخ.")
                return

            copied_files = 0

            # نسخ مع التقدم
            def copy_with_progress(src, dst):
                nonlocal copied_files
                os.makedirs(dst, exist_ok=True)
                for item in os.listdir(src):
                    if progress.wasCanceled():
                        return False
                    s = os.path.join(src, item)
                    d = os.path.join(dst, item)
                    if os.path.isdir(s):
                        copy_with_progress(s, d)
                    else:
                        shutil.copy2(s, d)
                        copied_files += 1
                        progress_value = int((copied_files / total_files) * 50)  # 50% للملفات
                        progress.setValue(progress_value)
                        progress.setLabelText(f"جارٍ نسخ الملفات: {copied_files}/{total_files}")
                        QApplication.processEvents()
                return True

            # نسخ الملفات
            if not copy_with_progress(folder_path, dest_folder_backup_path):
                progress.close()
                QMessageBox.information(self, "إلغاء", "تم إلغاء عملية النسخ الاحتياطي التلقائي.")
                return

            # نسخ قواعد البيانات (50% المتبقية)
            progress.setLabelText("جارٍ نسخ قاعدة البيانات...")
            if not backup_databases(dest_folder_path, dest_folder_backup_path, progress, start_progress=50, end_progress=100):
                progress.close()
                QMessageBox.information(self, "إلغاء", "تم إلغاء عملية النسخ الاحتياطي التلقائي.")
                return

            # إكمال التقدم
            progress.setValue(100)
            progress.close()

            # حذف النسخ القديمة
            remove_old_backup_folders(self, os.path.join(dest_folder_path, "Backup folders"))

            QMessageBox.information(self, "النسخ الاحتياطية", f"تم تحديث النسخة الإحتياطية بنجاح.\n{dest_folder_backup_path}")
        else:
            reply = GEN_MSG_BOX('النسخ الإحتياطي التلقائي', 'مسار النسخ الاحتياطي غير موجود، يرجى تحديد مسار جديد.', 'warning.png', 'مسار جديد', 'خروج', msg_box_color)
            if reply != QMessageBox.Ok:
                return
            Backup_DB(self)
    except Exception as e:
        progress.close()
        QMessageBox.critical(self, "نسخ تلقائي إحتياطي", f"فشل في إنشاء النسخة الاحتياطية: {e}")

# حذف بعد شهر
# قم بإزالة مجلدات النسخ الاحتياطي القديمة
def remove_old_backup_folders(self, path):
    now = datetime.now()
    one_month_ago = now - timedelta(days=90)
    old_folders = []  # قائمة لتخزين أسماء النسخ الاحتياطية القديمة

    for folder_name in os.listdir(path):
        folder_path = os.path.join(path, folder_name)

        if os.path.isdir(folder_path) and folder_name.startswith("Backup_DB"):
            try:
                # استخراج التاريخ من اسم المجلد
                #date_part = folder_name.split(f"Backup_DB V{CURRENT_VERSION} ")[1]
                date_part = folder_name.split("Backup_DB V")[1].split()[-1]  # يأخذ الجزء الأخير بعد المسافة
                folder_date = datetime.strptime(date_part, "%d-%m-%Y")

                if folder_date < one_month_ago:
                    old_folders.append(folder_path)  # إضافة المجلد إلى القائمة

            except (IndexError, ValueError) as e:
                QMessageBox.critical(self, "خطأ في اسم المجلد",
                                     f"اسم المجلد: {folder_name}\nخطأ: {str(e)}")
                continue

    if old_folders:
        # إنشاء نص رسالة التأكيد
        folders_list = "\n".join(os.path.basename(folder) for folder in old_folders)
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                     f"يوجد نسخ إحتياطية قديمة لأكثر من 3 أشهر !\nهل تريد حذف النسخ الاحتياطيةالتالية؟\n\n{folders_list}",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for folder in old_folders:
                shutil.rmtree(folder)  # حذف المجلد
            QMessageBox.information(self, "تم الحذف", "تم حذف جميع النسخ الاحتياطية القديمة بنجاح.")

#استعادة النسخة الاحتياطية \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# استيراد DB
def import_db(self):
    if self.license_type == "trial":
        reply = GEN_MSG_BOX("قيود النسخة التجريبية", "هذه الميزة متوفرة في النسخة المدفوعة فقط.", "license.png", "شراء", "إلغاء", "#dfcab4")
        if reply != QMessageBox.Ok:
            return
        else:
            self.changing_activation_dialog()
            return

    folder_path = QFileDialog.getExistingDirectory(None, "اختر المجلد الذي يحتوي على النسخ الاحتياطية")
    if folder_path:
        # جمع ملفات النسخ الاحتياطية
        backup_files = [f for f in os.listdir(folder_path) if f.startswith("project_manager") and f.endswith(".sql")]
        total_files = len(backup_files)

        if total_files == 0:
            QMessageBox.warning(self, "تحذير", "لم يتم العثور على ملفات نسخ احتياطية في المجلد.")
            return

        # إنشاء شريط التقدم
        progress = QProgressDialog("جارٍ استعادة النسخ الاحتياطية...", "إلغاء", 0, total_files, self)
        progress.setWindowTitle("استعادة النسخة الاحتياطية")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        processed_files = 0

        for filename in backup_files:
            # التحقق من إلغاء العملية
            if progress.wasCanceled():
                QMessageBox.information(self, "إلغاء", "تم إلغاء عملية الاستعادة.")
                return

            backup_file = os.path.join(folder_path, filename)
            db_name = filename.split('_backup')[0]  # استخراج اسم قاعدة البيانات
            mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
            mysqladmin_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqladmin.exe"

            # إنشاء قاعدة البيانات إذا لم تكن موجودة
            create_db_command = [mysql_path, f"--host={host}", f"--user={user_r}", f"--password={password_r}", "-e", f"CREATE DATABASE IF NOT EXISTS {db_name}"]
            try:
                subprocess.run(create_db_command, check=True)
                print(f"تم التأكد من وجود قاعدة البيانات أو إنشاؤها: {db_name}")
            except subprocess.CalledProcessError as e:
                print(f"فشل في إنشاء قاعدة البيانات {db_name}: {e}")
                continue

            # فحص وجود الجدول License_Status
            check_table_command = [mysql_path, f"--host={host}", f"--user={user}", f"--password={password}", db_name, "-e", "SHOW TABLES LIKE 'License_Status';"]
            table_exists = False
            try:
                result = subprocess.run(check_table_command, capture_output=True, text=True, check=True)
                if 'License_Status' in result.stdout:
                    table_exists = True
                    print(f"تم العثور على الجدول 'License_Status' في قاعدة البيانات: {db_name}")
            except subprocess.CalledProcessError as e:
                print(f"فشل في التحقق من وجود الجدول 'License_Status' في قاعدة البيانات {db_name}: {e}")

            if table_exists:
                print(f"تم استبعاد الجدول 'License_Status' من الاسترداد.")
                continue  # تخطي استعادة النسخة الاحتياطية إذا كان الجدول موجودًا

            # استعادة النسخة الاحتياطية
            restore_command = [mysql_path, f"--host={host}", f"--user={user}", f"--password={password}", db_name]
            try:
                with open(backup_file, 'r') as file:
                    subprocess.run(restore_command, stdin=file, check=True)
                print(f"تم استعادة النسخة الاحتياطية بنجاح لقاعدة البيانات: {db_name}")
            except subprocess.CalledProcessError as e:
                print(f"فشل في استعادة النسخة الاحتياطية لقاعدة البيانات {db_name}: {e}")
            except FileNotFoundError:
                print(f"الملف {backup_file} غير موجود.")

            # تحديث شريط التقدم
            processed_files += 1
            progress.setValue(processed_files)
            progress.setLabelText(f"جارٍ استعادة النسخة الاحتياطية: {processed_files}/{total_files}")
            QApplication.processEvents()  # تحديث واجهة المستخدم

        # إغلاق شريط التقدم
        progress.setValue(total_files)
        QMessageBox.information(self, "استعادة النسخ الاحتياطية", "تم استعادة جميع قواعد البيانات.\nسيتم إعادة تشغيل التطبيق.")
        restart_application()
    else:
        QMessageBox.warning(self, "تحذير", "لم يتم اختيار أي مجلد.")


# استعادة النسخة الاحتياطية
# استيراد DB
def import_db(self):
    if self.license_type == "trial":
        reply = GEN_MSG_BOX("قيود النسخة التجريبية", "هذه الميزة متوفرة في النسخة المدفوعة فقط.", "license.png", "شراء", "إلغاء", "#dfcab4")
        if reply != QMessageBox.Ok:
            return
        else:
            self.changing_activation_dialog()
            return

    folder_path = QFileDialog.getExistingDirectory(None, "اختر المجلد الذي يحتوي على النسخ الاحتياطية")
    if not folder_path:
        QMessageBox.warning(self, "تحذير", "لم يتم اختيار أي مجلد.")
        return

    # إنشاء ملف إعداد mysql
    config_path = create_mysql_config_file()
    if not config_path:
        return

    try:
        backup_files = [f for f in os.listdir(folder_path) if f.startswith("project_manager") and f.endswith(".sql")]
        total_files = len(backup_files)

        if total_files == 0:
            QMessageBox.warning(self, "تحذير", "لم يتم العثور على ملفات نسخ احتياطية في المجلد.")
            return

         # تغيير الترميز إلى UTF-8 لتفادي مشاكل cp720
        os.system("chcp 65001 > NUL")

        mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"


        progress = QProgressDialog("جارٍ استعادة النسخ الاحتياطية...", "إلغاء", 0, total_files, self)
        progress.setWindowTitle("استعادة النسخة الاحتياطية")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        processed_files = 0


        for filename in backup_files:
            if progress.wasCanceled():
                QMessageBox.information(self, "إلغاء", "تم إلغاء عملية الاستعادة.")
                return

            backup_file = os.path.join(folder_path, filename)
            db_name = filename.split('_backup')[0]

            # إنشاء قاعدة البيانات
            create_db_command = [
                mysql_path, f"--defaults-file={config_path}", "-e",
                f"CREATE DATABASE IF NOT EXISTS {db_name}"
            ]
            subprocess.run(create_db_command, check=True)

            # التحقق من وجود جدول License_Status
            check_table_command = [
                mysql_path, f"--defaults-file={config_path}", db_name, "-e",
                "SHOW TABLES LIKE 'License_Status';"
            ]
            try:
                result = subprocess.run(check_table_command, capture_output=True, text=True, check=True)
                if 'License_Status' in result.stdout:
                    continue  # تخطي الاستعادة إذا كان الجدول موجودًا
            except:
                pass

            # تنفيذ الاستعادة
            restore_command = [mysql_path, f"--defaults-file={config_path}", db_name]
            try:
                with open(backup_file, 'r') as file:
                    subprocess.run(restore_command, stdin=file, check=True)
            except Exception as e:
                print(f"خطأ أثناء استعادة {db_name}: {e}")
                continue

            processed_files += 1
            progress.setValue(processed_files)
            progress.setLabelText(f"جارٍ استعادة النسخة الاحتياطية: {processed_files}/{total_files}")
            QApplication.processEvents()

        progress.setValue(total_files)
        QMessageBox.information(self, "استعادة النسخ الاحتياطية", "تم استعادة جميع قواعد البيانات.\nسيتم إعادة تشغيل التطبيق.")
        restart_application()

    finally:
        if os.path.exists(config_path):
            try:
                os.remove(config_path)
            except Exception as e:
                print(f"تنبيه: لم يتم حذف ملف الإعداد المؤقت: {e}")


#GoogleDrive///////////////////////////////////////////////////////////////////////////////////

#تثبيت قاعدة البيانات ////////////////////////////////////////////////
# Instll DB
def instll_db():
    mysql_bin_path = r'C:\Program Files\MySQL\MySQL Server 8.4\bin'
    msi_path = os.path.join(application_path, "mysql8.4.msi")
    if not os.path.exists(mysql_bin_path):
        #QMessageBox.critical(self, ' قاعدة البيانات', f'يجب تثبيت قاعدة البيانات أولا... اتصل بالمطور لحل المشكلة')
        if os.path.exists(msi_path):
            os.startfile(msi_path)
        sys.exit()

#تغيير باسوورد الروت
# تغيير كلمة مرور الجذر
def change_root_password(self,new_password):
    try:
        # الاتصال بقاعدة البيانات باستخدام كلمة المرور القديمة
        connection = mysql.connector.connect(host=host,user="root",password="123456")
        if connection.is_connected():
            cursor = connection.cursor()
            # تنفيذ استعلام تغيير كلمة المرور
            cursor.execute(f"ALTER USER 'root'@'{host}' idENTIFIED BY '{new_password}';")
            # التحقق مما إذا كان المستخدم 'pme' موجودًا
            cursor.execute(f"SELECT COUNT(*) FROM mysql.user WHERE user = 'pme' AND host = '{host}';")
            user_exists = cursor.fetchone()[0]  # جلب النتيجة
            if user_exists:  # إذا كان المستخدم موجودً
                cursor.execute(f"ALTER USER 'pme'@'{host}' idENTIFIED BY '{new_password}';")

            connection.commit()  # تأكيد التغييرات
            cursor.close()
            connection.close()
            QMessageBox.information(self, "قاعدة البيانات", f"تم تغيير كلمة المرور بنجاح!")
    except Error as e:
        pass

#انشاء مستخدم pme
# مستخدم PME
def pme_user(self):
    add_registry_key(self)
    # استخدام الدالة مع كلمة المرور الجديدة
    change_root_password(self,"kh123456")
    # بيانات المستخدم الجديد
    new_user = 'pme'
    new_password = 'kh123456'
    new_host = host
    try:
        connection = mysql.connector.connect(host=host,user=user_r,password=password_r)
        cursor = connection.cursor()
        query_check_user = f"SELECT User FROM mysql.user WHERE User = '{new_user}' AND Host = '{new_host}';"
        cursor.execute(query_check_user)
        user_exists = cursor.fetchone()
        if not user_exists:
            query_create_user = f"CREATE USER '{new_user}'@'{new_host}' idENTIFIED BY '{new_password}';"
            query_grant_privileges = f"GRANT ALL PRIVILEGES ON *.* TO '{new_user}'@'{new_host}' WITH GRANT OPTION;"
            query_flush_privileges = "FLUSH PRIVILEGES;"
            cursor.execute(query_create_user)
            cursor.execute(query_grant_privileges)
            cursor.execute(query_flush_privileges)
            connection.commit()  # لحفظ التغييرات
        # إغلاق الاتصال
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            QMessageBox.critical(self, ' قاعدة البيانات', f"خطأ: اسم المستخدم أو كلمة المرور غير صحيحة.")
            sys.exit()
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            QMessageBox.critical(self, ' قاعدة البيانات', f"خطأ: قاعدة البيانات غير موجودة.")
            sys.exit()
        else:
            QMessageBox.critical(self, ' قاعدة البيانات', f"خطأ غير متوقع: {err}")
            sys.exit()
    except Exception as e:
        QMessageBox.critical(self, ' قاعدة البيانات', f"حدث خطأ: هناك مشكلة في الوصول لقاعدة البيانات تحقق من كلمة المرور او اتصل بالمطور {e}")
        sys.exit()
    except Error as e:
        QMessageBox.critical(self, ' قاعدة البيانات', f'حدثت مشكلة اثناء الإتصال بقاعدة البيانات ... قم بإعادة تشغيل الكمبيوتر ... في حالة لم يتم حل المشكلة اتصل بالمطور')
        sys.exit()

#ايقونه الغاء التثبيت
# ابحث عن مفتاح فرعي صحيح
def find_correct_subkey():
    try:
        # تحديد المسار الرئيسي
        root = reg.HKEY_LOCAL_MACHINE
        parent_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
        # فتح المفتاح الرئيسي
        with reg.OpenKey(root, parent_key, 0, reg.KEY_READ) as key:
            # تعداد المفاتيح الفرعية
            i = 0
            while True:
                try:
                    subkey_name = reg.EnumKey(key, i)
                    if "منظومة المهندس1" in subkey_name:
                        return f"{parent_key}\\{subkey_name}"
                    i += 1
                except OSError:
                    break
        return None
    except Exception as e:
        print(f"حدث خطأ أثناء البحث عن المفتاح: {e}")
        return None

#ايقونه الغاء التثبيت
# إضافة مفتاح التسجيل
def add_registry_key(self):
    try:
        # البحث عن المفتاح الفرعي الصحيح
        subkey = find_correct_subkey()
        if not subkey:
            print("لم يتم العثور على مفتاح مناسب.")
            return
        # فتح المفتاح أو إنشاؤه إذا لم يكن موجودًا
        root = reg.HKEY_LOCAL_MACHINE
        key = reg.CreateKeyEx(root, subkey, 0, reg.KEY_WRITE)

        # تحديد قيمة المفتاح
        value_name = "DisplayIcon"
        value_data = r"C:\\Program Files\\منظومة المهندس1\\icon_app.ico"
        # إضافة القيمة إلى الريجستري
        reg.SetValueEx(key, value_name, 0, reg.REG_SZ, value_data)
        # إغلاق المفتاح
        reg.CloseKey(key)
    except PermissionError:
        QMessageBox.critical(self, 'ايقونه الغاء التثبيت', "تحتاج إلى تشغيل السكربت كمسؤول.")
        sys.exit()
    except Exception as e:
        QMessageBox.critical(self, 'ايقونه الغاء التثبيت', f"حدث خطأ: {e}")



#اعدادات المستخدم///////////////////////////////////////////////////////
# قاعدة بيانات Ueser
def ueser_database(self):
    try:

        db_name = f"project_manager2_user"
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cursor = conn.cursor()

        # إنشاء قاعدة بيانات إذا لم تكن موجودة
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")

        # تعريف الجداول والأعمدة المطلوبة
        tables = {
            "users": [
                ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                ("username", "TEXT"),
                ("password_hash", "TEXT"),
                ("user_permissions", "TEXT"),
                ("Security_question", "TEXT"),
                ("Permissions_details", "TEXT"),

            ],

            "company": [
                ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                ("company_name", "TEXT"),
                ("company_logo", "TEXT"),
                ("Currency_type", "TEXT"),
                ("phone_number", "TEXT"),     # رقم الهاتف
                ("address", "TEXT"),
                ("email", "TEXT")

            ],

            "License_Status": [
              ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                ("license_type" ,"TEXT"),
                ("start_date" ,"TEXT"),
                ("end_date" ,"TEXT"),
            ],
        }

        # التحقق من وجود الجداول وتحديث الأعمدة
        for table_name, columns in tables.items():
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(f'{col} {dtype}' for col, dtype in columns)})")
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            existing_columns = {row[0] for row in cursor.fetchall()}

            # إضافة أعمدة جديدة إذا لم تكن موجودة
            for column_name, column_type in columns:
                if column_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

            # حذف الأعمدة غير المطلوبة
            for column in existing_columns - {col[0] for col in columns}:
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column}")

            # تعديل ترتيب الأعمدة (يتطلب إعادة إنشاء الجدول)
            reordered_columns = ", ".join([f"{col[0]} {col[1]}" for col in columns])
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name}_temp (
                    {reordered_columns}
                )
            """)
            cursor.execute(f"INSERT INTO {table_name}_temp SELECT * FROM {table_name}")
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"RENAME TABLE {table_name}_temp TO {table_name}")


            # التحقق من وجود الفهارس قبل إنشائها
        # إنشاء فهرس إن لم يكن موجودًا
        def create_index_if_not_exists(table, index_name, column, prefix_length=None):
            cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = '{index_name}'")
            if not cursor.fetchone():
                if prefix_length:
                    cursor.execute(f"CREATE INDEX {index_name} ON {table} ({column}({prefix_length}))")
                else:
                    cursor.execute(f"CREATE INDEX {index_name} ON {table} ({column})")

        # إنشاء الفهارس
        # create_index_if_not_exists('المشاريع', 'idx_المشاريع_الحالة', 'الحالة', 255)
        
        conn.commit()
        conn.close()

    except mysql.connector.Error as e:
        QMessageBox.critical(self, 'المستخدم قاعدة البيانات', f'لم يتم الوصول لقاعدة البيانات ... اتصل بالمطور لحل المشكلة\n{str(e)}')
        sys.exit()

#سجل الديون db ///////////////////////////////////////////////////////
# قاعدة بيانات الديون
def debts_database(self):
    try:

        db_name = f"project_manager2_debts"
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cursor = conn.cursor()

        # إنشاء قاعدة بيانات إذا لم تكن موجودة
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")

        # تعريف الجداول والأعمدة المطلوبة
        tables = {
            "حسابات_الديون": [
                ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                ("اسم_الحساب", "TEXT"),
                ("رقم_الهاتف", "TEXT"),
                ("نوع_الحساب", "TEXT"),
                ("الوصف", "TEXT"),
                ("المبلغ", "INT DEFAULT 0" ),
                ("المدفوع", "INT DEFAULT 0" ),
                ("الباقي", "INT DEFAULT 0" ),
                ("التاريخ", "DATE"),
                ("ملاحظات", "TEXT"),

            ],

            "سجل_الديون": [
                ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                ("معرف_الحساب" ,"INT"),
                ("اسم_الحساب", "TEXT"),
                ("نوع_الحساب" ,"TEXT"),
                ("الوصف", "TEXT"),
                ("المبلغ", "INT DEFAULT 0"),
                ("الباقي", "INT DEFAULT 0"),
                ("تاريخ_الدين", "DATE"),
                ("تاريخ_السداد", "TEXT"),
                ("ملاحظات", "TEXT"),

            ],

            "دفعات_الديون": [
              ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                ("معرف_الحساب" ,"INT"),
                ("اسم_الحساب", "TEXT"),
                ("نوع_الحساب" ,"TEXT"),
                ("وصف_المدفوع" ,"TEXT"),
                ("المبلغ_المدفوع" ,"INT DEFAULT 0"),
                ("تاريخ_الدفع" ,"DATE"),
                ("رقم_الفاتورة", "TEXT"),
                ("ملاحظات", "TEXT"),
            ],
        }

        # التحقق من وجود الجداول وتحديث الأعمدة
        for table_name, columns in tables.items():
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(f'{col} {dtype}' for col, dtype in columns)})")
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            existing_columns = {row[0] for row in cursor.fetchall()}

            # إضافة أعمدة جديدة إذا لم تكن موجودة
            for column_name, column_type in columns:
                if column_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

            # حذف الأعمدة غير المطلوبة
            for column in existing_columns - {col[0] for col in columns}:
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column}")

            # تعديل ترتيب الأعمدة (يتطلب إعادة إنشاء الجدول)
            reordered_columns = ", ".join([f"{col[0]} {col[1]}" for col in columns])
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name}_temp (
                    {reordered_columns}
                )
            """)
            cursor.execute(f"INSERT INTO {table_name}_temp SELECT * FROM {table_name}")
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"RENAME TABLE {table_name}_temp TO {table_name}")


            # التحقق من وجود الفهارس قبل إنشائها
        # إنشاء فهرس إن لم يكن موجودًا
        def create_index_if_not_exists(table, index_name, column, prefix_length=None):
            cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = '{index_name}'")
            if not cursor.fetchone():
                if prefix_length:
                    cursor.execute(f"CREATE INDEX {index_name} ON {table} ({column}({prefix_length}))")
                else:
                    cursor.execute(f"CREATE INDEX {index_name} ON {table} ({column})")

        # إنشاء الفهارس
        # create_index_if_not_exists('المشاريع', 'idx_المشاريع_الحالة', 'الحالة', 255)
        

        conn.commit()
        conn.close()

        return

    except mysql.connector.Error as e:
        QMessageBox.critical(self, 'المستخدم قاعدة البيانات', f'لم يتم الوصول لقاعدة البيانات ... اتصل بالمطور لحل المشكلة\n{str(e)}')
        sys.exit()

# جدوالترخيص  ========================================================================================
# حالة ترخيص DB
def DB_license_status(self,license_type,end_date_input, start_date=None):
    change_root_password(self,"kh123456")
    try:
        db_name = "project_manager2_user"
        conn = mysql.connector.connect(host=host, user=user_r, password=password_r)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        # تعريف جدول الترخيص
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS License_Status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                license_type TEXT,
                start_date TEXT,
                end_date TEXT
            )
        """)
        # حساب تاريخ النهاية بناءً على نوع الترخيص
        if start_date is None:
            start_date = datetime.now()

        if license_type == "trial":
            end_date = end_date_input
        elif license_type == "annual":
            end_date = end_date_input
        elif license_type == "permanent":
            end_date = "permanent"
        else:
            raise ValueError("Invalid license type.")
        # تحويل التواريخ إلى نصوص
        start_date_str = start_date.strftime('%Y-%m-%d')
        # تشفير البيانات
        hashed_license_type = bcrypt.hashpw(license_type.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        hashed_start_date = bcrypt.hashpw(start_date_str.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') #if end_date != "permanent" else "permanent"
        hashed_end_date = bcrypt.hashpw(end_date.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # تحديث أو إدخال بيانات الترخيص
        cursor.execute("SELECT id FROM License_Status LIMIT 1")
        if cursor.fetchone():
            cursor.execute("""
                UPDATE License_Status
                SET license_type = %s, start_date = %s, end_date = %s
                WHERE id = 1
            """, (hashed_license_type, hashed_start_date, hashed_end_date))
        else:
            cursor.execute("""
                INSERT INTO License_Status (license_type, start_date, end_date)
                VALUES (%s, %s, %s)
            """, (hashed_license_type, hashed_start_date, hashed_end_date))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating license status: {e}")


#------------استيراد ملفات اكسل ---------------------
# افتح Excel إلى DB Dialog
def open_excel_to_db_dialog(self,parent=None):
    # Initialize dialog
    dialog = QDialog(self)
    dialog.setLayoutDirection(Qt.RightToLeft)
    dialog.setWindowTitle("Excel to Database Importer")
    dialog.setGeometry(100, 100, 1200, 800)
    db_name = f"project_manager_V2"

    # Initialize database connection
    conn = None
    cursor = None
    table_columns = {}

    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=db_name)
        cursor = conn.cursor()

        # Fetch table names
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        # Fetch columns for each table
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            table_columns[table] = [(col[0], str(col[1], encoding="utf-8").split('(')[0].upper() if isinstance(col[1], bytes) else col[1].split('(')[0].upper()) for col in columns if col[0] != "id"]

    except mysql.connector.Error as err:
        QMessageBox.critical(dialog, "خطأ", f"فشل الاتصال بقاعدة البيانات: {err}")
        return

    # Store Excel data and mappings
    excel_df = None
    excel_columns = []
    column_mappings = {}
    selected_db_columns = set()

    # Main widget and layout
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    # Table selection
    table_selection_layout = QHBoxLayout()
    table_combo = QComboBox()
    table_combo.addItems(table_columns.keys())
    table_selection_layout.addWidget(QLabel("اختر الجدول:"))
    # table_combo.setStyleSheet("""
    #     QComboBox {
    #         font-size: 14px;
    #         padding: 5px;
    #     }
    #     QComboBox::drop-down {
    #         width: 20px;
    #     }
    # """)
    table_selection_layout.addWidget(table_combo)

    # Excel file upload
    upload_button = QPushButton("رفع ملف Excel")
    # upload_button.setStyleSheet("""
    #     QPushButton {
    #         font-size: 14px;
    #         padding: 5px;
    #     }
    # """)
    table_selection_layout.addWidget(upload_button)

    main_layout.addLayout(table_selection_layout)

    # Table columns display
    table_columns_table = QTableWidget()
    table_columns_table.setRowCount(1)
    table_columns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_layout.addWidget(QLabel("أعمدة الجدول في قاعدة البيانات:"))
    main_layout.addWidget(table_columns_table)

    # Excel columns and data preview (merged)
    mapping_table = QTableWidget()
    mapping_table.setRowCount(4)
    mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_layout.addWidget(QLabel("أعمدة ملف Excel ومعاينة البيانات (أول 4 صفوف):"))
    main_layout.addWidget(mapping_table)

    # Mapping combo boxes table
    combo_table = QTableWidget()
    combo_table.setRowCount(1)
    combo_table.setColumnCount(0)
    combo_table.setVerticalHeaderLabels(["عمود قاعدة البيانات"])
    combo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_layout.addWidget(QLabel("ربط أعمدة Excel بأعمدة قاعدة البيانات:"))
    main_layout.addWidget(combo_table)

    # Import button
    import_button = QPushButton("استيراد البيانات")
    import_button.setStyleSheet("""
        QPushButton {
            font-size: 14px;
            padding: 5px;
        }
    """)
    main_layout.addWidget(import_button)
    center_all_widgets(table_selection_layout)
    center_all_widgets(dialog)
    center_all_widgets(main_layout)
    center_all_widgets(main_widget)

    table_setting(combo_table)
    table_setting(mapping_table)
    #table_setting(table_columns_table)



    dialog.setLayout(main_layout)

    # عرض أعمدة جدول
    def display_table_columns(table_name):
        columns = table_columns.get(table_name, [])
        table_columns_table.setColumnCount(len(columns))
        table_columns_table.setRowCount(1)

        table_columns_table.setHorizontalHeaderLabels([col[0] for col in columns])

        for col_idx, (col_name, col_type) in enumerate(columns):
            #table_columns_table.setItem(0, col_idx, QTableWidgetItem(col_name))
            display_type = get_display_type(col_type)
            table_columns_table.setItem(0, col_idx, QTableWidgetItem(display_type))

        table_columns_table.resizeColumnsToContents()
        table_columns_table.hide()

    # احصل على نوع العرض
    def get_display_type(col_type):
        if col_type in ["FLOAT", "INT", "INTEGER"]:
            return "رقم"
        elif col_type == "DATE":
            return "تاريخ"
        else:
            return "نص"

    # على الطاولة تغيرت
    def on_table_changed(table_name):
        display_table_columns(table_name)
        if excel_columns:
            selected_db_columns.clear()
            column_mappings.clear()
            display_excel_columns()

    # تحميل Excel
    def upload_excel():
        nonlocal excel_df, excel_columns
        file_path, _ = QFileDialog.getOpenFileName(dialog, "اختر ملف Excel", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                excel_df = pd.read_excel(file_path)
                excel_columns = excel_df.columns.tolist()
                selected_db_columns.clear()
                column_mappings.clear()
                display_excel_columns()
            except Exception as e:
                QMessageBox.critical(dialog, "خطأ", f"فشل تحميل ملف Excel: {e}")

    # عرض أعمدة Excel
    def display_excel_columns():
        mapping_table.setRowCount(3)
        mapping_table.setColumnCount(len(excel_columns))
        combo_table.setColumnCount(len(excel_columns))

        mapping_table.setHorizontalHeaderLabels(excel_columns)
        combo_table.setHorizontalHeaderLabels(excel_columns)

        selected_table = table_combo.currentText()
        db_columns = [""] + [col[0] for col in table_columns.get(selected_table, [])]

        for col_idx, excel_col in enumerate(excel_columns):
            #mapping_table.setItem(0, col_idx, QTableWidgetItem(excel_col))

            col_data = excel_df[excel_col]
            if pd.api.types.is_integer_dtype(col_data):
                data_type = "رقم"
            elif pd.api.types.is_float_dtype(col_data):
                data_type = "رقم"
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                data_type = "تاريخ"
            else:
                data_type = "نص"
            mapping_table.setItem(0, col_idx, QTableWidgetItem(data_type))

            combo = QComboBox()
            available_columns = [""] + [col for col in db_columns[1:] if col not in selected_db_columns]
            combo.addItems(available_columns)
            combo.currentTextChanged.connect(lambda text, idx=col_idx: on_combo_changed(text, idx))
            combo_table.setCellWidget(0, col_idx, combo)

        preview_rows = min(3, len(excel_df))
        for row_idx in range(preview_rows):
            for col_idx, excel_col in enumerate(excel_columns):
                value = excel_df.iloc[row_idx][excel_col]
                value_str = str(value) if pd.notnull(value) else ""
                mapping_table.setItem(row_idx + 1, col_idx, QTableWidgetItem(value_str))

        for row_idx in range(preview_rows, 3):
            for col_idx in range(len(excel_columns)):
                mapping_table.setItem(row_idx + 1, col_idx, QTableWidgetItem(""))

        mapping_table.resizeColumnsToContents()
        combo_table.resizeColumnsToContents()

    # على التحرير والسرد تغيرت
    def on_combo_changed(selected_db_col, col_idx):
        combo = combo_table.cellWidget(0, col_idx)
        previous_selection = combo.property("previous_selection") or ""

        if previous_selection and previous_selection in selected_db_columns:
            selected_db_columns.remove(previous_selection)
        if selected_db_col:
            selected_db_columns.add(selected_db_col)

        combo.setProperty("previous_selection", selected_db_col)

        selected_table = table_combo.currentText()
        db_columns = [""] + [col[0] for col in table_columns.get(selected_table, [])]

        for idx in range(len(excel_columns)):
            combo = combo_table.cellWidget(0, idx)
            current_selection = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            available_columns = [""] + [col for col in db_columns[1:] if col not in selected_db_columns or col == current_selection]
            combo.addItems(available_columns)
            combo.setCurrentText(current_selection)
            combo.blockSignals(False)

    # التحقق من صحة أنواع البيانات
    def validate_data_types():
        selected_table = table_combo.currentText()
        db_columns = {col[0]: col[1] for col in table_columns.get(selected_table, [])}
        column_mappings.clear()

        for col_idx, excel_col in enumerate(excel_columns):
            combo = combo_table.cellWidget(0, col_idx)
            db_col = combo.currentText()
            data_type_item = mapping_table.item(1, col_idx)
            excel_data_type = data_type_item.text() if data_type_item else "نص"

            if db_col:
                db_data_type = db_columns.get(db_col)
                if db_data_type in ["TEXT", "VARCHAR"]:
                    pass
                elif excel_data_type == "رقم" and db_data_type not in ["INT", "INTEGER", "FLOAT"]:
                    return False, f"نوع بيانات العمود '{excel_col}' (رقم) لا يتطابق مع '{db_col}' ({db_data_type})"
                elif excel_data_type == "تاريخ" and db_data_type != "DATE":
                    return False, f"نوع بيانات العمود '{excel_col}' (تاريخ) لا يتطابق مع '{db_col}' ({db_data_type})"
                elif excel_data_type == "نص" and db_data_type not in ["TEXT", "VARCHAR", "CHAR"]:
                    return False, f"نوع بيانات العمود '{excel_col}' (نص) لا يتطابق مع '{db_col}' ({db_data_type})"
                column_mappings[excel_col] = db_col

        return True, ""

    # استيراد البيانات
    def import_data():
        if excel_df is None:
            QMessageBox.warning(dialog, "تحذير", "يرجى رفع ملف Excel أولاً")
            return

        selected_table = table_combo.currentText()
        valid, error_msg = validate_data_types()

        if not valid:
            QMessageBox.critical(dialog, "خطأ", error_msg)
            return

        try:
            columns = list(column_mappings.values())
            if not columns:
                conn.rollback()
                QMessageBox.warning(dialog, "تحذير", "يرجى ربط عمود واحد على الأقل")
                return

            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO {selected_table} ({', '.join(columns)}) VALUES ({placeholders})"

            for _, row in excel_df.iterrows():
                values = []
                is_empty_row = True
                for excel_col in column_mappings.keys():
                    value = row[excel_col]
                    if pd.isna(value) or value == "":
                        values.append(None)
                    else:
                        values.append(value)
                        is_empty_row = False

                if not is_empty_row:
                    cursor.execute(query, values)

            conn.commit()
            QMessageBox.information(dialog, "نجاح", "تم استيراد البيانات بنجاح")

        except mysql.connector.Error as err:
            conn.rollback()
            QMessageBox.critical(dialog, "خطأ", f"فشل استيراد البيانات: {err}")

    table_combo.currentTextChanged.connect(on_table_changed)
    upload_button.clicked.connect(upload_excel)
    import_button.clicked.connect(import_data)

    #display_table_columns(table_combo.currentText())

    dialog.exec_()

    if conn:
        conn.close()




