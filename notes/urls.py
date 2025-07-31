from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ✅ الصفحة الرئيسية
    path('', views.home, name='home'),
    # إضافة هذا السطر في urlpatterns
    path('news/add/', views.add_news, name='add_news'),

    # ✅ عرض الأخبار - إضافة المسار هنا
    path('news/', views.news_list, name='news'),
    path('news/<int:news_id>/comment/', views.add_news_comment, name='add_news_comment'),
    path('news/<int:news_id>/like/', views.toggle_news_like, name='toggle_news_like'),
    path('news/<int:news_id>/delete/', views.delete_news, name='delete_news'),

    # تفعيل الحساب عبر البريد
    path('activate/<str:token>/', views.activate_account, name='activate_account'),
    
    # ✅ مسح QR للجوال
    path('qr-scanner/', views.qr_scanner, name='qr_scanner'),
    
    # ✅ فحص PWA للتطبيق
    path('pwa-checker/', views.pwa_checker, name='pwa_checker'),
    
    # ✅ صفحة أوفلاين للPWA
    path('offline/', views.offline_page, name='offline'),

    # ✅ الوثائق: عرض، تفاصيل، QR، PDF
    path('note/<uuid:token>/', views.note_detail, name='note_detail'),
    path('note/<uuid:token>/qr_only/', views.note_qr_only, name='note_qr_only'),
    path('note/<uuid:token>/official-pdf/', views.note_official_pdf, name='note_official_pdf'),

    # ✅ الوصول عبر QR
    path('qr/<uuid:token>/', views.qr_note_access, name='qr_note_access'),
    path('ajax_quick_search/', views.ajax_quick_search, name='ajax_quick_search'),
]

from .views import (
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)

urlpatterns += [
    # ✅ إدارة الحساب وتسجيل الدخول
    path('audit/report-view/<str:report_type>/', views.audit_report_view, name='audit_report_view'),
    path('register/', views.register, name='register'),
    path('no_permission/', views.no_permission, name='no_permission'),
    path('profile/', views.profile, name='profile'),

    # ✅ إنشاء وثيقة جديدة
    path('create_note/', views.create_note, name='create_note'),

    # ✅ لوحة التحكم (Dashboard) — تم الإضافة
    path('dashboard/', views.dashboard, name='dashboard'),

    # ✅ لوحة الإحصائيات والتحليل
    path('stats/', views.stats_dashboard, name='stats_dashboard'),
    
    # 🆕 API للإحصائيات في الوقت الفعلي
    path('api/stats/realtime/', views.realtime_stats_api, name='realtime_stats_api'),

    # ✅ العمليات على الوثائق (أرشفة، حذف، استرجاع)
    path('note/<int:note_id>/archive/', views.archive_note, name='archive_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('note/<int:note_id>/restore/', views.restore_note, name='restore_note'),

    # ✅ الأقسام المختلفة حسب الحالة أو الاتجاه
    path('archived/', views.archived_notes, name='archived_notes'),
    path('expired/', views.expired_notes, name='expired_notes'),
    path('outgoing/', views.outgoing_notes, name='outgoing_notes'),
    path('incoming/', views.incoming_notes, name='incoming_notes'),
    path('my-notes/', views.user_notes, name='user_notes'),

    # ✅ السجلات والتتبع
    path('search-log/', views.search_log, name='search_log'),
    path('archive-log/', views.archive_log, name='archive_log'),
    path('login-history/', views.login_history, name='login_history'),
    path('role-change-log/', views.role_change_log, name='role_change_log'),
    path('activity-log/', views.activity_log_view, name='activity_log'),
    path('access-log/', views.access_log, name='access_log'),
    
    # ✅ نظام التدقيق المتقدم
    path('audit/', views.audit_dashboard, name='audit_dashboard'),
    path('audit/log-details/<int:log_id>/', views.audit_log_details, name='audit_log_details'),
    path('audit/resolve-alert/<int:alert_id>/', views.resolve_security_alert, name='resolve_security_alert'),
    path('audit/reports/daily/', views.daily_audit_report, name='daily_audit_report'),
    path('audit/reports/weekly/', views.weekly_audit_report, name='weekly_audit_report'),
    path('audit/reports/monthly/', views.monthly_audit_report, name='monthly_audit_report'),
    path('audit/reports/user/<str:username>/', views.user_audit_report, name='user_audit_report'),
    path('audit/reports/security/', views.security_audit_report, name='security_audit_report'),
    path('audit/export/', views.export_audit_log, name='export_audit_log'),
    path('audit/logs-ajax/', views.audit_logs_ajax, name='audit_logs_ajax'),

    # ✅ إدارة المستخدمين
    path('user-management/', views.user_management, name='user_management'),
    path('add-user/', views.add_user, name='add_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-user-role/<int:user_id>/', views.change_user_role, name='change_user_role'),

    # ✅ الإشعارات (تمت الإضافة هنا)
    path('notifications/', views.notifications, name='notifications'),
    
    # 🆕 مركز الإشعارات المتقدم
    path('notifications/center/', views.notifications_center, name='notifications_center'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/count/', views.get_unread_notifications_count, name='unread_notifications_count'),
    
    # 🆕 سجل النشاطات الشامل
    path('activities/', views.activity_feed, name='activity_feed'),
    path('activity-feed/', views.activity_feed, name='activity_feed_alt'),  # مسار بديل
    path('activities/api/', views.activity_feed_api, name='activity_feed_api'),
    path('activities/details/<int:activity_id>/', views.activity_details, name='activity_details'),
    path('activities/export/', views.export_activities, name='export_activities'),

    # ✅ استعادة وتغيير كلمة المرور (نظام Django الأساسي)
    # إعادة تعيين كلمة السر
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
