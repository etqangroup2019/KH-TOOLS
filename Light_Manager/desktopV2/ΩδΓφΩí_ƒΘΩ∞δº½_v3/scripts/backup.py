#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت النسخ الاحتياطي لقاعدة البيانات
يقوم بإنشاء نسخة احتياطية كاملة من قاعدة البيانات
"""

import sys
import os
import subprocess
import gzip
import shutil
from datetime import datetime
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import DATABASE_CONFIG, BACKUP_CONFIG, SYSTEM_CONFIG
import logging

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'backup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """
    كلاس النسخ الاحتياطي لقاعدة البيانات
    """
    
    def __init__(self):
        """تهيئة كلاس النسخ الاحتياطي"""
        self.db_config = DATABASE_CONFIG
        self.backup_config = BACKUP_CONFIG
        self.backup_path = Path(self.backup_config['backup_path'])
        
        # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("تم تهيئة نظام النسخ الاحتياطي")
    
    def create_backup(self, backup_name=None):
        """
        إنشاء نسخة احتياطية من قاعدة البيانات
        
        Args:
            backup_name: اسم النسخة الاحتياطية (اختياري)
            
        Returns:
            str: مسار ملف النسخة الاحتياطية أو None في حالة الفشل
        """
        try:
            # إنشاء اسم النسخة الاحتياطية
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.db_config['database']}_{timestamp}"
            
            # مسار ملف النسخة الاحتياطية
            backup_file = self.backup_path / f"{backup_name}.sql"
            
            logger.info(f"بدء إنشاء النسخة الاحتياطية: {backup_name}")
            
            # بناء أمر mysqldump
            mysqldump_cmd = [
                'mysqldump',
                f"--host={self.db_config['host']}",
                f"--user={self.db_config['user']}",
                f"--password={self.db_config['password']}",
                '--single-transaction',
                '--routines',
                '--triggers',
                '--default-character-set=utf8mb4',
                self.db_config['database']
            ]
            
            # تنفيذ أمر النسخ الاحتياطي
            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    mysqldump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
            
            if result.returncode != 0:
                logger.error(f"فشل في إنشاء النسخة الاحتياطية: {result.stderr}")
                if backup_file.exists():
                    backup_file.unlink()
                return None
            
            # ضغط النسخة الاحتياطية إذا كان مفعلاً
            if self.backup_config['compression']:
                compressed_file = self._compress_backup(backup_file)
                if compressed_file:
                    backup_file.unlink()  # حذف الملف غير المضغوط
                    backup_file = compressed_file
            
            # إضافة معلومات النسخة الاحتياطية
            self._add_backup_info(backup_file)
            
            logger.info(f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_file}")
            
            # تنظيف النسخ القديمة
            self._cleanup_old_backups()
            
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return None
    
    def _compress_backup(self, backup_file):
        """
        ضغط ملف النسخة الاحتياطية
        
        Args:
            backup_file: مسار ملف النسخة الاحتياطية
            
        Returns:
            Path: مسار الملف المضغوط أو None
        """
        try:
            compressed_file = backup_file.with_suffix('.sql.gz')
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"تم ضغط النسخة الاحتياطية: {compressed_file}")
            return compressed_file
            
        except Exception as e:
            logger.error(f"خطأ في ضغط النسخة الاحتياطية: {e}")
            return None
    
    def _add_backup_info(self, backup_file):
        """
        إضافة معلومات النسخة الاحتياطية
        
        Args:
            backup_file: مسار ملف النسخة الاحتياطية
        """
        try:
            info_file = backup_file.with_suffix('.info')
            
            backup_info = {
                'اسم_النسخة': backup_file.stem,
                'تاريخ_الإنشاء': datetime.now().isoformat(),
                'قاعدة_البيانات': self.db_config['database'],
                'حجم_الملف': backup_file.stat().st_size,
                'نوع_الضغط': 'gzip' if backup_file.suffix == '.gz' else 'none',
                'إصدار_النظام': SYSTEM_CONFIG['version']
            }
            
            with open(info_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.warning(f"تعذر إنشاء ملف معلومات النسخة الاحتياطية: {e}")
    
    def _cleanup_old_backups(self):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            max_backups = self.backup_config['max_backups']
            
            # الحصول على قائمة النسخ الاحتياطية مرتبة حسب التاريخ
            backup_files = []
            for file in self.backup_path.glob('*.sql*'):
                if file.suffix in ['.sql', '.gz']:
                    backup_files.append(file)
            
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # حذف النسخ الزائدة
            if len(backup_files) > max_backups:
                for old_backup in backup_files[max_backups:]:
                    try:
                        old_backup.unlink()
                        # حذف ملف المعلومات المرافق
                        info_file = old_backup.with_suffix('.info')
                        if info_file.exists():
                            info_file.unlink()
                        logger.info(f"تم حذف النسخة الاحتياطية القديمة: {old_backup}")
                    except Exception as e:
                        logger.warning(f"تعذر حذف النسخة الاحتياطية القديمة {old_backup}: {e}")
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف النسخ الاحتياطية القديمة: {e}")
    
    def list_backups(self):
        """
        عرض قائمة النسخ الاحتياطية المتاحة
        
        Returns:
            list: قائمة بمعلومات النسخ الاحتياطية
        """
        try:
            backups = []
            
            for backup_file in self.backup_path.glob('*.sql*'):
                if backup_file.suffix in ['.sql', '.gz']:
                    info_file = backup_file.with_suffix('.info')
                    
                    backup_info = {
                        'اسم_الملف': backup_file.name,
                        'المسار': str(backup_file),
                        'الحجم': backup_file.stat().st_size,
                        'تاريخ_الإنشاء': datetime.fromtimestamp(backup_file.stat().st_mtime)
                    }
                    
                    # قراءة ملف المعلومات إذا كان موجوداً
                    if info_file.exists():
                        try:
                            import json
                            with open(info_file, 'r', encoding='utf-8') as f:
                                extra_info = json.load(f)
                                backup_info.update(extra_info)
                        except:
                            pass
                    
                    backups.append(backup_info)
            
            # ترتيب النسخ حسب التاريخ (الأحدث أولاً)
            backups.sort(key=lambda x: x['تاريخ_الإنشاء'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة النسخ الاحتياطية: {e}")
            return []

def main():
    """الدالة الرئيسية لتشغيل النسخ الاحتياطي"""
    print("="*60)
    print("نظام النسخ الاحتياطي - منظومة المهندس v3")
    print("="*60)
    
    backup_system = DatabaseBackup()
    
    # إنشاء نسخة احتياطية
    backup_file = backup_system.create_backup()
    
    if backup_file:
        print(f"✅ تم إنشاء النسخة الاحتياطية بنجاح")
        print(f"📁 المسار: {backup_file}")
        
        # عرض قائمة النسخ الاحتياطية
        print("\n" + "="*60)
        print("النسخ الاحتياطية المتاحة:")
        print("="*60)
        
        backups = backup_system.list_backups()
        for i, backup in enumerate(backups[:5], 1):  # عرض آخر 5 نسخ
            size_mb = backup['الحجم'] / (1024 * 1024)
            print(f"{i}. {backup['اسم_الملف']}")
            print(f"   📅 التاريخ: {backup['تاريخ_الإنشاء']}")
            print(f"   📊 الحجم: {size_mb:.2f} MB")
            print()
        
    else:
        print("❌ فشل في إنشاء النسخة الاحتياطية")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)