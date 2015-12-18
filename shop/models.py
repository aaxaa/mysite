# coding:utf-8
from __future__ import unicode_literals
from django.db import models
from tinymce import models as tinymce_models


class Category(models.Model):
    parent = models.ForeignKey(
        'self',
        verbose_name=u'上级分类',
        null=True,
        blank=True,
        related_name="children"
    )
    name = models.CharField(u"类别名称", max_length=50)
    level = models.SmallIntegerField(editable=False)
    display_order = models.SmallIntegerField(u"显示排序")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'分类'
        verbose_name_plural = u'分类'
        ordering = (('display_order'), )


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

    model = models.CharField(u"商品序号", max_length=50)
    name = models.CharField(u"商品名称", max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=u'商品分类')
    description = models.TextField(u"商品简介")
    type = models.CharField(
        u"商品类型",
        max_length=1,
        choices=type_choices,
        default='G'
    )
    price = models.FloatField(u"商品价格")
    stock = models.IntegerField(u"库存数量")
    content = tinymce_models.HTMLField(u"产品详情")
    cover = models.FileField(u"封面图片", null=True, upload_to='upload/products/%Y/%m/%d/')
    image1 = models.FileField(u"产品图片1", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image2 = models.FileField(u"产品图片2", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image3 = models.FileField(u"产品图片3", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image4 = models.FileField(u"产品图片4", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image5 = models.FileField(u"产品图片5", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image6 = models.FileField(u"产品图片6", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image7 = models.FileField(u"产品图片7", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image8 = models.FileField(u"产品图片8", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
    image9 = models.FileField(u"产品图片9", null=True, blank=True, upload_to='upload/products/%Y/%m/%d/')
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=u'商品分类')
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
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name=u'字段')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=u'商品')
    value = models.CharField(u'值', max_length=50)

    class Meta:
        verbose_name = u'产品属性'
        verbose_name_plural = u'产品属性'


class Customer(models.Model):
    sex_choices = (
        ('0', '女'),
        ('1', '男'),
        ('2', '未知'),
    )

    username = models.CharField(u'帐号', max_length=15)
    realname = models.CharField(u'姓名', max_length=15)
    phone = models.CharField(u'手机', max_length=15)
    password = models.CharField(u'密码', max_length=50)
    avatar = models.FileField(u'头像', upload_to='upload/products/%Y/%m/%d/')
    sex = models.SmallIntegerField(
        u'性别',
        choices=sex_choices,
        default='2'
    )
    point = models.IntegerField(u'积分')
    address = models.CharField(u'收件地址', max_length=255)
    register_at = models.DateField(u'注册时间', auto_now_add=True)

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
    description = models.CharField(u'简介', max_length=255)
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
    status_choices = [
        (1, u'发布'),
        (0, u'草稿'),
    ]
    title = models.CharField(u'标题', max_length=255)
    content = tinymce_models.HTMLField(u'内容')
    type = models.CharField(u'类型', max_length=10)
    create_at = models.DateField(u'创建时间')
    public_at = models.DateField(u'发布时间')
    status = models.SmallIntegerField(u'状态', choices=status_choices, default=1)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'


class Setting(models.Model):
    key = models.CharField(u'字段', max_length=50)
    values = models.TextField(u'值')

    class Meta:
        verbose_name = u'设置'
        verbose_name_plural = u'设置'

    def __unicode__(self):
        return self.key
