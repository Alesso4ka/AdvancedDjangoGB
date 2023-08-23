from django.test import TestCase
from authapp.models import ShopUser
from django.test.client import Client
from django.core.management import call_command
# Create your tests here.

# В данном тесте проверяем вход в админку под разными пользователями
class TestUserManagement(TestCase):
    def setUp(self):
        self.client = Client()
        # Добавляем пользователей
        self.superuser = ShopUser.objects.create_superuser('django2', 'django2@geekshop.local', 'geekbrains')
        self.user = ShopUser.objects.create_user('tarantino', 'tarantino@geekshop.local', 'geekbrains')
        self.user_with__first_name = ShopUser.objects.create_user('umaturman', 'umaturman@geekshop.local',
                                                                  'geekbrains', first_name='Ума')
    def test_user_use_admin(self):
        # Проверяем вход в админку без логина
        response = self.client.get('/admin/users/read/')
        self.assertEqual(response.url, '/auth/login/?next=/admin/users/read/')
        self.assertEqual(response.status_code, 302)

        # Логинимся под обычным пользователем и пробуем войти в админку
        self.client.login(username='tarantino', password='geekbrains')
        response = self.client.get('/auth/login/')
        self.assertEqual(response.context['user'], self.user)
        response = self.client.get('/admin/users/read/')
        self.assertEqual(response.url, '/auth/login/?next=/admin/users/read/')
        self.assertEqual(response.status_code, 302)

        # Логинимся под администратором и пробуем войти в админку
        self.client.login(username='django2', password='geekbrains')
        response = self.client.get('/auth/login/')
        self.assertEqual(response.context['user'], self.superuser)
        response = self.client.get('/admin/users/read/')
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        call_command('sqlsequencereset', 'mainapp', 'authapp', 'ordersapp', 'basketapp')
