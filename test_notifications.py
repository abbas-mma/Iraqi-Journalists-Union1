#!/usr/bin/env python
import os
import sys
import django

# إعداد Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from notes.models import Notification
from django.contrib.auth.models import User

def mark_some_as_read():
    """وضع بعض الإشعارات كمقروءة لاختبار الفلترة"""
    user = User.objects.first()
    if not user:
        print("لم يتم العثور على مستخدمين.")
        return
    
    # وضع أول 3 إشعارات كمقروءة
    notifications = Notification.objects.filter(user=user, is_read=False)[:3]
    for notification in notifications:
        notification.is_read = True
        notification.save()
    
    print(f"✅ تم وضع {len(notifications)} إشعارات كمقروءة")
    
    # إحصائيات جديدة
    total = Notification.objects.filter(user=user).count()
    unread = Notification.objects.filter(user=user, is_read=False).count()
    read = total - unread
    
    print(f"📊 الإحصائيات الجديدة:")
    print(f"   - إجمالي الإشعارات: {total}")
    print(f"   - المقروءة: {read}")
    print(f"   - غير المقروءة: {unread}")

if __name__ == "__main__":
    mark_some_as_read()
