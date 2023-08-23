from django.http import JsonResponse
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import transaction

from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from basketapp.models import Basket
from mainapp.models import Product
from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderItemForm
from django.views.decorators.cache import never_cache


@method_decorator(never_cache, name='dispatch')
class OrderList(ListView):
    model = Order

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@method_decorator(never_cache, name='dispatch')
class OrderItemsCreate(CreateView):
    model = Order
    fields = []
    success_url = reverse_lazy('ordersapp:orders_list')

    def get_context_data(self, **kwargs):
        data = super(OrderItemsCreate, self).get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        from_admin = 'admin' in str(self.request)
        if from_admin:
            self.success_url = reverse_lazy('adminapp:orders')

        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            basket_items = Basket.get_items(self.request.user)
            if len(basket_items):
                OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=len(basket_items))
                formset = OrderFormSet()

                for num, form in enumerate(formset.forms):
                    form.initial['product'] = basket_items[num].product
                    form.initial['quantity'] = basket_items[num].quantity
                    form.initial['price'] = basket_items[num].product.price
                basket_items.delete()
            else:
                formset = OrderFormSet()

        data['orderitems'] = formset
        # добавил в контекст метку, которая позволяет вернуться назад в админку, если из нее пришли в обновление заказа
        data['url_return'] = 'adminapp' if from_admin else ''
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        # удаляем пустой заказ
        if self.object.get_total_cost() == 0:
            self.object.delete()

        return super(OrderItemsCreate, self).form_valid(form)


@method_decorator(never_cache, name='dispatch')
class OrderItemsUpdate(UpdateView):
    model = Order
    fields = []
    success_url = reverse_lazy('ordersapp:orders_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)
        # если перешли из администратиной части, то и вернемся туда после сохранения
        from_admin = 'admin' in str(self.request)
        if from_admin:
            self.success_url = reverse_lazy('adminapp:orders')

        if self.request.POST:
            formset = OrderFormSet(self.request.POST, instance=self.object)
        else:
            queryset = self.object.orderitems.select_related()
            formset = OrderFormSet(instance=self.object, queryset=queryset)
            for form in formset.forms:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price
        data['orderitems'] = formset

        # basket_items = Basket.get_items(self.request.user)
        # if len(basket_items):
        #     OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=len(basket_items))
        #     formset = OrderFormSet(instance=self.object)
        #     basket_items.delete()
        # else:
        #     formset = OrderFormSet(instance=self.object)

        # data['orderitems'] = formset
        # добавил в контекст метку, которая позволяет вернуться назад в админку, если из нее пришли в обновление заказа

        data['url_return'] = 'adminapp' if from_admin else ''
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        # удаляем пустой заказ
        if self.object.get_summary().get('total_cost') == 0:
            self.object.delete()
        return super(OrderItemsUpdate, self).form_valid(form)


class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('ordersapp:orders_list')


class OrderDeleteAdmin(DeleteView):
    model = Order
    success_url = reverse_lazy('adminapp:orders')


class OrderRead(DetailView):
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderRead, self).get_context_data(**kwargs)
        context['title'] = 'заказ/просмотр'
        return context


def order_forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()
    # если из админки совершили покупку, то и вернемся к заказам в админку
    revers_url = 'adminapp:orders' if 'admin' in str(request) else 'ordersapp:orders_list'
    return HttpResponseRedirect(reverse(revers_url))


# вариант из методички - 2 рабочий вариант
def get_product_price(request, pk):
    product = Product.objects.filter(pk=int(pk)).first()
    if product:
        return JsonResponse({'price': product.price})
    else:
        return JsonResponse({'price': 0})
