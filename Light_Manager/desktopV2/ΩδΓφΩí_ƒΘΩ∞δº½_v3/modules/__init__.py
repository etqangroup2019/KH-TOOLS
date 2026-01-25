#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدات النظام المحاسبي
"""

from .accounting import AccountingModule
from .projects import ProjectsModule
from .contracts import ContractsModule
from .employees import EmployeesModule
from .suppliers import SuppliersModule
from .clients import ClientsModule
from .training import TrainingModule
from .expenses import ExpensesModule
from .revenues import RevenuesModule
from .reports import ReportsModule

__all__ = [
    'AccountingModule',
    'ProjectsModule', 
    'ContractsModule',
    'EmployeesModule',
    'SuppliersModule',
    'ClientsModule',
    'TrainingModule',
    'ExpensesModule',
    'RevenuesModule',
    'ReportsModule'
]