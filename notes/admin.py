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
    AccessNotification
)

# ✅ إدارة سجل تسجيل الدخول
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address', 'user_agent')

# ✅ إدارة بروفايل المستخدم
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

# ✅ إدارة تغييرات الصلاحيات
@admin.register(RoleChangeLog)
class RoleChangeLogAdmin(admin.ModelAdmin):
    list_display = ('changed_by', 'changed_user', 'old_role', 'new_role', 'timestamp')

# ✅ إدارة الوثائق
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_token', 'created_at', 'issuer_name', 'is_archived', 'expiry_date')
    readonly_fields = ('access_token', 'copy_token_display')
    fields = ('title', 'content', 'file', 'issuer_name', 'recipient_name', 'stamp', 'signature',
              'is_archived', 'expiry_date', 'copy_token_display', 'created_at')

    def display_token(self, obj):
        return str(obj.access_token)
    display_token.short_description = 'Access Token'

    def copy_token_display(self, obj):
        return mark_safe(f'''
            <input type="text" value="{obj.access_token}" id="tokenField" readonly style="width: 60%;">
            <button type="button" onclick="copyToken()" style="margin-left: 10px;">📋 نسخ</button>
            <script>
                function copyToken() {{
                    var copyText = document.getElementById("tokenField");
                    copyText.select();
                    copyText.setSelectionRange(0, 99999); // للهواتف
                    document.execCommand("copy");
                    alert("✅ تم نسخ التوكن: " + copyText.value);
                }}
            </script>
        ''')
    copy_token_display.short_description = "التوكن (اضغط نسخ)"

# ✅ إدارة التحذير الأمني
admin.site.register(SecurityWarning)

# ✅ إدارة المرفقات
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('note', 'file', 'uploaded_at')

# ✅ إدارة سجل الوصول
@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'action', 'ip_address', 'timestamp')

# ✅ إدارة سجل النشاط
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'note', 'timestamp')

# ✅ إدارة إشعارات الوصول
@admin.register(AccessNotification)
class AccessNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'access_type', 'accessed_at', 'ip_address')
