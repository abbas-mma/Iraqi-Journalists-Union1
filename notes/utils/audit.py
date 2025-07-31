from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone
from notes.models import AuditLog, DocumentChangeLog, SecurityAlert
from django.db.models import Count
import json
import re
from typing import Dict, Any, Optional
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache

class ReportGenerator:
    @staticmethod
    def generate_weekly_security_report():
        """إنتاج تقرير أمني أسبوعي"""
        today = timezone.now().date()
        start_week = today - timezone.timedelta(days=today.weekday())
        end_week = start_week + timezone.timedelta(days=6)

        weekly_logs = AuditLog.objects.filter(timestamp__date__gte=start_week, timestamp__date__lte=end_week)
        weekly_alerts = SecurityAlert.objects.filter(timestamp__date__gte=start_week, timestamp__date__lte=end_week)

        report = {
            'week_start': start_week,
            'week_end': end_week,
            'total_actions': weekly_logs.count(),
            'failed_logins': weekly_logs.filter(action='LOGIN', success=False).count(),
            'successful_logins': weekly_logs.filter(action='LOGIN', success=True).count(),
            'document_downloads': weekly_logs.filter(action='DOWNLOAD').count(),
            'security_alerts': {
                'total': weekly_alerts.count(),
                'critical': weekly_alerts.filter(risk_level='CRITICAL').count(),
                'high': weekly_alerts.filter(risk_level='HIGH').count(),
                'medium': weekly_alerts.filter(risk_level='MEDIUM').count(),
                'low': weekly_alerts.filter(risk_level='LOW').count(),
            },
            'top_users': list(
                weekly_logs.values('user__username')
                .annotate(action_count=Count('id'))
                .order_by('-action_count')[:10]
            ),
            'top_ips': list(
                weekly_logs.values('ip_address')
                .annotate(action_count=Count('id'))
                .order_by('-action_count')[:10]
            )
        }
        return report
    @staticmethod
    def generate_full_security_report():
        """إنتاج تقرير أمني شامل لكل السجلات"""
        logs = AuditLog.objects.all()
        alerts = SecurityAlert.objects.all()
        report = {
            'total_actions': logs.count(),
            'failed_logins': logs.filter(action='LOGIN', success=False).count(),
            'successful_logins': logs.filter(action='LOGIN', success=True).count(),
            'document_downloads': logs.filter(action='DOWNLOAD').count(),
            'security_alerts': {
                'total': alerts.count(),
                'critical': alerts.filter(risk_level='CRITICAL').count(),
                'high': alerts.filter(risk_level='HIGH').count(),
                'medium': alerts.filter(risk_level='MEDIUM').count(),
                'low': alerts.filter(risk_level='LOW').count(),
            },
            'top_users': list(
                logs.values('user__username')
                .annotate(action_count=Count('id'))
                .order_by('-action_count')[:10]
            ),
            'top_ips': list(
                logs.values('ip_address')
                .annotate(action_count=Count('id'))
                .order_by('-action_count')[:10]
            )
        }
        return report
    @staticmethod
    def generate_daily_security_report():
        """إنتاج تقرير أمني يومي"""
        today = timezone.now().date()
        todays_logs = AuditLog.objects.filter(timestamp__date=today)
        todays_alerts = SecurityAlert.objects.filter(timestamp__date=today)
        report = {
            'date': today,
            'total_actions': todays_logs.count(),
            'failed_logins': todays_logs.filter(action='LOGIN', success=False).count(),
            'successful_logins': todays_logs.filter(action='LOGIN', success=True).count(),
            'document_downloads': todays_logs.filter(action='DOWNLOAD').count(),
            'security_alerts': {
                'total': todays_alerts.count(),
                'critical': todays_alerts.filter(risk_level='CRITICAL').count(),
                'high': todays_alerts.filter(risk_level='HIGH').count(),
                'medium': todays_alerts.filter(risk_level='MEDIUM').count(),
                'low': todays_alerts.filter(risk_level='LOW').count(),
            },
            'top_users': list(
                todays_logs.values('user__username')
                .annotate(action_count=Count('id'))
                .order_by('-action_count')[:10]
            ),
            'top_ips': list(
                todays_logs.values('ip_address')
                .annotate(action_count=Count('id'))
                .order_by('-action_count')[:10]
            )
        }
        return report
    @staticmethod
    def generate_user_activity_report(user: User, days: int = 30):
        """تقرير نشاط مستخدم محدد"""
        start_date = timezone.now() - timezone.timedelta(days=days)
        user_logs = AuditLog.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        return {
            'user': user.username,
            'period_days': days,
            'total_actions': user_logs.count(),
            'actions_by_type': dict(
                user_logs.values('action')
                .annotate(count=Count('id'))
                .values_list('action', 'count')
            ),
            'login_history': list(
                user_logs.filter(action='LOGIN')
                .values('timestamp', 'ip_address', 'success')
                .order_by('-timestamp')[:20]
            ),
            'document_access': list(
                user_logs.filter(resource_type='document')
                .values('action', 'resource_name', 'timestamp')
                .order_by('-timestamp')[:50]
            )
        }

# دوال التدقيق المتقدم - utils/audit.py

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone
from notes.models import AuditLog, DocumentChangeLog, SecurityAlert
from django.db.models import Count
import json
import re
from typing import Dict, Any, Optional
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache


class AuditLogger:
    """نظام تسجيل العمليات المتقدم"""
    
    @staticmethod
    def get_client_info(request: HttpRequest) -> Dict[str, str]:
        """استخراج معلومات العميل من الطلب"""
        return {
            'ip_address': AuditLogger.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'session_key': request.session.session_key,
            'referer': request.META.get('HTTP_REFERER', ''),
            'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
        }
    
    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """استخراج عنوان IP الحقيقي"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def log_action(
        user: User,
        action: str,
        resource_type: str,
        resource_id: str = None,
        resource_name: str = None,
        description: str = "",
        old_values: Dict = None,
        new_values: Dict = None,
        request: HttpRequest = None,
        severity: str = 'LOW',
        success: bool = True,
        error_message: str = None
    ) -> AuditLog:
        """تسجيل عملية في سجل التدقيق"""
        
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        audit_log = AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            resource_name=resource_name,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=client_info.get('ip_address'),
            user_agent=client_info.get('user_agent'),
            session_key=client_info.get('session_key'),
            severity=severity,
            success=success,
            error_message=error_message
        )
        
        # تحليل الأمان إذا كانت العملية مهمة
        if severity in ['HIGH', 'CRITICAL']:
            SecurityAnalyzer.analyze_action(audit_log, request)
        
        return audit_log
    
    @staticmethod
    def log_document_change(
        document,
        user: User,
        change_type: str,
        field_name: str = None,
        old_value: str = None,
        new_value: str = None,
        change_reason: str = None,
        request: HttpRequest = None
    ) -> DocumentChangeLog:
        """تسجيل تغيير في الوثيقة"""
        
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return DocumentChangeLog.objects.create(
            document=document,
            user=user,
            change_type=change_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            change_reason=change_reason,
            ip_address=client_info.get('ip_address')
        )


class SecurityAnalyzer:
    """محلل الأمان المتقدم"""
    
    @staticmethod
    def analyze_action(audit_log: AuditLog, request: HttpRequest = None):
        """تحليل العملية للكشف عن التهديدات"""
        
        # تحليل محاولات الدخول المتعددة
        SecurityAnalyzer.check_multiple_failed_logins(audit_log)
        
        # تحليل الأنشطة المشبوهة
        SecurityAnalyzer.check_suspicious_activity(audit_log)
        
        # تحليل عنوان IP
        SecurityAnalyzer.check_ip_reputation(audit_log.ip_address)
        
        # تحليل نمط الاستخدام
        SecurityAnalyzer.check_usage_patterns(audit_log)
    
    @staticmethod
    def check_multiple_failed_logins(audit_log: AuditLog):
        """فحص محاولات الدخول الفاشلة المتعددة"""
        if audit_log.action == 'LOGIN' and not audit_log.success:
            # عد محاولات الدخول الفاشلة في آخر 30 دقيقة
            thirty_minutes_ago = timezone.now() - timezone.timedelta(minutes=30)
            failed_attempts = AuditLog.objects.filter(
                ip_address=audit_log.ip_address,
                action='LOGIN',
                success=False,
                timestamp__gte=thirty_minutes_ago
            ).count()
            
            if failed_attempts >= 5:
                SecurityAlert.objects.create(
                    alert_type='MULTIPLE_FAILED_LOGINS',
                    risk_level='HIGH',
                    user=audit_log.user,
                    ip_address=audit_log.ip_address,
                    user_agent=audit_log.user_agent,
                    description=f'محاولات دخول فاشلة متعددة ({failed_attempts}) من نفس العنوان',
                    details={'failed_attempts': failed_attempts, 'time_window': '30 minutes'}
                )
    
    @staticmethod
    def check_suspicious_activity(audit_log: AuditLog):
        """فحص الأنشطة المشبوهة"""
        # تحميل كمي مشبوه
        if audit_log.action == 'DOWNLOAD':
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            recent_downloads = AuditLog.objects.filter(
                user=audit_log.user,
                action='DOWNLOAD',
                timestamp__gte=one_hour_ago
            ).count()
            
            if recent_downloads >= 20:  # أكثر من 20 تحميل في الساعة
                SecurityAlert.objects.create(
                    alert_type='BULK_DOWNLOAD',
                    risk_level='MEDIUM',
                    user=audit_log.user,
                    ip_address=audit_log.ip_address,
                    description=f'تحميل كمي مشبوه ({recent_downloads} ملف في ساعة واحدة)',
                    details={'downloads_count': recent_downloads}
                )
        
        # وصول خارج ساعات العمل
        current_hour = timezone.now().hour
        if current_hour < 6 or current_hour > 22:  # خارج ساعات 6 صباحاً - 10 مساءً
            if audit_log.action in ['LOGIN', 'READ', 'DOWNLOAD']:
                SecurityAlert.objects.create(
                    alert_type='UNUSUAL_ACTIVITY',
                    risk_level='LOW',
                    user=audit_log.user,
                    ip_address=audit_log.ip_address,
                    description=f'نشاط خارج ساعات العمل العادية ({current_hour}:00)',
                    details={'access_hour': current_hour}
                )
    
    @staticmethod
    def check_ip_reputation(ip_address: str):
        """فحص سمعة عنوان IP"""
        # قائمة سوداء بسيطة (يمكن توسيعها بقواعد بيانات خارجية)
        blacklisted_ips = cache.get('blacklisted_ips', [])
        
        if ip_address in blacklisted_ips:
            SecurityAlert.objects.create(
                alert_type='IP_BLACKLIST',
                risk_level='HIGH',
                ip_address=ip_address,
                description=f'وصول من عنوان IP في القائمة السوداء: {ip_address}',
                details={'ip_address': ip_address}
            )
        
        # فحص الموقع الجغرافي (اختياري)
        try:
            g = GeoIP2()
            country = g.country(ip_address)
            if country['country_code'] not in ['IQ', 'US', 'UK']:  # البلدان المسموحة
                SecurityAlert.objects.create(
                    alert_type='UNUSUAL_ACTIVITY',
                    risk_level='MEDIUM',
                    ip_address=ip_address,
                    description=f'وصول من بلد غير معتاد: {country["country_name"]}',
                    details={'country': country}
                )
        except:
            pass  # تجاهل أخطاء GeoIP
    


# ديكوريتر لتسجيل العمليات تلقائياً
def audit_action(action: str, resource_type: str, severity: str = 'LOW'):
    """ديكوريتر لتسجيل العمليات في سجل التدقيق"""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                result = func(request, *args, **kwargs)
                
                # تسجيل العملية الناجحة
                AuditLogger.log_action(
                    user=request.user,
                    action=action,
                    resource_type=resource_type,
                    description=f'تم تنفيذ {func.__name__} بنجاح',
                    request=request,
                    severity=severity,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # تسجيل العملية الفاشلة
                AuditLogger.log_action(
                    user=request.user if hasattr(request, 'user') else None,
                    action=action,
                    resource_type=resource_type,
                    description=f'فشل في تنفيذ {func.__name__}',
                    request=request,
                    severity='HIGH',
                    success=False,
                    error_message=str(e)
                )
                
                raise
        
        return wrapper
    return decorator
