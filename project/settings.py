import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # تحميل متغيرات البيئة من ملف .env

# ------------------------------
# المسار الأساسي للمشروع
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# الإعدادات الأمنية
# ------------------------------
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-1234567890')
DEBUG = False  # يجب أن يكون False في بيئة الإنتاج

# ---------------------------------
# ALLOWED_HOSTS يدعم متغير بيئة أو القيمة الافتراضية
# ---------------------------------
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'abbas114.pythonanywhere.com localhost 127.0.0.1').split()

# ------------------------------
# إعدادات البريد الإلكتروني
# ------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your_app_password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ------------------------------
# التطبيقات المثبتة
# ------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notes.apps.NotesConfig',
]

# ------------------------------
# الوسيطات
# ------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise لتقديم ملفات static
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------
# روابط المشروع
# ------------------------------
ROOT_URLCONF = 'project.urls'

# ------------------------------
# إعدادات القوالب
# ------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ------------------------------
# WSGI Application
# ------------------------------
WSGI_APPLICATION = 'project.wsgi.application'

# ------------------------------
# إعدادات قاعدة البيانات (SQLite)
# ------------------------------
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600,
        ssl_require=False
    )
}

# ------------------------------
# التحقق من كلمات المرور (بسيط للتجريب)
# ------------------------------
AUTH_PASSWORD_VALIDATORS = []

# ------------------------------
# الإعدادات اللغوية والتوقيت
# ------------------------------
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

# ------------------------------
# إعدادات الملفات الثابتة
# ------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ------------------------------
# إعدادات ملفات الوسائط
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ------------------------------
# إعدادات تسجيل الدخول والخروج
# ------------------------------
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'home'

# ------------------------------
# الحقل الافتراضي لنماذج Django
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------
# تعطيل ImageKit مؤقتًا
# ------------------------------
# IMAGEKIT_PUBLIC_KEY = ''
# IMAGEKIT_PRIVATE_KEY = ''
# IMAGEKIT_URL_ENDPOINT = ''
