# coding:utf8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from shop.models import Notice, Product, Setting, Customer


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
    if 'customer' in request.session:
        customer = request.session.get('customer')
        return render(request, 'customer.html', {
            'customer': customer
        })
    else:
        return redirect('/login?forward=customer')
    #return render(request, 'customer.html')


def login(request):
    if request.method == 'POST':
        login_account = request.POST['login_account']
        password = request.POST['password']
        forward = request.POST['forward']

        data = {}
        data['forward'] = forward
        try:
            
            if login_account.isdigit() and len(login_account)==11:
                q = Q(phone=login_account)

            else:
                q = Q(username=login_account)

            customer = Customer.objects.get(q)
            if password != '' and customer.check_password(password):
                request.session['customer'] = {
                    'id': customer.id,
                    'username': customer.username,
                    'phone': customer.phone,
                    'realname': customer.realname,
                    'avatar': str(customer.avatar),
                    'point': customer.point
                }

                return redirect(reverse('customer'))

            else:
                data['status'] = 'errors'
                data['message'] = u'帐号不存在或者密码不对'
                data['login_account'] = request.POST['login_account']

        except ObjectDoesNotExist:
            data['status'] = 'errors'
            data['message'] = u'帐号不存在或者密码不对'
            data['login_account'] = request.POST['login_account']


        return render(request, 'login.html', data)
    else:
        return render(request, 'login.html', {'status':None, 'forward':request.GET['forward']})


def register(request):

    return render(request, 'register.html')
