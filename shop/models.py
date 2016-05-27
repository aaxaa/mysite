# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.html import format_html

from datetime import date
import random, hashlib, re


class Category(models.Model):
    parent = models.ForeignKey(
        'self',
        verbose_name=u'上级分类',
        null=True,
        blank=True,
        related_name="children"
    )
    name = models.CharField(u"类别名称", max_length=50)
    path = models.CharField(max_length=255, null=True, blank=True, editable=False)
    display_order = models.SmallIntegerField(u"显示排序", default=0)

    def __unicode__(self):
        if self.id == self.path:
            return self.name

        else:
            return self.node

    def _node(self):
        indent_num = len(self.path.split(':')) - 1
        indent = '--' * indent_num
        node = u"%s%s" % (indent, self.name)
        return node

    node = property(_node)

    class Meta:
        verbose_name = u'分类'
        verbose_name_plural = u'商品分类'
        ordering = ['path']

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)

        if self.parent:
            self.path = "%s:%s" % (self.parent.path, self.id)

        else:
            self.path = self.id

        super(Category, self).save(*args, **kwargs)

        childrens = self.children.all()

        if len(childrens) > 0:
            for children in childrens:
                children.path = '%s:%s' % (self.path, children.id)
                children.save()


class Product(models.Model):
    type_choices = [
        ('G', u'产品'),
        ('S', u'项目'),
    ]
    status_choices = [
        (0, u'待上架'),
        (1, u'已上架'),
    ]
    recommend_choices = [
        (0, u'否'),
        (1, u'是')
    ]
    payment_choices = [
        (0, u'仅限现金购买'),
        (1, u'仅限积分兑换'),
        (2, u'可现金购买亦可积分兑换'),
        (3, u'需要同时支付现金和积分')
    ]

    model = models.CharField(u"商品SKU", max_length=50)
    name = models.CharField(u"商品名称", max_length=50)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=u'商品分类'
    )
    description = models.TextField(u"商品简介")
    type = models.CharField(
        u"商品类型",
        max_length=1,
        choices=type_choices,
        default='G'
    )
    recommend = models.SmallIntegerField(
        u'首页推荐',
        choices=recommend_choices,
        default=0,
    )
    price = models.DecimalField(u"所需价格", max_digits=8, default=0.00, decimal_places=2)
    point = models.IntegerField(u"积分奖励", default=0)
    point_1 = models.IntegerField(u"一级积分", default=0, help_text=u"当值为0时不给积分奖励")
    point_2 = models.IntegerField(u"二级积分", default=0, help_text=u"当值为0时不给积分奖励")
    point_3 = models.IntegerField(u"三级积分", default=0, help_text=u"当值为0时不给积分奖励")

    payment_type = models.SmallIntegerField(
        u'支付方式',
        choices=payment_choices,
        default=0,
    )
    payment_point = models.IntegerField(u"所需积分", default=0)
    content = RichTextUploadingField(u"产品详情")
    cover = models.ImageField(
        u"封面图片",
        null=True,
        upload_to='upload/products/%Y/%m/%d/',
        help_text=u'图片尺寸比例为4:3(长宽)'
    )
    create_at = models.DateField(u"创建时间", auto_now_add=True)
    status = models.SmallIntegerField(u"状态", choices=status_choices, default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'商品'
        verbose_name_plural = u'商品管理'
        ordering = (('create_at'), ('status'),)

    def save(self, *args, **kwargs):
        self.content = re.sub(r'style="height:\d+px; width:\d+px"', '', self.content)
        super(Product, self).save(*args, **kwargs)


class Item(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=u'商品分类'
    )
    name = models.CharField(u"属性名称", max_length=50)
    display_order = models.IntegerField(u"显示排序")
    products = models.ManyToManyField(
        Product,
        through='ProductItem',
        through_fields=('item', 'product'),
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'商品属性'
        verbose_name_plural = u'商品属性'


class ProductItem(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name=u'字段'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=u'商品',
        related_name="items"
    )
    value = models.CharField(u'值', max_length=50)

    class Meta:
        verbose_name = u'产品属性'
        verbose_name_plural = u'产品属性'


class Customer(models.Model):
    sex_choices = (
        (0, u'未知'),
        (1, u'男'),
        (2, u'女'),
    )

    status_choices = (
        (0, u'未激活'),
        (1, u'激活')
    )

    username = models.CharField(u'帐号', null=True, blank=True, max_length=15, unique=True)
    realname = models.CharField(u'姓名', null=True, blank=True, max_length=15)
    phone = models.CharField(u'手机', max_length=15, unique=True)
    password = models.CharField(u'密码', max_length=50)
    avatar = models.CharField(u'头像', null=True, blank=True, max_length=255)
    sex = models.SmallIntegerField(
        u'性别',
        choices=sex_choices,
        default=2
    )
    point = models.IntegerField(u'积分', default=0)
    address = models.CharField(u'收件地址', null=True, blank=True, max_length=255)
    register_at = models.DateField(u'注册时间', auto_now_add=True)
    status = models.SmallIntegerField(u'状态', choices=status_choices ,default=1)

    def save(self, *args, **kwargs):
        self.password = self.hash_password()
        super(Customer, self).save(*args, **kwargs)

    def hash_password(self):
        salt = "".join(random.sample('abcdefghijklmnopqrsiuvwxyz1234567890',6))
        h = hashlib.md5()
        h.update(salt)
        h.update(self.password)
        h.update(salt)
        return "%s:%s" % (salt, h.hexdigest())

    def check_password(self, password):
        salt , pwd = self.password.split(':')
        h = hashlib.md5()
        h.update(salt)
        h.update(password)
        h.update(salt)
        return str(pwd) == str(h.hexdigest())

    class Meta:
        verbose_name = u'客户'
        verbose_name_plural = u'客户管理'
        ordering = (('register_at'), )
        index_together = ('username', 'phone')

    def __unicode__(self):
        return self.username if self.username else (u"手机帐号%s" % (self.phone)) 


class CustomerConnect(models.Model):
    customer = models.ForeignKey(
        Customer,
        verbose_name=u'用户',
        on_delete=models.CASCADE,
        related_name='connect',
        null=True,
        blank=True,
    )
    platform = models.CharField(max_length=10)
    access_token = models.CharField(max_length=255, default='')
    openid = models.CharField(max_length=50, unique=True)
    expires_at = models.IntegerField(default=0)
    nickname = models.CharField(max_length=50, default='')
    sex = models.SmallIntegerField(default=0)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=20, default='')
    headimgurl = models.CharField(max_length=255, default='')
    unionid = models.CharField(max_length=50, blank=True, null=True)


class CustomerPointLog(models.Model):
    opertion_choices = (
        ('+', u'增加'),
        ('-', u'减去'),
    )

    customer = models.ForeignKey(
        Customer,
        verbose_name=u'所属客户',
        on_delete=models.CASCADE,
        related_name='point_log_owner'
    )
    opertor = models.ForeignKey(
        Customer,
        verbose_name=u'贡献者',
        on_delete=models.CASCADE,
        related_name='point_log_oper'
    )
    event_name = models.CharField(u'事件', max_length=15)
    opertion = models.CharField(
        u'操作类型',
        max_length=1,
        choices=opertion_choices,
        default='+'
    )
    score = models.IntegerField(u'分值')
    create_at = models.DateField(u'发生时间', auto_now_add=True)

    def __unicode__(self):
        return "%s %s %d" % (self.event_name, self.opertion, self.score)

    class Meta:
        verbose_name = u'积分记录'
        verbose_name_plural = u'积分记录'
        ordering = (('create_at'),)


class CustomerRelation(models.Model):
    level_choices = (
        (1, u'一级代言'),
        (2, u'二级代言'),
        (3, u'三级代言'),
    )

    customer = models.ForeignKey(
        Customer,
        verbose_name=u'客户',
        on_delete=models.CASCADE
    )
    upper = models.ForeignKey(
        Customer,
        verbose_name=u'上级客户',
        on_delete=models.CASCADE,
        related_name='upper'
    )
    level = models.SmallIntegerField(u'级别', choices=level_choices, default=1)
    create_at = models.DateField(u'时间', auto_now_add=True)

    class Meta:
        verbose_name = u'客户关系'
        verbose_name_plural = u'客户关系'


class CustomerOperationLog(models.Model):
    customer = models.ForeignKey(
        Customer,
        verbose_name=u'客户',
        null=True,
        blank=True
    )
    create_at = models.DateField(u'时间', auto_now_add=True)
    message = models.CharField(u'操作', max_length=255)
    data = models.TextField(u'信息')

    def __unicode__(self):
        return str(self.message)

    class Meta:
        verbose_name = u'操作日志'
        verbose_name_plural = u'操作日志'


class Shopcart(models.Model):
    customer = models.ForeignKey(
        Customer,
        verbose_name=u'客户',
        on_delete=models.CASCADE
    )
    products = models.ManyToManyField(Product, verbose_name=u'商品信息', through='ShopcartProduct')
    total_price = models.DecimalField(u'总价', max_digits=8, default=0.00, decimal_places=2)

    def __unicode__(self):
        return str(self.customer.id)

    class Meta:
        verbose_name = u"购物车"
        verbose_name_plural = u'购物车'


class ShopcartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shopcart = models.ForeignKey(Shopcart, on_delete=models.CASCADE, related_name="products_in")
    joined_at = models.DateField(u'添加时间', auto_now_add=True)
    count = models.SmallIntegerField(u'数量', default=1)
    price = models.DecimalField(u'价格', max_digits=8,  default=0.00, decimal_places=2)
    checked = models.BooleanField(u'选择', default=True)

    class Meta:
        verbose_name = u"购物车"
        verbose_name_plural = u'购物车'

    def __unicode__(self):
        return self.product.name


class Order(models.Model):
    status_choices = [
        (0, u'已创建'),
        (1, u'已下单'),
        (2, u'未支付'),
        (3, u'已付款'),
        (4, u'已关闭'),
    ]
    wxstatus_choices = [
        (0, u'-'),
        (1, u'对账通过'),
        (2, u'对账失败')
    ]

    order_txt = models.CharField(u'订单号', max_length=12, default='')
    customer = models.ForeignKey(
        Customer,
        verbose_name=u'客户',
        null=True,
        blank=True
    )
    products = models.ManyToManyField(Product, verbose_name=u'商品信息', through='OrderProduct')
    total_price = models.DecimalField(u'总价', max_digits=8, decimal_places=2)
    realname = models.CharField(u'收件人', max_length=50, null=True, blank=True)
    phone = models.CharField(u'联系电话', max_length=15, null=True, blank=True)
    address = models.CharField(u'收件地址', null=True, blank=True, max_length=255)
    message = models.CharField(u'附言', max_length=255, null=True, blank=True)
    create_at = models.DateField(u'创建时间', auto_now_add=True)
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=0)
    wxstatus = models.SmallIntegerField(u'对账', choices=wxstatus_choices, default=0)

    class Meta:
        verbose_name = u'订单'
        verbose_name_plural = u'客户订单'
        ordering = ('-create_at','-id')

class OrderProduct(models.Model):
    status_choices = [
        (0, u'未消费'),
        (1, u'已消费')
    ]
    product = models.ForeignKey(Product)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="products_in")
    joined_at = models.DateField(u'添加时间', auto_now_add=True)
    count = models.SmallIntegerField(u'数量', default=1)
    price = models.DecimalField(u'价格', max_digits=8, default=0.00, decimal_places=2)
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=0)

    def __unicode__(self):
        return str(self.order.id)

    # class Meta:
    #     auto_created = True


class Message(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name=u"客户")
    create_at = models.DateField(u'提问时间', auto_now_add=True)
    update_at = models.DateTimeField(u'更新时间', auto_now=True)
    question_text = models.TextField(u'提问内容')
    answer_text = models.TextField(u'答复内容', null=True, blank=True)

    def __unicode__(self):
        return self.question_text

    def answer_html(self):
        return self.answer_text if self.answer_text else format_html('<span style="color:red;">新留言</span>')

    answer_html.short_name = u'客服答复'
    answer_html.short_description = u'客服答复'

    class Meta:
        verbose_name = u'咨询'
        verbose_name_plural = u'客户咨询'
        ordering = (('-update_at'), )


class MessageLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name=u"客户")
    last_visite_at = models.DateTimeField(u'更新时间')


class Notice(models.Model):
    type_choices = [
        ('global', u'首页幻灯片'),
        ('news', u'实时公告')
    ]
    status_choices = [
        (0, u'草稿'),
        (1, u'发布'),
    ]
    title = models.CharField(u'标题', max_length=255)
    content = RichTextUploadingField(u'内容')
    type = models.CharField(
        u'类型',
        max_length=10,
        choices=type_choices,
        default='news'
    )
    cover = models.ImageField(
        u'图片',
        null=True,
        blank=True,
        upload_to='upload/notice/%Y/%m/%d/',
        help_text=u'图片尺寸比例为2:1(长宽)'
    )
    create_at = models.DateField(u'创建时间', auto_now_add=True)
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=1)

    class Meta:
        verbose_name = u'公告'
        verbose_name_plural = u'促销公告'
        ordering = (('-create_at'), )
