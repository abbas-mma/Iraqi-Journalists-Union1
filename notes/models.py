from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('employee', 'موظف'),
        ('normal', 'مستخدم عادي'),
        ('viewer', 'عرض فقط'),
        ('reader', 'قراءة'),
        ('supervisor', 'مشرف رئيسي'),
        ('admin', 'مدير النظام'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    activation_token = models.CharField(max_length=64, blank=True, null=True, help_text="رمز تفعيل الحساب عبر البريد")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Tag(models.Model):
    name = models.CharField("الوسم", max_length=100, unique=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    file_login_only = models.BooleanField("الملف المرفق محمي (يظهر فقط بعد تسجيل الدخول)", default=False)
    file_for_user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='protected_files', help_text="الملف يظهر فقط لهذا المستخدم إذا تم اختياره")
    login_only = models.BooleanField("تظهر فقط بعد تسجيل الدخول", default=False, help_text="لا يمكن لأي زائر أو غير مسجل الدخول رؤيتها حتى عبر QR")
    TYPE_CHOICES = [
        ('administrative', 'أمر إداري'),
        ('official', 'كتاب رسمي'),
        ('circular', 'تعميم'),
    ]
    DIRECTION_CHOICES = [
        ('outgoing', 'صادرة'),
        ('incoming', 'واردة'),
    ]
    IMPORTANCE_CHOICES = [
        ('normal', 'عادي'),
        ('important', 'مهم'),
        ('urgent', 'عاجل'),
    ]

    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='normal', verbose_name="درجة الأهمية")
    title = models.CharField("عنوان الوثيقة", max_length=255)
    content = models.TextField("محتوى الوثيقة", blank=True, null=True)
    doc_type = models.CharField("نوع الوثيقة", max_length=20, choices=TYPE_CHOICES, default='official')
    direction = models.CharField("جهة الوثيقة", max_length=10, choices=DIRECTION_CHOICES, default='outgoing')

    file = models.FileField("الملف المرفق", upload_to='attachments/', blank=True, null=True)
    stamp = models.ImageField("الختم", upload_to='documents/', blank=True, null=True)
    signature = models.ImageField("التوقيع", upload_to='documents/', blank=True, null=True)
    issuer_name = models.CharField("اسم الجهة المصدرة", max_length=255, blank=True, null=True)
    recipient_name = models.CharField("اسم الجهة المستقبلة", max_length=255, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_created')
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    expiry_date = models.DateTimeField("تاريخ انتهاء الصلاحية", blank=True, null=True)

    is_archived = models.BooleanField("أرشفة", default=False)
    is_deleted = models.BooleanField("تم الحذف؟", default=False)

    is_private = models.BooleanField("وثيقة خاصة (يظهرها فقط صاحبها)", default=False, help_text="إذا كانت الوثيقة خاصة، لا يمكن لأي مستخدم آخر رؤيتها حتى عبر QR")

    tags = models.ManyToManyField(Tag, verbose_name="الوسوم", blank=True)

    def __str__(self):
        return self.title


class SecurityWarning(models.Model):
    message = models.TextField("رسالة التحذير الأمني", default='')  # ✅ تم إضافة default مؤقتًا
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.message[:50]


class RoleChangeLog(models.Model):
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_changes_made')
    changed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_changes_received')
    old_role = models.CharField(max_length=50)
    new_role = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.changed_by} → {self.changed_user} ({self.old_role} → {self.new_role})"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class Attachment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note.title} - {self.file.name}"


class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.note.title}"


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class AccessNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=255)
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.access_type} - {self.note.title}"


# نظام التدقيق المتقدم
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'إنشاء'),
        ('READ', 'قراءة'),
        ('UPDATE', 'تحديث'),
        ('DELETE', 'حذف'),
        ('LOGIN', 'تسجيل دخول'),
        ('LOGOUT', 'تسجيل خروج'),
        ('DOWNLOAD', 'تحميل'),
        ('SHARE', 'مشاركة'),
        ('ARCHIVE', 'أرشفة'),
        ('RESTORE', 'استرجاع'),
        ('ROLE_CHANGE', 'تغيير صلاحية'),
        ('PASSWORD_CHANGE', 'تغيير كلمة السر'),
        ('SETTINGS_CHANGE', 'تغيير إعدادات'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, help_text='نوع المورد (وثيقة، مستخدم، إلخ)')
    resource_id = models.CharField(max_length=100, blank=True, null=True, help_text='معرف المورد')
    resource_name = models.CharField(max_length=255, blank=True, null=True, help_text='اسم المورد')
    description = models.TextField(help_text='وصف مفصل للعملية')
    old_values = models.JSONField(blank=True, null=True, help_text='القيم القديمة')
    new_values = models.JSONField(blank=True, null=True, help_text='القيم الجديدة')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='LOW')
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True, help_text='هل نجحت العملية؟')
    error_message = models.TextField(blank=True, null=True, help_text='رسالة الخطأ إن وجدت')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['resource_type', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.resource_type} - {self.timestamp}"


class DocumentChangeLog(models.Model):
    """سجل مفصل لتغييرات الوثائق"""
    CHANGE_TYPES = [
        ('FIELD_UPDATE', 'تحديث حقل'),
        ('FILE_UPLOAD', 'رفع ملف'),
        ('FILE_DELETE', 'حذف ملف'),
        ('STATUS_CHANGE', 'تغيير حالة'),
        ('PERMISSION_CHANGE', 'تغيير صلاحية'),
        ('METADATA_UPDATE', 'تحديث بيانات وصفية'),
    ]
    
    document = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='change_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    field_name = models.CharField(max_length=100, blank=True, null=True, help_text='اسم الحقل المتغير')
    old_value = models.TextField(blank=True, null=True, help_text='القيمة القديمة')
    new_value = models.TextField(blank=True, null=True, help_text='القيمة الجديدة')
    change_reason = models.TextField(blank=True, null=True, help_text='سبب التغيير')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.document.title} - {self.get_change_type_display()} - {self.user.username}"


class SecurityAlert(models.Model):
    """تنبيهات الأمان المتقدمة"""
    ALERT_TYPES = [
        ('SUSPICIOUS_LOGIN', 'تسجيل دخول مشبوه'),
        ('MULTIPLE_FAILED_LOGINS', 'محاولات دخول فاشلة متعددة'),
        ('UNAUTHORIZED_ACCESS', 'وصول غير مخول'),
        ('DATA_BREACH_ATTEMPT', 'محاولة اختراق بيانات'),
        ('UNUSUAL_ACTIVITY', 'نشاط غير عادي'),
        ('PERMISSION_ESCALATION', 'محاولة رفع صلاحيات'),
        ('BULK_DOWNLOAD', 'تحميل كمي مشبوه'),
        ('IP_BLACKLIST', 'IP في القائمة السوداء'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'خطر جداً'),
    ]
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    description = models.TextField(help_text='وصف التنبيه')
    details = models.JSONField(blank=True, null=True, help_text='تفاصيل إضافية')
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['alert_type', '-timestamp']),
            models.Index(fields=['risk_level', '-timestamp']),
            models.Index(fields=['is_resolved', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.get_risk_level_display()} - {self.timestamp}"


# ==========================================
# 🆕 نماذج مركز الإشعارات المتقدم
# ==========================================

class Notification(models.Model):
    """نظام الإشعارات المتقدم"""
    NOTIFICATION_TYPES = [
        ('document', 'وثيقة'),
        ('news', 'خبر'),
        ('user', 'مستخدم'),
        ('system', 'نظام'),
        ('security', 'أمني'),
        ('reminder', 'تذكير'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # ربط بكائنات أخرى (اختياري)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    
    # إعدادات الإشعار
    is_email_sent = models.BooleanField(default=False, verbose_name="تم إرسال بريد إلكتروني")
    priority = models.CharField(max_length=10, choices=[
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('high', 'عالي'),
        ('urgent', 'عاجل')
    ], default='normal')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({'مقروء' if self.is_read else 'جديد'})"
    
    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


# ==========================================
# 🆕 نماذج سجل النشاطات الشامل
# ==========================================

class ActivityFeed(models.Model):
    """سجل النشاطات الشامل للموقع"""
    ACTIVITY_TYPES = [
        ('document', 'وثيقة'),
        ('news', 'خبر'),
        ('user', 'مستخدم'),
        ('system', 'نظام'),
        ('auth', 'مصادقة'),
        ('admin', 'إداري'),
        ('security', 'أمني'),
        ('general', 'عام'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100, verbose_name="العملية")
    description = models.TextField(verbose_name="الوصف")
    action_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # معلومات إضافية
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # ربط بكائنات أخرى (اختياري)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    
    # إعدادات العرض
    is_public = models.BooleanField(default=True, verbose_name="عام (يظهر للجميع)")
    is_important = models.BooleanField(default=False, verbose_name="مهم")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ==========================================
# 🆕 نماذج الإحصائيات المتقدمة
# ==========================================

class SystemStats(models.Model):
    """إحصائيات النظام اليومية"""
    date = models.DateField(unique=True)
    
    # إحصائيات الوثائق
    documents_created = models.IntegerField(default=0)
    documents_viewed = models.IntegerField(default=0)
    documents_downloaded = models.IntegerField(default=0)
    documents_archived = models.IntegerField(default=0)
    
    # إحصائيات المستخدمين
    users_registered = models.IntegerField(default=0)
    users_active = models.IntegerField(default=0)
    user_logins = models.IntegerField(default=0)
    
    # إحصائيات الأخبار
    news_created = models.IntegerField(default=0)
    news_views = models.IntegerField(default=0)
    news_likes = models.IntegerField(default=0)
    news_comments = models.IntegerField(default=0)
    
    # إحصائيات الأمان
    security_alerts = models.IntegerField(default=0)
    failed_logins = models.IntegerField(default=0)
    suspicious_activities = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "إحصائيات يومية"
        verbose_name_plural = "الإحصائيات اليومية"
    
    def __str__(self):
        return f"إحصائيات {self.date}"


# ==========================================
# 🆕 نماذج إدارة الملفات المتقدمة
# ==========================================

class FileUpload(models.Model):
    """سجل رفع الملفات"""
    FILE_TYPES = [
        ('document', 'وثيقة'),
        ('image', 'صورة'),
        ('pdf', 'PDF'),
        ('office', 'ملف مكتبي'),
        ('other', 'أخرى'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(help_text="حجم الملف بالبايت")
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    mime_type = models.CharField(max_length=100)
    
    # معلومات الأمان
    is_safe = models.BooleanField(default=True)
    virus_scan_result = models.CharField(max_length=50, blank=True, null=True)
    
    # إحصائيات
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_name} - {self.user.username}"


# ==========================================
# 🆕 إشارات Django للإشعارات التلقائية
# ==========================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Note)
def create_note_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند إنشاء وثيقة جديدة"""
    if created:
        # إشعار للمستخدم المحدد إذا كانت الوثيقة موجهة له
        if instance.file_for_user and instance.file_for_user != instance.created_by:
            Notification.objects.create(
                user=instance.file_for_user,
                title="وثيقة جديدة موجهة لك",
                message=f"تم إنشاء وثيقة جديدة بعنوان '{instance.title}' وموجهة لك",
                type='document'
            )
        
        # تسجيل النشاط
        ActivityFeed.objects.create(
            user=instance.created_by,
            action="إنشاء وثيقة",
            description=f"تم إنشاء وثيقة جديدة بعنوان: {instance.title}",
            action_type='document',
            is_public=True
        )

@receiver(post_save, sender=User)
def create_user_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند تسجيل مستخدم جديد"""
    if created:
        # إشعار للمشرفين
        supervisors = User.objects.filter(profile__role__in=['admin', 'supervisor'])
        for supervisor in supervisors:
            Notification.objects.create(
                user=supervisor,
                title="مستخدم جديد",
                message=f"انضم مستخدم جديد: {instance.username}",
                type='user'
            )
        
        # تسجيل النشاط
        ActivityFeed.objects.create(
            user=instance,
            action="تسجيل مستخدم جديد",
            description=f"انضم مستخدم جديد: {instance.username}",
            action_type='user',
            is_public=False
        )
