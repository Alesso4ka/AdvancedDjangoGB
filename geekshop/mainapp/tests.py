from django.test import TestCase
from django.db.models import Sum
from django.test.client import Client
from mainapp.models import Product, ProductCategory
from django.core.management import call_command
import factory
from django.test import TestCase
from django.test.client import Client
from mainapp.models import Product, ProductCategory
# Create your tests here.


# Smoke-test c помощью фабрик factory-boy
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


class TestMainappSmoke(TestCase):
    def setUp(self):
        self.client = Client()
        categories = ProductCategoryFabric.create_batch(10)
        for category in categories:
            ProductFabric.create_batch(10, category=category)

    def test_mainapp_urls(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/products/category/0/')
        self.assertEqual(response.status_code, 200)

        for category in ProductCategory.objects.all():
            response = self.client.get(f'/products/category/{category.pk}/')
            self.assertEqual(response.status_code, 200)

        for product in Product.objects.all():
            response = self.client.get(f'/products/product/{product.pk}/')
            self.assertEqual(response.status_code, 200)


class CatalogTest(TestCase):

    def setUp(self):
        self.test_name = 'Тест'
        self.new_catalog = ProductCategory.objects.create(name=self.test_name, description='Удобные стулья', is_active=True)

    # проверим факт создания категории товаров
    def test_create(self):
        self.assertTrue(self.new_catalog.is_active)

    def test_create_product(self):
        # создадим 100 продуктов в каталоге по 100 рублей и проверим логику расчета - т.е. 10000 продуктов должно быть
        # на 10 тыс. рублей.
        for i in range(100):
            Product.objects.create(category_id=self.new_catalog.id, name=f'Стул {i}', price=100)
        select_all = Product.objects.all()
        all_sum = select_all.aggregate(Sum('price'))
        print('Создано записей:', select_all.count(), " Итого:", all_sum['price__sum'])
        self.assertTrue(select_all.count() * 100 == all_sum['price__sum'])
