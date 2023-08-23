from django.test import TestCase
from .models import Basket
from mainapp.models import Product, ProductCategory
from authapp.models import ShopUser
from random import randint
# Create your tests here.


class BasketTests(TestCase):

    def setUp(self):
        # Создадим категорию и товары в категории
        self.category = ProductCategory.objects.create(name="Стулья")
        self.products = Product.objects.bulk_create(
            [
                Product(name='Стул 1', price=100, quantity=10, category_id=self.category.id),
                Product(name='Стул 2', price=150, quantity=25, category_id=self.category.id),
                Product(name='Стул 3', price=200, quantity=30, category_id=self.category.id),
            ]
        )
        self.user = ShopUser.objects.create(username="Петя", age=18)

        self.users_basket = Basket
        # Создадим корзину c продуктами для пользователя и добавим рандомно 1-3 товара в количество
        for product in self.products:
            self.users_basket.objects.create(user_id=self.user.id, product_id=product.id, quantity=randint(1, 3))

    def test_prod_in_basket(self):
        print('Все созданные продукты:', self.products)
        print(f'Товары в корзине пользователя {self.user.username}:', self.users_basket.objects.all())
        print('Список:')
        products_in_user_basket = self.users_basket.objects.filter(user_id=self.user.id)
        sum_in_basket = 0  # тут храним итог
        for item_in_basket in products_in_user_basket:
            print(item_in_basket.product.price)
            sum_in_basket += item_in_basket.product.price * item_in_basket.quantity
            print(
                item_in_basket.product.id,
                item_in_basket.product.name,
                item_in_basket.product.price,
                item_in_basket.quantity,
                item_in_basket.product.price * item_in_basket.quantity
            )
        method_total_cost = products_in_user_basket[0].total_cost_for_test
        print(f"Сумма, полученная запросом к БД: {method_total_cost} "
              f"Расчетное значение: {sum_in_basket}")
        # если все корректно, то не будет ошибки
        self.assertEqual(sum_in_basket, method_total_cost)
