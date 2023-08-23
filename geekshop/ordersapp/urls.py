import ordersapp.views as ordersapp
from django.urls import re_path, path

app_name = "ordersapp"

urlpatterns = [
   path('', ordersapp.OrderList.as_view(), name='orders_list'),
   path('forming/complete/<int:pk>/', ordersapp.order_forming_complete, name='order_forming_complete'),
   path('forming/complete/admin/<int:pk>/', ordersapp.order_forming_complete, name='order_forming_complete_admin'),
   path('create/', ordersapp.OrderItemsCreate.as_view(), name='order_create'),
   path('read/<int:pk>/', ordersapp.OrderRead.as_view(), name='order_read'),
   path('update/<int:pk>/', ordersapp.OrderItemsUpdate.as_view(), name='order_update'),
   path('update/admin/<int:pk>/', ordersapp.OrderItemsUpdate.as_view(), name='order_update_admin'),
   path('delete/<int:pk>/', ordersapp.OrderDelete.as_view(), name='order_delete'),
   path('delete/admin/<int:pk>/', ordersapp.OrderDeleteAdmin.as_view(), name='order_delete_admin'),
   path('product/<int:pk>/price/', ordersapp.get_product_price),
]


# Вариант из методички

# urlpatterns = [
#    re_path(r'^$', ordersapp.OrderList.as_view(), name='orders_list'),
#    re_path(r'^forming/complete/(?P<pk>\d+)/$',
#            ordersapp.order_forming_complete, name='order_forming_complete'),
#    re_path(r'^create/$', ordersapp.OrderItemsCreate.as_view(),
#            name='order_create'),
#    re_path(r'^read/(?P<pk>\d+)/$', ordersapp.OrderRead.as_view(),
#            name='order_read'),
#    re_path(r'^update/(?P<pk>\d+)/$', ordersapp.OrderItemsUpdate.as_view(),
#            name='order_update'),
#    re_path(r'^delete/(?P<pk>\d+)/$', ordersapp.OrderDelete.as_view(),
#            name='order_delete'),
# ]