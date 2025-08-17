from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Note

class ProtectedDocumentTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.note_private = Note.objects.create(
            title='وثيقة خاصة',
            content='محتوى خاص',
            created_by=self.user1,
            is_private=True
        )
        self.note_for_user = Note.objects.create(
            title='وثيقة لمستخدم محدد',
            content='محتوى خاص',
            created_by=self.user1,
            file_for_user=self.user2
        )
        self.client = Client()

    def test_private_document_access(self):
        # مستخدم غير صاحب الوثيقة
        self.client.login(username='user2', password='pass2')
        response = self.client.get(f'/attachment/{self.note_private.access_token}/')
        self.assertContains(response, 'لا صلاحية', status_code=200)

    def test_file_for_user_access(self):
        # مستخدم غير مخول
        self.client.login(username='user1', password='pass1')
        response = self.client.get(f'/attachment/{self.note_for_user.access_token}/')
        self.assertContains(response, 'لا صلاحية', status_code=200)
        # المستخدم المخول
        self.client.login(username='user2', password='pass2')
        response = self.client.get(f'/attachment/{self.note_for_user.access_token}/')
        self.assertNotContains(response, 'لا صلاحية', status_code=200)
