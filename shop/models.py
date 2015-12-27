# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


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
        verbose_name_plural = u'分类'
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
        (2, u'已下架'),
        (3, u'售罄'),
    ]
    recommend_choices = [
        (0, u'否'),
        (1, u'是')
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
    price = models.FloatField(u"商品价格", default=0.00)
    stock = models.IntegerField(u"库存数量", default=0)
    content = RichTextUploadingField(u"产品详情")
    cover = models.ImageField(
        u"封面图片",
        null=True,
        upload_to='upload/products/%Y/%m/%d/'
    )
    create_at = models.DateField(u"创建时间", auto_now_add=True)
    open_at = models.DateField(u"上架时间")
    close_at = models.DateField(u"下架时间")
    status = models.SmallIntegerField(u"状态", choices=status_choices, default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'商品'
        verbose_name_plural = u'商品'
        ordering = (('open_at'), ('status'),)


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
        verbose_name = u'属性'
        verbose_name_plural = u'属性'


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
        (0, '女'),
        (1, '男'),
        (2, '未知'),
    )

    status_choices = (
        (0, '未激活'),
        (1, '激活')
    )

    username = models.CharField(u'帐号', max_length=15)
    realname = models.CharField(u'姓名', max_length=15)
    phone = models.CharField(u'手机', max_length=15)
    password = models.CharField(u'密码', max_length=50)
    avatar = models.FileField(u'头像', upload_to='upload/avatar/%Y/%m/%d/')
    sex = models.SmallIntegerField(
        u'性别',
        choices=sex_choices,
        default='2'
    )
    point = models.IntegerField(u'积分', default=0)
    address = models.CharField(u'收件地址', max_length=255)
    register_at = models.DateField(u'注册时间', auto_now_add=True)
    status = models.SmallIntegerField(u'状态', default=1)

    class Meta:
        verbose_name = u'客户'
        verbose_name_plural = u'客户'
        ordering = (('register_at'), )

    def __unicode__(self):
        return self.username


class CustomerConnect(models.Model):
    customer = models.ForeignKey(
        Customer,
        verbose_name=u'用户',
        on_delete=models.CASCADE,
        related_name='connect',
        editable=False,
    )
    platform = models.CharField(max_length=10)
    openid = models.CharField(max_length=50)


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
    create_at = models.DateField(u'发生时间')

    def __unicode__(self):
        return "%s %s %d" % (self.event_name, self.opertion, self.score)

    class Meta:
        verbose_name = u'积分记录'
        verbose_name_plural = u'积分记录'
        ordering = (('create_at'),)


class CustomerRelation(models.Model):
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
    level = models.SmallIntegerField(u'级别')
    create_at = models.DateField(u'时间', auto_now_add=True)

    class Meta:
        verbose_name = u'客户关系'
        verbose_name_plural = u'客户关系'


class Order(models.Model):
    type_choices = [
        ('G', u'产品'),
        ('S', u'项目'),
    ]
    status_choices = [
        (0, u'未下单'),
        (1, u'已下单'),
        (2, u'未支付'),
        (3, u'已付款'),
        (4, u'待审核'),
        (5, u'已审核'),
        (6, u'已发货'),
        (7, u'已消费'),
        (8, u'已完成'),
    ]
    customer = models.ForeignKey(
        Customer,
        verbose_name=u'客户',
        on_delete=models.CASCADE
    )
    products = models.TextField(u'商品信息')
    total_price = models.FloatField(u'总价')
    type = models.CharField(
        u'类型',
        max_length=1,
        choices=type_choices,
        editable=False
    )
    booking_at = models.DateField(u'预约时间')
    address = models.CharField(u'收件地址', max_length=255)
    create_at = models.DateField(u'创建时间', auto_now_add=True)
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=0)

    class Meta:
        verbose_name = u'订单'
        verbose_name_plural = u'订单'
        ordering = (('create_at'), ('status'))


class Doctor(models.Model):
    name = models.CharField(u'姓名', max_length=15)
    description = models.TextField(u'简介')
    product = models.ForeignKey(
        Product,
        verbose_name=u'项目',
        limit_choices_to={'type': 'S'},
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'医生'
        verbose_name_plural = u'医生'


class DoctorDuty(models.Model):
    status_choices = [
        (1, u'正常值班'),
        (0, u'缺勤'),
    ]
    doctor = models.OneToOneField(
        Doctor,
        verbose_name='医生',
        on_delete=models.CASCADE
    )
    duty_at = models.DateTimeField(u'值班时间')
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=1)

    class Meta:
        verbose_name = u'值班'
        verbose_name_plural = u'值班'


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
        help_text=u'适合尺寸：200x120'
    )
    create_at = models.DateField(u'创建时间', auto_now_add=True)
    public_at = models.DateField(u'发布时间')
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=1)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'


class Setting(models.Model):
    key = models.CharField(u'字段', max_length=50)
    name = models.CharField(u'说明', max_length=50)
    values = models.TextField(u'值')

    class Meta:
        verbose_name = u'设置'
        verbose_name_plural = u'设置'

    def __unicode__(self):
        return self.key
