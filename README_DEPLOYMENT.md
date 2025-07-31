# 🇮🇶 نظام إدارة الوثائق - اتحاد الصحفيين العراقيين

نظام شامل لإدارة الوثائق والأخبار مع دعم PWA وميزات متقدمة للأمان والتدقيق.

## ✨ الميزات الرئيسية

### 📄 إدارة الوثائق
- إنشاء وتحرير الوثائق الرسمية
- دعم الملفات المرفقة والصور
- نظام QR Code للوصول السريع
- تصنيف الوثائق (واردة/صادرة)
- نظام الوسوم والبحث المتقدم

### 🔐 الأمان والتدقيق
- نظام صلاحيات متقدم
- تسجيل جميع العمليات (Audit Log)
- تتبع محاولات الدخول
- إشعارات أمنية
- حماية الملفات والوثائق

### 📱 تطبيق محمول (PWA)
- يعمل كتطبيق أصلي على الهواتف
- دعم العمل بدون إنترنت
- إشعارات فورية
- واجهة متجاوبة

### 🔔 نظام الإشعارات
- إشعارات فورية للتحديثات
- مركز إشعارات شامل
- تتبع النشاطات
- إشعارات مخصصة حسب الدور

## 🚀 التنصيب والتشغيل

### متطلبات النظام
- Python 3.8+
- Django 5.2+
- PostgreSQL (للإنتاج) أو SQLite (للتطوير)

### خطوات التنصيب

1. **استنساخ المشروع**
```bash
git clone https://github.com/abbas-mma/Iraqi-Journalists-Union1.git
cd Iraqi-Journalists-Union1
```

2. **إعداد البيئة الافتراضية**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows
```

3. **تنصيب المتطلبات**
```bash
pip install -r requirements.txt
```

4. **إعداد متغيرات البيئة**
```bash
cp .env.example .env
# عدل الملف .env وأضف القيم المناسبة
```

5. **إعداد قاعدة البيانات**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

6. **إنشاء مستخدم إداري**
```bash
python manage.py createsuperuser
```

7. **تشغيل الخادم**
```bash
python manage.py runserver
```

## 🌐 النشر على الاستضافة

### Render.com
1. اربط حساب GitHub مع Render
2. اختر هذا المستودع
3. استخدم إعدادات `render.yaml`
4. أضف متغيرات البيئة المطلوبة

### PythonAnywhere
1. ارفع الملفات عبر Git
2. عدل إعدادات WSGI
3. أضف متغيرات البيئة
4. فعل HTTPS

### Heroku
1. ثبت Heroku CLI
2. أنشئ تطبيق جديد
3. ادفع الكود
```bash
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

## 📁 هيكل المشروع

```
project/
├── notes/                  # التطبيق الرئيسي
│   ├── models.py          # نماذج قاعدة البيانات
│   ├── views.py           # منطق التطبيق
│   ├── urls.py            # المسارات
│   └── templates/         # القوالب
├── static/                # الملفات الثابتة
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # قوالب HTML
├── media/                 # الملفات المرفوعة
├── requirements.txt       # متطلبات Python
├── Procfile              # إعدادات Heroku
├── render.yaml           # إعدادات Render
└── manage.py             # إدارة Django
```

## ⚙️ الإعدادات المهمة

### متغيرات البيئة المطلوبة
- `DJANGO_SECRET_KEY`: مفتاح سري قوي
- `DEBUG`: False للإنتاج
- `DJANGO_ALLOWED_HOSTS`: نطاقاتك المسموحة
- `DATABASE_URL`: رابط قاعدة البيانات
- `EMAIL_HOST_USER`: بريد إرسال الإشعارات
- `EMAIL_HOST_PASSWORD`: كلمة مرور التطبيق

### إعدادات الأمان
- HTTPS مفعل تلقائياً في الإنتاج
- حماية CSRF
- حماية XSS
- تسجيل جميع العمليات

## 👥 إدارة المستخدمين

### الأدوار المتاحة
- **مدير النظام**: صلاحيات كاملة
- **مشرف رئيسي**: إدارة المحتوى والمستخدمين
- **موظف**: إنشاء وتحرير الوثائق
- **قراءة**: عرض الوثائق فقط
- **عرض فقط**: عرض محدود

### إدارة الصلاحيات
```python
# في Django Admin أو عبر الكود
user_profile = UserProfile.objects.get(user=user)
user_profile.role = 'admin'
user_profile.save()
```

## 📊 المراقبة والتحليلات

### نظام التدقيق
- تسجيل جميع العمليات
- تتبع تغييرات الوثائق  
- مراقبة محاولات الدخول
- تقارير أمنية شاملة

### الإحصائيات
- عدد الوثائق الكلي
- النشاط اليومي
- المستخدمين النشطين
- تحليل الاستخدام

## 🔧 التخصيص والتطوير

### إضافة ميزات جديدة
1. أنشئ نموذج في `models.py`
2. أضف المنظر في `views.py`
3. أنشئ القالب في `templates/`
4. أضف المسار في `urls.py`

### تخصيص الواجهة
- عدل ملفات CSS في `static/css/`
- استخدم نظام الثيمات المدمج
- أضف مكونات Bootstrap حسب الحاجة

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة
1. **خطأ 500**: تحقق من logs في `/logs/django.log`
2. **الصور لا تظهر**: تأكد من إعدادات MEDIA_URL
3. **خطأ قاعدة البيانات**: تحقق من DATABASE_URL
4. **مشاكل HTTPS**: فعل SECURE_SSL_REDIRECT

### أوامر مفيدة
```bash
# جمع الملفات الثابتة
python manage.py collectstatic

# إنشاء بيانات تجريبية
python create_sample_data.py

# فحص جاهزية PWA
python manage.py runserver
# ثم زر /pwa-checker/
```

## 📞 الدعم والمساعدة

- **المطور**: عباس محمد
- **GitHub**: [abbas-mma](https://github.com/abbas-mma)
- **البريد**: يتم توفيره عند الحاجة

## 📄 الرخصة

هذا المشروع مرخص تحت رخصة MIT - راجع ملف LICENSE للتفاصيل.

## 🏆 الإنجازات

✅ نظام إدارة وثائق شامل  
✅ تطبيق PWA متقدم  
✅ نظام أمان متطور  
✅ واجهة عربية محسنة  
✅ دعم الهواتف الذكية  
✅ نظام إشعارات فوري  
✅ تدقيق وتسجيل شامل

---

**تم تطويره بـ ❤️ لخدمة اتحاد الصحفيين العراقيين**
