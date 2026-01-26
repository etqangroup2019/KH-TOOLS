"""
ملف تكوين أنواع المشاريع والتابات المطلوبة لكل نوع
"""

# تكوين أنواع المشاريع والتابات المطلوبة لكل نوع
PROJECT_TYPES_CONFIG = {
    "تصميم معماري": {
        "tabs": [
            {
                "name": "معلومات المشروع",
                "icon": "fa5s.info-circle",
                "color": "blue",
                "type": "project_info"
            },
            {
                "name": "مراحل التصميم", 
                "icon": "fa5s.tasks",
                "color": "purple",
                "type": "design_phases"
            },
            {
                "name": "الجدول الزمني",
                "icon": "fa5s.calendar",
                "color": "orange", 
                "type": "timeline"
            },
            {
                "name": "حسابات المهندسين",
                "icon": "fa5s.users",
                "color": "teal",
                "type": "engineers_accounts"
            },
            {
                "name": "الملفات والمرفقات",
                "icon": "fa5s.paperclip",
                "color": "gray",
                "type": "attachments"
            }
        ],
        "phases": [
            "دراسة الموقع",
            "التصميم المعماري الأولي", 
            "التصميم المعماري النهائي",
            "التصميم الإنشائي",
            "التصميم الكهربائي",
            "التصميم الصحي",
            "التصميم الميكانيكي",
            "إعداد المخططات النهائية"
        ]
    },
    
    "تنفيذ": {
        "tabs": [
            {
                "name": "معلومات المشروع",
                "icon": "fa5s.info-circle", 
                "color": "blue",
                "type": "project_info"
            },
            {
                "name": "حالة التنفيذ",
                "icon": "fa5s.chart-line",
                "color": "green",
                "type": "execution_status"
            },
            {
                "name": "مراحل التنفيذ",
                "icon": "fa5s.hammer",
                "color": "brown",
                "type": "execution_phases"
            },
            {
                "name": "الإشراف والمتابعة",
                "icon": "fa5s.eye",
                "color": "navy",
                "type": "supervision"
            },
            {
                "name": "الجدول الزمني",
                "icon": "fa5s.calendar",
                "color": "orange",
                "type": "timeline"
            },
            {
                "name": "حسابات المهندسين",
                "icon": "fa5s.users",
                "color": "teal",
                "type": "engineers_accounts"
            },
            {
                "name": "مصروفات المشروع",
                "icon": "fa5s.money-bill",
                "color": "red",
                "type": "project_expenses"
            },
            {
                "name": "العهد والدفعات",
                "icon": "fa5s.credit-card",
                "color": "green",
                "type": "payments"
            },
            {
                "name": "حسابات المقاولين",
                "icon": "fa5s.hard-hat",
                "color": "orange",
                "type": "contractors_accounts"
            },
            {
                "name": "حسابات العمال",
                "icon": "fa5s.user-hard-hat",
                "color": "brown",
                "type": "workers_accounts"
            }
        ],
        "phases": [
            "أعمال الحفر والأساسات",
            "أعمال الخرسانة المسلحة",
            "أعمال البناء والمباني",
            "أعمال التشطيبات الداخلية",
            "أعمال التشطيبات الخارجية",
            "أعمال الكهرباء",
            "أعمال السباكة والصحي",
            "أعمال التكييف",
            "أعمال اللمسات الأخيرة"
        ]
    },
    
    "إشراف": {
        "tabs": [
            {
                "name": "معلومات المشروع",
                "icon": "fa5s.info-circle",
                "color": "blue", 
                "type": "project_info"
            },
            {
                "name": "تقارير الإشراف",
                "icon": "fa5s.file-alt",
                "color": "blue",
                "type": "supervision_reports"
            },
            {
                "name": "الجدول الزمني",
                "icon": "fa5s.calendar",
                "color": "orange",
                "type": "timeline"
            },
            {
                "name": "حسابات المهندسين",
                "icon": "fa5s.users",
                "color": "teal",
                "type": "engineers_accounts"
            }
        ],
        "phases": [
            "إشراف على الأساسات",
            "إشراف على الهيكل الإنشائي",
            "إشراف على أعمال البناء",
            "إشراف على التشطيبات",
            "إشراف على الأعمال الكهربائية",
            "إشراف على أعمال السباكة",
            "الفحص النهائي والتسليم"
        ]
    },
    
    "مقاولات": {
        "tabs": [
            {
                "name": "معلومات المشروع",
                "icon": "fa5s.info-circle",
                "color": "blue",
                "type": "project_info"
            },
            {
                "name": "مراحل المقاولات",
                "icon": "fa5s.building",
                "color": "brown",
                "type": "contracting_phases"
            },
            {
                "name": "الجدول الزمني",
                "icon": "fa5s.calendar",
                "color": "orange",
                "type": "timeline"
            },
            {
                "name": "المصروفات والتكاليف",
                "icon": "fa5s.calculator",
                "color": "red",
                "type": "costs"
            },
            {
                "name": "العمالة والمعدات",
                "icon": "fa5s.tools",
                "color": "gray",
                "type": "labor_equipment"
            },
            {
                "name": "الدفعات والعهد",
                "icon": "fa5s.credit-card",
                "color": "green",
                "type": "payments"
            }
        ],
        "phases": [
            "تحضير الموقع",
            "توريد المواد",
            "تنفيذ الأعمال",
            "مراقبة الجودة",
            "التسليم الأولي",
            "التسليم النهائي"
        ]
    }
}

# تكوين حالات المشاريع
PROJECT_STATUSES = [
    "لم يبدأ",
    "قيد التنفيذ", 
    "مكتمل",
    "متوقف",
    "ملغي",
    "مؤجل",
    "في المراجعة",
    "بانتظار الموافقة"
]

# تكوين حالات المراحل
PHASE_STATUSES = [
    "لم تبدأ",
    "قيد التنفيذ",
    "مكتملة", 
    "متوقفة",
    "ملغاة",
    "بحاجة مراجعة"
]

# تكوين أنواع المصروفات
EXPENSE_TYPES = [
    "مواد بناء",
    "عمالة",
    "معدات",
    "نقل ومواصلات",
    "رسوم حكومية",
    "استشارات",
    "أخرى"
]

# تكوين طرق الدفع
PAYMENT_METHODS = [
    "نقداً",
    "شيك",
    "تحويل بنكي",
    "بطاقة ائتمان",
    "أخرى"
]

# تكوين تخصصات العمال
WORKER_SPECIALIZATIONS = [
    "عامل عام",
    "نجار",
    "حداد",
    "كهربائي",
    "سباك",
    "دهان",
    "بلاط",
    "جبس",
    "عامل نظافة"
]

# تكوين أنواع المعدات
EQUIPMENT_TYPES = [
    "آلات حفر",
    "رافعات",
    "خلاطات خرسانة",
    "مولدات كهرباء",
    "أدوات يدوية",
    "سقالات",
    "أخرى"
]

# احصل على تكوين المشروع
def get_project_config(project_type):
    """
    الحصول على تكوين نوع مشروع محدد
    
    Args:
        project_type (str): نوع المشروع
        
    Returns:
        dict: تكوين المشروع أو تكوين افتراضي
    """
    return PROJECT_TYPES_CONFIG.get(project_type, PROJECT_TYPES_CONFIG["تصميم معماري"])

# الحصول على أنواع المشروع المتاحة
def get_available_project_types():
    """
    الحصول على قائمة بأنواع المشاريع المتاحة
    
    Returns:
        list: قائمة بأنواع المشاريع
    """
    return list(PROJECT_TYPES_CONFIG.keys())

# الحصول على مراحل المشروع
def get_project_phases(project_type):
    """
    الحصول على مراحل نوع مشروع محدد
    
    Args:
        project_type (str): نوع المشروع
        
    Returns:
        list: قائمة بمراحل المشروع
    """
    config = get_project_config(project_type)
    return config.get("phases", [])

# الحصول على علامات تبويب المشروع
def get_project_tabs(project_type):
    """
    الحصول على تابات نوع مشروع محدد
    
    Args:
        project_type (str): نوع المشروع
        
    Returns:
        list: قائمة بتابات المشروع
    """
    config = get_project_config(project_type)
    return config.get("tabs", [])
