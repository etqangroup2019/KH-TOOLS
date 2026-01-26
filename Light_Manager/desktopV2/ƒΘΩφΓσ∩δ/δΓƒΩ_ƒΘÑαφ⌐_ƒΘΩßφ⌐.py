from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector
from الإعدادات_العامة import *
from ستايل import *
import qtawesome as qta
from datetime import datetime, time, date, timedelta

# نظام الحضور والانصراف المطور
class AdvancedAttendanceSystem:
    
    @staticmethod
    # حساب تفاصيل الحضور والانصراف بدقة
    def calculate_attendance_details(checkin_time, checkout_time, work_date):
        try:
            from إدارة_مواعيد_العمل import get_current_work_schedule, is_work_day
            
            # التحقق من كون اليوم يوم عمل
            if not is_work_day(work_date):
                return {
                    'checkin_status': None,
                    'checkin_early_minutes': 0,
                    'checkin_late_minutes': 0,
                    'checkout_status': None,
                    'checkout_early_minutes': 0,
                    'checkout_late_minutes': 0,
                    'is_work_day': False
                }
            
            # الحصول على مواعيد العمل
            schedule = get_current_work_schedule()
            if not schedule:
                return None
            
            # تحويل أوقات العمل
            morning_start = schedule['وقت_حضور_صباحي']
            morning_end = schedule['وقت_انصراف_صباحي']
            tolerance_minutes = schedule['فترة_التأخير_المسموحة'] or 15
            
            if isinstance(morning_start, str):
                morning_start = datetime.strptime(morning_start, '%H:%M:%S').time()
            if isinstance(morning_end, str):
                morning_end = datetime.strptime(morning_end, '%H:%M:%S').time()
            
            result = {
                'checkin_status': None,
                'checkin_early_minutes': 0,
                'checkin_late_minutes': 0,
                'checkout_status': None,
                'checkout_early_minutes': 0,
                'checkout_late_minutes': 0,
                'is_work_day': True
            }
            
            # حساب حالة الحضور
            if checkin_time:
                checkin_diff = AdvancedAttendanceSystem._calculate_time_difference(checkin_time, morning_start)
                
                if checkin_diff < 0:  # حضور مبكر
                    result['checkin_status'] = 'مبكر'
                    result['checkin_early_minutes'] = abs(checkin_diff)
                elif checkin_diff > tolerance_minutes:  # حضور متأخر
                    result['checkin_status'] = 'متأخر'
                    result['checkin_late_minutes'] = checkin_diff
                else:  # في الموعد
                    result['checkin_status'] = 'في_الموعد'
            
            # حساب حالة الانصراف
            if checkout_time:
                checkout_diff = AdvancedAttendanceSystem._calculate_time_difference(checkout_time, morning_end)
                
                if checkout_diff < 0:  # انصراف مبكر
                    result['checkout_status'] = 'مبكر'
                    result['checkout_early_minutes'] = abs(checkout_diff)
                elif checkout_diff > 0:  # انصراف متأخر
                    result['checkout_status'] = 'متأخر'
                    result['checkout_late_minutes'] = checkout_diff
                else:  # في الموعد
                    result['checkout_status'] = 'في_الموعد'
            
            return result
            
        except Exception as e:
            print(f"خطأ في حساب تفاصيل الحضور: {e}")
            return None
    
    @staticmethod
    # حساب الفرق بين الوقت الفعلي والمجدول بالدقائق
    def _calculate_time_difference(actual_time, scheduled_time):
        try:
            # تحويل الأوقات إلى datetime للحساب
            base_date = date.today()
            actual_datetime = datetime.combine(base_date, actual_time)
            scheduled_datetime = datetime.combine(base_date, scheduled_time)
            
            # حساب الفرق بالدقائق
            diff = (actual_datetime - scheduled_datetime).total_seconds() / 60
            return int(diff)
            
        except Exception as e:
            print(f"خطأ في حساب فرق الوقت: {e}")
            return 0
    
    @staticmethod
    # تحويل الدقائق إلى تنسيق ساعات ودقائق
    def format_duration(minutes):
        if minutes == 0:
            return "0 دقيقة"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if hours == 0:
            return f"{remaining_minutes} دقيقة"
        elif remaining_minutes == 0:
            return f"{hours} ساعة"
        else:
            return f"{hours} ساعة و {remaining_minutes} دقيقة"
    
    @staticmethod
    # التحقق من وجود سجل حضور لنفس اليوم
    def check_existing_attendance(employee_id, work_date):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT id, وقت_الحضور, وقت_الانصراف
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s AND التاريخ = %s
            """, (employee_id, work_date))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"خطأ في التحقق من الحضور الموجود: {e}")
            return None
    
    @staticmethod
    # تسجيل حضور الموظف
    def register_checkin(employee_id, checkin_time, work_date, notes=""):
        try:
            # التحقق من وجود سجل لنفس اليوم
            existing = AdvancedAttendanceSystem.check_existing_attendance(employee_id, work_date)
            
            if existing and existing['وقت_الحضور']:
                return {
                    'success': False,
                    'message': 'تم تسجيل الحضور مسبقاً لهذا اليوم'
                }
            
            # حساب تفاصيل الحضور
            details = AdvancedAttendanceSystem.calculate_attendance_details(checkin_time, None, work_date)
            if not details:
                return {
                    'success': False,
                    'message': 'فشل في حساب تفاصيل الحضور'
                }
            
            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()
            
            if existing:
                # تحديث السجل الموجود
                cursor.execute("""
                    UPDATE الموظفين_الحضور_والانصراف
                    SET وقت_الحضور = %s,
                        حالة_الحضور = %s,
                        مدة_تأخير_الحضور = %s,
                        مدة_تبكير_الحضور = %s,
                        ملاحظات = %s,
                        تاريخ_التحديث = NOW()
                    WHERE id = %s
                """, (
                    checkin_time,
                    details['checkin_status'],
                    details['checkin_late_minutes'],
                    details['checkin_early_minutes'],
                    notes,
                    existing['id']
                ))
            else:
                # إنشاء سجل جديد
                cursor.execute("""
                    INSERT INTO الموظفين_الحضور_والانصراف
                    (معرف_الموظف, التاريخ, وقت_الحضور, حالة_الحضور,
                     مدة_تأخير_الحضور, مدة_تبكير_الحضور, ملاحظات)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    employee_id, work_date, checkin_time,
                    details['checkin_status'],
                    details['checkin_late_minutes'],
                    details['checkin_early_minutes'],
                    notes
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'تم تسجيل الحضور بنجاح',
                'details': details
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'فشل في تسجيل الحضور: {str(e)}'
            }
    
    @staticmethod
    # تسجيل انصراف الموظف
    def register_checkout(employee_id, checkout_time, work_date, notes=""):
        try:
            # التحقق من وجود سجل حضور لنفس اليوم
            existing = AdvancedAttendanceSystem.check_existing_attendance(employee_id, work_date)
            
            if not existing:
                return {
                    'success': False,
                    'message': 'لا يمكن تسجيل الانصراف بدون تسجيل الحضور أولاً'
                }
            
            if not existing['وقت_الحضور']:
                return {
                    'success': False,
                    'message': 'لا يمكن تسجيل الانصراف بدون تسجيل الحضور أولاً'
                }
            
            if existing['وقت_الانصراف']:
                return {
                    'success': False,
                    'message': 'تم تسجيل الانصراف مسبقاً لهذا اليوم'
                }
            
            # حساب تفاصيل الانصراف
            details = AdvancedAttendanceSystem.calculate_attendance_details(
                existing['وقت_الحضور'], checkout_time, work_date
            )
            if not details:
                return {
                    'success': False,
                    'message': 'فشل في حساب تفاصيل الانصراف'
                }
            
            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()
            
            # تحديث السجل بوقت الانصراف
            cursor.execute("""
                UPDATE الموظفين_الحضور_والانصراف
                SET وقت_الانصراف = %s,
                    حالة_الانصراف = %s,
                    مدة_تأخير_الانصراف = %s,
                    مدة_تبكير_الانصراف = %s,
                    ملاحظات = CONCAT(IFNULL(ملاحظات, ''), %s),
                    تاريخ_التحديث = NOW()
                WHERE id = %s
            """, (
                checkout_time,
                details['checkout_status'],
                details['checkout_late_minutes'],
                details['checkout_early_minutes'],
                f" | انصراف: {notes}" if notes else "",
                existing['id']
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'تم تسجيل الانصراف بنجاح',
                'details': details
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'فشل في تسجيل الانصراف: {str(e)}'
            }
