from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),
    url(r'^notice/(?P<id>[0-9]+)/$', views.notice, name='notice'),
    url(r'^order$', views.order, name='order'),
    url(r'^server$', views.server, name='server'),
    url(r'^beauty$', views.beauty, name='beauty'),
    url(r'^addtocart/(?P<id>[0-9]+)/$', views.addtocart, name='addtocart'),
    url(r'^shopcart$', views.shopcart, name='shopcart'),
    url(r'^shopcart/update/(?P<op>up|down|check|uncheck)/$', views.shopcart_update, name='shopcart_update'),
    url(r'^customer$', views.customer, name='customer'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
]
