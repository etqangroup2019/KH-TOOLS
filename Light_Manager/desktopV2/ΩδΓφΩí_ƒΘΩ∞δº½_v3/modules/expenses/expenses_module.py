#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة المصروفات
"""

import logging
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.base_module import BaseModule
from core.database import DatabaseManager

logger = logging.getLogger(__name__)

class ExpensesModule(BaseModule):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, "المصروفات")
        self.tables = ['المصروفات_العامة', 'فئات_المصروفات', 'مراكز_التكلفة']
    
    def create_tables(self) -> bool:
        try:
            logger.info("إنشاء جداول المصروفات...")
            # سيتم إضافة جداول المصروفات هنا
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول المصروفات: {e}")
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        return {
            'اسم_الوحدة': self.module_name,
            'الوصف': 'وحدة إدارة المصروفات العامة',
            'الجداول': self.tables
        }