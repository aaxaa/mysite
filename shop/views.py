from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from shop.models import Notice, Product, Setting


def main(request):
    notice_list = Notice.objects.filter(type='global', status=1)
    recommend_products = Product.objects.filter(recommend=1)
    return render(request, 'home.html', {
        'notice_list': notice_list,
        'recommend_products': recommend_products,
    })


def product(request, id=0):
    product = Product.objects.get(pk=id)

    product_items = []
    for item in product.items.all():
        product_items.append(item)

    return render(request, 'product/view.html', {
        'product': product,
        'product_items': product_items
    })


def server(request):
    notice_list = Notice.objects.filter(type='news', status=1)

    tel = Setting.objects.get(key='tel')
    traffic = Setting.objects.get(key='traffic')
    address = Setting.objects.get(key='address')

    return render(request, 'server.html', {
        'notice_list': notice_list,
        'tel': tel,
        'traffic': traffic,
        'address': address,
    })


def beauty(request):
    return render(request, 'beauty.html')


def shopcart(request):
    return render(request, 'shopcart.html')


def customer(request):
    return HttpResponseRedirect(reverse('register'))
    #return render(request, 'customer.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')
