from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^product/(?P<id>[0-9]+)/$', views.product, name='product'),
    url(r'^server$', views.server, name='server'),
    url(r'^beauty$', views.beauty, name='beauty'),
    url(r'^shopcart$', views.shopcart, name='shopcart'),
    url(r'^customer$', views.customer, name='customer'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
]
