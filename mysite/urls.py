from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.index),
    path('', views.index),
    # path('actionUrl/', views.clc,name='actionUrl')
    path('login', views.login),
    path('signup', views.signup),
    path('create_shop', views.create_shop),
    # path('seller_dashbaord',views.seller_dashbaord),
    path('add_product_0', views.add_product_btn),
    path('edit_product_0', views.edit_product_btn),
    path('add_product', views.add_product),
    # path('seller_dashbaord_0',views.seller_dashbaord_0)
    path('edit_product', views.edit_product),
    path('after_edit_product', views.after_edit_product),

    path('del_product_0', views.del_product_btn),
    path('after_del_product', views.after_del_product),
    path('select_shop', views.select_shop),
    path('buyer_dashboard', views.buyer_dashboard),
    path('cart', views.cart)











]
