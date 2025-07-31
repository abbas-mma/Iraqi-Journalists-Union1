// Service Worker للتطبيق المحمول
const CACHE_NAME = 'iraqi-journalists-union-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/images/logo.png',
  '/news/',
  '/incoming/',
  '/outgoing/',
  '/offline.html'
];

// تثبيت Service Worker
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('تم فتح الكاش');
        return cache.addAll(urlsToCache);
      })
  );
});

// استرجاع الملفات من الكاش
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // إرجاع الملف من الكاش إذا وُجد
        if (response) {
          return response;
        }
        
        // محاولة تحميل الملف من الشبكة
        return fetch(event.request).catch(function() {
          // إذا فشل التحميل، إرجاع صفحة أوفلاين
          if (event.request.mode === 'navigate') {
            return caches.match('/offline.html');
          }
        });
      }
    )
  );
});

// تحديث الكاش
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// إشعارات الهاتف المحمول
self.addEventListener('push', function(event) {
  const options = {
    body: event.data ? event.data.text() : 'إشعار جديد من اتحاد الصحفيين العراقيين',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '2'
    },
    actions: [
      {
        action: 'explore', 
        title: 'عرض التفاصيل',
        icon: '/static/images/checkmark.png'
      },
      {
        action: 'close', 
        title: 'إغلاق',
        icon: '/static/images/xmark.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('اتحاد الصحفيين العراقيين', options)
  );
});

// التعامل مع نقر الإشعارات
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  
  if (event.action === 'explore') {
    // فتح الصفحة الرئيسية
    event.waitUntil(clients.openWindow('/'));
  } else if (event.action === 'close') {
    // مجرد إغلاق الإشعار
    event.notification.close();
  } else {
    // النقر على الإشعار نفسه
    event.waitUntil(clients.openWindow('/'));
  }
});
