#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة المشاريع
وحدة شاملة لإدارة المشاريع مع جميع العمليات المطلوبة
"""

# from .models.project import Project
# from .controllers.project_controller import ProjectController
# from .views.projects_window import ProjectsWindow
# from .views.projects_summary_widget import ProjectsSummaryWidget
# from .projects_integration import projects_integration

from .إدارة_المشروع import*
from .إدارة_أسعار_المراحل import*

# معلومات الوحدة
__version__ = "1.0.0"
__author__ = "فريق التطوير"
__description__ = "وحدة إدارة المشاريع الشاملة"

# تصدير الفئات الرئيسية
__all__ = []

# معلومات الوحدة للنظام الرئيسي
MODULE_INFO = {
    'name': 'المشاريع',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'category': 'إدارة',
    'icon': 'المشاريع',
    'main_window_class': 'ProjectsWindow',
    'integration_class': 'projects_integration',
    'dependencies': ['العملاء'],  # يعتمد على وحدة العملاء
    'permissions': [
        'projects.view',
        'projects.add', 
        'projects.edit',
        'projects.delete',
        'projects.reports'
    ]
}