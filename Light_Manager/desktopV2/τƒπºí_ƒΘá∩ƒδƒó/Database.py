# cSpell:disable
"""
نظام إدارة قاعدة البيانات المحسن
تم إعادة هيكلة وتحسين نظام إنشاء الجداول بطريقة احترافية ومترابطة
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import logging

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات المحسن"""
    
    def __init__(self, host='localhost', user='pme', password='kh123456'):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = 'project_manager_V2'
        self.connection = None
        self.cursor = None
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
            return self.connection
        except Error as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            return None
    
    def close_connection(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def create_database_if_not_exists(self) -> bool:
        """إنشاء قاعدة البيانات والجداول بطريقة احترافية"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            self.cursor = conn.cursor()
            
            # إنشاء قاعدة البيانات
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self.cursor.execute(f"USE `{self.db_name}`")
            
            logger.info("بدء إنشاء الجداول...")
            
            # إنشاء الجداول حسب الوحدات
            self._create_system_tables()
            self._create_hr_tables()
            self._create_project_tables()
            self._create_accounting_tables()
            self._create_training_tables()
            self._create_audit_tables()
            
            # إنشاء الفهارس
            self._create_indexes()
            
            # إنشاء المشغلات (Triggers)
            self._create_triggers()
            
            # إدراج البيانات الافتراضية
            self._insert_default_data()
            
            conn.commit()
            logger.info("تم إنشاء قاعدة البيانات والجداول بنجاح")
            return True
            
        except Error as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            self.close_connection()
    
    def انشاء_جداول_النظام(self):
        """إنشاء جداول النظام والإعدادات"""
        logger.info("إنشاء جداول النظام...")
        
        # جدول الإعدادات العامة
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `إعدادات_النظام` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `المفتاح` VARCHAR(100) NOT NULL UNIQUE,
                `القيمة` TEXT,
                `نوع_البيانات` ENUM('string', 'number', 'boolean', 'json', 'date') DEFAULT 'string',
                `الوصف` TEXT,
                `قابل_للتعديل` BOOLEAN DEFAULT TRUE,
                `المجموعة` VARCHAR(50) DEFAULT 'عام',
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_المفتاح` (`المفتاح`),
                INDEX `idx_المجموعة` (`المجموعة`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
    def انشاء_جداول_الموارد_البشرية(self):
        """إنشاء جداول الموارد البشرية (العملاء والموظفين)"""
        logger.info("إنشاء جداول الموارد البشرية...")
        # جدول العملاء المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `العملاء` (
                `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                `معرف_التصنيف` INT,
                `اسم_العميل` VARCHAR(255) NOT NULL,
                `العنوان` VARCHAR(255),
                `رقم_الهاتف` VARCHAR(50),
                `الايميل` VARCHAR(100),
                `تاريخ_الحساب` DATE,

                `رصيد_العميل` DECIMAL(15,2) DEFAULT 0,
                `التقييم` INT DEFAULT 0 CHECK (`التقييم` BETWEEN 0 AND 5),
                `ملاحظات` TEXT,

                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإضافة`)) STORED,
                INDEX `idx_السنة` (`السنة`),
                INDEX `idx_الاسم_العميل` (`اسم_العميل`),
                INDEX `idx_رقم_الهاتف` (`رقم_الهاتف`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الموظفين المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_التصنيف` INT,
                `اسم_الموظف` VARCHAR(255) NOT NULL,
                `العنوان` VARCHAR(255),
                `رقم_الهاتف` VARCHAR(50),
                `الايميل` VARCHAR(100),
                `الوظيفة` VARCHAR(255),
                `تاريخ_التوظيف` DATE,
                `المرتب` DECIMAL(15,2) DEFAULT 0,
                `نسبة_العمولة` DECIMAL(5,2) DEFAULT 0,
                `الرصيد` DECIMAL(15,2) DEFAULT 0,
                `الحالة` ENUM('نشط', 'إجازة', 'مستقيل', 'مفصول', 'غير نشط') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `جدولة_المرتب_تلقائية` BOOLEAN DEFAULT FALSE,
                `خاضع_لنظام_الحضور` BOOLEAN DEFAULT TRUE,
                
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التوظيف`)) STORED,
                INDEX `idx_الاسم_الموظف` (`اسم_الموظف`),
                INDEX `idx_الوظيفة` (`الوظيفة`),
                INDEX `idx_الرصيد` (`الرصيد`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المعاملات المالية للموظفين المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الموظفين_معاملات_مالية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `رقم_المعاملة` VARCHAR(50) UNIQUE,
                `النوع` ENUM('إيداع', 'سحب', 'خصم', 'عمولة', 'مكافأة') NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `الوصف` VARCHAR(255),
                `التاريخ` DATE NOT NULL,
                `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل_بنكي', 'أجل') DEFAULT 'نقدي',
                `معرف_القيد_المحاسبي` INT,

                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_التاريخ` (`التاريخ`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول حضور وانصراف الموظفين المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الموظفين_الحضور` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `التاريخ` DATE NOT NULL,
                `اليوم` VARCHAR(20) GENERATED ALWAYS AS (DAYNAME(`التاريخ`)) STORED,
                `وقت_الحضور` TIME,
                `وقت_الانصراف` TIME,
                `ساعات_العمل` DECIMAL(4,2) GENERATED ALWAYS AS (
                    CASE 
                        WHEN `وقت_الحضور` IS NOT NULL AND `وقت_الانصراف` IS NOT NULL 
                        THEN TIME_TO_SEC(TIMEDIFF(`وقت_الانصراف`, `وقت_الحضور`)) / 3600
                        ELSE 0
                    END
                ) STORED,
                `حالة_الحضور` ENUM('حاضر', 'متأخر', 'غائب', 'إجازة', 'مرضية', 'مأمورية') DEFAULT 'حاضر',
                `دقائق_التأخير` INT DEFAULT 0,
                `دقائق_المغادرة_المبكرة` INT DEFAULT 0,
                `ساعات_إضافية` DECIMAL(4,2) DEFAULT 0,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,
                UNIQUE KEY `unique_attendance` (`معرف_الموظف`, `التاريخ`),
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_التاريخ` (`التاريخ`),
                INDEX `idx_حالة_الحضور` (`حالة_الحضور`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول تقييم الموظفين المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الموظفين_التقييمات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `معرف_المرجع` INT COMMENT 'معرف المشروع أو المهمة',

                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإضافة`)) STORED,
                
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_نوع_التقييم` (`نوع_التقييم`),
                INDEX `idx_المعدل` (`المعدل`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المقيم`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
    
    def انشاء_جداول_المشاريع(self):
        """إنشاء جداول المشاريع والمقاولات"""
        logger.info("إنشاء جداول المشاريع...")
        
        # جدول المشاريع المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المشاريع` (
                `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                `القسم` ENUM('المشاريع', 'المقاولات') DEFAULT 'المشاريع',
                `معرف_التصنيف` INT,
                `معرف_العميل` INT NOT NULL,
                `معرف_المهندس` INT,
                
                `اسم_المشروع` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `الموقع` VARCHAR(255),
                `المساحة` DECIMAL(15,2) DEFAULT 0,
                `المبلغ` DECIMAL(15,2) DEFAULT 0,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `الباقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ` - `المدفوع`) STORED,

                `تاريخ_البداية` DATE,
                `تاريخ_النهاية_المخطط` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `المدة_بالأيام` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية`)) STORED,
                `الوقت_المتبقي` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية`)) STORED,
                `الحالة` ENUM('جديد', 'قيد_التنفيذ', 'متوقف', 'مكتمل', 'ملغي', 'قيد_التسليم') DEFAULT 'جديد',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `ملاحظات` TEXT,


                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                INDEX `idx_رقم_المشروع` (`رقم_المشروع`),
                INDEX `idx_القسم` (`القسم`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_معرف_العميل` (`معرف_العميل`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_المدير`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مراحل المشروع المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المشاريع_المراحل` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_المرحلة` VARCHAR(50),
                `اسم_المرحلة` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `معرف_سعر_المرحلة` INT,
                `الوحدة` VARCHAR(50),
                `الكمية` DECIMAL(15,3) DEFAULT 0,
                `سعر_الوحدة` DECIMAL(15,2) DEFAULT 0,
                `الإجمالي` DECIMAL(15,2) GENERATED ALWAYS AS (`الكمية` * `سعر_الوحدة`) STORED,
                `تاريخ_البداية` DATE,
                `تاريخ_النهاية` DATE,
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0 CHECK (`نسبة_الإنجاز` BETWEEN 0 AND 100),
                `الحالة` ENUM('مخطط', 'قيد_التنفيذ', 'مكتمل', 'متوقف', 'ملغي') DEFAULT 'مخطط',
                `حالة_المبلغ` ENUM('غير_مدرج', 'مدرج') DEFAULT 'غير_مدرج',
                `الترتيب` INT DEFAULT 0,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_سعر_المرحلة`) REFERENCES `أسعار_المراحل`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول فريق المشروع والمهام الموحد
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المشاريع_الفريق` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `نوع_المهمة` ENUM('مهمة عامة', 'مرحلة في المقاولات', 'المقاولات', 'مرحلة في مشروع',' مشروع') NOT NULL,
                `معرف_المرجع` INT DEFAULT NULL,
                `معرف_المرحلة` INT DEFAULT NULL,

                `عنوان_المهمة` VARCHAR(255),
                `وصف_المهمة` TEXT,
                `نسبة_العمولة` DECIMAL(5,2) DEFAULT 0,
                `المبلغ_الإجمالي` DECIMAL(15,2),
                `حالة_المبلغ` ENUM('غير_مدرج', 'مدرج') DEFAULT 'غير_مدرج',

                `تاريخ_البداية` DATE,
                `تاريخ_النهاية` DATE,
                `حالة_المهمة` ENUM('مخطط', 'قيد_التنفيذ', 'مكتمل', 'متأخر', 'ملغي','متوقف') DEFAULT 'مخطط',
                `ملاحظات` TEXT,

                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(COALESCE(`تاريخ_البداية`, `تاريخ_الإضافة`))) STORED,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_نوع_المهمة` (`نوع_المهمة`),
                INDEX `idx_معرف_المرجع` (`معرف_المرجع`),
                INDEX `idx_معرف_المرحلة` (`معرف_المرحلة`),
                INDEX `حالة_المهمة` (`حالة_المهمة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المرحلة`) REFERENCES `المشاريع_المراحل`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المدفوعات الموحد
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المدفوعات` (
                `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                `رقم_الدفعة` VARCHAR(50) UNIQUE,
                `النوع` ENUM('دفعة_مشروع', 'دفعة_عهدة', 'دفعة_مورد', 'دفعة_دين', 'دفعة_تدريب') NOT NULL,
                `معرف_المرجع` INT NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_الدفع` DATE NOT NULL,
                `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل_بنكي', 'أجل') DEFAULT 'نقدي',
                `رقم_المرجع` VARCHAR(100),
                `البنك` VARCHAR(100),
                `الوصف` TEXT,
                `المستلم` VARCHAR(255),
                `الخصم` DECIMAL(15,2) DEFAULT 0,
                `صافي_المبلغ` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ` - `الخصم`) STORED,
                `معرف_القيد_المحاسبي` INT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الدفع`)) STORED,
                INDEX `idx_رقم_الدفعة` (`رقم_الدفعة`),
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_معرف_المرجع` (`معرف_المرجع`),
                INDEX `idx_تاريخ_الدفع` (`تاريخ_الدفع`),
                INDEX `idx_السنة` (`السنة`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول العهد المالية للمقاولات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المقاولات_العهد` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_العهدة` VARCHAR(50) UNIQUE,
                `الوصف` VARCHAR(255),
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `نسبة_المكتب` DECIMAL(5,2) DEFAULT 0,
                `عمولة_المكتب` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ` * `نسبة_المكتب` / 100) STORED,
                `المصروف` DECIMAL(15,2) DEFAULT 0,
                `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ` - `عمولة_المكتب` - `المصروف`) STORED,
                `تاريخ_الاستلام` DATE NOT NULL,
                `تاريخ_الإغلاق` DATE,
                `الحالة` ENUM('مفتوحة', 'مغلقة', 'مرحلة') DEFAULT 'مفتوحة',
                `معرف_العهدة_السابقة` INT,
                `مبلغ_مرحل` DECIMAL(15,2) DEFAULT 0,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الاستلام`)) STORED,
                INDEX `idx_رقم_العهدة` (`رقم_العهدة`),
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_العهدة_السابقة`) REFERENCES `المقاولات_العهد`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المصروفات الموحد
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المصروفات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المصروف` VARCHAR(50) UNIQUE,
                `النوع` ENUM('مصروف_عام', 'مصروف_مشروع', 'مصروف_عهدة', 'خسائر', 'مردودات') NOT NULL,
                `معرف_التصنيف` INT,
                `معرف_المرجع` INT COMMENT 'معرف المشروع أو العهدة',
                `الوصف` VARCHAR(255) NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_المصروف` DATE NOT NULL,
                `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل_بنكي', 'أجل') DEFAULT 'نقدي',
                `رقم_الفاتورة` VARCHAR(100),
                `المورد` VARCHAR(255),
                `المسؤول` VARCHAR(255),
                `متحمل_الخسائر` ENUM('الشركة', 'موظف', 'مقاول', 'عميل') DEFAULT 'الشركة',
                `معرف_المتحمل` INT,
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المصروف`)) STORED,
                INDEX `idx_رقم_المصروف` (`رقم_المصروف`),
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_معرف_المرجع` (`معرف_المرجع`),
                INDEX `idx_تاريخ_المصروف` (`تاريخ_المصروف`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المرفقات الموحد
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المرفقات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `النوع` ENUM('مشروع', 'عميل', 'موظف', 'مصروف', 'عقد', 'أخرى') NOT NULL,
                `معرف_المرجع` INT NOT NULL,
                `اسم_الملف` VARCHAR(255) NOT NULL,
                `نوع_الملف` VARCHAR(50) NOT NULL,
                `امتداد_الملف` VARCHAR(10),
                `حجم_الملف` BIGINT DEFAULT 0,
                `المسار` VARCHAR(500) NOT NULL,
                `الوصف` TEXT,
                `العلامات` JSON,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_معرف_المرجع` (`معرف_المرجع`),
                INDEX `idx_نوع_الملف` (`نوع_الملف`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
    
    def جداول_الموردين(self):

        # جدول الموردين المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الموردين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الشخص` INT NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `رقم_المورد` VARCHAR(50) UNIQUE,
                `نوع_المورد` ENUM('محلي', 'دولي') DEFAULT 'محلي',
                `معرف_حساب_المورد` VARCHAR(20),
                `شروط_الدفع` VARCHAR(100),
                `فترة_الائتمان` INT DEFAULT 0,
                `الحد_الائتماني` DECIMAL(15,2) DEFAULT 0,
                `إجمالي_المشتريات` DECIMAL(15,2) DEFAULT 0,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `الرصيد` DECIMAL(15,2) GENERATED ALWAYS AS (`إجمالي_المشتريات` - `المدفوع`) STORED,
                `التقييم` INT DEFAULT 0 CHECK (`التقييم` BETWEEN 0 AND 5),
                `الحالة` ENUM('نشط', 'غير_نشط', 'محظور') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإضافة`)) STORED,
                INDEX `idx_رقم_المورد` (`رقم_المورد`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الشخص`) REFERENCES `الأشخاص`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_حساب_المورد`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الفواتير الموحد
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الفواتير` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_الفاتورة` VARCHAR(50) UNIQUE NOT NULL,
                `نوع_الفاتورة` ENUM('مبيعات', 'مشتريات', 'مرتجع_مبيعات', 'مرتجع_مشتريات') NOT NULL,
                `معرف_العميل` INT,
                `معرف_المورد` INT,
                `التاريخ` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `المبلغ_الإجمالي` DECIMAL(15,2) NOT NULL,
                `الخصم` DECIMAL(15,2) DEFAULT 0,
                `الضريبة` DECIMAL(15,2) DEFAULT 0,
                `المبلغ_الصافي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ_الإجمالي` - `الخصم` + `الضريبة`) STORED,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ_الصافي` - `المدفوع`) STORED,
                `الحالة` ENUM('مسودة', 'معتمدة', 'مدفوعة_جزئيا', 'مدفوعة_كليا', 'ملغاة') DEFAULT 'مسودة',
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,
                INDEX `idx_رقم_الفاتورة` (`رقم_الفاتورة`),
                INDEX `idx_نوع_الفاتورة` (`نوع_الفاتورة`),
                INDEX `idx_التاريخ` (`التاريخ`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

    def جداول_الديون_والذمم(self):

        # جدول الديون والذمم
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الذمم` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `النوع` ENUM('ذمة_مدينة', 'ذمة_دائنة') NOT NULL,
                `معرف_الشخص` INT NOT NULL,
                `معرف_التصنيف` INT,
                `الوصف` VARCHAR(255),
                `المبلغ_الأصلي` DECIMAL(15,2) NOT NULL,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ_الأصلي` - `المدفوع`) STORED,
                `تاريخ_النشوء` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `الحالة` ENUM('جارية', 'متأخرة', 'مسددة', 'معدومة') DEFAULT 'جارية',
                `أيام_التأخير` INT GENERATED ALWAYS AS (
                    CASE 
                        WHEN `تاريخ_الاستحقاق` IS NOT NULL AND CURDATE() > `تاريخ_الاستحقاق` AND `المتبقي` > 0
                        THEN DATEDIFF(CURDATE(), `تاريخ_الاستحقاق`)
                        ELSE 0
                    END
                ) STORED,
                `معرف_حساب_الذمة` VARCHAR(20),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_النشوء`)) STORED,
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_معرف_الشخص` (`معرف_الشخص`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الشخص`) REFERENCES `الأشخاص`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_حساب_الذمة`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

    def انشاء_جداول_التدريب(self):
        """إنشاء جداول التدريب"""
        logger.info("إنشاء جداول التدريب...")
        
        # جدول الدورات التدريبية
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `التدريب_الدورات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_التصنيف` INT,
                `رقم_الدورة` VARCHAR(50) UNIQUE,
                `عنوان_الدورة` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `معرف_المدرب` INT,
                `المكان` VARCHAR(255),
                `عدد_الساعات` INT DEFAULT 0,
                `التكلفة_الإجمالية` DECIMAL(15,2) DEFAULT 0,
                `سعر_الاشتراك` DECIMAL(15,2) DEFAULT 0,
                `الحد_الأدنى` INT DEFAULT 1,
                `الحد_الأقصى` INT DEFAULT 30,
                `تاريخ_البداية` DATE,
                `تاريخ_النهاية` DATE,
                `الحالة` ENUM('قيد_التسجيل', 'جارية', 'منتهية', 'ملغية', 'مؤجلة') DEFAULT 'قيد_التسجيل',
                `شهادة_معتمدة` BOOLEAN DEFAULT FALSE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                INDEX `idx_رقم_الدورة` (`رقم_الدورة`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_معرف_المدرب` (`معرف_المدرب`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_المدرب`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المجموعات التدريبية
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `التدريب_المجموعات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الدورة` INT NOT NULL,
                `اسم_المجموعة` VARCHAR(255) NOT NULL,
                `رقم_المجموعة` VARCHAR(50),
                `التوقيت` VARCHAR(255),
                `أيام_التدريب` JSON,
                `العدد_الحالي` INT DEFAULT 0,
                `العدد_المطلوب` INT DEFAULT 20,
                `الحالة` ENUM('مفتوحة', 'مكتملة', 'جارية', 'منتهية', 'ملغية') DEFAULT 'مفتوحة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_الدورة` (`معرف_الدورة`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_الدورة`) REFERENCES `التدريب_الدورات`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المتدربين
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `التدريب_المتدربون` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الشخص` INT NOT NULL,
                `معرف_الدورة` INT NOT NULL,
                `معرف_المجموعة` INT,
                `رقم_التسجيل` VARCHAR(50) UNIQUE,
                `رسوم_التسجيل` DECIMAL(15,2) DEFAULT 0,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`رسوم_التسجيل` - `المدفوع`) STORED,
                `تاريخ_التسجيل` DATE NOT NULL,
                `الحالة` ENUM('مسجل', 'منتظم', 'منقطع', 'منسحب', 'مكمل') DEFAULT 'مسجل',
                `نسبة_الحضور` DECIMAL(5,2) DEFAULT 0,
                `الدرجة_النهائية` DECIMAL(5,2),
                `حصل_على_شهادة` BOOLEAN DEFAULT FALSE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY `unique_registration` (`معرف_الشخص`, `معرف_الدورة`),
                INDEX `idx_رقم_التسجيل` (`رقم_التسجيل`),
                INDEX `idx_معرف_الدورة` (`معرف_الدورة`),
                INDEX `idx_معرف_المجموعة` (`معرف_المجموعة`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_الشخص`) REFERENCES `الأشخاص`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_الدورة`) REFERENCES `التدريب_الدورات`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المجموعة`) REFERENCES `التدريب_المجموعات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
    
    def انشاء_جداول_المحاسبة(self):
        """إنشاء جداول المحاسبة والمالية"""
        logger.info("إنشاء جداول المحاسبة...")
        
        # جدول شجرة الحسابات المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `شجرة_الحسابات` (
                `معرف_الحساب` VARCHAR(20) PRIMARY KEY,
                `اسم_الحساب` VARCHAR(255) NOT NULL,
                `نوع_الحساب` ENUM('أصول', 'خصوم', 'حقوق_الملكية', 'إيرادات', 'مصروفات') NOT NULL,
                `طبيعة_الحساب` ENUM('مدين', 'دائن') NOT NULL,
                `الحساب_الأب` VARCHAR(20),
                `المستوى` TINYINT NOT NULL DEFAULT 1 CHECK (`المستوى` BETWEEN 1 AND 5),
                `هو_حساب_تفصيلي` BOOLEAN DEFAULT FALSE,
                `الحالة` ENUM('نشط', 'غير_نشط', 'مؤرشف') DEFAULT 'نشط',
                `العملة` VARCHAR(10) DEFAULT 'SAR',
                `مركز_التكلفة_الافتراضي` VARCHAR(20),
                `الوصف` TEXT,
                `الترتيب` INT DEFAULT 0,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_نوع_الحساب` (`نوع_الحساب`),
                INDEX `idx_الحساب_الأب` (`الحساب_الأب`),
                INDEX `idx_المستوى` (`المستوى`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`الحساب_الأب`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE RESTRICT
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول القيود المحاسبية المحسن
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `القيود_المحاسبية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_القيد` VARCHAR(50) NOT NULL UNIQUE,
                `تاريخ_القيد` DATE NOT NULL,
                `نوع_القيد` ENUM('افتتاحي', 'يومي', 'تسوية', 'إقفال', 'عكسي') DEFAULT 'يومي',
                `مصدر_القيد` ENUM('يدوي', 'تلقائي', 'مستورد') DEFAULT 'يدوي',
                `البيان` VARCHAR(500) NOT NULL,
                `إجمالي_المدين` DECIMAL(15,2) NOT NULL,
                `إجمالي_الدائن` DECIMAL(15,2) NOT NULL,
                `حالة_القيد` ENUM('مسودة', 'معتمد', 'مرحل', 'ملغي') DEFAULT 'مسودة',
                `معرف_المعاملة_الأصلية` VARCHAR(100),
                `نوع_المعاملة_الأصلية` VARCHAR(50),
                `المرفقات` JSON,
                `المراجع` VARCHAR(50),
                `تاريخ_الاعتماد` DATETIME,
                `معتمد_بواسطة` VARCHAR(50),
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_القيد`)) STORED,
                INDEX `idx_رقم_القيد` (`رقم_القيد`),
                INDEX `idx_تاريخ_القيد` (`تاريخ_القيد`),
                INDEX `idx_نوع_القيد` (`نوع_القيد`),
                INDEX `idx_حالة_القيد` (`حالة_القيد`),
                INDEX `idx_السنة` (`السنة`),
                CHECK (`إجمالي_المدين` = `إجمالي_الدائن`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول تفاصيل القيود المحاسبية
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `تفاصيل_القيود` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_القيد` INT NOT NULL,
                `معرف_الحساب` VARCHAR(20) NOT NULL,
                `المبلغ_المدين` DECIMAL(15,2) DEFAULT 0,
                `المبلغ_الدائن` DECIMAL(15,2) DEFAULT 0,
                `البيان` VARCHAR(255),
                `مركز_التكلفة` VARCHAR(20),
                `المشروع` INT,
                `العملة` VARCHAR(10) DEFAULT 'SAR',
                `سعر_الصرف` DECIMAL(10,4) DEFAULT 1,
                `المبلغ_بالعملة_الأجنبية` DECIMAL(15,2),
                `الترتيب` INT DEFAULT 0,
                INDEX `idx_معرف_القيد` (`معرف_القيد`),
                INDEX `idx_معرف_الحساب` (`معرف_الحساب`),
                FOREIGN KEY (`معرف_القيد`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE RESTRICT,
                CHECK ((`المبلغ_المدين` > 0 AND `المبلغ_الدائن` = 0) OR (`المبلغ_المدين` = 0 AND `المبلغ_الدائن` > 0))
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول أرصدة الحسابات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `أرصدة_الحسابات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الحساب` VARCHAR(20) NOT NULL,
                `السنة_المالية` INT NOT NULL,
                `الشهر` INT,
                `الرصيد_الافتتاحي` DECIMAL(15,2) DEFAULT 0,
                `مجموع_المدين` DECIMAL(15,2) DEFAULT 0,
                `مجموع_الدائن` DECIMAL(15,2) DEFAULT 0,
                `الرصيد_الحالي` DECIMAL(15,2) GENERATED ALWAYS AS (`الرصيد_الافتتاحي` + `مجموع_المدين` - `مجموع_الدائن`) STORED,
                `آخر_حركة` DATE,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY `unique_account_period` (`معرف_الحساب`, `السنة_المالية`, `الشهر`),
                INDEX `idx_معرف_الحساب` (`معرف_الحساب`),
                INDEX `idx_السنة_المالية` (`السنة_المالية`),
                FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE CASCADE,
                FOREIGN KEY (`السنة_المالية`) REFERENCES `السنوات_المالية`(`السنة`) ON DELETE RESTRICT
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مراكز التكلفة
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `مراكز_التكلفة` (
                `معرف_المركز` VARCHAR(20) PRIMARY KEY,
                `اسم_المركز` VARCHAR(255) NOT NULL,
                `النوع` ENUM('إنتاجي', 'خدمي', 'إداري', 'تسويقي') NOT NULL,
                `المركز_الأب` VARCHAR(20),
                `المستوى` TINYINT DEFAULT 1,
                `الحالة` ENUM('نشط', 'غير_نشط') DEFAULT 'نشط',
                `الوصف` TEXT,
                `الترتيب` INT DEFAULT 0,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_المركز_الأب` (`المركز_الأب`),
                FOREIGN KEY (`المركز_الأب`) REFERENCES `مراكز_التكلفة`(`معرف_المركز`) ON DELETE RESTRICT
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
    
    def انشاء_جداول_التدقيق(self):
        """إنشاء جداول التدقيق والمتابعة"""
        logger.info("إنشاء جداول التدقيق...")
        
        # جدول سجل الأنشطة
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `سجل_الأنشطة` (
                `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
                `المستخدم` VARCHAR(50) NOT NULL,
                `النشاط` VARCHAR(100) NOT NULL,
                `الجدول` VARCHAR(50),
                `معرف_السجل` INT,
                `البيانات_القديمة` JSON,
                `البيانات_الجديدة` JSON,
                `عنوان_IP` VARCHAR(45),
                `الجهاز` VARCHAR(255),
                `التاريخ_والوقت` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_المستخدم` (`المستخدم`),
                INDEX `idx_النشاط` (`النشاط`),
                INDEX `idx_الجدول` (`الجدول`),
                INDEX `idx_التاريخ_والوقت` (`التاريخ_والوقت`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الإشعارات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الإشعارات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `المستخدم` VARCHAR(50),
                `النوع` ENUM('معلومة', 'تحذير', 'خطأ', 'نجاح') DEFAULT 'معلومة',
                `العنوان` VARCHAR(255) NOT NULL,
                `الرسالة` TEXT,
                `الرابط` VARCHAR(255),
                `مقروء` BOOLEAN DEFAULT FALSE,
                `تاريخ_القراءة` DATETIME,
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `تاريخ_الإنشاء` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_المستخدم` (`المستخدم`),
                INDEX `idx_مقروء` (`مقروء`),
                INDEX `idx_الأولوية` (`الأولوية`),
                INDEX `idx_تاريخ_الإنشاء` (`تاريخ_الإنشاء`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المهام والتذكيرات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المهام_والتذكيرات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `المستخدم` VARCHAR(50) NOT NULL,
                `النوع` ENUM('مهمة', 'تذكير', 'موعد') DEFAULT 'مهمة',
                `العنوان` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `تاريخ_البداية` DATETIME,
                `تاريخ_النهاية` DATETIME,
                `الحالة` ENUM('جديد', 'قيد_التنفيذ', 'مكتمل', 'ملغي', 'متأخر') DEFAULT 'جديد',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `التكرار` ENUM('لا_يتكرر', 'يومي', 'أسبوعي', 'شهري', 'سنوي'),
                `المرجع_النوع` VARCHAR(50),
                `المرجع_المعرف` INT,
                `تاريخ_الإنجاز` DATETIME,
                `ملاحظات` TEXT,
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_المستخدم` (`المستخدم`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_الأولوية` (`الأولوية`),
                INDEX `idx_تاريخ_البداية` (`تاريخ_البداية`),
                INDEX `idx_تاريخ_النهاية` (`تاريخ_النهاية`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
    
    def انشاء_فهارس_الجداول(self):
        """إنشاء الفهارس لتحسين الأداء"""
        logger.info("إنشاء الفهارس...")
        
        # قائمة الفهارس المطلوبة
        indexes = [
            # فهارس مركبة للبحث والاستعلامات الشائعة
            ("idx_projects_status_year", "المشاريع", "(`الحالة`, `السنة`)"),
            ("idx_employees_status_dept", "الموظفين", "(`الحالة`, `معرف_القسم`)"),
            ("idx_payments_type_date", "المدفوعات", "(`النوع`, `تاريخ_الدفع`)"),
            ("idx_expenses_type_date", "المصروفات", "(`النوع`, `تاريخ_المصروف`)"),
            ("idx_invoices_type_status", "الفواتير", "(`نوع_الفاتورة`, `الحالة`)"),
            ("idx_journal_date_status", "القيود_المحاسبية", "(`تاريخ_القيد`, `حالة_القيد`)"),
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                self.cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE TABLE_SCHEMA = '{self.db_name}' 
                    AND TABLE_NAME = '{table_name}' 
                    AND INDEX_NAME = '{index_name}'
                """)
                
                if self.cursor.fetchone()[0] == 0:
                    self.cursor.execute(f"CREATE INDEX `{index_name}` ON `{table_name}` {columns}")
                    logger.info(f"تم إنشاء الفهرس: {index_name}")
            except Exception as e:
                logger.warning(f"تحذير في إنشاء الفهرس {index_name}: {e}")
    
    def انشاء_المشغلات(self):
        """إنشاء المشغلات (Triggers)"""
        logger.info("إنشاء المشغلات...")
        
        triggers = [
            # تحديث رصيد الموظف عند إضافة معاملة مالية
            {
                "name": "update_employee_balance_after_insert",
                "sql": """
                    CREATE TRIGGER update_employee_balance_after_insert
                    AFTER INSERT ON `الموظفين_معاملات_مالية`
                    FOR EACH ROW
                    BEGIN
                        UPDATE `الموظفين`
                        SET `الرصيد` = NEW.`الرصيد_بعد`
                        WHERE `id` = NEW.`معرف_الموظف`;
                    END
                """
            },
            
            # تحديث المدفوع في المشروع عند إضافة دفعة
            {
                "name": "update_project_paid_after_payment",
                "sql": """
                    CREATE TRIGGER update_project_paid_after_payment
                    AFTER INSERT ON `المدفوعات`
                    FOR EACH ROW
                    BEGIN
                        IF NEW.`النوع` = 'دفعة_مشروع' THEN
                            UPDATE `المشاريع`
                            SET `المدفوع` = `المدفوع` + NEW.`صافي_المبلغ`
                            WHERE `id` = NEW.`معرف_المرجع`;
                        END IF;
                    END
                """
            },
            
            # تحديث المصروف في العهدة عند إضافة مصروف
            {
                "name": "update_custody_expense_after_insert",
                "sql": """
                    CREATE TRIGGER update_custody_expense_after_insert
                    AFTER INSERT ON `المصروفات`
                    FOR EACH ROW
                    BEGIN
                        IF NEW.`النوع` = 'مصروف_عهدة' THEN
                            UPDATE `المقاولات_العهد`
                            SET `المصروف` = `المصروف` + NEW.`المبلغ`
                            WHERE `id` = NEW.`معرف_المرجع`;
                        END IF;
                    END
                """
            },
            
            # تسجيل النشاط عند حذف سجل مهم
            {
                "name": "log_project_deletion",
                "sql": """
                    CREATE TRIGGER log_project_deletion
                    BEFORE DELETE ON `المشاريع`
                    FOR EACH ROW
                    BEGIN
                        INSERT INTO `سجل_الأنشطة` 
                        (`المستخدم`, `النشاط`, `الجدول`, `معرف_السجل`, `البيانات_القديمة`)
                        VALUES 
                        (USER(), 'حذف', 'المشاريع', OLD.`id`, 
                        JSON_OBJECT('اسم_المشروع', OLD.`اسم_المشروع`, 'قيمة_العقد', OLD.`قيمة_العقد`));
                    END
                """
            }
        ]
        
        for trigger in triggers:
            try:
                # التحقق من وجود المشغل
                self.cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.TRIGGERS
                    WHERE TRIGGER_SCHEMA = '{self.db_name}' 
                    AND TRIGGER_NAME = '{trigger["name"]}'
                """)
                
                if self.cursor.fetchone()[0] == 0:
                    self.cursor.execute(trigger["sql"])
                    logger.info(f"تم إنشاء المشغل: {trigger['name']}")
            except Exception as e:
                logger.warning(f"تحذير في إنشاء المشغل {trigger['name']}: {e}")
    
    def انشاء_البيانات_الافتراضية(self):
        """إدراج البيانات الافتراضية"""
        logger.info("إدراج البيانات الافتراضية...")
        
        # إدراج السنة المالية الحالية
        current_year = datetime.now().year
        self.cursor.execute("""
            INSERT IGNORE INTO `السنوات_المالية`
            (`السنة`, `تاريخ_البداية`, `تاريخ_النهاية`, `الحالة`, `هي_السنة_الحالية`, `ملاحظات`)
            VALUES (%s, %s, %s, 'مفتوحة', TRUE, 'السنة المالية الحالية')
        """, (current_year, f"{current_year}-01-01", f"{current_year}-12-31"))
        
        # إدراج الإعدادات الافتراضية
        default_settings = [
            ('company_name', 'اسم الشركة', 'string', 'الاسم الرسمي للشركة', 'معلومات_الشركة'),
            ('company_logo', '', 'string', 'شعار الشركة', 'معلومات_الشركة'),
            ('currency', 'SAR', 'string', 'العملة الافتراضية', 'مالي'),
            ('tax_rate', '15', 'number', 'نسبة الضريبة الافتراضية', 'مالي'),
            ('invoice_prefix', 'INV-', 'string', 'بادئة أرقام الفواتير', 'مالي'),
            ('project_prefix', 'PRJ-', 'string', 'بادئة أرقام المشاريع', 'مشاريع'),
            ('employee_prefix', 'EMP-', 'string', 'بادئة أرقام الموظفين', 'موظفين'),
            ('customer_prefix', 'CUS-', 'string', 'بادئة أرقام العملاء', 'عملاء'),
            ('backup_days', '7', 'number', 'عدد أيام الاحتفاظ بالنسخ الاحتياطية', 'نظام'),
            ('session_timeout', '30', 'number', 'مدة انتهاء الجلسة بالدقائق', 'نظام'),
        ]
        
        for key, value, data_type, description, group in default_settings:
            self.cursor.execute("""
                INSERT IGNORE INTO `إعدادات_النظام`
                (`المفتاح`, `القيمة`, `نوع_البيانات`, `الوصف`, `المجموعة`)
                VALUES (%s, %s, %s, %s, %s)
            """, (key, value, data_type, description, group))
        
        # إدراج التصنيفات الافتراضية
        default_categories = [
            # تصنيفات المشاريع
            ("المشاريع", "تصميم معماري", "ARCH", "#3498db", "تصميم المباني والمنشآت"),
            ("المشاريع", "تصميم إنشائي", "STRUC", "#e74c3c", "التصميم الإنشائي والهيكلي"),
            ("المشاريع", "تصميم داخلي", "INT", "#9b59b6", "التصميم الداخلي والديكور"),
            ("المشاريع", "إشراف هندسي", "SUP", "#f39c12", "الإشراف على التنفيذ"),
            
            # تصنيفات العملاء
            ("العملاء", "أفراد", "IND", "#27ae60", "عملاء أفراد"),
            ("العملاء", "شركات", "CORP", "#2980b9", "شركات ومؤسسات"),
            ("العملاء", "حكومي", "GOV", "#34495e", "جهات حكومية"),
            
            # تصنيفات الموظفين
            ("الموظفين", "إدارة", "MGT", "#c0392b", "الإدارة العليا"),
            ("الموظفين", "مهندسون", "ENG", "#27ae60", "المهندسون والفنيون"),
            ("الموظفين", "إداريون", "ADM", "#3498db", "الموظفون الإداريون"),
            ("الموظفين", "عمال", "WRK", "#f39c12", "العمال والحرفيون"),
            
            # تصنيفات المصروفات
            ("المصروفات", "رواتب", "SAL", "#e74c3c", "الرواتب والأجور"),
            ("المصروفات", "إيجارات", "RENT", "#9b59b6", "الإيجارات"),
            ("المصروفات", "مرافق", "UTIL", "#3498db", "الكهرباء والماء والاتصالات"),
            ("المصروفات", "صيانة", "MAINT", "#2ecc71", "الصيانة والإصلاحات"),
            
            # تصنيفات التدريب
            ("التدريب", "دورات هندسية", "ENG-TRN", "#3498db", "الدورات الهندسية المتخصصة"),
            ("التدريب", "دورات إدارية", "MGT-TRN", "#e67e22", "الدورات الإدارية والقيادية"),
            ("التدريب", "ورش عمل", "WRKSHP", "#9b59b6", "ورش العمل التطبيقية"),
            
            # تصنيفات المقاولات
            ("المقاولات", "بناء عظم", "CONST", "#95a5a6", "أعمال البناء والخرسانة"),
            ("المقاولات", "تشطيبات", "FINISH", "#e67e22", "أعمال التشطيب والديكور"),
            ("المقاولات", "صيانة", "MAINT-CON", "#2ecc71", "أعمال الصيانة والترميم"),
        ]
        
        for section, name, code, color, description in default_categories:
            self.cursor.execute("""
                INSERT IGNORE INTO `التصنيفات`
                (`القسم`, `الاسم`, `الكود`, `اللون`, `الوصف`)
                VALUES (%s, %s, %s, %s, %s)
            """, (section, name, code, color, description))
        
        # إدراج مواعيد العمل الافتراضية
        self.cursor.execute("""
            INSERT IGNORE INTO `مواعيد_العمل`
            (`الاسم`, `النوع`, `نوع_النظام`, `وقت_حضور_صباحي`, `وقت_انصراف_صباحي`, `ملاحظات`)
            VALUES ('الدوام الرسمي', 'افتراضي', 'فترة_واحدة', '08:00:00', '17:00:00', 'مواعيد العمل الافتراضية')
        """)
        
        # إدراج شجرة الحسابات الأساسية
        basic_accounts = [
            # الحسابات الرئيسية
            ("1", "الأصول", "أصول", "مدين", None, 1, False),
            ("2", "الخصوم", "خصوم", "دائن", None, 1, False),
            ("3", "حقوق الملكية", "حقوق_الملكية", "دائن", None, 1, False),
            ("4", "الإيرادات", "إيرادات", "دائن", None, 1, False),
            ("5", "المصروفات", "مصروفات", "مدين", None, 1, False),
            
            # الأصول المتداولة
            ("11", "الأصول المتداولة", "أصول", "مدين", "1", 2, False),
            ("111", "النقدية والبنوك", "أصول", "مدين", "11", 3, False),
            ("1111", "الصندوق", "أصول", "مدين", "111", 4, True),
            ("1112", "البنوك", "أصول", "مدين", "111", 4, True),
            ("112", "العملاء", "أصول", "مدين", "11", 3, True),
            ("113", "المخزون", "أصول", "مدين", "11", 3, True),
            
            # الأصول الثابتة
            ("12", "الأصول الثابتة", "أصول", "مدين", "1", 2, False),
            ("121", "الأراضي والمباني", "أصول", "مدين", "12", 3, True),
            ("122", "المعدات والآلات", "أصول", "مدين", "12", 3, True),
            
            # الخصوم المتداولة
            ("21", "الخصوم المتداولة", "خصوم", "دائن", "2", 2, False),
            ("211", "الموردون", "خصوم", "دائن", "21", 3, True),
            ("212", "المصروفات المستحقة", "خصوم", "دائن", "21", 3, True),
            
            # حقوق الملكية
            ("31", "رأس المال", "حقوق_الملكية", "دائن", "3", 2, True),
            ("32", "الأرباح المحتجزة", "حقوق_الملكية", "دائن", "3", 2, True),
            
            # الإيرادات
            ("41", "إيرادات التشغيل", "إيرادات", "دائن", "4", 2, False),
            ("411", "إيرادات المشاريع", "إيرادات", "دائن", "41", 3, True),
            ("412", "إيرادات المقاولات", "إيرادات", "دائن", "41", 3, True),
            
            # المصروفات
            ("51", "مصروفات التشغيل", "مصروفات", "مدين", "5", 2, False),
            ("511", "الرواتب والأجور", "مصروفات", "مدين", "51", 3, True),
            ("512", "الإيجارات", "مصروفات", "مدين", "51", 3, True),
        ]
        
        for account_id, name, account_type, nature, parent, level, is_detail in basic_accounts:
            self.cursor.execute("""
                INSERT IGNORE INTO `شجرة_الحسابات`
                (`معرف_الحساب`, `اسم_الحساب`, `نوع_الحساب`, `طبيعة_الحساب`, 
                `الحساب_الأب`, `المستوى`, `هو_حساب_تفصيلي`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (account_id, name, account_type, nature, parent, level, is_detail))
        
        # إدراج مراكز التكلفة الافتراضية
        cost_centers = [
            ("CC001", "المشاريع الهندسية", "إنتاجي", None),
            ("CC002", "المقاولات", "إنتاجي", None),
            ("CC003", "التدريب", "خدمي", None),
            ("CC004", "الإدارة العامة", "إداري", None),
            ("CC005", "التسويق والمبيعات", "تسويقي", None),
        ]
        
        for cc_id, name, cc_type, parent in cost_centers:
            self.cursor.execute("""
                INSERT IGNORE INTO `مراكز_التكلفة`
                (`معرف_المركز`, `اسم_المركز`, `النوع`, `المركز_الأب`)
                VALUES (%s, %s, %s, %s)
            """, (cc_id, name, cc_type, parent))
        
        logger.info("تم إدراج البيانات الافتراضية بنجاح")


# استخدام الفئة الجديدة
def انشاء_قاعدة_البيانات(self):
    """دالة لإنشاء قاعدة البيانات المحسنة"""
    db_manager = DatabaseManager()
    success = db_manager.create_database_if_not_exists()
    
    if success:
        logger.info("تم إنشاء قاعدة البيانات بنجاح")
        return True
    else:
        logger.error("فشل في إنشاء قاعدة البيانات")
        return False 