from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from authapp.models import ShopUser
from mainapp.models import ProductCategory, Product
from ordersapp.models import Order, OrderItem
from authapp.forms import ShopUserRegisterForm
from adminapp.forms import ShopUserEditForm
from adminapp.forms import ShopUserAdminEditForm
from adminapp.forms import ProductCategoryEditForm
from adminapp.forms import ProductEditForm
from adminapp.forms import OrderEditStatus
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import connection
from django.db.models import F

# Create your views here.


# Пользователи


# @user_passes_test(lambda u: u.is_superuser)
# def users(request):
#     title = 'админка/пользователи'
#     users_list = ShopUser.objects.all().order_by('-is_active', '-is_superuser', '-is_staff', 'username')
#     content = {
#         'title': title,
#         'objects': users_list
#     }
#     return render(request, 'adminapp/users.html', content)
@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UsersListView(ListView):
    model = ShopUser
    queryset = ShopUser.objects.all().order_by('-is_active', '-is_superuser', '-is_staff', 'username')
    template_name = 'adminapp/users.html'

    # Или можно было так применить декоратор
    # @method_decorator(user_passes_test(lambda u: u.is_superuser))
    # def dispatch(self, *args, **kwargs):
    #     print('сработал')
    #     return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи'
        return context


# @login_required
# def user_create(request):
#     title = 'пользователи / создание'
#     if request.method == 'POST':
#         user_form = ShopUserRegisterForm(request.POST, request.FILES)
#         if user_form.is_valid():
#             user_form.save()
#             return HttpResponseRedirect(reverse('admin:users'))
#     else:
#         user_form = ShopUserRegisterForm()
#     content = {'title': title, 'update_form': user_form}
#     return render(request, 'adminapp/user_update.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserCreate(CreateView):
    model = ShopUser
    success_url = reverse_lazy('admin:users')
    # fields = '__all__'
    template_name = 'adminapp/user_update.html'
    form_class = ShopUserAdminEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового пользователя'
        return context


# @login_required
# def user_update(request, pk):
#     title = 'пользователи / редактирование'
#     edit_user = get_object_or_404(ShopUser, pk=pk)
#     if request.method == 'POST':
#         edit_form = ShopUserEditForm(request.POST, request.FILES, instance=edit_user)
#         if edit_form.is_valid():
#             edit_form.save()
#             return HttpResponseRedirect(reverse('admin:user_update', args=[edit_user.pk]))
#     else:
#         edit_form = ShopUserAdminEditForm(instance=edit_user)
#     content = {'title': title, 'update_form': edit_form}
#     return render(request, 'adminapp/user_update.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserUpdate(UpdateView):
    model = ShopUser
    success_url = reverse_lazy('admin:users')
    # fields = '__all__'
    template_name = 'adminapp/user_update.html'
    form_class = ShopUserAdminEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        return context


# @login_required
# def user_delete(request, pk):
#     title = 'пользователи / удаление'
#     user = get_object_or_404(ShopUser, pk=pk)
#     if request.method == 'POST':
#         # user.delete
#         # делаем неактивынм вместо удаления
#         user.is_active = False
#         user.save()
#         return HttpResponseRedirect(reverse('admin:users'))
#     content = {
#         'title': title,
#         'user_to_delete': user,
#     }
#     return render(request, 'adminapp/user_delete.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserDelete(DeleteView):
    model = ShopUser
    template_name = 'adminapp/user_delete.html'
    success_url = reverse_lazy('admin:users')

    def delete(self, request, *args, **kwarg):
        self.object = self.get_object()
        if not self.object .is_active:
            self.object.delete()
        else:
            self.object.is_active = False
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UserDelete, self).get_context_data(**kwargs)
        del_user = self.get_object()
        msg_1 = f'Данная операция сделает пользователя {del_user.username} неактивным и не удалит информацию о нем из базы.' \
                'Повторный вызов операции приведет к его полному удалению.'

        msg_2 = f"Данная операция полностью удалит пользователя {del_user.username} из базы. Продолжить?"
        context['msg_warning'] = msg_1 if del_user.is_active else msg_2
        return context


# Категории

# @login_required
# def categories(request):
#     title = 'админка/категории'
#     categories_list = ProductCategory.objects.all()
#     content = {
#         'title': title,
#         'objects': categories_list
#     }
#     return render(request, 'adminapp/categories.html', content)
@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class CategoriesList(ListView):
    model = ProductCategory
    template_name = 'adminapp/categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Категории'
        return context


# def category_create(request):
#     title = 'категории / создание'
#     if request.method == 'POST':
#         category_form = ProductCategoryEditForm(request.POST)
#         if category_form.is_valid():
#             category_form.save()
#             return HttpResponseRedirect(reverse('admin:categories'))
#     else:
#         category_form = ProductCategoryEditForm()
#     content = {'title': title, 'update_form': category_form}
#     return render(request, 'adminapp/category_update.html', content)


@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ProductCategoryCreateView(CreateView):
    model = ProductCategory
    template_name = 'adminapp/category_update.html'
    success_url = reverse_lazy('admin:categories')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание категории'
        return context

# def category_update(request, pk):
#     title = 'категории / обновление'
#     edit_category = get_object_or_404(ProductCategory, pk=pk)
#     if request.method == 'POST':
#         edit_category_form = ProductCategoryEditForm(request.POST, instance=edit_category)
#         if edit_category_form.is_valid():
#             edit_category_form.save()
#             return HttpResponseRedirect(reverse('admin:category_update', args=[edit_category.pk]))
#     else:
#         edit_category_form = ProductCategoryEditForm(instance=edit_category)
#     content = {'title': title, 'update_form': edit_category_form}
#     return render(request, 'adminapp/category_update.html', content)


@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ProductCategoryUpdateView(UpdateView):
    model = ProductCategory
    template_name = 'adminapp/category_update.html'
    success_url = reverse_lazy('admin:categories')
    # fields = '__all__'
    form_class = ProductCategoryEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'категории / редактирование'
        return context

    def form_valid(self, form):
        if 'discount' in form.cleaned_data:
            discount = form.cleaned_data['discount']
            if discount:
                self.object.product_set. \
                    update(price=F('price') * (1 - discount / 100))
                db_profile_by_type(self.__class__, 'UPDATE', connection.queries)
        return super().form_valid(form)


# def category_delete(request, pk):
#     title = 'категории / удаление'
#     delete_category = get_object_or_404(ProductCategory, pk=pk)
#     if request.method == 'POST':
#         delete_category.is_active = False  # это поле is_active в модели ProductCategory
#         delete_category.save()
#         return HttpResponseRedirect(reverse('admin:categories'))
#     content = {
#         'title': title,
#         'delete_category': delete_category
#     }
#     return render(request, 'adminapp/category_delete.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ProductCategoryDeleteView(DeleteView):
    model = ProductCategory
    template_name = 'adminapp/category_delete.html'
    success_url = reverse_lazy('admin:categories')

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryDeleteView, self).get_context_data(**kwargs)
        if self.object.is_active:
            context['msg'] = 'Выбранная категория будет неактивной.\n Для полного удаления повторите операцию.'
        else:
            context['msg'] = 'Выбранная категория будет удалена полностью . Вы уверены?'
        return context

    def delete(self, request, *args, **kwarg):
        self.object = self.get_object()
        if self.object.is_active:
            self.object.is_active = False
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


# Продукты
# def products(request, pk=None, page=1):
#     title = 'админка/продукт'
#
#     category = get_object_or_404(ProductCategory, pk=pk)
#     products_list = Product.objects.filter(category__pk=pk).order_by('name')
#
#     paginator = Paginator(products_list, 3)
#     try:
#         products_paginator = paginator.page(page)
#     except PageNotAnInteger:
#         products_paginator = paginator.page(1)
#     except EmptyPage:
#         products_paginator = paginator.page(paginator.num_pages)
#
#     content = {
#         'title': title,
#         'category': category,
#         'objects': products_paginator,
#     }
#     return render(request, 'adminapp/products.html', content)

# CBV c пагинацией - вывод в отдельный шаблон с окончанием CBV
@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ProductsList(ListView):
    model = Product
    paginate_by = 3
    template_name = 'adminapp/products_cbv.html'

    def get_queryset(self):
        print(self.request)
        return Product.objects.filter(category__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(ProductsList, self).get_context_data(**kwargs)
        context['cat_id'] = self.kwargs['pk']
        return context


# def product_create(request, pk):
#     title = 'продукт/создание'
#     category = get_object_or_404(ProductCategory, pk=pk)
#
#     if request.method == 'POST':
#         product_form = ProductEditForm(request.POST, request.FILES)
#         if product_form.is_valid():
#             product_form.save()
#             return HttpResponseRedirect(reverse('admin:products', args=[pk]))
#     else:
#         product_form = ProductEditForm(initial={'category': category})
#
#     content = {'title': title,
#                'create_form': product_form,
#                'category': category
#                }
#     return render(request, 'adminapp/create_product.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    template_name = 'adminapp/create_product.html'
    # success_url = reverse_lazy('adminapp:products', args=['11'])
    # fields = '__all__'
    form_class = ProductEditForm

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        category = ProductCategory.objects.filter(id=self.kwargs['pk'])
        context['title'] = 'Создание продукта'
        context['category'] = category
        return context

    def get_success_url(self, **kwargs):
        data = super(ProductCreateView, self).get_context_data()
        print(data)
        return reverse('adminapp:products', args=[self.kwargs['pk']])


# def product_read(request, pk):
#     title = 'продукт / показать'
#     product_show = get_object_or_404(Product, pk=pk)
#     category = get_object_or_404(ProductCategory, pk=product_show.category_id)
#     content = {
#         'title': title,
#         'product_show': product_show,
#         'category': category,
#     }
#     return render(request, 'adminapp/product_show.html', content)
@method_decorator(never_cache, name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    template_name = 'adminapp/product_show.html'


# def product_update(request, pk):
#     title = 'продукт/редактирование'
#     edit_product = get_object_or_404(Product, pk=pk)
#     if request.method == 'POST':
#         edit_form = ProductEditForm(request.POST, request.FILES, instance=edit_product)
#         if edit_form.is_valid():
#             edit_form.save()
#             return HttpResponseRedirect(reverse('admin:product_update', args=[edit_product.pk]))
#     else:
#         edit_form = ProductEditForm(instance=edit_product)
#
#     content = {'title': title,
#                'update_form': edit_form,
#                'category': edit_product.category
#                }
#     return render(request, 'adminapp/product_update.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProductUpdate(UpdateView):
    model = Product
    template_name = 'adminapp/create_product.html'
    # success_url = reverse_lazy('adminapp:products', args=['9'])
    # fields = '__all__'
    form_class = ProductEditForm

    def get_context_data(self, **kwargs):
        context = super(ProductUpdate, self).get_context_data(**kwargs)
        category = ProductCategory.objects.filter(id=context.get('product').category.id)
        context['title'] = 'Редактирование продукта'
        context['category'] = category
        return context

    def get_success_url(self):
        # data = super(ProductUpdate, self).get_context_data()
        data = self.get_object()
        return reverse('adminapp:products', args=[data.category.id])

# def product_delete(request, pk):
#     title = 'продукт / удаление'
#     delete_product = get_object_or_404(Product, pk=pk)
#     if request.method == 'POST':
#         # в данном случае удалим продукт полностью
#         delete_product.delete()
#         # print('удален')
#         return HttpResponseRedirect(reverse('admin:products', args=[delete_product.category_id]))
#     content = {
#         'title': title,
#         'delete_product': delete_product
#     }
#     return render(request, 'adminapp/product_delete.html', content)

@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProductDelete(DeleteView):
    model = Product
    template_name = 'adminapp/product_delete.html'
    # success_url = reverse_lazy('admin:categories')

    def get_context_data(self, **kwargs):
        context = super(ProductDelete, self).get_context_data(**kwargs)
        # self.object = self.get_object()
        if self.object.is_active:
            context['msg'] = 'Продукт не будет удален из базы данных.\n Для полного удаления повторите операцию.'
        else:
            context['msg'] = 'Продукт будет полностью удален из базы данных. Вы уверены?'
        return context

    def delete(self, request, *args, **kwarg):
        self.object = self.get_object()
        if self.object.is_active == False:
            self.object.delete()
        else:
            self.object.is_active = False
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        data = super(ProductDelete, self).get_context_data()
        return reverse('adminapp:products', args=[data.get('product').category.id])


def admin_ajax(request):
    сontent = {}
    return render(request, 'adminapp/admin_ajax.html', сontent)


@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
class OrderList(ListView):
    model = Order
    template_name = 'adminapp/order_list.html'

    # @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        print('сработал')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Order.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Заказы по всем пользователям'
        return context


# Можно посмотреть информацию о покупателе
class UserInfo(DetailView):
    model = ShopUser
    fields = []
    template_name = 'adminapp/user_info_cbv.html'


def user_info_def(request, pk):
    user = ShopUser.objects.get(id=pk)
    title = user.id
    сontent = {
        'title': title,
        'userinfo': user,
    }
    return render(request, 'adminapp/user_info.html', сontent)


class OrderRead(DetailView):
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderRead, self).get_context_data(**kwargs)
        context['title'] = 'заказ/просмотр'
        context['url_return'] = 'adminapp'
        return context


def OrderStatus(request, pk):
    order = get_object_or_404(Order, pk=pk)
    title = f'Изменение статуса заказа № {order.id}'
    print(order.id)
    if request.method == 'POST':
        edit_form = OrderEditStatus(request.POST, instance=order)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('admin:orders'))
    else:
        edit_form = OrderEditStatus(instance=order)

    content = {'title': title,
               'order_info': order,
               'status_form': edit_form,
               }
    return render(request, 'adminapp/edit_status.html', content)


# Обновление атрибутов при помощи update()
def db_profile_by_type(prefix, type, queries):
    update_queries = list(filter(lambda x: type in x['sql'], queries))
    print(f'db_profile {type} for {prefix}:')
    [print(query['sql']) for query in update_queries]


@receiver(pre_save, sender=ProductCategory)
def product_is_active_update_productcategory_save(sender, instance, **kwargs):
    if instance.pk:
        if instance.is_active:
            instance.product_set.update(is_active=True)
        else:
            instance.product_set.update(is_active=False)
        db_profile_by_type(sender, 'UPDATE', connection.queries)
