# حذف تعليق خبر (للمشرف فقط)
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .models_news import NewsComment

@user_passes_test(lambda u: u.is_superuser or getattr(u, 'profile', None) and u.profile.role in ['admin', 'supervisor'])
@require_POST
def delete_news_comment(request, comment_id):
    comment = NewsComment.objects.filter(id=comment_id).first()
    if comment:
        comment.delete()
        from django.contrib import messages
        messages.success(request, "تم حذف التعليق بنجاح.")
    # إعادة التوجيه إلى صفحة الخبر
    return redirect(request.META.get('HTTP_REFERER', 'news'))
from django.http import FileResponse, Http404
# دالة تحميل الملف المرفق بشكل محمي
from django.contrib.auth.decorators import login_required
import mimetypes

@login_required
def download_attachment(request, token):
    note = get_object_or_404(Note, access_token=token)
    # تحقق من الصلاحية كما في qr_note_access
    if note.is_private and note.created_by != request.user:
        return render(request, 'notes/no_permission.html')
    if getattr(note, 'file_for_user', None) and note.file_for_user != request.user:
        return render(request, 'notes/no_permission.html')
    if not note.file:
        return render(request, 'notes/no_attachment.html', {'note': note})
    file_path = note.file.path
    file_mimetype, _ = mimetypes.guess_type(file_path)
    try:
        return FileResponse(open(file_path, 'rb'), content_type=file_mimetype or 'application/octet-stream')
    except Exception:
        raise Http404("الملف غير موجود")
from django.shortcuts import render, get_object_or_404
from .models_news import News

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'notes/news_detail.html', {'news': news})
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def audit_report_view(request, report_type):
    """عرض مباشر للتقارير الأمنية"""
    from .utils.audit import ReportGenerator
    report = None
    report_type_display = ''
    if report_type == 'daily':
        report = ReportGenerator.generate_daily_security_report()
        report_type_display = 'يومي'
    elif report_type == 'weekly':
        report = ReportGenerator.generate_weekly_security_report()
        report_type_display = 'أسبوعي'
    elif report_type == 'monthly':
        report = ReportGenerator.generate_monthly_security_report()
        report_type_display = 'شهري'
    elif report_type == 'full':
        report = ReportGenerator.generate_full_security_report()
        report_type_display = 'شامل'
    else:
        return HttpResponse('نوع التقرير غير مدعوم', status=400)
    return render(request, 'notes/audit_report_view.html', {
        'report': report,
        'report_type_display': report_type_display,
    })
# الاستيرادات الأساسية
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# حذف خبر (للمشرفين فقط)
@user_passes_test(lambda u: u.is_superuser or getattr(u, 'profile', None) and u.profile.role in ['admin', 'supervisor'])
@require_POST
def delete_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.delete()
    messages.success(request, "تم حذف الخبر بنجاح.")
    return redirect('news')
# تفعيل الحساب عبر البريد الإلكتروني
from django.shortcuts import get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

def activate_account(request, token):
    from .models import UserProfile
    profile = get_object_or_404(UserProfile, activation_token=token)
    user = profile.user
    if not user.is_active:
        user.is_active = True
        user.save()
        profile.activation_token = None
        profile.save()
        auth_login(request, user)
        return render(request, 'notes/activation_success.html')
    else:
        return render(request, 'notes/activation_success.html', {'already_active': True})

# =====================
# إعادة تعيين كلمة السر
# =====================

# إرسال رابط إعادة تعيين كلمة السر
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

# تم إرسال الإيميل
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

# رابط التعيين الجديد
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

# تم تعيين كلمة السر
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
from .models_news import News, NewsComment, NewsLike

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def add_news_comment(request, news_id):
    news = get_object_or_404(News, id=news_id)
    content = request.POST.get('content', '').strip()
    if content:
        NewsComment.objects.create(news=news, user=request.user, content=content)
    return HttpResponseRedirect(reverse('news'))

# تفعيل/إلغاء الإعجاب بخبر
@login_required
def toggle_news_like(request, news_id):
    news = get_object_or_404(News, id=news_id)
    like, created = NewsLike.objects.get_or_create(news=news, user=request.user)
    if not created:
        like.delete()
    return HttpResponseRedirect(reverse('news'))
from .models import AccessNotification
from .models import ActivityLog
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import UserProfile

@user_passes_test(lambda u: u.is_superuser or u.profile.role in ['admin', 'supervisor'])
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'viewer')
        if not username or not email or not password:
            messages.error(request, 'جميع الحقول مطلوبة.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مستخدم بالفعل.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            # تحقق إذا كان هناك UserProfile مرتبط بهذا المستخدم
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, role=role)
            messages.success(request, f'تم إضافة المستخدم {username} بنجاح.')
            return redirect('user_management')
    return render(request, 'notes/add_user.html')

from dotenv import load_dotenv
load_dotenv()
# لوحة إحصائيات وتقارير
from django.shortcuts import render, redirect
from django.conf import settings  # type: ignore
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def stats_dashboard(request):
    # إحصائيات الوثائق حسب النوع
    notes_by_type = Note.objects.values('doc_type').annotate(count=Count('id'))
    # إحصائيات الوثائق حسب الشهر
    notes_by_month = Note.objects.extra(select={'month': "strftime('%Y-%m', created_at)"}).values('month').annotate(count=Count('id')).order_by('month')
    # إحصائيات المستخدمين حسب الدور
    users_by_role = UserProfile.objects.values('role').annotate(count=Count('id'))
    return render(request, 'notes/stats_dashboard.html', {
        'notes_by_type': list(notes_by_type),
        'notes_by_month': list(notes_by_month),
        'users_by_role': list(users_by_role),
    })
# أرشفة تلقائية للوثائق المنتهية الصلاحية
from django.utils import timezone
def auto_archive_expired_notes():
    now = timezone.now()
    expired_notes = Note.objects.filter(is_archived=False, expiry_date__lt=now, is_deleted=False)
    for note in expired_notes:
        note.is_archived = True
        note.save()
        # إشعار بريد إلكتروني لصاحب الوثيقة
        if note.created_by.email:
            subject = "تمت أرشفة وثيقتك تلقائياً"
            message = f"تمت أرشفة وثيقتك المنتهية بعنوان: {note.title}"
            send_notification_email(subject, message, [note.created_by.email])

from django.core.mail import send_mail
from django.conf import settings

# دالة مساعدة لإرسال بريد
def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=True,
    )
from .models import LoginHistory

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

# تسجيل الدخول في LoginHistory
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    LoginHistory.objects.create(user=user, ip_address=ip, user_agent=user_agent)

# عرض سجل الدخول للمشرفين
from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def login_history(request):
    logs = LoginHistory.objects.select_related('user').order_by('-login_time')[:100]
    return render(request, 'notes/login_history.html', {'logs': logs})
# سجل تغييرات الصلاحيات - عرض للمشرفين
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def role_change_log(request):
    from .models import RoleChangeLog
    logs = RoleChangeLog.objects.select_related('changed_by', 'changed_user').order_by('-timestamp')[:100]
    return render(request, 'notes/role_change_log.html', {'logs': logs})
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings # type: ignore
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Note, SecurityWarning, UserProfile, Tag

import qrcode
import base64
from io import BytesIO
import uuid
import os
from weasyprint import HTML


def get_user_profile(request):
    try:
        return UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # إنشاء بروفايل تلقائي بصلاحية "viewer" إن لم يكن موجوداً
        return UserProfile.objects.create(user=request.user, role='viewer')

# ✅ تسجيل مستخدم جديد
def register(request):
    import uuid
    from django.core.mail import send_mail
    from django.conf import settings
    from django.urls import reverse
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            return render(request, 'notes/register.html', {'error': 'اسم المستخدم موجود بالفعل'})
        if User.objects.filter(email=email).exists():
            return render(request, 'notes/register.html', {'error': 'البريد الإلكتروني مستخدم بالفعل'})
        if not email:
            return render(request, 'notes/register.html', {'error': 'يجب إدخال بريد إلكتروني صحيح'})

        user = User.objects.create_user(username=username, password=password, email=email, is_active=True)
        profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'viewer'})
        # تفعيل المستخدم مباشرة بدون تحقق من البريد
        return render(request, 'notes/register.html', {'error': 'تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.'})

    return render(request, 'notes/register.html')


# ✅ الصفحة الرئيسية (لوحة التحكم)

@login_required
def home(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    # إذا كان المستخدم عادي (وليس مشرف أو موظف أو قارئ)، يحول إلى لوحة خاصة به
    if user_profile.role not in ['admin', 'supervisor', 'employee', 'reader']:
        return redirect('user_notes')

    now = timezone.now()
    # البحث المتقدم
    q = request.GET.get('q', '').strip()
    doc_type = request.GET.get('doc_type', '').strip()
    created_at = request.GET.get('created_at', '').strip()

    notes_qs = Note.objects.filter(is_deleted=False)
    if q:
        notes_qs = notes_qs.filter(title__icontains=q)
    if doc_type:
        notes_qs = notes_qs.filter(doc_type=doc_type)
    if created_at:
        notes_qs = notes_qs.filter(created_at__date=created_at)

    active_notes = notes_qs.filter(is_archived=False).filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gt=now)
    )

    stats = {
        'active': active_notes.count(),
        'archived': notes_qs.filter(is_archived=True).count(),
        'expired': notes_qs.filter(expiry_date__lt=now).count(),
        'users': UserProfile.objects.count(),
    }

    # 🆕 إضافة إحصائيات التدقيق المتقدم
    try:
        from .models import AuditLog, SecurityAlert, DocumentChangeLog
        from datetime import date
        
        # إحصائيات سجلات التدقيق لليوم
        today = date.today()
        stats['audit_logs'] = AuditLog.objects.filter(timestamp__date=today).count()
        
        # التنبيهات الأمنية غير المحلولة
        stats['security_alerts'] = SecurityAlert.objects.filter(is_resolved=False).count()
        
        # التنبيهات الأمنية الحديثة للعرض
        security_alerts = SecurityAlert.objects.filter(
            is_resolved=False,
            risk_level__in=['HIGH', 'CRITICAL']
        ).order_by('-timestamp')[:5]
        
        # سجلات التدقيق الحديثة
        recent_audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
        
    except ImportError:
        # إذا لم تكن نماذج التدقيق متوفرة
        stats['audit_logs'] = 0
        stats['security_alerts'] = 0
        security_alerts = []
        recent_audit_logs = []

    if user_profile.role in ['admin', 'supervisor']:
        notes = notes_qs.order_by('-created_at')
    elif user_profile.role == 'employee':
        notes = active_notes.order_by('-created_at')
    elif user_profile.role == 'reader':
        notes = notes_qs.filter(
            is_archived=False, expiry_date__isnull=True
        ).order_by('-created_at')
    else:
        notes = Note.objects.none()

    return render(request, 'notes/home.html', {
        'notes': notes,
        'user_profile': user_profile,
        'stats': stats,
        'now': now,
        'request': request,
        # 🆕 بيانات جديدة للميزات المتقدمة
        'security_alerts': security_alerts,
        'recent_audit_logs': recent_audit_logs,
    })

import datetime
import logging
import os
import uuid
import base64
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import qrcode
from weasyprint import HTML

logger = logging.getLogger(__name__)

def shorten_uuid(uuid_str):
    # إزالة الشرطة وأخذ أول 8 حروف
    short = uuid_str.replace('-', '')[:8]
    # تحويل كل حرف إلى رقم (مثلا: قيمة الـ ASCII مقسومة على 10 وأخذ باقي القسمة)
    numbers = ''.join(str(ord(c) % 10) for c in short)
    return numbers

@login_required
def note_detail(request, token):
    note = get_object_or_404(Note, access_token=token)
    # سجل فتح الوثيقة
    from .models import ActivityLog
    if request.user.is_authenticated:
        ActivityLog.objects.create(user=request.user, action='عرض الوثيقة', note=note)
    user_profile = get_user_profile(request)

    if (user_profile.role == 'viewer' or 
        (note.is_archived and user_profile.role not in ['admin', 'supervisor']) or 
        (note.expiry_date and note.expiry_date < timezone.now() and user_profile.role != 'admin')):
        return render(request, 'notes/no_permission.html')

    # تحقق من الخصوصية: إذا كانت الوثيقة خاصة لمستخدم معين
    if note.is_private:
        allowed_user = note.file_for_user
        if allowed_user:
            if request.user != allowed_user and request.user != note.created_by:
                return render(request, 'notes/no_permission.html')
        else:
            if request.user != note.created_by:
                return render(request, 'notes/no_permission.html')

    if note.file:
        # توليد رابط محمي للتحميل
        protected_url = request.build_absolute_uri(reverse('download_attachment', args=[note.access_token]))
        attachment_url = protected_url

        qr = qrcode.make(protected_url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    else:
        qr_code_base64 = None
        attachment_url = ''

    short_token = shorten_uuid(str(note.access_token))

    pdf_filename = f"{note.title.replace(' ', '_')}_{note.access_token}.pdf"
    note_pdf_url = f"{settings.MEDIA_URL}generated_pdfs/{pdf_filename}"

    return render(request, 'notes/note_detail.html', {
        'note': note,
        'user_profile': user_profile,
        'img_str': qr_code_base64,
        'short_token': short_token,  # أضفنا النص المختصر هنا
        'security_warning': SecurityWarning.objects.first(),
        'note_pdf_url': note_pdf_url,
        'attachment_url': attachment_url,
    })

def shorten_uuid(uuid_str):
    # إزالة الشرطات وأخذ أول 8 حروف
    short = uuid_str.replace('-', '')[:8]
    # تحويل كل حرف لرقم (مثلاً بقيمة ASCII % 10)
    numbers = ''.join(str(ord(c) % 10) for c in short)
    return numbers

@login_required
def note_qr_only(request, token):
    # حماية: يجب أن يكون المستخدم مسجل دخول
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')

    note = get_object_or_404(Note, access_token=token)
    user_profile = get_user_profile(request)

    if (user_profile.role == 'viewer' or 
        (note.is_archived and user_profile.role not in ['admin', 'supervisor']) or 
        (note.expiry_date and note.expiry_date < timezone.now() and user_profile.role != 'admin')):
        return render(request, 'notes/no_permission.html')

    # تحقق من الخصوصية: إذا كانت الوثيقة خاصة لمستخدم معين
    if note.is_private:
        allowed_user = note.file_for_user
        if allowed_user:
            if request.user != allowed_user and request.user != note.created_by:
                return render(request, 'notes/no_permission.html')
        else:
            if request.user != note.created_by:
                return render(request, 'notes/no_permission.html')

    show_print = request.GET.get('print') == '1'

    if note.file:
        qr_data = request.build_absolute_uri(f'/attachment/{note.access_token}/')
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        short_token = shorten_uuid(str(note.access_token))

        return render(request, 'notes/note_qr_only.html', {
            'note': note,
            'img_str': qr_code_base64,
            'serial_number': note.id,
            'logo_url': request.build_absolute_uri('/static/logo.png'),
            'show_print': show_print,
            'short_token': short_token,
        })
    else:
        return render(request, 'notes/no_attachment.html', {
            'note': note,
        })

@login_required
def create_note(request):
    user_profile = get_user_profile(request)

    if user_profile.role not in ['admin', 'supervisor', 'employee']:
        return render(request, 'notes/no_permission.html')

    from django.contrib.auth.models import User
    if request.method == 'POST':
        # معاينة قبل الحفظ النهائي
        if 'preview' in request.POST and not request.POST.get('confirm'):
            title = request.POST.get('title')
            content = request.POST.get('content')
            # يمكن تمرير باقي الحقول حسب الحاجة
            return render(request, 'notes/preview_note.html', {
                'title': title,
                'content': content,
            })

        # حفظ نهائي وإنشاء PDF
        if request.POST.get('confirm'):
            title = request.POST.get('title')
            content = request.POST.get('content')
            doc_type = request.POST.get('doc_type')
            direction = request.POST.get('direction')
            importance = request.POST.get('importance')
            issuer_name = request.POST.get('issuer_name')
            recipient_name = request.POST.get('recipient_name')
            attachment = request.FILES.get('attachment')
            # حماية نوع الملف
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'application/pdf',
                'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ]
            if attachment and hasattr(attachment, 'content_type'):
                if attachment.content_type not in allowed_types:
                    from django.contrib import messages
                    messages.error(request, 'نوع الملف غير مسموح. الرجاء رفع صورة أو ملف PDF أو Word فقط.')
                    from django.contrib.auth.models import User
                    users = User.objects.all()
                    return render(request, 'notes/create_note.html', {
                        'user_profile': user_profile,
                        'tags': Tag.objects.all(),
                        'selected_tags': request.POST.getlist('tags') if request.method == 'POST' else [],
                        'users': users,
                    })
            # ضغط الصورة إذا كانت صورة
            from PIL import Image
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import io
            import sys
            if attachment and hasattr(attachment, 'content_type') and attachment.content_type.startswith('image'):
                try:
                    img = Image.open(attachment)
                    img_format = img.format if img.format else 'JPEG'
                    img_io = io.BytesIO()
                    img = img.convert('RGB')
                    img.save(img_io, format=img_format, quality=70, optimize=True)
                    img_io.seek(0)
                    attachment = InMemoryUploadedFile(
                        img_io, None, attachment.name, attachment.content_type, sys.getsizeof(img_io), None
                    )
                except Exception:
                    pass
            tag_ids = request.POST.getlist('tags')
            token = uuid.uuid4()

            expiry_date_str = request.POST.get('expiry_date')
            expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d') if expiry_date_str else None

            is_private = bool(request.POST.get('is_private')) or request.GET.get('private') == '1'
            login_only = request.GET.get('login_only') == '1'

            file_for_user_id = request.POST.get('file_for_user')
            file_for_user = None
            if file_for_user_id:
                try:
                    file_for_user = User.objects.get(id=file_for_user_id)
                except User.DoesNotExist:
                    file_for_user = None

            note = Note.objects.create(
                title=title,
                content=content,
                doc_type=doc_type,
                direction=direction,
                importance=importance,
                expiry_date=expiry_date,
                issuer_name=issuer_name,
                recipient_name=recipient_name,
                created_by=request.user,
                access_token=token,
                file=attachment,
                is_private=is_private,
                login_only=login_only,
                file_for_user=file_for_user
            )

            if tag_ids:
                tags = Tag.objects.filter(id__in=tag_ids)
                note.tags.set(tags)

            if note.file:
                qr_data = request.build_absolute_uri(f'/qr/{token}/')
            else:
                qr_data = request.build_absolute_uri(f'/note/{token}/')
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            html_qr_only = render_to_string('notes/note_qr_only.html', {
                'note': note,
                'img_str': qr_code_base64,
                'serial_number': note.id,
                'logo_url': request.build_absolute_uri('/static/logo.png'),
            })

            pdf_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            qr_only_pdf_path = os.path.join(pdf_dir, f"qr_only_{token}.pdf")
            HTML(string=html_qr_only, base_url=request.build_absolute_uri('/')).write_pdf(qr_only_pdf_path)

            if request.user.email:
                send_mail(
                    "تم إنشاء وثيقة جديدة",
                    f"تم إنشاء وثيقة جديدة بعنوان: {title}",
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True
                )

            return redirect(f"/note/{token}/qr_only/?print=1")

    from django.contrib.auth.models import User
    users = User.objects.all()
    return render(request, 'notes/create_note.html', {
        'user_profile': user_profile,
        'tags': Tag.objects.all(),
        'selected_tags': request.POST.getlist('tags') if request.method == 'POST' else [],
        'users': users,
    })

# ✅ عمليات الأرشفة والحذف والاسترجاع
@login_required
def archive_note(request, note_id):
    user_profile = get_user_profile(request)
    if user_profile.role not in ['admin', 'supervisor', 'employee']:
        return render(request, 'notes/no_permission.html')
    note = get_object_or_404(Note, id=note_id)
    note.is_archived = True
    note.save()
    # إشعار بريد إلكتروني لصاحب الوثيقة
    if note.created_by.email:
        subject = "تم أرشفة وثيقتك"
        message = f"تم أرشفة وثيقتك بعنوان: {note.title}"
        send_notification_email(subject, message, [note.created_by.email])
    from django.contrib import messages
    messages.success(request, f"تم أرشفة الوثيقة بنجاح: {note.title}")
    return redirect('home')

@login_required
def delete_note(request, note_id):
    user_profile = get_user_profile(request)
    if user_profile.role not in ['admin', 'supervisor']:
        return render(request, 'notes/no_permission.html')
    note = get_object_or_404(Note, id=note_id)
    note.is_deleted = True
    note.save()
    # إشعار بريد إلكتروني لصاحب الوثيقة
    if note.created_by.email:
        subject = "تم حذف وثيقتك"
        message = f"تم حذف وثيقتك بعنوان: {note.title}"
        send_notification_email(subject, message, [note.created_by.email])
    from django.contrib import messages
    messages.success(request, f"تم حذف الوثيقة بنجاح: {note.title}")
    return redirect('home')

@login_required
def restore_note(request, note_id):
    user_profile = get_user_profile(request)
    if user_profile.role not in ['admin', 'supervisor']:
        return render(request, 'notes/no_permission.html')
    note = get_object_or_404(Note, id=note_id)
    note.is_deleted = False
    note.save()
    from django.contrib import messages
    messages.success(request, f"تم استرجاع الوثيقة بنجاح: {note.title}")
    return redirect('deleted_notes')


# ✅ عرض أنواع الوثائق
@login_required
def archived_notes(request):
    return render(request, 'notes/archived.html', {
        'notes': Note.objects.filter(is_archived=True, is_deleted=False).order_by('-created_at'),
        'user_profile': get_user_profile(request)
    })

@login_required
def expired_notes(request):
    return render(request, 'notes/expired.html', {
        'notes': Note.objects.filter(expiry_date__lt=timezone.now(), is_deleted=False).order_by('-created_at'),
        'user_profile': get_user_profile(request)
    })

@login_required
def outgoing_notes(request):
    return render(request, 'notes/outgoing_notes.html', {
        'notes': Note.objects.filter(created_by=request.user, is_deleted=False).order_by('-created_at')
    })

@login_required
def incoming_notes(request):
    return render(request, 'notes/incoming_notes.html', {
        'notes': Note.objects.exclude(created_by=request.user).filter(is_deleted=False).order_by('-created_at'),
        'user_profile': get_user_profile(request)
    })

@login_required
def user_notes(request):
    from .models_news import News
    user_profile = get_user_profile(request)
    notes = Note.objects.filter(file_for_user=request.user, is_deleted=False).order_by('-created_at')
    news_list = News.objects.filter(is_published=True).order_by('-created_at')
    latest_news = news_list.first() if news_list else None
    return render(request, 'notes/user_dashboard.html', {
        'notes': notes,
        'user_profile': user_profile,
        'news_list': news_list,
        'latest_news': latest_news,
        'request': request,
    })

@login_required
def deleted_notes(request):
    return render(request, 'notes/deleted_notes.html', {
        'notes': Note.objects.filter(is_deleted=True).order_by('-created_at'),
        'user_profile': get_user_profile(request)
    })


# ✅ ملفات تعريف وسجلات
@login_required
def profile(request):
    return render(request, 'notes/profile.html', {
        'user': request.user,
        'user_profile': request.user.profile
    })


@login_required
def search_log(request):
    return render(request, 'notes/search_log.html', {'user_profile': get_user_profile(request)})

@login_required
def archive_log(request):
    return render(request, 'notes/archive_log.html', {'user_profile': get_user_profile(request)})

@login_required
def no_permission(request):
    return render(request, 'notes/no_permission.html')



# ✅ الوصول السريع للوثيقة عبر QR: يعرض مباشرة ملف PDF المرفق إذا وجد
from django.http import FileResponse, Http404
import mimetypes

from django.contrib.auth.decorators import login_required

@login_required
def qr_note_access(request, token):
    note = get_object_or_404(Note, access_token=token)
    # إذا كانت الوثيقة خاصة، لا يمكن لأي مستخدم غير صاحبها رؤيتها حتى عبر QR
    if note.is_private and note.created_by != request.user:
        return render(request, 'notes/no_permission.html')
    # حماية الملف المرفق: لا يظهر إلا للمسجلين أو لمستخدم محدد
    if note.file:
        # سجل تحميل الملف
        from .models import ActivityLog
        if request.user.is_authenticated:
            ActivityLog.objects.create(user=request.user, action='تحميل المرفق', note=note)
        # إذا كان الملف محمي للمسجلين فقط
        if getattr(note, 'file_login_only', False) and not request.user.is_authenticated:
            return render(request, 'notes/no_permission.html')
        # إذا كان الملف موجه لمستخدم محدد
        if getattr(note, 'file_for_user', None) and note.file_for_user != request.user:
            return render(request, 'notes/no_permission.html')
        file_path = note.file.path
        file_mimetype, _ = mimetypes.guess_type(file_path)
        try:
            return FileResponse(open(file_path, 'rb'), content_type=file_mimetype or 'application/pdf')
        except Exception:
            raise Http404("الملف غير موجود")
    # إذا لا يوجد ملف مرفق، يعرض صفحة التفاصيل
    return note_detail(request, token)


# ✅ بحث متقدم
@login_required
def search_notes(request):
    query = request.GET.get('q')
    doc_type = request.GET.get('doc_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    order = request.GET.get('order', 'desc')

    user_profile = get_user_profile(request)
    notes = Note.objects.filter(is_deleted=False)

    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    if doc_type:
        notes = notes.filter(doc_type=doc_type)

    if date_from:
        notes = notes.filter(created_at__gte=date_from)

    if date_to:
        notes = notes.filter(created_at__lte=date_to)

    notes = notes.order_by('created_at' if order == 'asc' else '-created_at')

    return render(request, 'notes/search_results.html', {
        'notes': notes,
        'query': query,
        'doc_type': doc_type,
        'date_from': date_from,
        'date_to': date_to,
        'order': order,
        'user_profile': user_profile,
    })


@user_passes_test(lambda u: u.is_superuser or u.profile.role in ['admin', 'supervisor'])
def user_management(request):
    users = User.objects.all().select_related('profile')
    from .models import Note, UserProfile
    from django.db.models import Count

    total_users = users.count()
    roles_stats = UserProfile.objects.values('role').annotate(count=Count('id'))
    active_docs = Note.objects.filter(is_archived=False, is_deleted=False).count()
    archived_docs = Note.objects.filter(is_archived=True, is_deleted=False).count()

    # تحديد الصلاحيات المسموحة حسب صلاحية المستخدم الحالي
    current_user_profile = None
    try:
        current_user_profile = request.user.profile
    except Exception:
        pass
    def get_allowed_roles(role):
        if role == 'admin':
            return ['admin', 'supervisor', 'employee', 'normal', 'viewer', 'reader']
        elif role == 'supervisor':
            return ['employee', 'normal', 'viewer', 'reader']
        elif role == 'employee':
            return ['normal', 'viewer', 'reader']
        else:
            return ['viewer', 'reader']
    def get_allowed_roles(current_role, target_role):
        if current_role == 'admin':
            return ['admin', 'supervisor', 'employee', 'normal', 'viewer', 'reader']
        elif current_role == 'supervisor':
            if target_role in ['admin', 'supervisor']:
                return []
            return ['employee', 'normal', 'viewer', 'reader']
        elif current_role == 'employee':
            return ['normal', 'viewer', 'reader']
        else:
            return ['viewer', 'reader']

    current_role = current_user_profile.role if current_user_profile else 'viewer'
    users_with_roles = []
    for user in users:
        target_role = getattr(user.profile, 'role', 'viewer')
        allowed_roles = get_allowed_roles(current_role, target_role) if user != request.user else []
        users_with_roles.append({'user': user, 'allowed_roles': allowed_roles})

    return render(request, 'notes/user_management.html', {
        'users_with_roles': users_with_roles,
        'request': request,
        'total_users': total_users,
        'roles_stats': roles_stats,
        'active_docs': active_docs,
        'archived_docs': archived_docs,
    })


@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def delete_user(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.delete()
    return redirect('user_management')


from django.contrib import messages
from .models import RoleChangeLog
import datetime

@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
@require_POST
def change_user_role(request, user_id):
    current_user_profile = get_user_profile(request)
    user = User.objects.get(id=user_id)
    # تحديد الصلاحيات الممكن تغييرها حسب صلاحية المستخدم الحالي
    allowed_roles = []
    if current_user_profile.role == 'admin':
        allowed_roles = ['admin', 'supervisor', 'employee', 'normal', 'viewer', 'reader']
    elif current_user_profile.role == 'supervisor':
        allowed_roles = ['employee', 'normal', 'viewer', 'reader']
    elif current_user_profile.role == 'employee':
        allowed_roles = ['normal', 'viewer', 'reader']
    else:
        allowed_roles = ['viewer', 'reader']

    new_role = request.POST.get('role')
    target_profile = user.profile
    old_role = target_profile.role
    # لا يمكن تغيير صلاحية نفسك أو مستخدم أعلى منك
    if user == request.user:
        messages.error(request, "لا يمكنك تغيير صلاحيتك بنفسك.")
    elif current_user_profile.role == 'supervisor' and target_profile.role in ['admin', 'supervisor']:
        messages.error(request, "لا يمكنك تغيير صلاحية مشرف أو مدير النظام.")
    elif new_role not in allowed_roles:
        messages.error(request, "لا يمكنك تعيين هذه الصلاحية.")
    elif old_role == new_role:
        messages.info(request, "لم يتم تغيير الصلاحية لأنها كما هي.")
    else:
        target_profile.role = new_role
        target_profile.save()
        # سجل العملية
        RoleChangeLog.objects.create(
            changed_by=request.user,
            changed_user=user,
            old_role=old_role,
            new_role=new_role,
            timestamp=datetime.datetime.now()
        )
        # إشعار بريد إلكتروني للمستخدم
        if user.email:
            subject = "تم تغيير صلاحيتك في النظام"
            message = f"تم تغيير صلاحيتك من {dict(UserProfile.ROLE_CHOICES).get(old_role, old_role)} إلى {dict(UserProfile.ROLE_CHOICES).get(new_role, new_role)}."
            send_notification_email(subject, message, [user.email])
        messages.success(request, f"تم تغيير صلاحية المستخدم {user.username} من {dict(UserProfile.ROLE_CHOICES).get(old_role, old_role)} إلى {dict(UserProfile.ROLE_CHOICES).get(new_role, new_role)}.")
    return redirect('user_management')


@login_required
def note_official_pdf(request, token):
    note = get_object_or_404(Note, access_token=token)
    # سجل طباعة الوثيقة الرسمية
    from .models import ActivityLog
    if request.user.is_authenticated:
        ActivityLog.objects.create(user=request.user, action='طباعة PDF رسمي', note=note)
    user_profile = get_user_profile(request)

    if user_profile.role not in ['admin', 'supervisor', 'employee']:
        return render(request, 'notes/no_permission.html')

    qr_data = request.build_absolute_uri(f'/attachment/{note.access_token}/' if note.file else request.path)
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    font_path = "file://" + os.path.abspath(
        os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
    ).replace("\\", "/")

    html = render_to_string('notes/note_official_pdf.html', {
        'note': note,
        'img_str': img_str,
        'logo_url': request.build_absolute_uri('/static/images/logo.png'),
        'font_path': font_path,
    })

    pdf_filename = f"{note.title.replace(' ', '_')}_{note.access_token}_official.pdf"
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    try:
        HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(pdf_path)
    except Exception as e:
        print("PDF Generation Error:", e)
        return HttpResponse("خطأ في توليد ملف PDF", status=500)

    return redirect(f"{settings.MEDIA_URL}generated_pdfs/{pdf_filename}")

    from .models import ActivityLog
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def activity_log_view(request):
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')[:200]
    return render(request, 'notes/activity_log.html', {'logs': logs})
from .models import AccessLog
from django.contrib.admin.views.decorators import staff_member_required

def log_access(request, note, action):
    ip = request.META.get('REMOTE_ADDR')
    AccessLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        note=note,
        action=action,
        ip_address=ip
    )

@staff_member_required
def access_log(request):
    logs = AccessLog.objects.select_related('note', 'user').order_by('-timestamp')[:100]
    return render(request, 'notes/access_log.html', {'logs': logs})
@login_required
def notifications(request):
    notifications_list = AccessNotification.objects.filter(user=request.user).order_by('-accessed_at')
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'notes/notifications.html', {
        'notifications': notifications_list,
        'user_profile': user_profile,
    })
from django.shortcuts import render
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Note, UserProfile, Tag  # عدل حسب أسماء موديلاتك

@login_required
def dashboard(request):
    user = request.user
    # احصل على بيانات المستخدم الموسعة (افترضت وجود UserProfile مربوط بالمستخدم)
    user_profile = None
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = None

    # احصل على الوثائق الخاصة بالمستخدم (أو جميع الوثائق للمشرفين)
    if user_profile and user_profile.role in ['admin', 'supervisor']:
        notes = Note.objects.all().order_by('-created_at')
    else:
        notes = Note.objects.filter(created_by=user).order_by('-created_at')

    # جلب الإحصائيات الأساسية
    stats = {
        'active': Note.objects.filter(is_archived=False, expiry_date__gt=now()).count(),
        'archived': Note.objects.filter(is_archived=True).count(),
        'expired': Note.objects.filter(expiry_date__lte=now(), is_archived=False).count(),
        'users': UserProfile.objects.count(),
    }

    context = {
        'user': user,
        'user_profile': user_profile,
        'notes': notes,
        'stats': stats,
        'now': now(),  # لتستخدم في القالب للمقارنات
    }
    return render(request, 'notes/dashboard.html', context)

from django.shortcuts import render
from .models_news import News

def news_list(request):
    # جلب الأخبار المنشورة للجميع، أو جميع أخبار المستخدم إذا كان ناشر أو مشرف
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)
        if user_profile and (user_profile.role in ['admin', 'supervisor'] or News.objects.filter(created_by=request.user).exists()):
            # عرض كل الأخبار التي أنشأها المستخدم أو كل الأخبار إذا كان مشرف
            news_list = News.objects.filter(models.Q(is_published=True) | models.Q(created_by=request.user)).order_by('-created_at').distinct()
        else:
            news_list = News.objects.filter(is_published=True).order_by('-created_at')
    else:
        user_profile = None
        news_list = News.objects.filter(is_published=True).order_by('-created_at')

    latest_news = news_list.first() if news_list.exists() else None

    # تجهيز قائمة IDs الأخبار التي أعجبها المستخدم الحالي
    user_liked_news_ids = set()
    if request.user.is_authenticated:
        user_liked_news_ids = set(
            news_like.news_id for news_like in NewsLike.objects.filter(user=request.user)
        )

    return render(request, 'notes/news.html', {
        'news_list': news_list,
        'latest_news': latest_news,
        'user_profile': user_profile,
        'user_liked_news_ids': user_liked_news_ids,
    })
from django.shortcuts import render, redirect
from .models_news import News
from django.contrib.auth.decorators import login_required

@login_required
def add_news(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if not title or not content:
            return render(request, 'notes/add_news.html', {'error': 'العنوان والمحتوى مطلوبان'})


        news_obj = News.objects.create(
            title=title,
            content=content,
            image=image,
            created_by=request.user
        )

        # تم تعطيل إرسال إشعار لكل مستخدم عند إنشاء خبر جديد بناءً على طلب المستخدم

        return redirect('news')

    return render(request, 'notes/add_news.html')


# ==========================================
# الميزات الجديدة: PWA، QR Scanner، التدقيق
# ==========================================

def qr_scanner(request):
    """صفحة مسح QR للهواتف المحمولة"""
    return render(request, 'notes/qr_scanner.html')


def pwa_checker(request):
    """صفحة فحص جاهزية PWA للتطبيق"""
    return render(request, 'pwa_checker.html')


def offline_page(request):
    """صفحة أوفلاين للPWA"""
    return render(request, 'offline.html')


# ==========================================
# نظام التدقيق المتقدم
# ==========================================
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
import json
import csv
from django.http import HttpResponse


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def audit_dashboard(request):
    """لوحة التدقيق والأمان المتقدمة"""
    try:
        from .models import AuditLog, DocumentChangeLog, SecurityAlert
    except ImportError:
        # إذا لم تكن النماذج موجودة بعد، اعرض صفحة بسيطة
        return render(request, 'notes/audit_dashboard.html', {
            'audit_logs': [],
            'security_alerts': [],
            'document_changes': [],
            'stats': {
                'total_actions_today': 0,
                'active_users_today': 0,
                'security_alerts_today': 0,
                'failed_logins_today': 0
            },
            'top_users': [],
            'top_ips': []
        })
    
    today = timezone.now().date()
    
    # الإحصائيات اليومية
    stats = {
        'total_actions_today': AuditLog.objects.filter(timestamp__date=today).count(),
        'active_users_today': AuditLog.objects.filter(timestamp__date=today).values('user').distinct().count(),
        'security_alerts_today': SecurityAlert.objects.filter(timestamp__date=today).count(),
        'failed_logins_today': AuditLog.objects.filter(
            timestamp__date=today, 
            action='LOGIN', 
            success=False
        ).count()
    }
    
    # أحدث سجلات التدقيق
    audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:50]
    
    # التنبيهات الأمنية غير المحلولة
    security_alerts = SecurityAlert.objects.filter(is_resolved=False).order_by('-timestamp')
    
    # تغييرات الوثائق الأخيرة
    document_changes = DocumentChangeLog.objects.select_related('document', 'user').order_by('-timestamp')[:30]
    
    # أكثر المستخدمين نشاطاً اليوم
    top_users = list(
        AuditLog.objects.filter(timestamp__date=today)
        .values('user__username')
        .annotate(action_count=Count('id'))
        .order_by('-action_count')[:10]
    )
    
    # أكثر عناوين IP نشاطاً
    top_ips = list(
        AuditLog.objects.filter(timestamp__date=today)
        .values('ip_address')
        .annotate(action_count=Count('id'))
        .order_by('-action_count')[:10]
    )
    
    return render(request, 'notes/audit_dashboard.html', {
        'audit_logs': audit_logs,
        'security_alerts': security_alerts,
        'document_changes': document_changes,
        'stats': stats,
        'top_users': top_users,
        'top_ips': top_ips
    })


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def audit_log_details(request, log_id):
    """تفاصيل سجل تدقيق محدد"""
    try:
        from .models import AuditLog
        log = get_object_or_404(AuditLog, id=log_id)
        
        data = {
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user': log.user.username if log.user else 'غير محدد',
            'action': log.get_action_display(),
            'description': log.description,
            'ip_address': log.ip_address or 'غير محدد',
            'user_agent': log.user_agent or 'غير محدد',
            'success': log.success,
            'old_values': log.old_values,
            'new_values': log.new_values,
            'error_message': log.error_message
        }
        
        return JsonResponse(data)
    except ImportError:
        return JsonResponse({'error': 'النظام غير متاح'})


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def resolve_security_alert(request, alert_id):
    """حل تنبيه أمني"""
    if request.method == 'POST':
        try:
            from .models import SecurityAlert
            alert = get_object_or_404(SecurityAlert, id=alert_id)
            alert.is_resolved = True
            alert.resolved_by = request.user
            alert.resolved_at = timezone.now()
            alert.resolution_notes = request.POST.get('notes', '')
            alert.save()
            
            return JsonResponse({'success': True})
        except ImportError:
            return JsonResponse({'error': 'النظام غير متاح'})
    
    return JsonResponse({'error': 'طريقة غير مدعومة'})


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def daily_audit_report(request):
    """تقرير تدقيق يومي"""
    try:
        from .utils.audit import ReportGenerator
        
        report = ReportGenerator.generate_daily_security_report()
        
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="daily_report_{report["date"]}.json"'
        json.dump(report, response, ensure_ascii=False, indent=2, default=str)
        
        return response
    except ImportError:
        return HttpResponse('النظام غير متاح', status=404)


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def weekly_audit_report(request):
    """تقرير تدقيق أسبوعي"""
    try:
        from .utils.audit import ReportGenerator
        report = ReportGenerator.generate_weekly_security_report()
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="weekly_report.json"'
        import json
        json.dump(report, response, ensure_ascii=False, indent=2, default=str)
        return response
    except ImportError:
        return HttpResponse('النظام غير متاح', status=404)


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def monthly_audit_report(request):
    """تقرير تدقيق شهري"""
    try:
        from .utils.audit import ReportGenerator
        report = ReportGenerator.generate_monthly_security_report()
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="monthly_report.json"'
        import json
        json.dump(report, response, ensure_ascii=False, indent=2, default=str)
        return response
    except ImportError:
        return HttpResponse('النظام غير متاح', status=404)


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def user_audit_report(request, username):
    """تقرير تدقيق لمستخدم محدد"""
    try:
        from .utils.audit import ReportGenerator
        
        user = get_object_or_404(User, username=username)
        report = ReportGenerator.generate_user_activity_report(user)
        
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="user_report_{username}.json"'
        json.dump(report, response, ensure_ascii=False, indent=2, default=str)
        
        return response
    except ImportError:
        return HttpResponse('النظام غير متاح', status=404)


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def security_audit_report(request):
    """تقرير أمني شامل"""
    try:
        from .utils.audit import ReportGenerator
        report = ReportGenerator.generate_full_security_report()
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="full_security_report.json"'
        import json
        json.dump(report, response, ensure_ascii=False, indent=2, default=str)
        return response
    except ImportError:
        return HttpResponse('النظام غير متاح', status=404)


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def export_audit_log(request):
    """تصدير سجل التدقيق كـ CSV"""
    try:
        from .models import AuditLog
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_log.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['التاريخ', 'المستخدم', 'العملية', 'المورد', 'الوصف', 'عنوان IP', 'النجاح'])
        
        logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:1000]
        for log in logs:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user.username if log.user else 'غير محدد',
                log.get_action_display(),
                log.resource_type,
                log.description,
                log.ip_address or 'غير محدد',
                'نعم' if log.success else 'لا'
            ])
        
        return response
    except ImportError:
        return HttpResponse('النظام غير متاح', status=404)


@user_passes_test(lambda u: u.is_superuser or getattr(u, 'userprofile', None) and u.userprofile.role in ['admin', 'supervisor'])
def audit_logs_ajax(request):
    """تحديث سجلات التدقيق عبر AJAX"""
    try:
        from .models import AuditLog
        
        logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:20]
        
        html = ''
        for log in logs:
            status_class = '' if log.success else 'bg-red-50'
            action_class = {
                'LOGIN': 'bg-green-100 text-green-800',
                'DELETE': 'bg-red-100 text-red-800',
                'UPDATE': 'bg-yellow-100 text-yellow-800'
            }.get(log.action, 'bg-blue-100 text-blue-800')
            
            severity_class = {
                'CRITICAL': 'bg-red-100 text-red-800',
                'HIGH': 'bg-orange-100 text-orange-800',
                'MEDIUM': 'bg-yellow-100 text-yellow-800'
            }.get(log.severity, 'bg-gray-100 text-gray-800')
            
            html += f'''
            <tr class="{status_class}">
                <td>{log.timestamp.strftime("%Y-%m-%d %H:%M")}</td>
                <td>
                    <div class="flex items-center">
                        <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-2">
                            {log.user.username[0].upper() if log.user else '?'}
                        </div>
                        {log.user.username if log.user else 'غير محدد'}
                    </div>
                </td>
                <td><span class="px-2 py-1 rounded text-xs font-semibold {action_class}">{log.get_action_display()}</span></td>
                <td>{log.resource_type}</td>
                <td>{log.ip_address or 'غير محدد'}</td>
                <td>{'✅ نجح' if log.success else '❌ فشل'}</td>
                <td><span class="px-2 py-1 rounded text-xs font-semibold {severity_class}">{log.get_severity_display()}</span></td>
                <td><button class="text-blue-600 hover:underline" onclick="showLogDetails({log.id})">عرض</button></td>
            </tr>
            '''
        
        return HttpResponse(html)
    except ImportError:
        return HttpResponse('')


# دالة مساعدة لتسجيل العمليات
def log_audit_action(user, action, resource_type, description="", request=None, success=True):
    """دالة مساعدة لتسجيل العمليات في سجل التدقيق"""
    try:
        from .utils.audit import AuditLogger
        
        AuditLogger.log_action(
            user=user,
            action=action,
            resource_type=resource_type,
            description=description,
            request=request,
            success=success
        )
    except ImportError:
        pass  # تجاهل إذا لم يكن نظام التدقيق متاحاً


from django.shortcuts import render
from django.db.models import Count
from django.db import models  # مهم جدًا لاستدعاء functions.TruncMonth
from .models import Note
from django.contrib.auth.models import User

def stats_dashboard(request):
    notes_by_type_qs = Note.objects.values('doc_type').annotate(count=Count('id'))
    notes_by_type_labels = [item['doc_type'] for item in notes_by_type_qs]
    notes_by_type_data = [item['count'] for item in notes_by_type_qs]

    notes_by_month_qs = Note.objects.annotate(month=models.functions.TruncMonth('created_at')) \
                                    .values('month').annotate(count=Count('id')).order_by('month')
    notes_by_month_labels = [item['month'].strftime('%Y-%m') for item in notes_by_month_qs]
    notes_by_month_data = [item['count'] for item in notes_by_month_qs]

    users_by_role_qs = User.objects.values('profile__role').annotate(count=Count('id'))
    users_by_role_labels = [item['profile__role'] or 'غير محدد' for item in users_by_role_qs]
    users_by_role_data = [item['count'] for item in users_by_role_qs]

    return render(request, 'notes/stats_dashboard.html', {
        'notes_by_type_labels': notes_by_type_labels,
        'notes_by_type_data': notes_by_type_data,
        'notes_by_month_labels': notes_by_month_labels,
        'notes_by_month_data': notes_by_month_data,
        'users_by_role_labels': users_by_role_labels,
        'users_by_role_data': users_by_role_data,
    })


# 🆕 API للإحصائيات في الوقت الفعلي

from django.http import JsonResponse
from datetime import date

# =============================
# البحث السريع (AJAX Quick Search)
# =============================
from django.views.decorators.http import require_GET
@login_required
@require_GET
def ajax_quick_search(request):
    """
    Endpoint متكامل للبحث السريع عن الوثائق أو الأخبار (AJAX)
    يرجع النتائج بصيغة JSON لعرضها مباشرة في الواجهة.
    يدعم البحث في العنوان، المحتوى، واسم المستخدم للوثائق، مع التحقق من صلاحيات المستخدم.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'يجب تسجيل الدخول'}, status=403)

    query = request.GET.get('q', '').strip()
    results = []
    if not query:
        return JsonResponse({'results': []})

    # بحث في الوثائق (العنوان، المحتوى، اسم المستخدم)
    notes = Note.objects.filter(
        is_deleted=False
    ).filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(created_by__username__icontains=query)
    ).order_by('-created_at')[:10]
    for note in notes:
        results.append({
            'type': 'note',
            'id': note.id,
            'title': note.title,
            'created_at': note.created_at.strftime('%Y-%m-%d'),
            'author': note.created_by.username if hasattr(note, 'created_by') else '',
            'url': f'/note/{note.access_token}/',
            'label': f"وثيقة: {note.title} (بواسطة {note.created_by.username})",
        })

    # بحث في الأخبار (العنوان والمحتوى)
    try:
        from .models_news import News
        news_list = News.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')[:5]
        for news in news_list:
            results.append({
                'type': 'news',
                'id': news.id,
                'title': news.title,
                'created_at': news.created_at.strftime('%Y-%m-%d'),
                'author': news.created_by.username if hasattr(news, 'created_by') else '',
                'url': f'/news/{news.id}/',
                'label': f"خبر: {news.title} (بواسطة {news.created_by.username})",
            })
    except ImportError:
        pass

    # ترتيب النتائج: الوثائق أولاً ثم الأخبار
    results = sorted(results, key=lambda x: (x['type'] != 'note', x['created_at']), reverse=True)

    return JsonResponse({'results': results})

@login_required
def realtime_stats_api(request):
    """API لجلب الإحصائيات في الوقت الفعلي"""
    try:
        from .models import AuditLog, SecurityAlert
        from datetime import date
        
        today = date.today()
        data = {
            'audit_logs': AuditLog.objects.filter(timestamp__date=today).count(),
            'security_alerts': SecurityAlert.objects.filter(is_resolved=False).count(),
        }
        
        # التحقق من وجود تنبيهات أمنية جديدة خلال آخر دقيقة
        from django.utils import timezone
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        new_alert = SecurityAlert.objects.filter(
            timestamp__gte=one_minute_ago,
            risk_level__in=['HIGH', 'CRITICAL']
        ).first()
        
        if new_alert:
            data['new_security_alert'] = {
                'description': new_alert.description,
                'risk_level': new_alert.get_risk_level_display(),
                'timestamp': new_alert.timestamp.isoformat()
            }
        
        return JsonResponse(data)
        
    except ImportError:
        return JsonResponse({
            'audit_logs': 0,
            'security_alerts': 0
        })


# ==========================================
# 🆕 مركز الإشعارات المتقدم
# ==========================================

@login_required
def notifications_center(request):
    """مركز الإشعارات الموحد"""
    try:
        from .models import Notification
        
        # جلب الإشعارات الخاصة بالمستخدم (بدون slice أولاً)
        base_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        # فلترة حسب النوع إذا طُلب
        filter_type = request.GET.get('type', 'all')
        if filter_type != 'all':
            filtered_notifications = base_notifications.filter(type=filter_type)
        else:
            filtered_notifications = base_notifications
        
        # تطبيق slice بعد الفلترة
        notifications = filtered_notifications[:50]
        
        # تصنيف الإشعارات حسب النوع (استخدام base_notifications للإحصائيات)
        notification_types = {
            'all': base_notifications.count(),
            'unread': base_notifications.filter(is_read=False).count(),
            'document': base_notifications.filter(type='document').count(),
            'news': base_notifications.filter(type='news').count(),
            'user': base_notifications.filter(type='user').count(),
            'system': base_notifications.filter(type='system').count(),
        }
        
        return render(request, 'notes/notifications_center.html', {
            'notifications': notifications,
            'notification_types': notification_types,
            'current_filter': filter_type,
            'user_profile': get_user_profile(request),
        })
    
    except ImportError:
        # إذا لم يكن نموذج الإشعارات موجود، استخدم AccessNotification
        notifications = AccessNotification.objects.filter(user=request.user).order_by('-accessed_at')[:50]
        
        notification_types = {
            'all': notifications.count(),
            'unread': notifications.count(),  # جميع AccessNotification تعتبر جديدة
        }
        
        return render(request, 'notes/notifications_center.html', {
            'notifications': notifications,
            'notification_types': notification_types,
            'current_filter': 'all',
            'user_profile': get_user_profile(request),
            'legacy_mode': True,
        })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """تحديد إشعار كمقروء"""
    try:
        from .models import Notification
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'success': True})
    except ImportError:
        return JsonResponse({'error': 'النظام غير متاح'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_POST
def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    try:
        from .models import Notification
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return JsonResponse({'success': True})
    except ImportError:
        return JsonResponse({'error': 'النظام غير متاح'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_unread_notifications_count(request):
    """API للحصول على عدد الإشعارات غير المقروءة"""
    try:
        from .models import Notification
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'count': count})
    except ImportError:
        # استخدام AccessNotification كبديل
        count = AccessNotification.objects.filter(user=request.user).count()
        return JsonResponse({'count': count})


def create_notification(user, title, message, notification_type='system', related_object=None):
    """دالة مساعدة لإنشاء إشعار جديد"""
    try:
        from .models import Notification
        
        # تجنب إنشاء إشعارات مكررة
        existing = Notification.objects.filter(
            user=user,
            title=title,
            message=message,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).exists()
        
        if not existing:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                type=notification_type,
                related_object_id=related_object.id if related_object else None,
                related_object_type=related_object.__class__.__name__ if related_object else None
            )
    except ImportError:
        # إنشاء AccessNotification كبديل
        AccessNotification.objects.create(
            user=user,
            note=related_object if hasattr(related_object, 'access_token') else None,
            accessed_at=timezone.now()
        )


# ==========================================
# 🆕 سجل النشاطات الشامل
# ==========================================

@login_required
def activity_feed(request):
    """سجل النشاطات الشامل للموقع"""
    try:
        from .models import ActivityFeed
        
        user_profile = get_user_profile(request)
        
        # فقط المشرفين والإداريين يمكنهم رؤية كل النشاطات
        if user_profile.role in ['admin', 'supervisor']:
            activities = ActivityFeed.objects.all()
        else:
            # المستخدمين العاديين يرون نشاطاتهم فقط أو النشاطات العامة
            activities = ActivityFeed.objects.filter(
                Q(user=request.user) | Q(is_public=True)
            )
        
        # فلترة حسب النوع
        activity_type = request.GET.get('type', 'all')
        if activity_type != 'all':
            activities = activities.filter(action_type=activity_type)
        
        # فلترة حسب المستخدم (للمشرفين فقط)
        user_filter = request.GET.get('user')
        if user_filter and user_profile.role in ['admin', 'supervisor']:
            activities = activities.filter(user__username__icontains=user_filter)
        
        # فلترة حسب التاريخ
        date_filter = request.GET.get('date')
        if date_filter:
            activities = activities.filter(created_at__date=date_filter)
        
        # حفظ QuerySet الأساسي للإحصائيات قبل slice
        base_activities_for_stats = activities
        
        activities = activities.order_by('-created_at')[:100]
        
        # إحصائيات النشاطات (استخدام base_activities_for_stats)
        from django.utils import timezone
        activity_stats = {
            'total': base_activities_for_stats.count(),
            'today': base_activities_for_stats.filter(created_at__date=timezone.now().date()).count(),
            'this_week': base_activities_for_stats.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
        }
        
        # أنواع النشاطات للفلترة
        activity_types = ActivityFeed.objects.values('action_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return render(request, 'notes/activity_feed.html', {
            'activities': activities,
            'activity_stats': activity_stats,
            'activity_types': activity_types,
            'current_type_filter': activity_type,
            'current_user_filter': user_filter,
            'current_date_filter': date_filter,
            'user_profile': user_profile,
        })
        
    except ImportError:
        # استخدام ActivityLog كبديل
        user_profile = get_user_profile(request)
        
        if user_profile.role in ['admin', 'supervisor']:
            activities = ActivityLog.objects.all().order_by('-timestamp')[:100]
        else:
            activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
        
        activity_stats = {
            'total': activities.count(),
            'today': activities.filter(timestamp__date=timezone.now().date()).count(),
            'this_week': activities.filter(timestamp__gte=timezone.now() - timezone.timedelta(days=7)).count(),
        }
        
        return render(request, 'notes/activity_feed.html', {
            'activities': activities,
            'activity_stats': activity_stats,
            'activity_types': [],
            'current_type_filter': 'all',
            'user_profile': user_profile,
            'legacy_mode': True,
        })


@login_required
def activity_feed_api(request):
    """API لجلب النشاطات عبر AJAX"""
    try:
        from .models import ActivityFeed
        
        user_profile = get_user_profile(request)
        
        # جلب النشاطات حسب الصلاحيات
        if user_profile.role in ['admin', 'supervisor']:
            activities = ActivityFeed.objects.all()
        else:
            activities = ActivityFeed.objects.filter(
                Q(user=request.user) | Q(is_public=True)
            )
        
        # فلترة
        activity_type = request.GET.get('type', 'all')
        if activity_type != 'all':
            activities = activities.filter(action_type=activity_type)
        
        activities = activities.order_by('-created_at')[:20]
        
        # تحويل إلى JSON
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'user': activity.user.username,
                'action': activity.action,
                'description': activity.description,
                'action_type': activity.action_type,
                'created_at': activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_public': activity.is_public,
            })
        
        return JsonResponse({'activities': activities_data})
        
    except ImportError:
        # استخدام ActivityLog كبديل
        user_profile = get_user_profile(request)
        
        if user_profile.role in ['admin', 'supervisor']:
            activities = ActivityLog.objects.all().order_by('-timestamp')[:20]
        else:
            activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:20]
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'user': activity.user.username if activity.user else 'نظام',
                'action': activity.action,
                'description': f"{activity.action} - {getattr(activity, 'note', 'نشاط عام')}",
                'action_type': 'general',
                'created_at': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_public': True,
            })
        
        return JsonResponse({'activities': activities_data})


def log_activity(user, action, description, action_type='general', is_public=True, related_object=None):
    """دالة مساعدة لتسجيل النشاطات"""
    try:
        from .models import ActivityFeed
        ActivityFeed.objects.create(
            user=user,
            action=action,
            description=description,
            action_type=action_type,
            is_public=is_public,
            related_object_id=related_object.id if related_object else None,
            related_object_type=related_object.__class__.__name__ if related_object else None
        )
    except ImportError:
        # استخدام ActivityLog كبديل
        if hasattr(related_object, 'access_token'):  # إذا كان Note
            ActivityLog.objects.create(
                user=user,
                action=action,
                note=related_object,
                timestamp=timezone.now()
            )
        else:
            ActivityLog.objects.create(
                user=user,
                action=action,
                timestamp=timezone.now()
            )


# ==========================================
# 🆕 تحديث الدوال الموجودة لإضافة الإشعارات والنشاطات
# ==========================================

# تحديث دالة إنشاء الوثيقة لإضافة الإشعارات
def enhanced_create_note_with_notifications(request, note):
    """دالة مساعدة لإضافة الإشعارات عند إنشاء وثيقة جديدة"""
    # إشعار للمستخدم المحدد إذا كانت الوثيقة موجهة له
    if note.file_for_user and note.file_for_user != note.created_by:
        create_notification(
            user=note.file_for_user,
            title="وثيقة جديدة موجهة لك",
            message=f"تم إنشاء وثيقة جديدة بعنوان '{note.title}' وموجهة لك",
            notification_type='document',
            related_object=note
        )
    
    # إشعار للمشرفين
    supervisors = User.objects.filter(profile__role__in=['admin', 'supervisor'])
    for supervisor in supervisors:
        if supervisor != note.created_by:
            create_notification(
                user=supervisor,
                title="وثيقة جديدة في النظام",
                message=f"تم إنشاء وثيقة جديدة بعنوان '{note.title}' بواسطة {note.created_by.username}",
                notification_type='document',
                related_object=note
            )
    
    # تسجيل النشاط
    log_activity(
        user=note.created_by,
        action="إنشاء وثيقة",
        description=f"تم إنشاء وثيقة جديدة بعنوان: {note.title}",
        action_type='document',
        is_public=True,
        related_object=note
    )


# تحديث دالة إضافة الأخبار لإضافة الإشعارات
def enhanced_add_news_with_notifications(request, news):
    """دالة مساعدة لإضافة الإشعارات عند إنشاء خبر جديد"""
    # إشعار لجميع المستخدمين النشطين
    active_users = User.objects.filter(is_active=True).exclude(id=news.created_by.id)
    
    for user in active_users[:20]:  # تحديد العدد لتجنب الإفراط
        create_notification(
            user=user,
            title="خبر جديد",
            message=f"تم نشر خبر جديد بعنوان: {news.title}",
            notification_type='news',
            related_object=news
        )
    
    # تسجيل النشاط
    log_activity(
        user=news.created_by,
        action="نشر خبر",
        description=f"تم نشر خبر جديد بعنوان: {news.title}",
        action_type='news',
        is_public=True,
        related_object=news
    )

# =====================
# دوال مساعدة لسجل النشاطات
# =====================

@login_required
def activity_details(request, activity_id):
    """عرض تفاصيل نشاط معين"""
    from .models import ActivityFeed
    activity = get_object_or_404(ActivityFeed, id=activity_id)
    
    # التحقق من الصلاحيات - الأدمن والمشرف يمكنهم رؤية كل النشاطات
    if not (request.user.profile.role in ['admin', 'supervisor'] or activity.user == request.user):
        return JsonResponse({'error': 'ليس لديك صلاحية لعرض هذا النشاط'}, status=403)
    
    data = {
        'user': activity.user.username,
        'action': activity.action,
        'description': activity.description,
        'action_type': activity.action_type,
        'created_at': activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'ip_address': activity.ip_address,
        'user_agent': activity.user_agent[:100] if activity.user_agent else None,
        'is_public': activity.is_public,
        'is_important': activity.is_important,
    }
    
    return JsonResponse(data)

@login_required
def export_activities(request):
    """تصدير النشاطات إلى CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    from .models import ActivityFeed
    
    # التحقق من الصلاحيات
    if not request.user.profile.role in ['admin', 'supervisor']:
        return HttpResponse('ليس لديك صلاحية للتصدير', status=403)
    
    # الحصول على المرشحات
    type_filter = request.GET.get('type', 'all')
    user_filter = request.GET.get('user', '')
    date_filter = request.GET.get('date', '')
    
    # بناء الاستعلام
    activities = ActivityFeed.objects.all().order_by('-created_at')
    
    if type_filter != 'all':
        activities = activities.filter(action_type=type_filter)
    
    if user_filter:
        activities = activities.filter(user__username__icontains=user_filter)
    
    if date_filter:
        activities = activities.filter(created_at__date=date_filter)
    
    # إنشاء ملف CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="activities_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # إضافة BOM لدعم العربية في Excel
    response.write('\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    writer.writerow(['المستخدم', 'العملية', 'الوصف', 'النوع', 'التاريخ', 'عنوان IP', 'عام', 'مهم'])
    
    for activity in activities[:1000]:  # تحديد عدد السجلات للتصدير
        writer.writerow([
            activity.user.username,
            activity.action,
            activity.description,
            activity.action_type,
            activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            activity.ip_address or '',
            'نعم' if activity.is_public else 'لا',
            'نعم' if activity.is_important else 'لا'
        ])
    
    return response
