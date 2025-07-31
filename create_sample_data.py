#!/usr/bin/env python
import os
import sys
import django

# إعداد Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from notes.models import Notification, ActivityFeed
from django.contrib.auth.models import User

def create_sample_data():
    # الحصول على أول مستخدم
    user = User.objects.first()
    if not user:
        print("لم يتم العثور على مستخدمين. يرجى إنشاء مستخدم أولاً.")
        return
    
    print(f"إنشاء بيانات تجريبية للمستخدم: {user.username}")
    
    # تنظيف البيانات القديمة لتجنب التكرار
    Notification.objects.filter(user=user).delete()
    ActivityFeed.objects.filter(user=user).delete()
    print("✅ تم حذف البيانات التجريبية السابقة")
    
    # إنشاء بعض الإشعارات التجريبية
    notifications = [
        {
            'title': "مرحباً بك في النظام الجديد 🎉",
            'message': "تم تحديث النظام بميزات جديدة رائعة! استكشف مركز الإشعارات وسجل النشاطات.",
            'type': 'system',
            'priority': 'normal'
        },
        {
            'title': "إشعار مهم ⚠️",
            'message': "يرجى مراجعة الوثائق المعلقة في حسابك.",
            'type': 'reminder',
            'priority': 'high'
        },
        {
            'title': "تحديث أمني 🔐",
            'message': "تم تحديث إعدادات الأمان في النظام. كلمة المرور محمية بمستوى أعلى.",
            'type': 'security',
            'priority': 'normal'
        },
        {
            'title': "وثيقة جديدة 📄",
            'message': "تم إضافة وثيقة جديدة تتطلب مراجعتك.",
            'type': 'document',
            'priority': 'low'
        },
        {
            'title': "خبر عاجل 📰",
            'message': "تم نشر خبر مهم يتطلب انتباهك الفوري.",
            'type': 'news',
            'priority': 'urgent'
        },
        {
            'title': "تحديث الملف الشخصي 👤",
            'message': "يرجى تحديث معلوماتك الشخصية لضمان الحصول على أفضل خدمة.",
            'type': 'user',
            'priority': 'normal'
        },
        {
            'title': "إشعار نظام 💻",
            'message': "سيتم إجراء صيانة دورية للنظام الليلة من 12:00 - 2:00 صباحاً.",
            'type': 'system',
            'priority': 'high'
        },
        {
            'title': "تذكير موعد 📅",
            'message': "لديك موعد مراجعة للوثائق غداً في تمام الساعة 10:00 صباحاً.",
            'type': 'reminder',
            'priority': 'normal'
        }
    ]
    
    for notification_data in notifications:
        Notification.objects.create(
            user=user,
            **notification_data
        )
    
    # إنشاء بعض النشاطات التجريبية
    activities = [
        {
            'action': "تسجيل دخول",
            'description': f"تم تسجيل دخول المستخدم {user.username} للنظام",
            'action_type': 'auth',
            'is_public': True
        },
        {
            'action': "استعراض الصفحة الرئيسية",
            'description': "تم عرض الصفحة الرئيسية للنظام",
            'action_type': 'general',
            'is_public': True
        },
        {
            'action': "إنشاء وثيقة جديدة",
            'description': "تم إنشاء وثيقة جديدة في النظام",
            'action_type': 'document',
            'is_public': True,
            'is_important': True
        },
        {
            'action': "تحديث الملف الشخصي",
            'description': "تم تحديث معلومات الملف الشخصي",
            'action_type': 'user',
            'is_public': False
        },
        {
            'action': "إضافة خبر جديد",
            'description': "تم نشر خبر جديد على الموقع",
            'action_type': 'news',
            'is_public': True,
            'is_important': True
        },
        {
            'action': "رفع ملف جديد",
            'description': "تم رفع ملف PDF جديد للنظام",
            'action_type': 'document',
            'is_public': True
        },
        {
            'action': "تحديث كلمة المرور",
            'description': "تم تغيير كلمة المرور بنجاح",
            'action_type': 'security',
            'is_public': False,
            'is_important': True
        },
        {
            'action': "إنشاء مستخدم جديد",
            'description': "تم إنشاء حساب مستخدم جديد من قبل المشرف",
            'action_type': 'admin',
            'is_public': True,
            'is_important': True
        },
        {
            'action': "تسجيل خروج",
            'description': f"تم تسجيل خروج المستخدم {user.username} من النظام",
            'action_type': 'auth',
            'is_public': True
        },
        {
            'action': "بحث في الوثائق",
            'description': "تم البحث عن وثائق بالكلمة المفتاحية",
            'action_type': 'general',
            'is_public': False
        },
        {
            'action': "أرشفة وثيقة",
            'description': "تم أرشفة وثيقة قديمة",
            'action_type': 'document',
            'is_public': True
        },
        {
            'action': "تحديث إعدادات النظام",
            'description': "تم تحديث إعدادات الأمان العامة",
            'action_type': 'system',
            'is_public': True,
            'is_important': True
        }
    ]
    
    for activity_data in activities:
        ActivityFeed.objects.create(
            user=user,
            **activity_data
        )
    
    print(f"✅ تم إنشاء {len(notifications)} إشعارات و {len(activities)} نشاطات بنجاح!")
    
    # إحصائيات
    total_notifications = Notification.objects.filter(user=user).count()
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    total_activities = ActivityFeed.objects.filter(user=user).count()
    
    print(f"📊 الإحصائيات:")
    print(f"   - إجمالي الإشعارات: {total_notifications}")
    print(f"   - الإشعارات غير المقروءة: {unread_notifications}")
    print(f"   - إجمالي النشاطات: {total_activities}")

if __name__ == "__main__":
    create_sample_data()
