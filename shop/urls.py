from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),
    url(r'^notice/(?P<id>[0-9]+)/$', views.notice, name='notice'),
    url(r'^order/$', views.order, name='order'),
    url(r'^order/operation/$', views.order, name='order_operation'),
    url(r'^server/$', views.server, name='server'),
    url(r'^beauty/$', views.beauty, name='beauty'),
    url(r'^ask/$', views.ask, name='ask'),
    url(r'^addtocart/(?P<id>[0-9]+)/$', views.addtocart, name='addtocart'),
    url(r'^shopcart/$', views.shopcart, name='shopcart'),
    url(r'^shopcart/update/(?P<op>up|down|check|uncheck|check_all|uncheck_all|delete)/$', views.shopcart_update, name='shopcart_update'),
    url(r'^shopcart/order/$', views.shopcart_order, name='shopcart_order'),
    url(r'^shopcart/order/checkout/$', views.shopcart_order_checkout, name='shopcart_order_checkout'),
    url(r'^purchase/$', views.purchase, name='purchase'),
    url(r'^customer/$', views.customer, name='customer'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^repw/$', views.repw, name='repw'),
    url(r'^code/(?P<code>[0-9]+)/$', views.code, name='code'),
    url(r'^verify/$', views.verify, name='verify'),
    url(r'^wx_verify/$', views.wx_verify, name='wx_verify'),
    url(r'^wx_callback/$', views.wx_callback, name='wx_callback'),
    url(r'^wxpay_test/$', views.wxpay_test, name='wxpay_test'),
    url(r'^wxpay_notify/$', views.wxpay_notify, name='wxpay_notify'),
]
