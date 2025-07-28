from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# نموذج التعليقات على الأخبار
class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

# نموذج الإعجابات على الأخبار
class NewsLike(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('news', 'user')

    def __str__(self):
        return f"{self.user.username} أعجب بـ {self.news.title}"
