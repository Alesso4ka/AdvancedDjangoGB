from django.db import models
from django.conf import settings
from mainapp.models import Product
from django.utils.functional import cached_property

class BasketQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for object in self:
            object.product.quantity += object.quantity
            object.product.save()
            super(BasketQuerySet, self).delete(*args, **kwargs)


class Basket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='basket')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)
    add_datetime = models.DateTimeField(verbose_name='время', auto_now_add=True)
    objects = BasketQuerySet.as_manager()  # Метод класса, который возвращает экземпляр Manager с копией методов QuerySet

    def __str__(self):
        return f' user_id: {self.user_id}, {self.product.name} - {self.quantity}'

    @property
    def product_cost(self):
        "return cost of all products this type"
        return self.product.price * self.quantity

    @cached_property
    def get_items_cached(self):
        return self.user.basket.select_related()

    def total_quantity(self):
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.quantity, _items)))

    def total_cost(self):
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.product_cost, _items)))

    # Добавлен метод, объединящий total_cost и total_quantity, чтобы протестировать  with в шаблоне
    def basket_info(self):
        _items = self.get_items_cached
        basket_info = {
            'total_quantity': sum(list(map(lambda x: x.quantity, _items))),
            'total_cost': sum(list(map(lambda x: x.product_cost, _items))),
        }
        return basket_info
    # @property
    # def total_quantity(self):
    #     "return total quantity for user"
    #     _items = Basket.objects.filter(user=self.user)
    #     _totalquantity = sum(list(map(lambda x: x.quantity, _items)))
    #     return _totalquantity
    #

    # Метод используется в тесте
    @property
    def total_cost_for_test(self):
        "return total cost for user"
        _items = Basket.objects.filter(user=self.user)
        _totalcost = sum(list(map(lambda x: x.product_cost, _items)))
        return _totalcost


    @classmethod
    def get_items(self, user):
        # print(Basket.objects.filter(user=user))
        return Basket.objects.filter(user=user)


    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.product.quantity -= self.quantity - self.__class__.get_item(self.pk).quantity
    #     else:
    #         self.product.quantity -= self.quantity
    #     self.product.save()
    #     super(self.__class__, self).save(*args, **kwargs)

    # def delete(self):
    #     self.product.quantity += self.quantity
    #     self.product.save()
    #     super(self.__class__, self).delete()  # это обеспечивает доступ к унаследованному методу
