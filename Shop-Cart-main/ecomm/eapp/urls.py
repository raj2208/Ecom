#from django.contrib import admin
from django.urls import path,include
from eapp import views
from django.conf.urls.static import static 
from django.conf import settings
urlpatterns = [
    path('',views.index,name="index"),
    path('contact',views.contact,name="contact"),
    path('about',views.about,name="about"),
    path('add/<pid>',views.addCart,name="addCart"),
    path('viewproduct/<pid>',views.viewproduct, name="viewproduct"),
    path('dele/<pid>',views.delCart,name="delCart"),
    path('cart',views.cart,name="cart"),
    path('checkout',views.checkout,name="checkout"),
    path('success/<pid>/<oid>/<sgn>',views.success,name="success"),
    path('failed/<oid>',views.failed,name="failed"),
    path('orders',views.orders,name="orders"),
    path('cancelord/<oid>',views.cancelOrder,name="cancelOrder"),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
