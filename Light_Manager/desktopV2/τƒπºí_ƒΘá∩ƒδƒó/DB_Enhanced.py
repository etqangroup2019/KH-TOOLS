
            # 1. جدول العمليات المالية الواردة (الإيرادات والمقبوضات)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `العمليات_المالية_الواردة` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `نوع_العملية` ENUM('إيراد', 'مقبوضات', 'دفعة عميل', 'دفعة مورد', 'أخرى') NOT NULL,
                    `القسم` VARCHAR(100) NOT NULL COMMENT 'مشاريع، مقاولات، تدريب، موظفين، موردين، إلخ',
                    `الجهة` VARCHAR(255) NOT NULL COMMENT 'اسم العميل/المورد/الموظف/المشروع',
                    `معرف_الجهة` INT NULL COMMENT 'معرف الجهة (اختياري)',
                    `الوصف` TEXT NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `تاريخ_العملية` DATE NOT NULL,
                    `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل بنكي', 'أجل/دين') DEFAULT 'نقدي',
                    `رقم_المرجع` VARCHAR(100) NULL COMMENT 'رقم الفاتورة أو المرجع',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_العملية`)) STORED,
                    
                    
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)

            # 2. جدول العمليات المالية الصادرة (المصروفات والمدفوعات)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `العمليات_المالية_الصادرة` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `نوع_العملية` ENUM('مصروف', 'مدفوعات', 'رواتب', 'مصاريف مشاريع', 'مصاريف تدريب', 'أخرى') NOT NULL,
                    `القسم` VARCHAR(100) NOT NULL COMMENT 'مشاريع، مقاولات، تدريب، موظفين، موردين، إدارة، إلخ',
                    `الجهة` VARCHAR(255) NOT NULL COMMENT 'اسم المورد/الموظف/المشروع/الدورة',
                    `معرف_الجهة` INT NULL COMMENT 'معرف الجهة (اختياري)',
                    `الوصف` TEXT NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `تاريخ_العملية` DATE NOT NULL,
                    `طريقة_الدفع` ENUM('نقدي', 'بطاقة', 'شيك', 'تحويل بنكي', 'أجل/دين') DEFAULT 'نقدي',
                    `رقم_الفاتورة` VARCHAR(100) NULL,
                    `المستلم` VARCHAR(255) NULL,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_العملية`)) STORED,
                    
                    
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)

            # 3. جدول الالتزامات المالية والديون
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `الالتزامات_المالية_والديون` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `نوع_الالتزام` ENUM('دين على الشركة', 'دين للشركة', 'التزام مالي', 'عهدة مالية') NOT NULL,
                    `القسم` VARCHAR(100) NOT NULL COMMENT 'مشاريع، مقاولات، تدريب، موظفين، موردين، إدارة، إلخ',
                    `الجهة` VARCHAR(255) NOT NULL COMMENT 'اسم العميل/المورد/الموظف/المشروع',
                    `معرف_الجهة` INT NULL COMMENT 'معرف الجهة (اختياري)',
                    `الوصف` TEXT NOT NULL,
                    `المبلغ_الأصلي` DECIMAL(15,2) NOT NULL,
                    `المدفوع` DECIMAL(15,2) DEFAULT 0,
                    `الباقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ_الأصلي` - `المدفوع`) STORED,
                    `تاريخ_الالتزام` DATE NOT NULL,
                    `تاريخ_الاستحقاق` DATE NULL,
                    `حالة_الالتزام` ENUM('معلق', 'غير مسدد', 'مسدد', 'متأخر') NOT NULL DEFAULT 'معلق',
                    `نوع_الضمان` ENUM('ضمان نقدي', 'ضمان بنكي', 'ضمان شخصي', 'بدون ضمان') DEFAULT 'بدون ضمان',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الالتزام`)) STORED,
                    
                    
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)

            # 4. جدول المهام الموحدة
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `المهام_الموحدة` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_الموظف` INT NOT NULL,
                    `نوع_المهمة` ENUM('مهمة عامة', 'مهمة تدريب', 'مهمة مشروع', 'مهمة مقاولات', 'مهمة إدارية') NOT NULL DEFAULT 'مهمة عامة',
                    `القسم` VARCHAR(100) NOT NULL COMMENT 'مشاريع، مقاولات، تدريب، موظفين، إدارة، إلخ',
                    `معرف_القسم` INT NULL COMMENT 'معرف القسم المرتبط (اختياري)',
                    `نوع_دور_المهمة` ENUM('ربط_بمرحلة', 'دور_عام', 'مهمة_مستقلة') DEFAULT 'مهمة_مستقلة',
                    `معرف_المرحلة` INT NULL COMMENT 'معرف المرحلة (اختياري)',
                    `عنوان_المهمة` VARCHAR(255) NOT NULL,
                    `وصف_المهمة` TEXT,
                    `نسبة_الموظف` DECIMAL(5,2) NULL COMMENT 'نسبة الموظف من المهمة',
                    `مبلغ_الموظف` DECIMAL(10,2) NULL COMMENT 'مبلغ الموظف من المهمة',
                    `حالة_مبلغ_الموظف` ENUM('غير مدرج', 'تم الإدراج') DEFAULT 'غير مدرج',
                    `تاريخ_البدء` DATE NULL,
                    `تاريخ_الانتهاء` DATE NULL,
                    `الحالة` ENUM('قيد التنفيذ', 'مكتملة', 'ملغاة', 'متأخرة', 'لم يبدأ', 'متوقف') NOT NULL DEFAULT 'لم يبدأ',
                    `الأولوية` ENUM('عالية', 'متوسطة', 'منخفضة') DEFAULT 'متوسطة',
                    `النسبة_المئوية_للإنجاز` DECIMAL(5,2) DEFAULT 0 COMMENT 'نسبة إنجاز المهمة',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة` INT GENERATED ALWAYS AS (YEAR(COALESCE(`تاريخ_البدء`, `تاريخ_الإضافة`))) STORED,
      
                    CONSTRAINT `fk_المهام_الموحدة_معرف_الموظف`
                        FOREIGN KEY (`معرف_الموظف`)
                        REFERENCES `الموظفين`(`id`)
                        ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)

            
            # ========================
            # إدراج البيانات الافتراضية
            # ========================

            # إدراج التصنيفات الافتراضية
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

        # جدول الأقسام
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الأقسام` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_القسم` VARCHAR(100) NOT NULL,
                `كود_القسم` VARCHAR(20) UNIQUE,
                `وصف_القسم` TEXT,
                `معرف_المدير` INT,
                `معرف_القسم_الأب` INT,
                `الميزانية_السنوية` DECIMAL(15,2) DEFAULT 0,
                `عدد_الموظفين` INT DEFAULT 0,
                `نشط` BOOLEAN DEFAULT TRUE,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_كود_القسم` (`كود_القسم`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`معرف_المدير`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_القسم_الأب`) REFERENCES `الأقسام`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المستخدمين
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `المستخدمين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_المستخدم` VARCHAR(50) NOT NULL UNIQUE,
                `كلمة_المرور` VARCHAR(255) NOT NULL,
                `معرف_الموظف` INT UNIQUE,
                `الايميل` VARCHAR(100) UNIQUE,
                `الصلاحيات` JSON,
                `آخر_تسجيل_دخول` DATETIME,
                `عدد_محاولات_الدخول` INT DEFAULT 0,
                `محظور` BOOLEAN DEFAULT FALSE,
                `انتهاء_كلمة_المرور` DATE,
                `نشط` BOOLEAN DEFAULT TRUE,
                `المستخدم_المنشئ` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_اسم_المستخدم` (`اسم_المستخدم`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول العطل الرسمية
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `العطل_الرسمية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_العطلة` VARCHAR(100) NOT NULL,
                `تاريخ_البداية` DATE NOT NULL,
                `تاريخ_النهاية` DATE NOT NULL,
                `النوع` ENUM('رسمي', 'ديني', 'وطني', 'شركة') DEFAULT 'رسمي',
                `يتكرر_سنوياً` BOOLEAN DEFAULT FALSE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_تاريخ_البداية` (`تاريخ_البداية`),
                INDEX `idx_النوع` (`النوع`),
                CHECK (`تاريخ_النهاية` >= `تاريخ_البداية`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

        # جدول البنوك
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `البنوك` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_البنك` VARCHAR(100) NOT NULL,
                `كود_البنك` VARCHAR(20) UNIQUE,
                `العنوان` TEXT,
                `رقم_الهاتف` VARCHAR(50),
                `الموقع_الإلكتروني` VARCHAR(255),
                `نشط` BOOLEAN DEFAULT TRUE,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_كود_البنك` (`كود_البنك`),
                INDEX `idx_نشط` (`نشط`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الحسابات البنكية
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الحسابات_البنكية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_البنك` INT NOT NULL,
                `رقم_الحساب` VARCHAR(50) NOT NULL,
                `اسم_الحساب` VARCHAR(100) NOT NULL,
                `نوع_الحساب` ENUM('جاري', 'توفير', 'ودائع', 'ائتمان') DEFAULT 'جاري',
                `العملة` VARCHAR(10) DEFAULT 'SAR',
                `الرصيد` DECIMAL(15,2) DEFAULT 0,
                `الحد_الائتماني` DECIMAL(15,2) DEFAULT 0,
                `معرف_حساب_محاسبي` VARCHAR(20),
                `نشط` BOOLEAN DEFAULT TRUE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY `unique_bank_account` (`معرف_البنك`, `رقم_الحساب`),
                INDEX `idx_رقم_الحساب` (`رقم_الحساب`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`معرف_البنك`) REFERENCES `البنوك`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_حساب_محاسبي`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الضرائب
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الضرائب` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_الضريبة` VARCHAR(100) NOT NULL,
                `كود_الضريبة` VARCHAR(20) UNIQUE,
                `النوع` ENUM('قيمة_مضافة', 'استقطاع', 'دخل', 'أخرى') NOT NULL,
                `النسبة` DECIMAL(5,2) NOT NULL,
                `معرف_حساب_الضريبة` VARCHAR(20),
                `تطبق_تلقائياً` BOOLEAN DEFAULT FALSE,
                `نشط` BOOLEAN DEFAULT TRUE,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_كود_الضريبة` (`كود_الضريبة`),
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`معرف_حساب_الضريبة`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
                 
        # جدول الأصول الثابتة
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الأصول_الثابتة` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_الأصل` VARCHAR(255) NOT NULL,
                `كود_الأصل` VARCHAR(50) UNIQUE,
                `معرف_التصنيف` INT,
                `تاريخ_الشراء` DATE NOT NULL,
                `تكلفة_الشراء` DECIMAL(15,2) NOT NULL,
                `القيمة_الحالية` DECIMAL(15,2),
                `طريقة_الاستهلاك` ENUM('خط_مستقيم', 'متناقص', 'وحدات_إنتاج') DEFAULT 'خط_مستقيم',
                `سنوات_العمر_الإنتاجي` INT NOT NULL,
                `القيمة_المتبقية` DECIMAL(15,2) DEFAULT 0,
                `الاستهلاك_المتراكم` DECIMAL(15,2) DEFAULT 0,
                `معرف_حساب_الأصل` VARCHAR(20),
                `معرف_حساب_الاستهلاك` VARCHAR(20),
                `نشط` BOOLEAN DEFAULT TRUE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_كود_الأصل` (`كود_الأصل`),
                INDEX `idx_تاريخ_الشراء` (`تاريخ_الشراء`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_حساب_الأصل`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_حساب_الاستهلاك`) REFERENCES `شجرة_الحسابات`(`معرف_الحساب`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الاجتماعات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `الاجتماعات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `عنوان_الاجتماع` VARCHAR(255) NOT NULL,
                `النوع` ENUM('داخلي', 'مع_عميل', 'مع_مقاول', 'مع_مورد') NOT NULL,
                `معرف_المشروع` INT,
                `تاريخ_الاجتماع` DATETIME NOT NULL,
                `المدة_بالدقائق` INT,
                `المكان` VARCHAR(255),
                `جدول_الأعمال` TEXT,
                `محضر_الاجتماع` TEXT,
                `القرارات` TEXT,
                `المتابعة_المطلوبة` TEXT,
                `الحضور` JSON,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_تاريخ_الاجتماع` (`تاريخ_الاجتماع`),
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

        # جدول النسخ الاحتياطية
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `النسخ_الاحتياطية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_النسخة` VARCHAR(255) NOT NULL,
                `المسار` VARCHAR(500) NOT NULL,
                `الحجم_بالبايت` BIGINT DEFAULT 0,
                `نوع_النسخة` ENUM('تلقائي', 'يدوي', 'مجدول') DEFAULT 'يدوي',
                `حالة_النسخة` ENUM('جاري', 'مكتمل', 'فاشل', 'محذوف') DEFAULT 'مكتمل',
                `تاريخ_الإنشاء` DATETIME NOT NULL,
                `تاريخ_الحذف_المتوقع` DATETIME,
                `تم_التحقق` BOOLEAN DEFAULT FALSE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_تاريخ_الإنشاء` (`تاريخ_الإنشاء`),
                INDEX `idx_نوع_النسخة` (`نوع_النسخة`),
                INDEX `idx_حالة_النسخة` (`حالة_النسخة`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
