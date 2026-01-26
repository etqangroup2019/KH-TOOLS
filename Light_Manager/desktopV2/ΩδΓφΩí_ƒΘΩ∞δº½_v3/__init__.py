#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منظومة المهندس v3 - النظام المحاسبي الشامل
نظام محاسبي متكامل وقابل للتوسع مع دعم كامل للغة العربية

الوحدات الرئيسية:
- المحاسبة والتقارير (accounting)
- إدارة المشاريع (projects) 
- إدارة المقاولات (contracts)
- إدارة الموظفين (employees)
- إدارة الموردين (suppliers)
- إدارة العملاء (clients)
- إدارة التدريب (training)
- إدارة المصروفات (expenses)
- إدارة الإيرادات (revenues)
- التقارير الشاملة (reports)
"""

__version__ = "3.0.0"
__author__ = "فريق منظومة المهندس"
__email__ = "info@engineer-system.com"
__description__ = "نظام محاسبي شامل للمقاولات والتدريب"

# استيراد الوحدات الأساسية
from .core.database import DatabaseManager
from .core.base_module import BaseModule
from .core.system_manager import SystemManager

# استيراد وحدات النظام
from .modules.accounting import AccountingModule
from .modules.projects import ProjectsModule
from .modules.contracts import ContractsModule
from .modules.employees import EmployeesModule
from .modules.suppliers import SuppliersModule
from .modules.clients import ClientsModule
from .modules.training import TrainingModule
from .modules.expenses import ExpensesModule
from .modules.revenues import RevenuesModule
from .modules.reports import ReportsModule

# استيراد الأدوات المساعدة
from .utils.logger import setup_logger
from .utils.validators import DataValidator
from .utils.helpers import DateHelper, NumberHelper

__all__ = [
    'DatabaseManager',
    'BaseModule', 
    'SystemManager',
    'AccountingModule',
    'ProjectsModule',
    'ContractsModule',
    'EmployeesModule',
    'SuppliersModule',
    'ClientsModule',
    'TrainingModule',
    'ExpensesModule',
    'RevenuesModule',
    'ReportsModule',
    'setup_logger',
    'DataValidator',
    'DateHelper',
    'NumberHelper'
]