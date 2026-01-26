#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعدادات النظام المركزية
يحتوي على جميع الإعدادات والثوابت المستخدمة في النظام
"""

import os
from pathlib import Path

# مسارات النظام
PROJECT_ROOT = Path(__file__).parent.parent
MODULES_PATH = PROJECT_ROOT / "modules"
CORE_PATH = PROJECT_ROOT / "core"
LOGS_PATH = PROJECT_ROOT / "logs"
BACKUP_PATH = PROJECT_ROOT / "backups"

# إعدادات قاعدة البيانات
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'kh123456'),
    'database': os.getenv('DB_NAME', 'منظومة_المهندس_v3')
}

# إعدادات النظام
SYSTEM_CONFIG = {
    'name': 'منظومة المهندس v3',
    'version': '3.0.0',
    'description': 'نظام المحاسبة الشامل',
    'author': 'فريق منظومة المهندس',
    'license': 'MIT',
    'encoding': 'utf-8',
    'timezone': 'Asia/Riyadh',
    'language': 'ar'
}

# إعدادات السجلات
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file_encoding': 'utf-8',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'files': {
        'main': LOGS_PATH / 'system.log',
        'database': LOGS_PATH / 'database.log',
        'modules': LOGS_PATH / 'modules.log',
        'errors': LOGS_PATH / 'errors.log'
    }
}

# إعدادات الأمان
SECURITY_CONFIG = {
    'password_min_length': 8,
    'password_require_special': True,
    'password_require_numbers': True,
    'session_timeout': 3600,  # ساعة واحدة
    'max_login_attempts': 5,
    'lockout_duration': 900,  # 15 دقيقة
    'encryption_algorithm': 'SHA-256',
    'salt_length': 32
}

# إعدادات النسخ الاحتياطي
BACKUP_CONFIG = {
    'auto_backup': True,
    'backup_interval': 24,  # ساعة
    'max_backups': 30,  # عدد النسخ المحفوظة
    'compression': True,
    'include_logs': False,
    'backup_path': BACKUP_PATH,
    'backup_format': 'sql'
}

# إعدادات التقارير
REPORTS_CONFIG = {
    'default_format': 'pdf',
    'supported_formats': ['pdf', 'excel', 'csv', 'html'],
    'template_path': PROJECT_ROOT / 'templates' / 'reports',
    'output_path': PROJECT_ROOT / 'output' / 'reports',
    'logo_path': PROJECT_ROOT / 'assets' / 'logo.png',
    'company_info': {
        'name': 'منظومة المهندس',
        'address': 'المملكة العربية السعودية',
        'phone': '+966-XX-XXX-XXXX',
        'email': 'info@engineer-system.com',
        'website': 'www.engineer-system.com'
    }
}

# إعدادات الوحدات
MODULES_CONFIG = {
    'auto_load': True,
    'load_order': [
        'accounting',
        'clients',
        'suppliers',
        'employees',
        'projects',
        'contracts',
        'training',
        'expenses',
        'revenues',
        'reports'
    ],
    'required_modules': [
        'accounting',
        'reports'
    ],
    'optional_modules': [
        'training',
        'contracts'
    ]
}

# إعدادات واجهة المستخدم
UI_CONFIG = {
    'theme': 'default',
    'language': 'ar',
    'direction': 'rtl',
    'date_format': 'dd/mm/yyyy',
    'time_format': '24h',
    'currency': 'SAR',
    'decimal_places': 2,
    'thousand_separator': ',',
    'decimal_separator': '.'
}

# إعدادات الأداء
PERFORMANCE_CONFIG = {
    'cache_enabled': True,
    'cache_timeout': 300,  # 5 دقائق
    'max_records_per_page': 100,
    'query_timeout': 30,  # ثانية
    'connection_timeout': 10,  # ثانية
    'max_concurrent_users': 50
}

# إعدادات التطوير
DEVELOPMENT_CONFIG = {
    'debug_mode': False,
    'test_mode': False,
    'profiling_enabled': False,
    'sql_logging': False,
    'auto_reload': False,
    'test_database': 'منظومة_المهندس_v3_test'
}

# دوال مساعدة للإعدادات
def get_database_config(test_mode=False):
    """
    الحصول على إعدادات قاعدة البيانات
    
    Args:
        test_mode: استخدام قاعدة بيانات الاختبار
        
    Returns:
        dict: إعدادات قاعدة البيانات
    """
    config = DATABASE_CONFIG.copy()
    if test_mode:
        config['database'] = DEVELOPMENT_CONFIG['test_database']
    return config

def get_log_file_path(log_type='main'):
    """
    الحصول على مسار ملف السجل
    
    Args:
        log_type: نوع السجل
        
    Returns:
        Path: مسار ملف السجل
    """
    return LOGGING_CONFIG['files'].get(log_type, LOGGING_CONFIG['files']['main'])

def is_module_required(module_name):
    """
    التحقق من كون الوحدة مطلوبة
    
    Args:
        module_name: اسم الوحدة
        
    Returns:
        bool: True إذا كانت الوحدة مطلوبة
    """
    return module_name in MODULES_CONFIG['required_modules']

def get_module_load_order():
    """
    الحصول على ترتيب تحميل الوحدات
    
    Returns:
        list: قائمة أسماء الوحدات مرتبة
    """
    return MODULES_CONFIG['load_order']

# إنشاء المجلدات المطلوبة
def create_required_directories():
    """إنشاء المجلدات المطلوبة للنظام"""
    directories = [
        LOGS_PATH,
        BACKUP_PATH,
        REPORTS_CONFIG['template_path'],
        REPORTS_CONFIG['output_path'],
        PROJECT_ROOT / 'assets',
        PROJECT_ROOT / 'temp'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# تشغيل إنشاء المجلدات عند استيراد الملف
if __name__ != '__main__':
    create_required_directories()