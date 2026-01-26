#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
التقارير المالية المتقدمة
يحتوي على جميع التقارير المالية المطلوبة مع إمكانيات التصدير والطباعة
"""

import sys
import os
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from متغيرات import Currency_type


# فئة التقارير المالية المتقدمة
class AdvancedFinancialReports:
    
    # init
    def __init__(self, main_window):
        self.main_window = main_window
        self.company_name = "شركة المهندس للاستشارات الهندسية"
    
    # إنشاء قائمة الدخل
    def generate_income_statement(self, from_date=None, to_date=None):
        try:
            if not from_date:
                from_date = date(date.today().year, 1, 1)
            if not to_date:
                to_date = date.today()
            
            conn = self.main_window.get_db_connection()
            if not conn:
                return self.get_sample_income_statement()
            
            cursor = conn.cursor()
            
            # حساب الإيرادات
            revenues = self.calculate_revenues(cursor, from_date, to_date)
            
            # حساب المصروفات
            expenses = self.calculate_expenses(cursor, from_date, to_date)
            
            # حساب صافي الربح
            net_income = revenues["total"] - expenses["total"]
            
            cursor.close()
            conn.close()
            
            # إنشاء HTML للتقرير
            html = self.create_income_statement_html(revenues, expenses, net_income, from_date, to_date)
            
            return html
            
        except Exception as e:
            print(f"خطأ في إنشاء قائمة الدخل: {e}")
            return self.get_sample_income_statement()
    
    # حساب الإيرادات
    def calculate_revenues(self, cursor, from_date, to_date):
        revenues = {
            "project_revenues": 0,
            "contract_revenues": 0,
            "training_revenues": 0,
            "other_revenues": 0,
            "total": 0
        }
        
        try:
            # إيرادات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المدفوع), 0) 
                FROM المشاريع 
                WHERE اسم_القسم = 'المشاريع' 
                AND تاريخ_التسليم BETWEEN %s AND %s
            """, (from_date, to_date))
            revenues["project_revenues"] = cursor.fetchone()[0] or 0
            
            # إيرادات المقاولات
            cursor.execute("""
                SELECT COALESCE(SUM(المدفوع), 0) 
                FROM المشاريع 
                WHERE اسم_القسم = 'المقاولات' 
                AND تاريخ_التسليم BETWEEN %s AND %s
            """, (from_date, to_date))
            revenues["contract_revenues"] = cursor.fetchone()[0] or 0
            
            # إيرادات التدريب (من دفعات الطلاب)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM التدريب_دفعات_الطلاب
                WHERE تاريخ_الدفع BETWEEN %s AND %s
            """, (from_date, to_date))
            revenues["training_revenues"] = cursor.fetchone()[0] or 0
            
            # إيرادات أخرى (يمكن إضافتها لاحقاً)
            revenues["other_revenues"] = 0
            
            # إجمالي الإيرادات
            revenues["total"] = (revenues["project_revenues"] + 
                               revenues["contract_revenues"] + 
                               revenues["training_revenues"] + 
                               revenues["other_revenues"])
            
        except Exception as e:
            print(f"خطأ في حساب الإيرادات: {e}")
        
        return revenues
    
    # حساب المصروفات
    def calculate_expenses(self, cursor, from_date, to_date):
        expenses = {
            "project_expenses": 0,
            "employee_expenses": 0,
            "administrative_expenses": 0,
            "other_expenses": 0,
            "total": 0
        }
        
        try:
            # مصروفات المشاريع
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM المقاولات_مصروفات_العهد 
                WHERE تاريخ_المصروف BETWEEN %s AND %s
            """, (from_date, to_date))
            expenses["project_expenses"] = cursor.fetchone()[0] or 0
            
            # مصروفات الموظفين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM الموظفين_معاملات_مالية 
                WHERE نوع_العملية IN ('إيداع') 
                AND التاريخ BETWEEN %s AND %s
            """, (from_date, to_date))
            expenses["employee_expenses"] = cursor.fetchone()[0] or 0
            
            # المصروفات الإدارية
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM الحسابات 
                WHERE تاريخ_المصروف BETWEEN %s AND %s
            """, (from_date, to_date))
            expenses["administrative_expenses"] = cursor.fetchone()[0] or 0
            
            # مصروفات أخرى
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM التدريب_مصروفات 
                WHERE تاريخ_المصروف BETWEEN %s AND %s
            """, (from_date, to_date))
            expenses["other_expenses"] = cursor.fetchone()[0] or 0
            
            # إجمالي المصروفات
            expenses["total"] = (expenses["project_expenses"] + 
                               expenses["employee_expenses"] + 
                               expenses["administrative_expenses"] + 
                               expenses["other_expenses"])
            
        except Exception as e:
            print(f"خطأ في حساب المصروفات: {e}")
        
        return expenses
    
    # إنشاء HTML لقائمة الدخل
    def create_income_statement_html(self, revenues, expenses, net_income, from_date, to_date):
        html = f"""
        <html dir="rtl">
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .company-name {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .report-title {{ font-size: 16px; font-weight: bold; color: #34495e; margin: 10px 0; }}
                .period {{ font-size: 14px; color: #7f8c8d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ecf0f1; }}
                th {{ background-color: #3498db; color: white; font-weight: bold; }}
                .section-header {{ background-color: #ecf0f1; font-weight: bold; }}
                .total-row {{ background-color: #2ecc71; color: white; font-weight: bold; }}
                .net-income {{ background-color: #e74c3c; color: white; font-weight: bold; }}
                .amount {{ text-align: center; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">{self.company_name}</div>
                <div class="report-title">قائمة الدخل</div>
                <div class="period">للفترة من {from_date.strftime('%d/%m/%Y')} إلى {to_date.strftime('%d/%m/%Y')}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>البيان</th>
                        <th>المبلغ ({Currency_type})</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="section-header">
                        <td>الإيرادات</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">إيرادات المشاريع</td>
                        <td class="amount">{revenues['project_revenues']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">إيرادات المقاولات</td>
                        <td class="amount">{revenues['contract_revenues']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">إيرادات التدريب</td>
                        <td class="amount">{revenues['training_revenues']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">إيرادات أخرى</td>
                        <td class="amount">{revenues['other_revenues']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td>إجمالي الإيرادات</td>
                        <td class="amount">{revenues['total']:,.2f}</td>
                    </tr>
                    
                    <tr class="section-header">
                        <td>المصروفات</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">مصروفات المشاريع</td>
                        <td class="amount">{expenses['project_expenses']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">مصروفات الموظفين</td>
                        <td class="amount">{expenses['employee_expenses']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">مصروفات إدارية</td>
                        <td class="amount">{expenses['administrative_expenses']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 30px;">مصروفات أخرى</td>
                        <td class="amount">{expenses['other_expenses']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td>إجمالي المصروفات</td>
                        <td class="amount">{expenses['total']:,.2f}</td>
                    </tr>
                    
                    <tr class="{'net-income' if net_income < 0 else 'total-row'}">
                        <td>صافي {'الخسارة' if net_income < 0 else 'الربح'}</td>
                        <td class="amount">{abs(net_income):,.2f}</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin-top: 30px; font-size: 12px; color: #7f8c8d;">
                تم إنشاء التقرير في: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </body>
        </html>
        """
        
        return html
    
    # إنشاء الميزانية العمومية
    def generate_balance_sheet(self, as_of_date=None):
        try:
            if not as_of_date:
                as_of_date = date.today()
            
            conn = self.main_window.get_db_connection()
            if not conn:
                return self.get_sample_balance_sheet()
            
            cursor = conn.cursor()
            
            # حساب الأصول
            assets = self.calculate_assets(cursor, as_of_date)
            
            # حساب الخصوم
            liabilities = self.calculate_liabilities(cursor, as_of_date)
            
            # حساب حقوق الملكية
            equity = self.calculate_equity(cursor, as_of_date)
            
            cursor.close()
            conn.close()
            
            # إنشاء HTML للتقرير
            html = self.create_balance_sheet_html(assets, liabilities, equity, as_of_date)
            
            return html
            
        except Exception as e:
            print(f"خطأ في إنشاء الميزانية العمومية: {e}")
            return self.get_sample_balance_sheet()
    
    # حساب الأصول
    def calculate_assets(self, cursor, as_of_date):
        assets = {
            "current_assets": {
                "cash": 0,
                "accounts_receivable": 0,
                "inventory": 0,
                "prepaid_expenses": 0,
                "total": 0
            },
            "fixed_assets": {
                "land_buildings": 0,
                "equipment": 0,
                "furniture": 0,
                "vehicles": 0,
                "total": 0
            },
            "total": 0
        }
        
        try:
            # النقدية (تقدير من المدفوعات)
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0) 
                FROM المشاريع_المدفوعات 
                WHERE تاريخ_الدفع <= %s
            """, (as_of_date,))
            cash_in = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) 
                FROM الحسابات 
                WHERE تاريخ_المصروف <= %s
            """, (as_of_date,))
            cash_out = cursor.fetchone()[0] or 0
            
            assets["current_assets"]["cash"] = max(0, cash_in - cash_out)
            
            # العملاء والذمم المدينة
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي), 0) 
                FROM المشاريع 
                WHERE الباقي > 0 AND تاريخ_التسليم <= %s
            """, (as_of_date,))
            assets["current_assets"]["accounts_receivable"] = cursor.fetchone()[0] or 0
            
            # المخزون (تقدير)
            assets["current_assets"]["inventory"] = 0
            
            # المصروفات المدفوعة مقدماً (تقدير)
            assets["current_assets"]["prepaid_expenses"] = 0
            
            # إجمالي الأصول المتداولة
            assets["current_assets"]["total"] = (
                assets["current_assets"]["cash"] +
                assets["current_assets"]["accounts_receivable"] +
                assets["current_assets"]["inventory"] +
                assets["current_assets"]["prepaid_expenses"]
            )
            
            # الأصول الثابتة (تقديرات)
            assets["fixed_assets"]["land_buildings"] = 500000
            assets["fixed_assets"]["equipment"] = 200000
            assets["fixed_assets"]["furniture"] = 50000
            assets["fixed_assets"]["vehicles"] = 150000
            
            # إجمالي الأصول الثابتة
            assets["fixed_assets"]["total"] = (
                assets["fixed_assets"]["land_buildings"] +
                assets["fixed_assets"]["equipment"] +
                assets["fixed_assets"]["furniture"] +
                assets["fixed_assets"]["vehicles"]
            )
            
            # إجمالي الأصول
            assets["total"] = assets["current_assets"]["total"] + assets["fixed_assets"]["total"]
            
        except Exception as e:
            print(f"خطأ في حساب الأصول: {e}")
        
        return assets
    
    # حساب الخصوم
    def calculate_liabilities(self, cursor, as_of_date):
        liabilities = {
            "current_liabilities": {
                "accounts_payable": 0,
                "accrued_expenses": 0,
                "short_term_loans": 0,
                "total": 0
            },
            "long_term_liabilities": {
                "long_term_loans": 0,
                "total": 0
            },
            "total": 0
        }
        
        try:
            # الموردين والذمم الدائنة
            cursor.execute("""
                SELECT COALESCE(SUM(الباقي_للمورد), 0) 
                FROM الموردين 
                WHERE الباقي_للمورد > 0
            """, ())
            liabilities["current_liabilities"]["accounts_payable"] = cursor.fetchone()[0] or 0
            
            # المصروفات المستحقة (تقدير)
            liabilities["current_liabilities"]["accrued_expenses"] = 0
            
            # القروض قصيرة الأجل (تقدير)
            liabilities["current_liabilities"]["short_term_loans"] = 0
            
            # إجمالي الخصوم المتداولة
            liabilities["current_liabilities"]["total"] = (
                liabilities["current_liabilities"]["accounts_payable"] +
                liabilities["current_liabilities"]["accrued_expenses"] +
                liabilities["current_liabilities"]["short_term_loans"]
            )
            
            # القروض طويلة الأجل (تقدير)
            liabilities["long_term_liabilities"]["long_term_loans"] = 0
            liabilities["long_term_liabilities"]["total"] = liabilities["long_term_liabilities"]["long_term_loans"]
            
            # إجمالي الخصوم
            liabilities["total"] = liabilities["current_liabilities"]["total"] + liabilities["long_term_liabilities"]["total"]
            
        except Exception as e:
            print(f"خطأ في حساب الخصوم: {e}")
        
        return liabilities
    
    # حساب حقوق الملكية
    def calculate_equity(self, cursor, as_of_date):
        equity = {
            "capital": 1000000,  # رأس المال (تقدير)
            "retained_earnings": 0,
            "total": 0
        }
        
        try:
            # الأرباح المحتجزة (تقدير من صافي الربح)
            # يمكن حسابها من قائمة الدخل للسنوات السابقة
            equity["retained_earnings"] = 0
            
            # إجمالي حقوق الملكية
            equity["total"] = equity["capital"] + equity["retained_earnings"]
            
        except Exception as e:
            print(f"خطأ في حساب حقوق الملكية: {e}")
        
        return equity

    # إنشاء HTML للميزانية العمومية
    def create_balance_sheet_html(self, assets, liabilities, equity, as_of_date):
        html = f"""
        <html dir="rtl">
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .company-name {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .report-title {{ font-size: 16px; font-weight: bold; color: #34495e; margin: 10px 0; }}
                .period {{ font-size: 14px; color: #7f8c8d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ecf0f1; }}
                th {{ background-color: #3498db; color: white; font-weight: bold; }}
                .section-header {{ background-color: #ecf0f1; font-weight: bold; }}
                .total-row {{ background-color: #2ecc71; color: white; font-weight: bold; }}
                .amount {{ text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">{self.company_name}</div>
                <div class="report-title">الميزانية العمومية</div>
                <div class="period">كما في {as_of_date.strftime('%d/%m/%Y')}</div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>البيان</th>
                        <th>المبلغ ({Currency_type})</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="section-header">
                        <td>الأصول</td>
                        <td></td>
                    </tr>
                    <tr class="section-header">
                        <td style="padding-right: 20px;">الأصول المتداولة</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">النقدية والبنوك</td>
                        <td class="amount">{assets['current_assets']['cash']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">العملاء والذمم المدينة</td>
                        <td class="amount">{assets['current_assets']['accounts_receivable']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">المخزون</td>
                        <td class="amount">{assets['current_assets']['inventory']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">المصروفات المدفوعة مقدماً</td>
                        <td class="amount">{assets['current_assets']['prepaid_expenses']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">إجمالي الأصول المتداولة</td>
                        <td class="amount">{assets['current_assets']['total']:,.2f}</td>
                    </tr>

                    <tr class="section-header">
                        <td style="padding-right: 20px;">الأصول الثابتة</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">الأراضي والمباني</td>
                        <td class="amount">{assets['fixed_assets']['land_buildings']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">المعدات والآلات</td>
                        <td class="amount">{assets['fixed_assets']['equipment']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">الأثاث والتجهيزات</td>
                        <td class="amount">{assets['fixed_assets']['furniture']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">وسائل النقل</td>
                        <td class="amount">{assets['fixed_assets']['vehicles']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">إجمالي الأصول الثابتة</td>
                        <td class="amount">{assets['fixed_assets']['total']:,.2f}</td>
                    </tr>

                    <tr class="total-row">
                        <td>إجمالي الأصول</td>
                        <td class="amount">{assets['total']:,.2f}</td>
                    </tr>

                    <tr class="section-header">
                        <td>الخصوم وحقوق الملكية</td>
                        <td></td>
                    </tr>
                    <tr class="section-header">
                        <td style="padding-right: 20px;">الخصوم المتداولة</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">الموردين والذمم الدائنة</td>
                        <td class="amount">{liabilities['current_liabilities']['accounts_payable']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">المصروفات المستحقة</td>
                        <td class="amount">{liabilities['current_liabilities']['accrued_expenses']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">القروض قصيرة الأجل</td>
                        <td class="amount">{liabilities['current_liabilities']['short_term_loans']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">إجمالي الخصوم المتداولة</td>
                        <td class="amount">{liabilities['current_liabilities']['total']:,.2f}</td>
                    </tr>

                    <tr class="section-header">
                        <td style="padding-right: 20px;">حقوق الملكية</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">رأس المال</td>
                        <td class="amount">{equity['capital']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 40px;">الأرباح المحتجزة</td>
                        <td class="amount">{equity['retained_earnings']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">إجمالي حقوق الملكية</td>
                        <td class="amount">{equity['total']:,.2f}</td>
                    </tr>

                    <tr class="total-row">
                        <td>إجمالي الخصوم وحقوق الملكية</td>
                        <td class="amount">{liabilities['total'] + equity['total']:,.2f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top: 30px; font-size: 12px; color: #7f8c8d;">
                تم إنشاء التقرير في: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </body>
        </html>
        """

        return html

    # إنشاء قائمة التدفقات النقدية
    def generate_cash_flow_statement(self, from_date=None, to_date=None):
        try:
            if not from_date:
                from_date = date(date.today().year, 1, 1)
            if not to_date:
                to_date = date.today()

            conn = self.main_window.get_db_connection()
            if not conn:
                return self.get_sample_cash_flow()

            cursor = conn.cursor()

            # التدفقات النقدية من الأنشطة التشغيلية
            operating_flows = self.calculate_operating_cash_flows(cursor, from_date, to_date)

            # التدفقات النقدية من الأنشطة الاستثمارية
            investing_flows = self.calculate_investing_cash_flows(cursor, from_date, to_date)

            # التدفقات النقدية من الأنشطة التمويلية
            financing_flows = self.calculate_financing_cash_flows(cursor, from_date, to_date)

            # صافي التغير في النقدية
            net_change = operating_flows["net"] + investing_flows["net"] + financing_flows["net"]

            cursor.close()
            conn.close()

            # إنشاء HTML للتقرير
            html = self.create_cash_flow_html(operating_flows, investing_flows, financing_flows, net_change, from_date, to_date)

            return html

        except Exception as e:
            print(f"خطأ في إنشاء قائمة التدفقات النقدية: {e}")
            return self.get_sample_cash_flow()

    # حساب التدفقات النقدية من الأنشطة التشغيلية
    def calculate_operating_cash_flows(self, cursor, from_date, to_date):
        flows = {
            "receipts_from_customers": 0,
            "payments_to_suppliers": 0,
            "payments_to_employees": 0,
            "other_operating_payments": 0,
            "net": 0
        }

        try:
            # المقبوضات من العملاء
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ_المدفوع), 0)
                FROM المشاريع_المدفوعات
                WHERE تاريخ_الدفع BETWEEN %s AND %s
            """, (from_date, to_date))
            flows["receipts_from_customers"] = cursor.fetchone()[0] or 0

            # المدفوعات للموردين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات_دفعات_الموردين
                WHERE تاريخ_الدفعة BETWEEN %s AND %s
            """, (from_date, to_date))
            flows["payments_to_suppliers"] = cursor.fetchone()[0] or 0

            # المدفوعات للموظفين
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE نوع_العملية = 'إيداع'
                AND التاريخ BETWEEN %s AND %s
            """, (from_date, to_date))
            flows["payments_to_employees"] = cursor.fetchone()[0] or 0

            # مدفوعات تشغيلية أخرى
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات
                WHERE تاريخ_المصروف BETWEEN %s AND %s
            """, (from_date, to_date))
            flows["other_operating_payments"] = cursor.fetchone()[0] or 0

            # صافي التدفق النقدي من الأنشطة التشغيلية
            flows["net"] = (flows["receipts_from_customers"] -
                           flows["payments_to_suppliers"] -
                           flows["payments_to_employees"] -
                           flows["other_operating_payments"])

        except Exception as e:
            print(f"خطأ في حساب التدفقات التشغيلية: {e}")

        return flows

    # حساب التدفقات النقدية من الأنشطة الاستثمارية
    def calculate_investing_cash_flows(self, cursor, from_date, to_date):
        flows = {
            "purchase_of_assets": 0,
            "sale_of_assets": 0,
            "net": 0
        }

        try:
            # شراء أصول ثابتة (تقدير)
            flows["purchase_of_assets"] = 0

            # بيع أصول ثابتة (تقدير)
            flows["sale_of_assets"] = 0

            # صافي التدفق النقدي من الأنشطة الاستثمارية
            flows["net"] = flows["sale_of_assets"] - flows["purchase_of_assets"]

        except Exception as e:
            print(f"خطأ في حساب التدفقات الاستثمارية: {e}")

        return flows

    # حساب التدفقات النقدية من الأنشطة التمويلية
    def calculate_financing_cash_flows(self, cursor, from_date, to_date):
        flows = {
            "capital_contributions": 0,
            "loan_proceeds": 0,
            "loan_repayments": 0,
            "dividends_paid": 0,
            "net": 0
        }

        try:
            # مساهمات رأس المال (تقدير)
            flows["capital_contributions"] = 0

            # متحصلات القروض (تقدير)
            flows["loan_proceeds"] = 0

            # سداد القروض (تقدير)
            flows["loan_repayments"] = 0

            # توزيعات الأرباح (تقدير)
            flows["dividends_paid"] = 0

            # صافي التدفق النقدي من الأنشطة التمويلية
            flows["net"] = (flows["capital_contributions"] +
                           flows["loan_proceeds"] -
                           flows["loan_repayments"] -
                           flows["dividends_paid"])

        except Exception as e:
            print(f"خطأ في حساب التدفقات التمويلية: {e}")

        return flows

    # إنشاء HTML لقائمة التدفقات النقدية
    def create_cash_flow_html(self, operating_flows, investing_flows, financing_flows, net_change, from_date, to_date):
        html = f"""
        <html dir="rtl">
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .company-name {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .report-title {{ font-size: 16px; font-weight: bold; color: #34495e; margin: 10px 0; }}
                .period {{ font-size: 14px; color: #7f8c8d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ecf0f1; }}
                th {{ background-color: #3498db; color: white; font-weight: bold; }}
                .section-header {{ background-color: #ecf0f1; font-weight: bold; }}
                .total-row {{ background-color: #2ecc71; color: white; font-weight: bold; }}
                .amount {{ text-align: center; }}
                .negative {{ color: #e74c3c; }}
                .positive {{ color: #27ae60; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">{self.company_name}</div>
                <div class="report-title">قائمة التدفقات النقدية</div>
                <div class="period">للفترة من {from_date.strftime('%d/%m/%Y')} إلى {to_date.strftime('%d/%m/%Y')}</div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>البيان</th>
                        <th>المبلغ ({Currency_type})</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="section-header">
                        <td>التدفقات النقدية من الأنشطة التشغيلية</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">المقبوضات من العملاء</td>
                        <td class="amount positive">{operating_flows['receipts_from_customers']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">المدفوعات للموردين</td>
                        <td class="amount negative">({operating_flows['payments_to_suppliers']:,.2f})</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">المدفوعات للموظفين</td>
                        <td class="amount negative">({operating_flows['payments_to_employees']:,.2f})</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">مدفوعات تشغيلية أخرى</td>
                        <td class="amount negative">({operating_flows['other_operating_payments']:,.2f})</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">صافي التدفق النقدي من الأنشطة التشغيلية</td>
                        <td class="amount">{operating_flows['net']:,.2f}</td>
                    </tr>

                    <tr class="section-header">
                        <td>التدفقات النقدية من الأنشطة الاستثمارية</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">شراء أصول ثابتة</td>
                        <td class="amount negative">({investing_flows['purchase_of_assets']:,.2f})</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">بيع أصول ثابتة</td>
                        <td class="amount positive">{investing_flows['sale_of_assets']:,.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">صافي التدفق النقدي من الأنشطة الاستثمارية</td>
                        <td class="amount">{investing_flows['net']:,.2f}</td>
                    </tr>

                    <tr class="section-header">
                        <td>التدفقات النقدية من الأنشطة التمويلية</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">مساهمات رأس المال</td>
                        <td class="amount positive">{financing_flows['capital_contributions']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">متحصلات القروض</td>
                        <td class="amount positive">{financing_flows['loan_proceeds']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">سداد القروض</td>
                        <td class="amount negative">({financing_flows['loan_repayments']:,.2f})</td>
                    </tr>
                    <tr>
                        <td style="padding-right: 20px;">توزيعات الأرباح</td>
                        <td class="amount negative">({financing_flows['dividends_paid']:,.2f})</td>
                    </tr>
                    <tr class="total-row">
                        <td style="padding-right: 20px;">صافي التدفق النقدي من الأنشطة التمويلية</td>
                        <td class="amount">{financing_flows['net']:,.2f}</td>
                    </tr>

                    <tr class="total-row">
                        <td>صافي التغير في النقدية</td>
                        <td class="amount">{net_change:,.2f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top: 30px; font-size: 12px; color: #7f8c8d;">
                تم إنشاء التقرير في: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </body>
        </html>
        """

        return html

    # قائمة دخل نموذجية للاختبار
    def get_sample_income_statement(self):
        return """
        <h2 style='text-align: center; color: #2c3e50;'>قائمة الدخل (نموذجية)</h2>
        <p style='text-align: center;'>البيانات الفعلية غير متاحة حالياً</p>
        """

    # ميزانية عمومية نموذجية للاختبار
    def get_sample_balance_sheet(self):
        return """
        <h2 style='text-align: center; color: #2c3e50;'>الميزانية العمومية (نموذجية)</h2>
        <p style='text-align: center;'>البيانات الفعلية غير متاحة حالياً</p>
        """

    # قائمة تدفقات نقدية نموذجية للاختبار
    def get_sample_cash_flow(self):
        return """
        <h2 style='text-align: center; color: #2c3e50;'>قائمة التدفقات النقدية (نموذجية)</h2>
        <p style='text-align: center;'>البيانات الفعلية غير متاحة حالياً</p>
        """
