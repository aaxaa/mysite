# coding:utf8
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from shop.models import Notice, Product, Setting, Customer, Category, Shopcart, ShopcartProduct

from decimal import *
import json


def main(request):
    notice_list = Notice.objects.filter(type='global', status=1)
    recommend_products = Product.objects.filter(recommend=1)

    category_list = Category.objects.filter(parent=None)
    product_list = {}
    for category in category_list:
        category.product_list = Product.objects.filter(category=category)

    return render(request, 'home.html', {
        'notice_list': notice_list,
        'recommend_products': recommend_products,
        'category_list':category_list
    })


def product(request, id=0):
    product = Product.objects.get(pk=id)

    product_items = []
    for item in product.items.all():
        product_items.append(item)

    return render(request, 'product.html', {
        'product': product,
        'product_items': product_items
    })

def notice(request, id=0):
    try:
        notice = Notice.objects.get(pk=id)
    except:
        notice = None
    return render(request, 'notice.html', {"notice": notice})

def order(request):
    return render(request, 'order.html')

def server(request):
    notice_list = Notice.objects.filter(type='news', status=1)
    try:
        tel = Setting.objects.get(key='tel')
        traffic = Setting.objects.get(key='traffic')
        address = Setting.objects.get(key='address')
    except:
        tel = ''
        traffic = ''
        address = ''

    return render(request, 'server.html', {
        'notice_list': notice_list,
        'tel': tel,
        'traffic': traffic,
        'address': address,
    })


def beauty(request):
    return render(request, 'beauty.html')

def addtocart(request, id):
    data = {}

    try:
        product = Product.objects.get(pk=id)
        #如果是已登录的用户，则读出数据库购物车
        if 'customer' in request.session:
            customer = Customer.objects.get(pk=request.session['customer'].get('id'))
            #获取购物车信息，不存在则创建新购物车
            try:
                shopcart = Shopcart.objects.get(customer=customer)

            except ObjectDoesNotExist:               
                shopcart = Shopcart.objects.create(customer=customer)
                shopcart.save()
            #添加产品到购物车
            shopcart_product = ShopcartProduct(product=product, shopcart=shopcart, count=1, price=product.price)
            shopcart_product.save()

            #计算总价
            shopcart.total_price += product.price
            shopcart.save()

            data['status'] = 'ok'
        #非登录用户，把商品添加到session中
        else:
            #初始化购物车信息
            if 'shopcart' in request.session:
                shopcart = request.session['shopcart']
                
            else:
                shopcart = {}
                shopcart['products'] = []

            #保存到session内
            shopcart.get('products').append(product.id)
            request.session['shopcart'] = shopcart
            
            data['status'] = 'ok'

    except ObjectDoesNotExist:
        data['status'] = 'failed'
        data['message'] = u'商品不存在！'

    return HttpResponse(json.dumps(data), content_type="application/json")

def shopcart(request):
    shopcart = {}
    products_in = []
    #已登陆用户，直接从数据库读取购物车内产品列表
    if 'customer' in request.session:
        shopcart = Shopcart.objects.get(customer__pk=request.session['customer'].get('id'))
        products_in = shopcart.products_in.all()
    #非登陆用户，读取session内购物车
    else:
        if 'shopcart' in request.session:
            #根据保存在session内的product_id获取产品列表
            shopcart = request.session['shopcart']
            
            #组装产品信息，如果session有保存，则从session读取，没有则组装并放入session保存
            #不存在的情况
            if 'products_list' not in shopcart:
                products = Product.objects.filter(id__in=shopcart['products'])
                products_list = {}
                for product in products:
                    product_in = {
                        'product':{
                            'id':product.id,
                            'name':product.name,
                            'cover':str(product.cover),
                            'price':"%0.2f"%float(product.price),
                        },
                        'count': 1,
                        'price':"%0.2f"%float(product.price),
                        'checked':True
                    }
                    products_in.append(product_in)
                    products_list.update({product.id:product_in})
                    #购物车产品列表保存入session
                    shopcart['products_list'] = products_list          
            
            #session已保存的情况
            else:
                for pid in set(shopcart['products']):
                    product_in = shopcart['products_list'][str(pid)]
                    products_in.append(product_in)
            
            #计算总价
            shopcart['total_price'] = "%0.2f" % sum([float(pro['price']) for pro in products_in])
            
            #把更新的购物车信息保存到session内
            request.session['shopcart'] = shopcart

    return render(request, 'shopcart.html', {'shopcart': shopcart, 'products_in':products_in})

def shopcart_update(request, op):
    data = {}
    id = request.GET.get('id')
    #已登陆用户，直接操作数据库关联表字段的增减
    if 'customer' in request.session:
        #获取购物车
        shopcart = Shopcart.objects.get(customer__pk=request.session['customer'].get('id'))
        #从关联表中获取购物车中该产品的信息
        shopcart_product = ShopcartProduct.objects.get(shopcart__customer__pk=request.session['customer'].get('id'), product__pk=id)
        #加1
        if op == 'up':
            price = shopcart_product.price / shopcart_product.count
            shopcart_product.count = F('count')+1
            shopcart_product.price = F('price')+price
            shopcart_product.save()

            shopcart.total_price = F('total_price') + shopcart_product.price
            shopcart.save()
        #减1
        elif op == 'down':
            if shopcart_product.count - 1 > 0:
                price = shopcart_product.price / shopcart_product.count
                shopcart_product.count = F('count')-1
                shopcart_product.price = F('price')-price
                shopcart_product.save()

                shopcart.total_price = F('total_price') - shopcart_product.price
                shopcart.save()

        else:
            return HttpResponse(json.dumps({'status':'failed'}))

        data['status'] = 'success'
        data['count'] = shopcart_product.count
        data['price'] = shopcart_product.price
        data['total_price'] = shopcart.total_price
    #非登陆用户，从session内获取购物车信息，计算结果，并更新session
    else:
        #session内有数据
        if 'shopcart' in request.session:
            shopcart = request.session['shopcart']
            products_count = shopcart['counts'] if 'counts' in shopcart else {}
            #全选的情况，循环购物车产品列表，全部更新状态
            if op in ('check_all', 'uncheck_all'):
                for i, pro in shopcart['products_list'].items():
                    pro['checked'] = True if op == 'check_all' else False
                    shopcart['products_list'].update({i:pro})
            #其他的，数量加减，单个勾选的情况，按操作进行  
            else:
                #取出购物车相应产品
                if 'products_list' in shopcart:
                    product = shopcart['products_list'][id]
                else:
                    product = Product.objects.get(pk=int(id))
                #根据op操作数据
                if op == 'up':
                    product['count'] += 1
                    product['price'] = product['product']['price'] * product['count']

                elif op == 'down':
                    product['count'] += 1
                    product['price'] = product['product']['price'] * product['count']

                elif op == 'check':
                    product['checked'] = True

                elif op == 'uncheck':
                    product['checked'] = False

                shopcart['products_list'].update({id:product})

            if op in ('up', 'down'):
                shopcart['total_price'] = sum([pro['price'] for pro in shopcart['products_list'].values()])

                data['status'] = 'success'
                data['count'] = product['count']
                data['price'] = "%0.2f"%float(product['price'])
                data['total_price'] = "%0.2f"%float(shopcart['total_price'])
            else:
                data['status'] = 'success'

            request.session['shopcart'] = shopcart
        else:
            data['status'] = 'failed'

    return HttpResponse(json.dumps(data), content_type="application/json")


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

        data = {}
        data['forward'] = request.POST['forward']
        data['login_account'] = request.POST['login_account']
        data['status'] = 'errors'
        data['message'] = u'帐号不存在或者密码不对'
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

        except ObjectDoesNotExist:
            pass

        return render(request, 'login.html', data)
    else:
        return render(request, 'login.html', {'status':None, 'forward':request.GET['forward']})


def register(request):
    if request.method == 'POST':
        errors = {}
        empty_fields = []
        data = {}

        for field in ('phone', 'password'):
            data[field] = request.POST.get(field)
            if data[field] is None or data[field] == '':
                empty_fields.append(field)

        if len(empty_fields):
            return render(request, 'register.html', {'errors': empty_fields, 'status': 'field-failed'})

        try:
            customer = Customer.objects.create(**data)
            print customer.save()

            if customer.id:
                request.session['customer'] = {
                    'id': customer.id,
                    'username': customer.username,
                    'phone': customer.phone,
                    'realname': customer.realname,
                    'avatar': str(customer.avatar),
                    'point': customer.point
                }
                return render(request, 'register.html', {'errors': None, 'status': 'success'})
        except IntegrityError:
            errors['message'] = u'手机号码已存在'

        except:
            errors['message'] = u'数据库创建出错'

        return render(request, 'register.html', {'errors': errors, 'status': 'db-failed'})


    return render(request, 'register.html', {'errors': None, 'status': 'None'})
