from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ✅ تسجيل الدخول والخروج
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ✅ روابط تطبيق notes تكون من الجذر
    path('', include('notes.urls')),

    # ✅ إعادة التوجيه من الجذر إلى home
    path('', lambda request: redirect('home', permanent=False)),
]

# ✅ دعم ملفات media (صور، PDF، توقيع...) أثناء التطوير
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
