from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from basketapp.models import Basket
from mainapp.models import Product
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from django.views.generic import CreateView, DeleteView
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import never_cache
from django.db.models import F

# метод по условию ДЗ -
# def basket_info(id):
#    bi = Basket.objects.filter(user_id=1)
#    print(bi)

# @login_required
# def basket(request):
#     title = 'корзина'
#     basket_items = Basket.objects.filter(user=request.user). \
#         order_by('product__category')
#
#     content = {
#         'title': title,
#         'basket_items': basket_items,
#     }
#     return render(request, 'basketapp/basket.html', content)


@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class BasketListView(ListView):
    model = Basket
    template_name = 'basketapp/basket.html'


    def get_basket_user_cache(self):
        return Basket.objects.filter(user=self.request.user).select_related().order_by('id')

    def get_queryset(self):
        # return Basket.objects.filter(user=self.request.user).select_related().order_by('product__category')
        return self.get_basket_user_cache

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # basket_items = Basket.objects.filter(user=self.request.user).select_related().order_by('product__category')
        basket_items = self.get_basket_user_cache
        context['basket_items'] = basket_items
        return context


# CreateView
# @login_required
# def basket_add(request, pk):
#     print(request.META['REMOTE_ADDR'])
#     if 'login' in request.META.get('HTTP_REFERER'):
#         return HttpResponseRedirect(reverse('products:product', args=[pk]))
#
#     product = get_object_or_404(Product, pk=pk)
#     basket = Basket.objects.filter(user=request.user, product=product).first()
#
#     if not basket:
#         basket = Basket(user=request.user, product=product)
#     basket.quantity += 1
#     basket.save()
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class BasketAddView(View):

    def get(self, request, pk):
        print(request.user, pk)
        product = get_object_or_404(Product, pk=pk)
        print(product, product.quantity)
        basket = Basket.objects.filter(user=self.request.user, product=product).first()
        if not basket:
            basket = Basket(user=request.user, product=product, quantity=1)
        else:
            basket.quantity = F('quantity') + 1 # доработано с помощью F
        # basket.quantity += 1
        basket.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# @login_required
# def basket_remove(request, pk):
#     basket_record = get_object_or_404(Basket, pk=pk)
#     basket_record.delete()
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class BasketRemoveView(DeleteView):
    model = Basket
    success_url = reverse_lazy('basketapp:view')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

# UpdateView


@login_required
@never_cache
def basket_edit(request, pk, quantity):
    print(is_ajax(request=request))
    print(pk, quantity)
    if is_ajax(request=request):
        quantity = quantity
        new_basket_item = Basket.objects.get(pk=pk)

        if quantity > 0:
            new_basket_item.quantity = quantity
            new_basket_item.save()
        else:
            new_basket_item.delete()

        basket_items = Basket.objects.filter(user=request.user).order_by('id')

        content = {
            'basket_items': basket_items,
        }
        result = render_to_string('basketapp/includes/inc_basket_list.html', content)
        return JsonResponse({'result': result})



