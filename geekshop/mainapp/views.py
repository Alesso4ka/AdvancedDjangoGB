import os.path
import random
import json
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ProductCategory, Product
from basketapp.models import Basket
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.http import JsonResponse


# Create your views here.


''' Главное меню сайта, которое встраивается на каждой странице.
products -- написать так -- products:index сделать обязательно, учитывая то, что использщовался include в urls
'''
main_menu = [
    {'menu_section': 'index', 'main_urls': 'index', 'name': 'Главная'},
    {'menu_section': 'products:index',  'main_urls': 'products', 'name': 'Продукты'},
    {'menu_section': 'contact',  'main_urls': 'contact', 'name': 'Контакты'},
]

# Функции добавленные на 7 уроке


def get_links_menu():
    if settings.LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_category(pk):
    if settings.LOW_CACHE:
        key = f'category_{pk}'
        category = cache.get(key)
        if category is None:
            category = get_object_or_404(ProductCategory, pk=pk)
            cache.set(key, category)
        return category
    else:
        return get_object_or_404(ProductCategory, pk=pk)


def get_products():
    if settings.LOW_CACHE:
        key = 'products'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, \
                         category__is_active=True).select_related('category')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, \
                         category__is_active=True).select_related('category')


def get_product(pk):
    if settings.LOW_CACHE:
        key = f'product_{pk}'
        product = cache.get(key)
        if product is None:
            product = get_object_or_404(Product, pk=pk)
            cache.set(key, product)
        return product
    else:
        return get_object_or_404(Product, pk=pk)


def get_products_orederd_by_price():
    if settings.LOW_CACHE:
        key = 'products_orederd_by_price'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, \
                                  category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True,\
                                 category__is_active=True).order_by('price')


def get_products_in_category_orederd_by_price(pk):
    if settings.LOW_CACHE:
        key = f'products_in_category_orederd_by_price_{pk}'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(category__pk=pk, is_active=True,\
                              category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(category__pk=pk, is_active=True, \
                              category__is_active=True).order_by('price')



def get_basket(user):
    if user.is_authenticated:
        return Basket.objects.filter(user=user).select_related()
    else:
        return []


# Горячее предложение
def get_hot_product():
    # products = Product.objects.all()
    products = get_products()
    return random.sample(list(products), 1)[0]


# Похожие продукты
def get_same_products(hot_product):
    same_products = Product.objects.filter(category=hot_product.category).select_related().exclude(pk=hot_product.pk)[:4]
    return same_products


''' Подгружаем данные о пользователе из json - это только для теста сделано'''


def user_info(user_login):
    with open("users_bd.json", "r", encoding="utf8") as read_file:
        data_user = json.load(read_file)
    return data_user.get(user_login)


user = user_info('user_login')

''' получаем текущую директорию '''
module_dir = os.path.dirname(__file__)


def index(request):
    # products = Product.objects.all()[:4]
    products = get_products()[:4]
    content = {
        'title': 'Главная',
        'main_menu': main_menu,
        'user_info': user,
        'products': products
    }
    return render(request, 'mainapp/index.html', content)


# def products(request, pk=None):
#
#     title = 'продукты'
#     basket = []
#     if request.user.is_authenticated:
#         basket = Basket.objects.filter(user=request.user)
#
#     # Вариант вывода по запросу для категории
#     # 1. Получим все категории
#     links_menu = ProductCategory.objects.all()
#
#     if pk is not None:
#         if pk == 0:
#             products = Product.objects.all().order_by('price')
#             category = {'name': 'все'}
#         else:
#             category = get_object_or_404(ProductCategory, pk=pk)
#             products = Product.objects.filter(category__pk=pk).order_by('price')
#         print(basket[0].product)
#         content = {
#             'title': 'Продукты',
#             'links_menu': links_menu,
#             'main_menu': main_menu,
#             'user_info': user,
#             'products': products,
#             'category': category,
#             'basket': basket,
#         }
#         return render(request, 'mainapp/products_list.html', content)
#
#     # Горячее предложение
#     hot_product = get_hot_product()
#     same_products = get_same_products(hot_product)
#
#     content = {
#         'title': 'Продукты',
#         'links_menu': links_menu,
#         'main_menu': main_menu,
#         'hot_product': hot_product,
#         'same_products': same_products,
#     }
#     return render(request, 'mainapp/products.html', content)


# @cache_page(3600)
def products(request, pk=None, page=1):
    title = 'продукты'
    # links_menu = ProductCategory.objects.filter(is_active=True)
    links_menu = get_links_menu()
    basket = get_basket(request.user)
    if pk is not None:
        if pk == 0:
            category = {
                'pk': 0,
                'name': 'все'
            }
            # products = Product.objects.filter(is_active=True, category__is_active=True).order_by('price')
            products = get_products_orederd_by_price()
        else:
            # category = get_object_or_404(ProductCategory, pk=pk)
            # products = Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by('price')
            category = get_category(pk)
            products = get_products_in_category_orederd_by_price(pk)

        paginator = Paginator(products, 4)
        try:
            products_paginator = paginator.page(page)
        except PageNotAnInteger:
            products_paginator = paginator.page(1)
        except EmptyPage:
            products_paginator = paginator.page(paginator.num_pages)
        content = {
            'title': title,
            'links_menu': links_menu,
            'category': category,
            'products': products_paginator,
            'main_menu': main_menu,
            # 'basket': basket
        }
        return render(request, 'mainapp/products_list.html', content)

    hot_product = get_hot_product()
    same_products = get_same_products(hot_product)

    content = {
        'title': 'Продукты',
        'links_menu': links_menu,
        'main_menu': main_menu,
        'hot_product': hot_product,
        'same_products': same_products,
        }
    return render(request, 'mainapp/products.html', content)


def load_json(path_file):
    with open(path_file, "r", encoding='utf8') as jsonfile:
        data = json.load(jsonfile)
        return data


def contact(request):
    # Доработка под использование кеша
    if settings.LOW_CACHE:
        key = f'location'
        locations = cache.get(key)
        if locations is None:
            locations = load_json(r'mainapp/json/contacts.json')
            cache.set(key, locations)
    else:
        locations = load_json(r'mainapp/json/contacts.json')
    content = {
        'title': 'Контакты',
        'main_menu': main_menu,
        'user_info': user,
        'contacts': locations,
    }
    return render(request, 'mainapp/contact.html', content)


''' Тестовая функция '''

#
# def context(request):
#     # данные, которые будут передаваться в шаблон
#     content = {
#         'title': 'магазин',
#         'header': 'Добро пожаловать на сайт',
#         'username': 'Иван Иванов',
#         'products': [
#             {'name': 'Стулья', 'price': 4535},
#             {'name': 'Диваны', 'price': 1535},
#             {'name': 'Кровати', 'price': 2535},
#         ]
#     }
#     return render(request, 'mainapp/test_context.html', content)


# Страница продукта
@never_cache
def product(request, pk):
    title = 'продукты'
    links_menu = get_links_menu()
    product = get_product(pk)

    content = {
        'title': title,
        'main_menu': main_menu,
        'product': product,
        'basket': get_basket(request.user),
        'links_menu': links_menu,
    }
    return render(request, 'mainapp/product.html', content)


# контроллее, который возвращает стоимость выбранного продукта
# def product_price(request):
#     print('сработал')
#     id_product = request.GET.get("pk", "")
#     product = Product.objects.get(pk=id_product)
#     print(product.price)
#     return HttpResponse(product.price)


def product_price(request):
    # print('сработал')
    id_product = request.GET.get("pk", "")
    product = Product.objects.get(pk=id_product)
    if product:
        return JsonResponse({'price': product.price})
    else:
        return JsonResponse({'price': 0})


def products_ajax(request, pk=None, page=1):
    if request.is_ajax():
        links_menu = get_links_menu()
        print('Cработал', type(pk))
        if pk is not None:
            if pk == 0:
                category = {
                   'pk': 0,
                   'name': 'все'
                }
                print('ПК = 0')
                products = get_products_orederd_by_price()
            else:
                category = get_category(pk)
                products = get_products_in_category_orederd_by_price(pk)

            paginator = Paginator(products, 4)
            try:
                products_paginator = paginator.page(page)
            except PageNotAnInteger:
                products_paginator = paginator.page(1)
            except EmptyPage:
                products_paginator = paginator.page(paginator.num_pages)

            content = {
               'links_menu': links_menu,
               'category': category,
               'products': products_paginator,
            }

            result = render_to_string(
                        'includes/inc_products_list_content.html',
                        context=content,
                        request=request)
            return JsonResponse({'result': result})
