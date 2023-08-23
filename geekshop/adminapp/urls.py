import adminapp.views as adminapp
from django.urls import path

app_name = 'adminapp'


'''
    работа с объектами пользователей;
    работа с объектами категорий;
    работа с объектами продуктов.
 
'''
# path('users/read/', adminapp.users, name='users'),
urlpatterns = [
    # path('users/create/', adminapp.user_create, name='user_create'),
    path('users/create/', adminapp.UserCreate.as_view(), name='user_create'),
    path('users/read/', adminapp.UsersListView.as_view(), name='users'),
    # path('users/update/<int:pk>/', adminapp.user_update, name='user_update'),
    path('users/update/<int:pk>/', adminapp.UserUpdate.as_view(), name='user_update'),
    # path('users/delete/<int:pk>/', adminapp.user_delete, name='user_delete'),
    path('users/delete/<int:pk>/', adminapp.UserDelete.as_view(), name='user_delete'),
    path('categories/create/', adminapp.ProductCategoryCreateView.as_view(), name='category_create'),
    #path('categories/read/', adminapp.categories, name='categories'),
    path('categories/read/', adminapp.CategoriesList.as_view(), name='categories'),
    path('categories/update/<int:pk>/', adminapp.ProductCategoryUpdateView.as_view(), name='category_update'),
    path('categories/delete/<int:pk>/', adminapp.ProductCategoryDeleteView.as_view(), name='category_delete'),

    # path('products/create/category/<int:pk>/', adminapp.product_create, name='product_create'),
    path('products/create/category/<int:pk>/', adminapp.ProductCreateView.as_view(), name='product_create'),
    # path('products/read/category/<int:pk>/', adminapp.products, name='products'),  # выводит список продуктов в категории
    path('products/read/category/<int:pk>/', adminapp.ProductsList.as_view(), name='products'),  # выводит список продуктов в категории
    #path('products/read/category/<int:pk>/page/<int:page>/', adminapp.products, name='page'),  # пагинатор
    path('products/read/category/<int:pk>/page/<int:page>/', adminapp.ProductsList.as_view(), name='page'),  # пагинатор
    path('products/read/<int:pk>/', adminapp.ProductDetailView.as_view(), name='product_read'),  # выводит страницу выбранного продукта
    # path('products/update/<int:pk>/', adminapp.product_update, name='product_update'),
    path('products/update/<int:pk>/', adminapp.ProductUpdate.as_view(), name='product_update'),
    #path('products/delete/<int:pk>/', adminapp.product_delete, name='product_delete'),
    path('products/delete/<int:pk>/', adminapp.ProductDelete.as_view(), name='product_delete'),
    path('adminajax/', adminapp.admin_ajax, name="admin_ajax"),

    path('orders/', adminapp.OrderList.as_view(), name='orders'),
    path('order/<int:pk>', adminapp.OrderStatus, name='order_status'),
    path('read/<int:pk>/', adminapp.OrderRead.as_view(), name="order_read"),
    path('userinfo/<int:pk>/', adminapp.UserInfo.as_view(), name='user_info'),
    path('userinfo_def/<int:pk>/', adminapp.user_info_def, name='user_info_def'),
]
