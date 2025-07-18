from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ✅ الصفحة الرئيسية
    path('', views.home, name='home'),

    # ✅ عرض الوثيقة والتعامل معها
    path('note/<uuid:token>/', views.note_detail, name='note_detail'),
    path('note/<uuid:token>/qr_only/', views.note_qr_only, name='note_qr_only'),
    path('note/<uuid:token>/official-pdf/', views.note_official_pdf, name='note_official_pdf'),

    # ✅ دخول عبر QR
    path('qr/<uuid:token>/', views.qr_note_access, name='qr_note_access'),

    # ✅ تسجيل وإدارة الحساب
    path('register/', views.register, name='register'),
    path('no_permission/', views.no_permission, name='no_permission'),
    path('profile/', views.profile, name='profile'),

    # ✅ إنشاء وثيقة
    path('create_note/', views.create_note, name='create_note'),

    # ✅ لوحة الإحصائيات
    path('stats/', views.stats_dashboard, name='stats_dashboard'),

    # ✅ عمليات على الوثائق
    path('note/<int:note_id>/archive/', views.archive_note, name='archive_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('note/<int:note_id>/restore/', views.restore_note, name='restore_note'),

    # ✅ الأقسام المختلفة للوثائق
    path('archived/', views.archived_notes, name='archived_notes'),
    path('expired/', views.expired_notes, name='expired_notes'),
    path('outgoing/', views.outgoing_notes, name='outgoing_notes'),
    path('incoming/', views.incoming_notes, name='incoming_notes'),
    path('my-notes/', views.user_notes, name='user_notes'),

    # ✅ سجلات النظام
    path('search-log/', views.search_log, name='search_log'),
    path('archive-log/', views.archive_log, name='archive_log'),
    path('login-history/', views.login_history, name='login_history'),
    path('role-change-log/', views.role_change_log, name='role_change_log'),

    # ✅ الإشعارات وسجلات التفاعل
    path('notifications/', views.notifications_view, name='notifications'),
    path('activity-log/', views.activity_log_view, name='activity_log'),
    path('access-log/', views.access_log, name='access_log'),

    # ✅ إدارة المستخدمين
    path('user-management/', views.user_management, name='user_management'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-user-role/<int:user_id>/', views.change_user_role, name='change_user_role'),

    # ✅ استعادة كلمة المرور
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
]
