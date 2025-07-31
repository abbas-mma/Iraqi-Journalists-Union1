from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    Note,
    SecurityWarning,
    UserProfile,
    RoleChangeLog,
    LoginHistory,
    Attachment,
    AccessLog,
    ActivityLog,
    AccessNotification,
    Tag  # ⬅️ لا تنس تسجيل الوسوم أيضًا
)

# استيراد النماذج الجديدة للتدقيق المتقدم
try:
    from .models import AuditLog, DocumentChangeLog, SecurityAlert
    AUDIT_MODELS_AVAILABLE = True
except ImportError:
    AUDIT_MODELS_AVAILABLE = False

# ✅ إدارة المستخدمين
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'role')

# ✅ إدارة الوثائق
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'created_at', 'issuer_name', 'is_archived', 'expiry_date', 'display_token')
    list_filter = ('doc_type', 'direction', 'importance', 'is_archived')
    search_fields = ('title', 'issuer_name', 'recipient_name')
    readonly_fields = ('access_token', 'copy_token_display', 'created_at')
    fields = (
        'title', 'content', 'doc_type', 'direction', 'importance',
        'file', 'stamp', 'signature',
        'issuer_name', 'recipient_name',
        'tags', 'is_archived', 'expiry_date',
        'copy_token_display', 'created_at'
    )

    def display_token(self, obj):
        return str(obj.access_token)
    display_token.short_description = 'Access Token'

    def copy_token_display(self, obj):
        return mark_safe(f'''
            <input type="text" value="{obj.access_token}" id="tokenField{obj.pk}" readonly style="width: 60%;">
            <button type="button" onclick="copyToken{obj.pk}()" style="margin-left: 10px;">📋 نسخ</button>
            <script>
                function copyToken{obj.pk}() {{
                    var copyText = document.getElementById("tokenField{obj.pk}");
                    copyText.select();
                    copyText.setSelectionRange(0, 99999);
                    document.execCommand("copy");
                    alert("✅ تم نسخ التوكن: " + copyText.value);
                }}
            </script>
        ''')
    copy_token_display.short_description = "التوكن (نسخ)"

# ✅ إدارة التحذيرات الأمنية
@admin.register(SecurityWarning)
class SecurityWarningAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')
    search_fields = ('message',)

# ✅ إدارة سجل تغييرات الصلاحيات
@admin.register(RoleChangeLog)
class RoleChangeLogAdmin(admin.ModelAdmin):
    list_display = ('changed_by', 'changed_user', 'old_role', 'new_role', 'timestamp')
    list_filter = ('old_role', 'new_role')
    search_fields = ('changed_by__username', 'changed_user__username')

# ✅ إدارة سجل تسجيل الدخول
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address', 'user_agent')
    search_fields = ('user__username', 'ip_address', 'user_agent')

# ✅ إدارة المرفقات
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('note', 'file', 'uploaded_at')
    search_fields = ('note__title',)

# ✅ إدارة سجل الوصول
@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'action', 'ip_address', 'timestamp')
    search_fields = ('user__username', 'note__title', 'action')

# ✅ إدارة سجل النشاط
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'note', 'timestamp')
    search_fields = ('user__username', 'action', 'note__title')

# ✅ إدارة إشعارات الوصول
@admin.register(AccessNotification)
class AccessNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'access_type', 'accessed_at', 'ip_address')
    search_fields = ('user__username', 'note__title', 'access_type')

# ✅ إدارة الوسوم
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# ✅ إدارة نماذج التدقيق المتقدم (إذا كانت متوفرة)
if AUDIT_MODELS_AVAILABLE:
    @admin.register(AuditLog)
    class AuditLogAdmin(admin.ModelAdmin):
        list_display = ('action', 'user', 'resource_type', 'resource_name', 'timestamp', 'severity', 'success')
        list_filter = ('action', 'resource_type', 'severity', 'success', 'timestamp')
        search_fields = ('user__username', 'resource_name', 'description', 'ip_address')
        readonly_fields = ('timestamp', 'session_key', 'ip_address', 'user_agent')
        date_hierarchy = 'timestamp'
        
        fieldsets = (
            ('معلومات العملية', {
                'fields': ('action', 'user', 'resource_type', 'resource_id', 'resource_name', 'description')
            }),
            ('التفاصيل التقنية', {
                'fields': ('old_values', 'new_values', 'severity', 'success'),
                'classes': ('collapse',)
            }),
            ('معلومات الجلسة', {
                'fields': ('timestamp', 'ip_address', 'user_agent', 'session_key'),
                'classes': ('collapse',)
            }),
        )

    @admin.register(DocumentChangeLog)
    class DocumentChangeLogAdmin(admin.ModelAdmin):
        list_display = ('document', 'user', 'change_type', 'field_name', 'timestamp')
        list_filter = ('change_type', 'timestamp')
        search_fields = ('document__title', 'user__username', 'field_name', 'change_reason')
        readonly_fields = ('timestamp', 'ip_address')
        date_hierarchy = 'timestamp'
        
        fieldsets = (
            ('معلومات التغيير', {
                'fields': ('document', 'user', 'change_type', 'field_name', 'change_reason')
            }),
            ('تفاصيل التغيير', {
                'fields': ('old_value', 'new_value'),
                'classes': ('collapse',)
            }),
            ('معلومات تقنية', {
                'fields': ('timestamp', 'ip_address'),
                'classes': ('collapse',)
            }),
        )

    @admin.register(SecurityAlert)
    class SecurityAlertAdmin(admin.ModelAdmin):
        list_display = ('alert_type', 'risk_level', 'user', 'timestamp', 'is_resolved')
        list_filter = ('alert_type', 'risk_level', 'is_resolved', 'timestamp')
        search_fields = ('user__username', 'description', 'ip_address')
        readonly_fields = ('timestamp', 'details')
        date_hierarchy = 'timestamp'
        actions = ['mark_as_resolved', 'mark_as_unresolved']
        
        fieldsets = (
            ('معلومات التنبيه', {
                'fields': ('alert_type', 'risk_level', 'user', 'description')
            }),
            ('تفاصيل تقنية', {
                'fields': ('ip_address', 'user_agent', 'details'),
                'classes': ('collapse',)
            }),
            ('حالة الحل', {
                'fields': ('is_resolved', 'resolved_by', 'resolved_at', 'resolution_notes'),
                'classes': ('collapse',)
            }),
            ('الوقت', {
                'fields': ('timestamp',),
                'classes': ('collapse',)
            }),
        )
        
        def mark_as_resolved(self, request, queryset):
            from django.utils import timezone
            queryset.update(
                is_resolved=True,
                resolved_by=request.user,
                resolved_at=timezone.now()
            )
            self.message_user(request, f"تم وضع علامة على {queryset.count()} تنبيه كمحلول.")
        mark_as_resolved.short_description = "وضع علامة كمحلول"
        
        def mark_as_unresolved(self, request, queryset):
            queryset.update(
                is_resolved=False,
                resolved_by=None,
                resolved_at=None,
                resolution_notes=''
            )
            self.message_user(request, f"تم إلغاء علامة الحل من {queryset.count()} تنبيه.")
        mark_as_unresolved.short_description = "إلغاء علامة الحل"


# ==========================================
# 🆕 إدارة النماذج الجديدة
# ==========================================

# إدارة مركز الإشعارات
try:
    from .models import Notification
    
    @admin.register(Notification)
    class NotificationAdmin(admin.ModelAdmin):
        list_display = ('title', 'user', 'type', 'is_read', 'priority', 'created_at')
        list_filter = ('type', 'is_read', 'priority', 'created_at')
        search_fields = ('title', 'message', 'user__username')
        readonly_fields = ('created_at', 'read_at')
        
        fieldsets = (
            ('المعلومات الأساسية', {
                'fields': ('user', 'title', 'message', 'type', 'priority')
            }),
            ('الحالة', {
                'fields': ('is_read', 'read_at', 'is_email_sent')
            }),
            ('الربط', {
                'fields': ('related_object_id', 'related_object_type'),
                'classes': ('collapse',)
            }),
            ('التوقيت', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        
        actions = ['mark_as_read', 'mark_as_unread', 'send_email_notifications']
        
        def mark_as_read(self, request, queryset):
            from django.utils import timezone
            queryset.update(is_read=True, read_at=timezone.now())
            self.message_user(request, f"تم تحديد {queryset.count()} إشعار كمقروء.")
        mark_as_read.short_description = "تحديد كمقروء"
        
        def mark_as_unread(self, request, queryset):
            queryset.update(is_read=False, read_at=None)
            self.message_user(request, f"تم تحديد {queryset.count()} إشعار كغير مقروء.")
        mark_as_unread.short_description = "تحديد كغير مقروء"
        
        def send_email_notifications(self, request, queryset):
            count = 0
            for notification in queryset:
                if not notification.is_email_sent and notification.user.email:
                    # إرسال بريد إلكتروني
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    try:
                        send_mail(
                            subject=notification.title,
                            message=notification.message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[notification.user.email],
                            fail_silently=False,
                        )
                        notification.is_email_sent = True
                        notification.save()
                        count += 1
                    except Exception:
                        pass
            
            self.message_user(request, f"تم إرسال {count} بريد إلكتروني.")
        send_email_notifications.short_description = "إرسال إشعارات بريد إلكتروني"

except ImportError:
    pass


# إدارة سجل النشاطات
try:
    from .models import ActivityFeed
    
    @admin.register(ActivityFeed)
    class ActivityFeedAdmin(admin.ModelAdmin):
        list_display = ('user', 'action', 'action_type', 'is_public', 'is_important', 'created_at')
        list_filter = ('action_type', 'is_public', 'is_important', 'created_at')
        search_fields = ('action', 'description', 'user__username')
        readonly_fields = ('created_at',)
        
        fieldsets = (
            ('المعلومات الأساسية', {
                'fields': ('user', 'action', 'description', 'action_type')
            }),
            ('الإعدادات', {
                'fields': ('is_public', 'is_important')
            }),
            ('معلومات تقنية', {
                'fields': ('ip_address', 'user_agent'),
                'classes': ('collapse',)
            }),
            ('الربط', {
                'fields': ('related_object_id', 'related_object_type'),
                'classes': ('collapse',)
            }),
            ('التوقيت', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        
        actions = ['mark_as_important', 'mark_as_unimportant', 'make_public', 'make_private']
        
        def mark_as_important(self, request, queryset):
            queryset.update(is_important=True)
            self.message_user(request, f"تم تحديد {queryset.count()} نشاط كمهم.")
        mark_as_important.short_description = "تحديد كمهم"
        
        def mark_as_unimportant(self, request, queryset):
            queryset.update(is_important=False)
            self.message_user(request, f"تم إلغاء أهمية {queryset.count()} نشاط.")
        mark_as_unimportant.short_description = "إلغاء الأهمية"
        
        def make_public(self, request, queryset):
            queryset.update(is_public=True)
            self.message_user(request, f"تم جعل {queryset.count()} نشاط عام.")
        make_public.short_description = "جعل عام"
        
        def make_private(self, request, queryset):
            queryset.update(is_public=False)
            self.message_user(request, f"تم جعل {queryset.count()} نشاط خاص.")
        make_private.short_description = "جعل خاص"

except ImportError:
    pass


# إدارة الإحصائيات
try:
    from .models import SystemStats
    
    @admin.register(SystemStats)
    class SystemStatsAdmin(admin.ModelAdmin):
        list_display = ('date', 'documents_created', 'users_active', 'news_created', 'security_alerts')
        list_filter = ('date',)
        readonly_fields = ('date', 'created_at', 'updated_at')
        
        fieldsets = (
            ('التاريخ', {
                'fields': ('date',)
            }),
            ('إحصائيات الوثائق', {
                'fields': ('documents_created', 'documents_viewed', 'documents_downloaded', 'documents_archived')
            }),
            ('إحصائيات المستخدمين', {
                'fields': ('users_registered', 'users_active', 'user_logins')
            }),
            ('إحصائيات الأخبار', {
                'fields': ('news_created', 'news_views', 'news_likes', 'news_comments')
            }),
            ('إحصائيات الأمان', {
                'fields': ('security_alerts', 'failed_logins', 'suspicious_activities')
            }),
            ('التوقيت', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )

except ImportError:
    pass


# إدارة الملفات
try:
    from .models import FileUpload
    
    @admin.register(FileUpload)
    class FileUploadAdmin(admin.ModelAdmin):
        list_display = ('original_name', 'user', 'file_type', 'file_size_mb', 'is_safe', 'download_count', 'created_at')
        list_filter = ('file_type', 'is_safe', 'created_at')
        search_fields = ('original_name', 'user__username')
        readonly_fields = ('created_at', 'last_accessed', 'file_size_mb')
        
        def file_size_mb(self, obj):
            return f"{obj.file_size / (1024*1024):.2f} MB"
        file_size_mb.short_description = "حجم الملف (MB)"
        
        fieldsets = (
            ('معلومات الملف', {
                'fields': ('original_name', 'file_path', 'file_type', 'mime_type', 'file_size_mb')
            }),
            ('معلومات المستخدم', {
                'fields': ('user',)
            }),
            ('الأمان', {
                'fields': ('is_safe', 'virus_scan_result')
            }),
            ('الإحصائيات', {
                'fields': ('download_count', 'last_accessed')
            }),
            ('التوقيت', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        
        actions = ['mark_as_safe', 'mark_as_unsafe']
        
        def mark_as_safe(self, request, queryset):
            queryset.update(is_safe=True)
            self.message_user(request, f"تم تحديد {queryset.count()} ملف كآمن.")
        mark_as_safe.short_description = "تحديد كآمن"
        
        def mark_as_unsafe(self, request, queryset):
            queryset.update(is_safe=False)
            self.message_user(request, f"تم تحديد {queryset.count()} ملف كغير آمن.")
        mark_as_unsafe.short_description = "تحديد كغير آمن"

except ImportError:
    pass
