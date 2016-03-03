# coding:utf8
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, F, Sum
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from shop.models import Notice, Product, Customer, Category, Shopcart, ShopcartProduct, Order, OrderProduct, CustomerRelation, CustomerConnect, Message, MessageLog, CustomerPointLog
from shop.utils import build_form_by_params, get_client_ip, verify_notify_string, notify_xml_string_to_dict, dict_to_xml, generate_random_string
from main.settings import EMAY_SN, EMAY_KEY, EMAY_PWD, WECHAT_APPID, WECHAT_APPSECRET, WECHAT_TOKEN

from decimal import *
import json, time, random, requests, xmltodict
from datetime import datetime

from wechat_sdk.basic import WechatBasic

def main(request):
    notice_list = Notice.objects.filter(type='global', status=1)
    recommend_products = Product.objects.filter(recommend=1)

    category_list = Category.objects.filter(parent=None)
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
    if 'customer' in request.session and request.session['customer']:
        tabstatus = request.GET.get('tabstatus', 'all')
        order_data = []
        try:
            customer = Customer.objects.get(id=request.session['customer'].get('id'))
            order_list = Order.objects.filter(customer=customer, status__in = [3] if tabstatus == 'unuse' else [0,1,2,3])
            for order in order_list:
                if tabstatus == 'all':
                    order.products_in_all = order.products_in.filter()
                elif tabstatus == 'unuse':
                    order.products_in_all = order.products_in.filter(status=0)
                elif tabstatus == 'used':
                    order.products_in_all = order.products_in.filter(status=1)

                order_data.append(order)
        except:
            pass
            
        return render(request, 'order.html', {'order_list':order_data, 'tabstatus':tabstatus})
    else:
        return redirect('/login/?forward=order')

def order_operation(request):
    if 'customer' in request.session and request.session['customer']:
        message = ''
        operation = request.GET.get('operation', '')
        order_id = request.GET.get('order_id', '')

        if operation != '' and order_id != '':
            order = Order.objects.get(id=order_id)
            if request.session['customer']['id'] == order.customer.id:
                if operation == 'delete':
                    if order.status < 3:
                        order.status = 4
                        order.save()
                        message = u'订单取消成功，请返回！'
                    else:
                        message = u'不能结束进行中的订单'
            else:
                message = u'您不能操作不属于自己的订单'
        else:
            message = u'请您选择操作类型和对应的订单'

        return render(request, 'checkout_success.html', {'message':message, 'url': '/order'})
    else:
        return redirect('/login/?forward=order')

def server(request):
    notice_list = Notice.objects.filter(type='news')
    if 'customer' in request.session and request.session['customer']:
        customer_id = request.session['customer'].get('id')
        message_list = Message.objects.filter(customer__id=customer_id).order_by('create_at')
        message_data = []
        for message in message_list:
            message.question_text = message.question_text.split('\b')
            message_data.append(message)

        MessageLog.objects.filter(customer__id=customer_id).update(last_visite_at=datetime.now())
    else:
        customer_id = None
        message_data = None


    return render(request, 'server.html', {
        'notice_list': notice_list,
        'customer_id':customer_id,
        'message_data':message_data
    })


def ask(request):
    if 'customer' in request.session and request.session['customer']:
        customer = Customer.objects.get(id=request.session['customer'].get('id'))
        if request.method == 'POST':
            _message = request.POST.get('message','')

            if _message != '':
                try:
                    message = Message.objects.get(customer=customer, answer_text=None)
                    message.question_text = "%s\b%s" % (message.question_text, _message)
                    message.save()

                except:
                    message = Message.objects.create(customer=customer, question_text=_message)
                    message.save()
                try:
                    message_log = MessageLog.objects.get(customer=customer)
                    message_log.last_visite_at = datetime.now()
                    message_log.save()

                except:
                    message_log = MessageLog.objects.create(customer=customer, last_visite_at=datetime.now())
                    message_log.save()

                return redirect(reverse('server'))
    else:
        return redirect('/login/?forward=ask')


def beauty(request):
    if 'customer' in request.session and request.session['customer']:
        customer = Customer.objects.get(id=request.session['customer'].get('id'))
        relation_list = CustomerRelation.objects.filter(upper=customer)
        relation_list_sub = CustomerRelation.objects.filter(upper__in=set([row.customer for row in relation_list]))

        data = {}
        data['appId'] = WECHAT_APPID
        data['timeStamp'] = str(int(time.time()))
        data['nonceStr'] = generate_random_string()
        wx = WechatBasic(appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
        data['signature'] = wx.generate_jsapi_signature(timestamp=data['timeStamp'], noncestr=data['nonceStr'], url="http://shop.baremeii.com/beauty/")

        share = {}
        share['title'] = u'贝尔美，助您实现美丽人生'
        share['desc'] = u'我是贝尔美医学美容医院的美丽代言人，快来支持我吧！'
        share['img'] = 'http://www.baremeii.com/templets/images/logo.png'

        return render(request, 'beauty.html', {'customer':customer, 'relation_list':relation_list, 'relation_list_sub':relation_list_sub, 'data':data , 'share':share})
    else:
        return redirect('/login/?forward=customer')

def addtocart(request, id):
    data = {}
    count = int(request.GET.get('count', 1))
    checked = int(request.GET.get('checked', 0))
    total_price = 0

    try:
        product = Product.objects.get(pk=id)
        #如果是已登录的用户，则读出数据库购物车
        if 'customer' in request.session and request.session['customer']:
            customer = Customer.objects.get(pk=request.session['customer'].get('id'))
            #积分检查
            if product.payment_type == 1 or product.payment_type == 3:
                if customer.point < (product.payment_point*count):
                    data['status'] = 'failed'
                    data['message'] = u'您的积分不够，无法购买！'
                    return HttpResponse(json.dumps(data), content_type="application/json")

            #获取购物车信息，不存在则创建新购物车
            try:
                shopcart = Shopcart.objects.get(customer=customer)

            except ObjectDoesNotExist:               
                shopcart = Shopcart.objects.create(customer=customer)
                shopcart.save()

            #添加产品到购物车
            try:
                shopcart_product = ShopcartProduct.objects.get(product=product, shopcart=shopcart)
                shopcart_product.count = F('count') + count
                shopcart_product.price = F('price') + product.price * count
                if checked == 1:
                    shopcart_product.checked = True

                shopcart_product.save()
            except ObjectDoesNotExist:
                shopcart_product = ShopcartProduct(product=product, shopcart=shopcart, count=count, price=product.price*count, checked=(checked==1))
                shopcart_product.save() 

            #计算总价
            total_price = float(shopcart.total_price) + float(product.price) * count
            shopcart.total_price = total_price
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
                shopcart['products_list'] = {}

            #保存到session内
            shopcart.get('products').append(product.id)

            if str(product.id) in shopcart['products_list'].keys():
                product_in = shopcart['products_list'].get(str(product.id))
                product_in.update({'count':int(product_in['count'])+count,'price':float(product_in['price'])+float(product.price)*count})
                shopcart['products_list'].update({str(product.id):product_in})

            else:

                shopcart['products_list'].update({str(product.id):{
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'cover':str(product.cover),
                        'price':"%0.2f"%float(product.price),
                    },
                    'count': count,
                    'price':"%0.2f"%float(product.price*count),
                    'checked':True if checked==1 else False
                }})

            request.session['shopcart'] = shopcart
            
            data['status'] = 'ok'

    except ObjectDoesNotExist:
        data['status'] = 'failed'
        data['message'] = u'商品不存在！'

    return HttpResponse(json.dumps(data), content_type="application/json")

def shopcart(request):
    shopcart = {}
    products_in = []
    order = None
    #已登陆用户，直接从数据库读取购物车内产品列表
    customer = None
    if 'customer' in request.session and request.session['customer']:
        try:
            customer = Customer.objects.get(id=request.session['customer'].get('id'))

        except:
            pass

    if customer:
        try:
            order = Order.objects.get(customer__pk=request.session['customer'].get('id'), status=1)

        except:
            pass

        try:
            shopcart = Shopcart.objects.get(customer__pk=request.session['customer'].get('id'))
        except ObjectDoesNotExist:
            shopcart = Shopcart.objects.create(customer=customer)
            shopcart.save()

        products_in_ids = [p.product.id for p in shopcart.products_in.all()]

        if 'shopcart' in request.session:
            _shopcart = request.session['shopcart']
            products = Product.objects.filter(id__in=set(_shopcart['products']))

            for pro in products:
                product = _shopcart['products_list'][str(pro.id)]
                if pro.id not in products_in_ids:
                    product_in = ShopcartProduct.objects.create(product=pro, shopcart=shopcart, count=product['count'], price=product['price'], checked=product['checked'])
                    product_in.save()
                else:
                    ShopcartProduct.objects.filter(product=pro, shopcart=shopcart).update(count=F('count')+product['count'], price=F('price')+float(product['price']))
            del request.session['shopcart']

        products_in = shopcart.products_in.all()

        sp = ShopcartProduct.objects.filter(shopcart__customer__pk=request.session['customer'].get('id'), checked=True).aggregate(total=Sum('price'))
        shopcart.total_price = "%0.2f"%(sp['total']+0) if sp['total'] else "0"
        shopcart.save()
        

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

    return render(request, 'shopcart.html', {'shopcart': shopcart, 'products_in':products_in, 'order':order})

def shopcart_update(request, op):
    data = {}
    id = request.GET.get('id')
    #已登陆用户，直接操作数据库关联表字段的增减
    if 'customer' in request.session and request.session['customer']:
        #获取购物车
        shopcart = Shopcart.objects.get(customer__pk=request.session['customer'].get('id'))
        if op in ('check_all', 'uncheck_all'):
            checked = True if op == 'check_all' else False
            shopcart_product = ShopcartProduct.objects.filter(shopcart__customer__pk=request.session['customer'].get('id')).update(checked=checked)
        elif op == 'delete':
            shopcart_product = ShopcartProduct.objects.get(shopcart__customer__pk=request.session['customer'].get('id'), product__pk=id)
            shopcart_product.delete()
        else:
            product = Product.objects.get(pk=id)
            #从关联表中获取购物车中该产品的信息
            shopcart_product = ShopcartProduct.objects.get(shopcart__customer__pk=request.session['customer'].get('id'), product__pk=id)
            #加1
            if op == 'up':
                shopcart_product.count = F('count') + 1
                shopcart_product.price = F('price') + product.price
                shopcart_product.save()
                shopcart_product.refresh_from_db()

            #减1
            elif op == 'down':
                shopcart_product.count = F('count') - 1
                shopcart_product.price = F('price') - product.price
                shopcart_product.save()
                shopcart_product.refresh_from_db() 


            elif op == 'check':
                shopcart_product.checked = True
                shopcart_product.save()

            elif op == 'uncheck':
                shopcart_product.checked = False
                shopcart_product.save()

            else:
                return HttpResponse(json.dumps({'status':'failed'}))
        if op in ('up','down'):
            data['count'] = shopcart_product.count
            data['price'] = "%0.2f"%shopcart_product.price

        
        sp = ShopcartProduct.objects.filter(shopcart__customer__pk=request.session['customer'].get('id'), checked=True).aggregate(total=Sum('price'))
        
        data['total_price'] = "%0.2f"%(sp['total']+0) if sp['total'] else "0"

        shopcart.total_price = data['total_price']
        shopcart.save()

        data['status'] = 'success'
    #非登陆用户，从session内获取购物车信息，计算结果，并更新session
    else:
        #session内有数据
        if 'shopcart' in request.session:
            shopcart = request.session['shopcart']
            #全选的情况，循环购物车产品列表，全部更新状态
            if op in ('check_all', 'uncheck_all'):
                for i, pro in shopcart['products_list'].items():
                    pro['checked'] = True if op == 'check_all' else False
                    shopcart['products_list'].update({i:pro})
            #其他的，数量加减，单个勾选的情况，按操作进行  
            elif op == 'delete':
                shopcart['products_list'].pop(id)
            else:
                #取出购物车相应产品
                if 'products_list' in shopcart:
                    product = shopcart['products_list'][id]
                else:
                    product = Product.objects.get(pk=int(id))
                #根据op操作数据
                if op == 'up':
                    product['count'] += 1
                    product['price'] = float(product['product']['price']) * product['count']

                elif op == 'down':
                    product['count'] -= 1
                    product['price'] = float(product['product']['price']) * product['count']

                elif op == 'check':
                    product['checked'] = True

                elif op == 'uncheck':
                    product['checked'] = False

                shopcart['products_list'].update({id:product})

            if op in ('up', 'down'):
                shopcart['total_price'] = sum([float(pro['price']) for pro in shopcart['products_list'].values()])
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

def shopcart_order(request):
    data = {}
    quick_id = int(request.GET.get('quick_id',0))
    count = int(request.GET.get('count',0))
    customer = None if 'customer' not in request.session else Customer.objects.get(id=request.session['customer'].get('id'))
    data['login'] = True if customer else False
    data['status'] = 'ok'     
    data['products'] = ''
    
    ids = set()
    products_list = {}
    total_price = 0
    if quick_id:
        product = Product.objects.get(id=quick_id)
        #积分检查
        if product.payment_type == 1 or product.payment_type == 3:
            if customer.point < (product.payment_point*count):
                data['status'] = 'failed'
                data['message'] = u'您的积分不够，无法购买！'
                return HttpResponse(json.dumps(data), content_type="application/json")

        ids.add(quick_id)
        products_list.update({product.id:{'count':count, 'price':product.price*count}})
    else:
        if customer:
            _shopcart = Shopcart.objects.get(customer=customer)

            for product_in in _shopcart.products_in.all():
                if product_in.checked and product_in.count>0:
                    ids.add(product_in.product.id)
                    products_list.update({product_in.product.id:{'count':product_in.count, 'price':product_in.price}})


        if 'shopcart' in request.session:
            shopcart = request.session['shopcart']

            for _id,product in shopcart['products_list'].items():
                if product['checked'] and product['count']>0:
                    ids.add(int(_id))
                    if int(_id) in products_list:
                        p = products_list[int(_id)]
                        products_list.update({int(_id):{'count':product['count']+p['count'], 'price':float(product['price'])+float(p['price'])}})
                    else:
                        products_list.update({int(_id):product})
    
    if ids:
        for _id in ids:
            total_price += float(products_list[_id]['price'])

        data['total_price'] = u"￥%0.2f"%float(total_price)

        order = None
        products = Product.objects.filter(id__in=ids)
        if 'order_id' in request.session:
            data['order_id'] = request.session['order_id']
            #获取订单，若订单是未登录创建的，还要更新订单归属
            try:
                order = Order.objects.get(id=int(data['order_id']))
                if customer and not order.customer:
                    order.customer = customer
                    order.save()

            except ObjectDoesNotExist:
                pass
        #最新的订单结束，则创建薪订单
        if (not order) or order.status > 1:
            order = Order.objects.create(
                customer=customer,
                status=0,
                total_price=total_price,
                address=''
            )
            order.save()

            order.order_txt = "%s%04d" % (datetime.today().strftime("%Y%m%d"), (order.id%10000))
            order.save()

        data['order_txt'] = order.order_txt
        data['order_id'] = order.id
        request.session['order_id'] = order.id
        
        if quick_id:
            order.products.clear()

        for prod in products:
            data['products'] += "%s * %s = %s <br/>" % (prod.name, products_list[prod.id]['count'], products_list[prod.id]['price'])

            if prod.id not in [p.product.id for p in order.products_in.all()]:
                order_product = OrderProduct.objects.create(
                    product=prod,
                    order=order,
                    count=products_list[prod.id]['count'],
                    price=products_list[prod.id]['price']
                )
                order_product.save()
            else:
                OrderProduct.objects.filter(order=order, product=prod).update(count=products_list[prod.id]['count'],price=products_list[prod.id]['price'])  
        
    return HttpResponse(json.dumps(data), content_type="application/json")

def shopcart_order_checkout(request):
    order_id = request.GET.get('order_id', '')
    if "customer" in request.session and request.session['customer']:
        data = {}
        
        data['customer'] = Customer.objects.get(id=request.session['customer'].get('id'))

        if order_id:
            order = Order.objects.get(id=order_id)
            order.status = 1
            order.save()

            data['order_id'] = order_id
            data['order_txt'] = order.order_txt
            data['products'] = ''
            data['total_point'] = 0
            products_count = {}
            total_price = 0
            for product in order.products_in.all():
                products_count[product.product.id] = product.count
                if product.product.payment_type == 1:
                    data['total_point'] += product.product.payment_point * product.count
                    data['products'] += u"%s * %s = <del>￥%s</del><br/>" % (product.product.name, product.count, product.price)
                elif product.product.payment_type == 3:
                    data['total_point'] += product.product.payment_point * product.count
                    data['products'] += u"%s * %s = ￥%s<br/>" % (product.product.name, product.count, product.price)
                    total_price += float(product.price)
                else:
                    data['products'] += u"%s * %s = ￥%s<br/>" % (product.product.name, product.count, product.price)
                    total_price += float(product.price)

            data['products_all'] = []
            for product in order.products.all():
                product.count = products_count[product.id]
                data['products_all'].append(product)

            data['total_price'] = "%0.2f"%total_price
            data['order'] = order

        else:
            pass
        return render(request, 'checkout.html', data)
    else:
        return redirect('/login?forward=shopcart_order_checkout&order_id=%s'%(order_id))


def purchase(request):
    if  "customer" in request.session and "openid" in request.session and request.method == 'POST':
        empty_fields = []
        data = {}
        for field in ('realname', 'phone', 'address'):
            data[field] = request.POST.get(field)
            if data[field] is None or data[field] == '':
                empty_fields.append(field)

        if len(empty_fields):
            return render(request, 'checkout.html', {'errors': empty_fields, 'status': 'field-failed'})

        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(id=order_id)

            if order.status == 3:
                return redirect('/order/')
            else:
                order.realname = data['realname']
                order.phone = data['phone']
                order.address = data['address']
                order.message = request.POST.get('message', '')
                order.status = 2

                order.save()

                products_str = ''
                discount = 0
                total_point = 0
                for product in order.products_in.all():
                    if product.product.payment_type == 1:
                        discount += product.product.price * product.count
                        total_point += product.product.payment_point * product.count
                    elif product.product.payment_type == 2:
                        if str(product.product.id) in request.POST.getlist('payment_point'):
                            discount += product.product.price * product.count
                            total_point += product.product.payment_point * product.count
                    elif product.product.payment_type == 3:
                        total_point += product.product.payment_point * product.count

                    products_str += u"%s * %s = ￥%s, " % (product.product.name, product.count, product.price)
                
                customer = Customer.objects.get(id=order.customer.id)
                if customer.point - total_point < 0:
                    return render(request, 'checkout_success.html', {'message':u'积分不够，支付不成功！', 'url':'/order'})
                else:
                    customer.point = F('point') - total_point
                    customer.save()

                    cpl = CustomerPointLog.objects.create(customer=customer, opertor=customer, event_name=u'购物消费', opertion='-', score=total_point)
                    cpl.save()

                    #从购物车内删除
                    pids = [int(product.product.id) for product in order.products_in.all()]
                    sp = ShopcartProduct.objects.filter(shopcart__customer__id=order.customer.id, product__id__in=pids)
                    sp.delete()


                total_price = order.total_price - discount
                if total_price > 0:
                    params = build_form_by_params({
                        'body': products_str.rstrip(', ').encode('utf8'),
                        'out_trade_no' : "%s"%str(order.order_txt),
                        'total_fee':int(total_price*100),
                        'spbill_create_ip':get_client_ip(request),
                        'openid':request.session['openid']
                    })
                    if params['paySign']:
                        params['order_id'] = str(order.id)

                        wx = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
                        params['signature'] = wx.generate_jsapi_signature(timestamp=params['timeStamp'], noncestr=params['nonceStr'], url="http://shop.baremeii.com/purchase/")
                        return render(request, 'purchase.html', params)
                    else:
                        return HttpResponse(params['err_code_des'])
                else:
                    order.status = 3
                    order.save()
                    return render(request, 'checkout_success.html', {'message':u'支付成功，请返回！', 'url':'/order'})
                    #return HttpResponse(u'支付成功！')


        except:
            return render(request, 'checkout_success.html', {'message':u'您不能操作不属于自己的订单', 'url':'/shopcart'})

    else:
        return redirect('/login/?forward=purchase')

def wx_verify(request):
    wx = WechatBasic(token=WECHAT_TOKEN, appid=WECHAT_APPID, appsecret=WECHAT_APPSECRET)
    if wx.check_signature(request.GET.get('signature'), request.GET.get('timestamp'), request.GET.get('nonce')):
        return HttpResponse(request.GET.get('echostr'))
    else:
        return HttpResponse('error')

def wx_callback(request):
    
    r = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(WECHAT_APPID, WECHAT_APPSECRET, request.GET.get('code')))
    if int(r.status_code) == 200:
        data = r.json()

        r2 = requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN'%(data['access_token'], data['openid']))
        r2.encoding='utf8'
        if int(r2.status_code) == 200:
            userinfo = r2.json()
            try:
                customer_connect = CustomerConnect.objects.get(openid=data['openid'])

                if customer_connect.customer:
                    request.session['customer'] = {
                        'id': customer_connect.customer.id,
                        'username': customer_connect.customer.username,
                        'phone': customer_connect.customer.phone,
                        'realname': customer_connect.customer.realname,
                        'avatar': str(customer_connect.customer.avatar),
                        'point': customer_connect.customer.point
                    }
                else:
                    if 'customer' in request.session:
                        del request.session['customer']

            except:
                customer_connect = CustomerConnect.objects.create(
                    platform='weixin',
                    access_token=data['access_token'],
                    openid=data['openid'],
                    expires_at=int(time.time())+int(data['expires_in']),
                    nickname=userinfo['nickname'].encode('utf8'),
                    sex=userinfo['sex'],
                    province=userinfo['province'].encode('utf8'),
                    city=userinfo['city'].encode('utf8'),
                    country=userinfo['country'].encode('utf8'),
                    headimgurl=userinfo['headimgurl'],
                    unionid=userinfo['unionid'] if 'unionid' in userinfo else ''
                )
                customer_connect.save()

            request.session['wx_code'] = request.GET.get('code')
            request.session['openid'] = customer_connect.openid

            state = request.GET.get('state')
            return redirect(state if state else '/')
        else:
            return HttpResponse(u'获取个人信息时，网络出现问题！')
    else:
        return HttpResponse(u'网络出现故障，请返回重试！')

def test(request):
    return render(request, 'test.html')

@csrf_exempt
def wxpay_notify(request):

    if verify_notify_string(request.body):
        params = notify_xml_string_to_dict(request.body)
        if params['return_code'] == 'SUCCESS':
            order_txt = params['out_trade_no']
            order = Order.objects.get(order_txt=order_txt)
            customer_connect = CustomerConnect.objects.get(openid=params['openid'])

            if order.customer.id == customer_connect.customer.id:
                order.status = 3
                order.save()

                customer = Customer.objects.get(pk=order.customer.id)
                customer.realname = order.realname
                customer.address = order.address
                #加积分
                point = sum([int(product.product.point) for product in order.products_in.all()])
                point_data = {}
                point_data['point'] = 0
                point_data['point_1'] = 0
                point_data['point_2'] = 0
                point_data['point_3'] = 0

                for prod in order.products_in.all():
                    point_data['point'] += prod.product.point
                    point_data['point_1'] += prod.product.point_1 if prod.product.point_1 else 0
                    point_data['point_2'] += prod.product.point_2 if prod.product.point_2 else 0
                    point_data['point_3'] += prod.product.point_3 if prod.product.point_3 else 0

                if point_data['point']>0:

                    customer.point = F('point') + point_data['point']
                    customer.save()

                    cpl = CustomerPointLog.objects.create(customer=customer, opertor=customer, event_name=u'支付订单', opertion='+', score=point)
                    cpl.save()

                if sum([point_data['point_1'], point_data['point_1'], point_data['point_1']])>0:

                    try:
                        customer_relations = CustomerRelation.objects.filter(customer=customer, level__in=[1,2,3])

                        for relation in customer_relations:

                            score = point_data.get("point_%d" % relation.level)

                            if score>0:
                                relation.upper.point = F('point') + score
                                relation.upper.save()

                                cpl = CustomerPointLog.objects.create(customer=relation.upper, opertor=customer, event_name=u'%s级下线支付订单'%(relation.level), opertion='+', score=score)
                                cpl.save()

                    except:
                        pass


                #从购物车内删除
                pids = [int(product.product.id) for product in order.products_in.all()]
                sp = ShopcartProduct.objects.filter(shopcart__customer__id=order.customer.id, product__id__in=pids)
                sp.delete()

                return HttpResponse(dict_to_xml({'return_code':'SUCCESS','return_msg':'OK'}))
    return HttpResponse(dict_to_xml({'return_code':'FAILED','return_msg':'ERROR'}))


def customer(request):
    if 'customer' in request.session and request.session['customer']:
        c = request.session.get('customer')
        customer = Customer.objects.get(id=int(c['id']))
        return render(request, 'customer.html', {
            'customer': customer
        })
    else:
        return redirect('/login/?forward=customer')


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
                if 'order_id' in request.session and request.session['order_id']:
                    return redirect("%s?order_id=%s"%(reverse('shopcart_order_checkout'),request.session['order_id']))
                else:
                    return redirect(reverse('customer'))

        except ObjectDoesNotExist:
            pass

        return render(request, 'login.html', data)
    else:
        return render(request, 'login.html', {
            'status':None,
            'forward':request.GET.get('forward','')
        })


def register(request):
    if request.method == 'POST':
        errors = {}
        empty_fields = []
        data = {}

        for field in ('phone', 'password', 'verifycode'):
            data[field] = request.POST.get(field)
            if data[field] is None or data[field] == '':
                empty_fields.append(field)

        if len(empty_fields):
            return render(request, 'register.html', {'errors': empty_fields, 'status': 'field-failed'})

        if 'verifycode' not in request.session:
            return render(request, 'register.html', {'status': 'verify-failed', 'message':u'验证码不存在'})

        elif int(data['verifycode']) != int(request.session['verifycode']):
            return render(request, 'register.html', {'status': 'verify-failed', 'message':u'验证码不正确'})
        else:
            del data['verifycode']
            del request.session['verifycode']
            del request.session['verifytoken']
            del request.session['verifytime']

        try:
            
            customer = Customer.objects.create(**data)

            if customer.id:
                if 'openid' in request.session and request.session['openid']:
                    customer_connect = CustomerConnect.objects.get(openid=request.session['openid'])
                    customer_connect.customer = customer

                    customer_connect.save()

                    customer.username = customer_connect.nickname
                    customer.sex = customer_connect.sex
                    customer.avatar = customer_connect.headimgurl
                    customer.save()

                request.session['customer'] = {
                    'id': customer.id,
                    'username': customer.username,
                    'phone': customer.phone,
                    'realname': customer.realname,
                    'avatar': str(customer.avatar),
                    'point': customer.point
                }
                if 'invite_customer_id' in request.session and request.session['invite_customer_id']:
                    try:
                        #创建一级关系
                        upper = Customer.objects.get(id=request.session['invite_customer_id'])
                        customer_relation = CustomerRelation.objects.create(customer=customer, upper=upper, level=1)
                        customer_relation.save()
                        #给一级关系加积分
                        upper.point = F('point') + 100
                        upper.save()
                        cpl = CustomerPointLog.objects.create(customer=upper, opertor=customer, event_name=u'邀请注册', opertion='+', score=100)
                        cpl.save()
                        #查找是否有二级关系，存在则创建二级关系
                        try:
                            upper_relation = CustomerRelation.objects.get(customer=upper, level=1)

                            customer_relation = CustomerRelation.objects.create(customer=customer, upper=upper_relation.upper, level=2)
                            customer_relation.save()

                            if upper_relation.upper.id != customer.id:
                                #给二级关系加积分
                                upper_relation.upper.point = F('point') + 50
                                upper_relation.upper.save()

                                cpl = CustomerPointLog.objects.create(customer=upper_relation.upper, opertor=customer, event_name=u'二级下线邀请注册', opertion='+', score=50)
                                cpl.save()

                            #三级关系
                            try:
                                upper_upper_relation = CustomerRelation.objects.get(customer=upper_relation.upper, level=1)

                                upper_customer_relation = CustomerRelation.objects.create(customer=customer, upper=upper_upper_relation.upper, level=3)
                                customer_relation.save()

                                if upper_relation.upper.id != customer.id and upper_upper_relation.upper.id != customer.id:
                                    #给三级关系加积分
                                    upper_upper_relation.upper.point = F('point') + 25
                                    upper_upper_relation.upper.save()

                                    cpl = CustomerPointLog.objects.create(customer=upper_upper_relation.upper, opertor=customer, event_name=u'三级下线邀请注册', opertion='+', score=25)
                                    cpl.save()

                            except:
                                pass
                        except:
                            pass

                        del request.session['invite_customer_id']
                    except:
                        pass

                if 'order_id' in request.session and request.session['order_id']:
                    return render(request, 'register.html', {'errors': None, 'status': 'success', 'order_id': request.session['order_id']})
                else:
                    return render(request, 'register.html', {'errors': None, 'status': 'success'})
        except IntegrityError:
           errors['message'] = u'手机号码已存在'

        except:
           errors['message'] = u'创建用户失败'

        return render(request, 'register.html', {'errors': errors, 'status': 'db-failed'})
    #verify token
    verify_token = random.randint(100000000,999999999)
    request.session['verifytoken'] = verify_token
    return render(request, 'register.html', {'errors': None, 'status': None, 'verify_token':verify_token})

def repw(request):
    if not ('customer' in request.session and request.session['customer']):
        return redirect('/login/?forward=repw')

    if request.method == 'POST':
        errors = {}
        empty_fields = []
        data = {}

        for field in ('newpassword', 'oldpassword'):
            data[field] = request.POST.get(field)
            if data[field] is None or data[field] == '':
                empty_fields.append(field)

        if len(empty_fields):
            return render(request, 'repw.html', {'errors': empty_fields, 'status': 'field-failed'})

        s_customer = request.session['customer']
        customer = Customer.objects.get(id=s_customer['id'])
        try:
            if customer.check_password(data['oldpassword']):
                customer.password = data['newpassword']

                customer.save()

                return render(request, 'repw.html', {'errors': None, 'status': 'success'})

            else:
                errors['message'] = u'旧密码不正确'

        except:
            errors['message'] = u'数据库出错'
            
        return render(request, 'repw.html', {'errors': errors, 'status': 'db-failed'})


    return render(request, 'repw.html', {'errors': None, 'status': None})

def code(request, code):
    if 'customer' in request.session and request.session['customer']:
        return redirect(reverse('main'))
    else:
        try:
            customer = Customer.objects.get(phone=code)
            request.session['invite_customer_id'] = customer.id
        except:
            pass

        return redirect(reverse('register'))

def verify(request):
    ret = {}
    if 'verifytime' in request.session:
        verifytime = int(request.session['verifytime'])
        if int(time.time()) - verifytime < 60:
            ret['status'] = 'waiting'
            return HttpResponse(json.dumps(ret), content_type="application/json")

    try:
        code = random.randint(100000,999999)
        print code
        
        r = requests.post('http://hprpt2.eucp.b2m.cn:8080/sdkproxy/sendsms.action', data={
            'cdkey':EMAY_KEY,
            'password':EMAY_PWD,
            'phone':request.GET.get('phone'),
            'message':u"%s您的验证码是：%s"%(EMAY_SN, code)
        })
        if int(r.status_code) == 200:
            data = xmltodict.parse(r.text.strip())
            if int(data['response']['error'])==0:
                ret['status'] = 'success'

                request.session['verifytime'] = int(time.time())
                request.session['verifycode'] = code
            else:
                data['status'] = data['response']['message']
        else:
            ret['status'] = status_code

    except:
        ret['status'] = 'error'

    return HttpResponse(json.dumps(ret), content_type="application/json")