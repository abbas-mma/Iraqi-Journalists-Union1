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

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Tag(models.Model):
    name = models.CharField("الوسم", max_length=100, unique=True)

    def __str__(self):
        return self.name


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
