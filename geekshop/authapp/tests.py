from django.test import TestCase
from .models import ShopUser
from django.utils.timezone import now
from datetime import timedelta
from django.test import TestCase
from django.test.client import Client
from authapp.models import ShopUser
from django.core.management import call_command
from mainapp.models import Product, ProductCategory
from basketapp.models import Basket
from basketapp.models import Basket
import factory
from random import randrange
from django.conf import settings


# Create your tests here.
class ModelTests(TestCase):

    # Пример с урока
    def test_user_is_created_with_age(self):
        user = ShopUser.objects.create(age=18)
        self.assertIsNotNone(user.age)

    # Проверка факта создания ключа активации и срока его использования
    def test_user_with_activation_key(self):
        user = ShopUser.objects.create(age=18)
        self.assertIsNotNone(user.activation_key)

    # Проверка срока действия ключа с момента создания
    def test_activation_key_expires(self):
        user = ShopUser.objects.create(age=18)
        # В данном случае решил сравнить значения до минут 2022-01-13 16:42 - или срез [:16]
        valid_val = str(now() + timedelta(hours=48))[:16]
        self.assertTrue(str(user.activation_key_expires)[:16] == valid_val)


class ProductCategoryFabric(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCategory
    name = factory.Faker('name')


class ProductFabric(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(ProductCategoryFabric)
    name = factory.Faker('name')
    quantity = factory.Faker('random_int')
    price = factory.Faker('random_int')


class TestUserManagement(TestCase):
    def setUp(self):
        self.client = Client()

        # Добавляем пользователей
        self.superuser = ShopUser.objects.create_superuser('django2', 'django2@geekshop.local', 'geekbrains')
        self.user = ShopUser.objects.create_user('tarantino', 'tarantino@geekshop.local', 'geekbrains')
        self.user_with__first_name = ShopUser.objects.create_user('umaturman', 'umaturman@geekshop.local',
                                                                  'geekbrains', first_name='Ума')

        # Добавляем категории и продукты в базу данных
        ProductCategory.objects.create(name='Стулья', description='Замечательные стулья')
        ProductCategory.objects.create(name='Диваны', description='Замечательные диваны')
        ProductCategory.objects.create(name='Столы', description='Замечательные столы')
        categories = ProductCategory.objects.all()

        for category in categories:
            ProductFabric.create_batch(10, category=category)
        print(categories)
        print(Product.objects.all())
        print(Product.objects.all().first().price)

        # Create Baskets for users with products
        product_random = Product.objects.all()
        product_count = len(product_random)
        for user in ShopUser.objects.all():
            Basket.objects.create(user_id=user.pk,
                                  product_id=product_random[randrange(1, product_count)].id, quantity=1)
        print('Содержимое корзины:', Basket.objects.all())

    def test_user_login(self):
        # главная без логина
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print('отработал')
        print(ShopUser.objects.all()[0])
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(response.context['title'], 'Главная')
        self.assertNotContains(response, 'Пользователь', status_code=200)
        self.assertNotIn('Пользователь', response.content.decode())

        # данные пользователя
        self.client.login(username='tarantino', password='geekbrains')

        # логинимся
        response = self.client.get('/auth/login/')
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertEqual(response.context['user'], self.user)

        # главная после логина
        response = self.client.get('/')
        self.assertContains(response, 'Пользователь', status_code=200)
        self.assertEqual(response.context['user'], self.user)
        self.assertIn('Пользователь', response.content.decode())

    def test_basket(self):
        # Проверяем вход в корзину без авторизации
        response = self.client.get('/basket/')
        self.assertEqual(response.url, '/auth/login/?next=/basket/')
        self.assertEqual(response.status_code, 302)

        # Логинимся и пробуем войти в корзину
        self.client.login(username='tarantino', password='geekbrains')
        response = self.client.get('/auth/login/')
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertEqual(response.context['user'], self.user)
        # Пробуем войти в корзину
        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(list(response.context['basket']), [])
        self.assertEqual(response.request['PATH_INFO'], '/basket/')

    def test_user_logout(self):
        # данные пользователя
        self.client.login(username='tarantino', password='geekbrains')

        # логинимся
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        # выходим из системы
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302)

        # главная после выхода
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)

    def test_user_register(self):
        # логин без данных пользователя
        response = self.client.get('/auth/register/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'регистрация')
        self.assertTrue(response.context['user'].is_anonymous)

        new_user_data = {
            'username': 'samuel',
            'first_name': 'Сэмюэл',
            'last_name': 'Джексон',
            'password1': 'geekbrains',
            'password2': 'geekbrains',
            'email': 'sumuel@geekshop.local',
            'age': '21'}

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEqual(response.status_code, 302)

        new_user = ShopUser.objects.get(username=new_user_data['username'])

        activation_url = f"{settings.DOMAIN_NAME}/auth/verify/{new_user_data['email']}/{new_user.activation_key}/"

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 200)

        # данные нового пользователя
        self.client.login(username=new_user_data['username'], \
                          password=new_user_data['password1'])

        # логинимся
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        # проверяем главную страницу
        response = self.client.get('/')
        self.assertContains(response, text=new_user_data['first_name'], \
                            status_code=200)

    def test_user_wrong_register(self):
        new_user_data = {
            'username': 'teen',
            'first_name': 'Мэри',
            'last_name': 'Поппинс',
            'password1': 'geekbrains',
            'password2': 'geekbrains',
            'email': 'merypoppins@geekshop.local',
            'age': '17'}

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'register_form', 'age', \
                             'Вы слишком молоды!')

    def tearDown(self):
        call_command('sqlsequencereset', 'mainapp', 'authapp', 'ordersapp', 'basketapp')
