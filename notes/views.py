# views.py (كود كامل محسّن ومعدّل)

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings  # type: ignore
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

import datetime
import os
import qrcode
import base64
import uuid
import mimetypes
from io import BytesIO
from weasyprint import HTML

from .models import (
    Note, SecurityWarning, UserProfile, Tag,
    LoginHistory, RoleChangeLog
)

# ---------- دوال مساعدة ----------

def get_user_profile(request):
    try:
        return UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(user=request.user, role='viewer')

def send_notification_email(subject, message, recipient_list):
    from django.core.mail import send_mail
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=True,
    )

# ---------- لوحة إحصائيات ----------

@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def stats_dashboard(request):
    notes_by_type = Note.objects.values('doc_type').annotate(count=Count('id'))
    notes_by_month = Note.objects.extra(
        select={'month': "strftime('%Y-%m', created_at)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    users_by_role = UserProfile.objects.values('role').annotate(count=Count('id'))
    return render(request, 'notes/stats_dashboard.html', {
        'notes_by_type': list(notes_by_type),
        'notes_by_month': list(notes_by_month),
        'users_by_role': list(users_by_role),
    })

# ---------- أرشفة تلقائية ----------

def auto_archive_expired_notes():
    now = timezone.now()
    expired_notes = Note.objects.filter(
        is_archived=False, expiry_date__lt=now, is_deleted=False
    )
    for note in expired_notes:
        note.is_archived = True
        note.save()
        if note.created_by.email:
            send_notification_email(
                subject="تمت أرشفة وثيقتك تلقائياً",
                message=f"تمت أرشفة وثيقتك المنتهية بعنوان: {note.title}",
                recipient_list=[note.created_by.email]
            )

# ---------- إشعارات الدخول ----------

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    LoginHistory.objects.create(user=user, ip_address=ip, user_agent=user_agent)

@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def login_history(request):
    logs = LoginHistory.objects.select_related('user').order_by('-login_time')[:100]
    return render(request, 'notes/login_history.html', {'logs': logs})

@user_passes_test(lambda u: u.is_superuser or u.userprofile.role in ['admin', 'supervisor'])
def role_change_log(request):
    logs = RoleChangeLog.objects.select_related('changed_by', 'changed_user').order_by('-timestamp')[:100]
    return render(request, 'notes/role_change_log.html', {'logs': logs})

# ---------- تسجيل وإنشاء ----------

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            return render(request, 'notes/register.html', {'error': 'اسم المستخدم موجود بالفعل'})
        user = User.objects.create_user(username=username, password=password, email=email)
        UserProfile.objects.create(user=user, role='viewer')
        login(request, user)
        return redirect('home')
    return render(request, 'notes/register.html')

# ---------- الصفحة الرئيسية ----------

@login_required
def home(request):
    user_profile = get_user_profile(request)
    if user_profile.role not in ['admin', 'supervisor', 'employee', 'reader']:
        return redirect('user_notes')

    now = timezone.now()
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
        notes = notes_qs.filter(is_archived=False, expiry_date__isnull=True).order_by('-created_at')
    else:
        notes = Note.objects.none()

    return render(request, 'notes/home.html', {
        'notes': notes,
        'user_profile': user_profile,
        'stats': stats,
        'now': now,
        'request': request,
    })

# ---------- عرض تفاصيل الوثيقة ----------

@login_required
def note_detail(request, token):
    note = get_object_or_404(Note, access_token=token)
    user_profile = get_user_profile(request)

    if (user_profile.role == 'viewer' or 
        (note.is_archived and user_profile.role not in ['admin', 'supervisor']) or 
        (note.expiry_date and note.expiry_date < timezone.now() and user_profile.role != 'admin')):
        return render(request, 'notes/no_permission.html')

    qr_data = request.build_absolute_uri(note.file.url if note.file else '')
    qr = qrcode.make(qr_data or request.build_absolute_uri())
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    pdf_filename = f"{note.title.replace(' ', '_')}_{note.access_token}.pdf"
    note_pdf_url = f"{settings.MEDIA_URL}generated_pdfs/{pdf_filename}"

    return render(request, 'notes/note_detail.html', {
        'note': note,
        'user_profile': user_profile,
        'img_str': qr_code_base64,
        'security_warning': SecurityWarning.objects.first(),
        'note_pdf_url': note_pdf_url,
        'attachment_url': note.file.url if note.file else '',
    })

# ✅ باقي الدوال مثل create_note وعمليات الأرشفة والحذف والاسترجاع والبحث وغيرها موجودة بالفعل وممتازة بنفس الصيغة التي أرسلتها.

