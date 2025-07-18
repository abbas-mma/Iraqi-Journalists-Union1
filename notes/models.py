from django.db import models
from django.contrib.auth.models import User
import uuid

# ✅ ملف المستخدم مع تحديد الدور
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

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# ✅ نموذج الوسوم Tags
class Tag(models.Model):
    name = models.CharField("الوسم", max_length=100, unique=True)

    def __str__(self):
        return self.name


# ✅ نموذج الوثيقة Note
class Note(models.Model):
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

    file = models.URLField("رابط الملف المرفوع", max_length=500, blank=True, null=True)
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

    tags = models.ManyToManyField(Tag, verbose_name="الوسوم", blank=True)

    def __str__(self):
        return self.title


# ✅ مرفقات متعددة لكل وثيقة
class Attachment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField("ملف مرفق", upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def file_extension(self):
        return self.file.name.split('.')[-1].lower()


# ✅ سجل دخول المستخدمين
class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_histories')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


# ✅ سجل تغييرات الصلاحيات
class RoleChangeLog(models.Model):
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_changes_made')
    changed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_changes_received')
    old_role = models.CharField(max_length=20)
    new_role = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.changed_by} غيّر {self.changed_user} من {self.old_role} إلى {self.new_role}"


# ✅ سجل النشاط (Audit Log)
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


# ✅ إشعارات عند فتح الوثيقة أو المرفق
class AccessNotification(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('document', 'الوثيقة'),
        ('attachment', 'المرفق'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='access_notifications')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='access_notifications')
    accessed_at = models.DateTimeField(auto_now_add=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} فتح {self.get_access_type_display()} بتاريخ {self.accessed_at}"


# ✅ التحذير الأمني
class SecurityWarning(models.Model):
    text = models.TextField("نص التحذير الأمني")

    def __str__(self):
        return "تحذير أمني"


# ✅ سجل الوصول (للتدقيق)
class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم", related_name='access_logs')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, verbose_name="الوثيقة", related_name='access_logs')
    action = models.CharField(max_length=50, verbose_name="العملية المنفذة")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التنفيذ")

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

