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
# إضافة تعليق على خبر
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
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

        activation_token = str(uuid.uuid4())
        user = User.objects.create_user(username=username, password=password, email=email, is_active=False)
        UserProfile.objects.create(user=user, role='viewer')
        user.profile.activation_token = activation_token
        user.profile.save()

        activation_link = request.build_absolute_uri(reverse('activate_account', args=[activation_token]))
        send_mail(
            'تفعيل حسابك في اتحاد الصحفيين العراقيين',
            f'مرحباً {username},\n\nيرجى الضغط على الرابط التالي لتفعيل حسابك:\n{activation_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )
        return render(request, 'notes/register.html', {'error': 'تم إرسال رسالة تفعيل إلى بريدك الإلكتروني. يرجى التحقق من البريد لتفعيل الحساب.'})

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
        qr_data = request.build_absolute_uri(note.file.url)
        attachment_url = qr_data

        qr = qrcode.make(qr_data)
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
        qr_data = request.build_absolute_uri(note.file.url)
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
    notes = Note.objects.filter(created_by=request.user, is_deleted=False).order_by('-created_at')
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

    return render(request, 'notes/user_management.html', {
        'users': users,
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
    user = User.objects.get(id=user_id)
    new_role = request.POST.get('role')
    current_user_profile = get_user_profile(request)
    target_profile = user.userprofile
    old_role = target_profile.role
    # لا يمكن تغيير صلاحية نفسك أو مستخدم أعلى منك
    if user == request.user:
        messages.error(request, "لا يمكنك تغيير صلاحيتك بنفسك.")
    elif current_user_profile.role == 'supervisor' and target_profile.role in ['admin', 'supervisor']:
        messages.error(request, "لا يمكنك تغيير صلاحية مشرف أو مدير النظام.")
    elif new_role not in ['admin', 'supervisor', 'employee', 'normal', 'viewer', 'reader']:
        messages.error(request, "صلاحية غير معروفة.")
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
    user_profile = get_user_profile(request)

    if user_profile.role not in ['admin', 'supervisor', 'employee']:
        return render(request, 'notes/no_permission.html')

    qr_data = request.build_absolute_uri(note.file.url if note.file else request.path)
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

        news = News.objects.create(
            title=title,
            content=content,
            image=image,
            created_by=request.user
        )
        return redirect('news')

    return render(request, 'notes/add_news.html')

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
