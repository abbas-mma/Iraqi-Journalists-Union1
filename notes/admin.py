
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Note, SecurityWarning, UserProfile, RoleChangeLog, LoginHistory

class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address', 'user_agent')

admin.site.register(LoginHistory, LoginHistoryAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

class RoleChangeLogAdmin(admin.ModelAdmin):
    list_display = ('changed_by', 'changed_user', 'old_role', 'new_role', 'timestamp')

class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_token', 'created_at', 'issuer_name', 'is_archived', 'expiry_date')
    readonly_fields = ('access_token', 'copy_token_display')
    fields = ('title', 'file', 'issuer_name', 'stamp', 'signature', 'is_archived', 'expiry_date', 'copy_token_display', 'created_at')

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


admin.site.register(Note, NoteAdmin)
admin.site.register(SecurityWarning)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RoleChangeLog, RoleChangeLogAdmin)

class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'doc_type', 'created_at']
