from django.db import models
from django.conf import settings
from mainapp.models import Product
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from basketapp.models import Basket
from django.utils.functional import cached_property
from django.db.models import F

class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'

    ORDER_STATUS_CHOICES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлен в обработку'),
        (PAID, 'оплачен'),
        (PROCEEDED, 'обрабатывается'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='создан', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='обновлен', auto_now=True)
    status = models.CharField(verbose_name='статус',
                              max_length=3,
                              choices=ORDER_STATUS_CHOICES,
                              default=FORMING)
    is_active = models.BooleanField(verbose_name='активен', db_index=True, default=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return 'Текущий заказ: {}'.format(self.id)

    # def get_total_quantity(self):
    #     items = self.orderitems.select_related()
    #     return sum(list(map(lambda x: x.quantity, items)))

    @cached_property
    def get_items_orders_cached(self):
        return self.orderitems.select_related()

    def get_product_type_quantity(self):
        # items = self.orderitems.select_related()
        # Добавил кеширование
        items = self.get_items_orders_cached;
        return len(items)

    def get_total_cost(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity * x.product.price, items)))

    # Создали вместо методов get_total_quantity и get_total_cost
    def get_summary(self):
        items = self.orderitems.select_related()
        # Добавил кеширование
        # items = self.get_items_orders_cached;
        return {
            'total_cost': sum(list(map(lambda x: x.quantity * x.product.price, items))),
            'total_quantity': sum(list(map(lambda x: x.quantity, items)))
        }

    # переопределяем метод, удаляющий объект
    def delete(self):
        for item in self.orderitems.select_related():
            item.product.quantity += item.quantity
            item.product.save()

        self.is_active = False
        self.save()


class OrderItemQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for object in self:
            object.product.quantity += object.quantity
            object.product.save()
        super(OrderItemQuerySet, self).delete(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name="orderitems",
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                verbose_name='продукт',
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество',
                                           default=0)
    objects = OrderItemQuerySet.as_manager()

    def get_product_cost(self):
        return self.product.price * self.quantity

    def delete(self):
        self.product.quantity += self.quantity
        self.product.save()
        super(self.__class__, self).delete()


@receiver(pre_save, sender=OrderItem)
@receiver(pre_save, sender=Basket)
def product_quantity_update_save(sender, update_fields, instance, **kwargs):
    if update_fields == 'quantity' or 'product':
        if instance.pk:
            # print(instance.product.quantity)
            # instance.product.quantity -= instance.quantity - sender.objects.get(pk=instance.pk).quantity
            instance.product.quantity = F('quantity') - 1  # доработано с помощью F
        else:
            # instance.product.quantity -= instance.quantity
            instance.product.quantity = F('quantity') - 1
        instance.product.save()


@receiver(pre_delete, sender=OrderItem)
@receiver(pre_delete, sender=Basket)
def product_quantity_update_delete(sender, instance, **kwargs):
    # instance.product.quantity += instance.quantity
    instance.product.quantity = F('quantity') + 1
    instance.product.save()
