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
