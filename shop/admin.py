# coding:utf8
from django.contrib import admin
from django.http import HttpResponse
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('treenode', 'patha')
    ordering = ['path']

    def patha(self, obj):
        if obj.parent:
            return u"%s > %s" % (obj.parent, obj.name)
        return obj.name

    patha.short_description = u'路径'
    patha.allow_tags = True

    def treenode(self, obj):
        indent_num = len(obj.path.split(':')) - 1
        p = '<div style="text-indent:%spx;">%s</div>' % (indent_num * 25, obj.name)
        return p

    treenode.short_description = u"分类"
    treenode.allow_tags = True


class ProductItemInline(admin.TabularInline):
    model = ProductItem
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'type', 'price', 'status', 'recommend')
    list_filter = ('recommend', 'type', 'status')

    date_hierarchy = 'create_at'

    inlines = (ProductItemInline, )

    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'model', 'type', 'cover')
        }),
        (u'价格设置', {
            'fields': ('payment_type', 'price', 'payment_point')
        }),
        (u'积分设置', {
            'fields': ('point','point_1', 'point_2', 'point_3'),
        }),
        (u'商品详情', {
            'fields': ('description', 'content', 'recommend', 'status')
        }),
    )

class ItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'display_order')
    fields = ('category', 'name', 'display_order')

class OrderProductInline(admin.TabularInline):
    model = OrderProduct

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_txt', 'customer',  'total_price', 'create_at', 'status')
    list_filter = ('status',)

    search_fields = ['customer__realname', 'customer__phone', 'order_txt']

    date_hierarchy = 'create_at'

    actions = ['export_selected_ojects']

    inlines = (OrderProductInline, )


    def export_selected_ojects(self, request, queryset):
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename = "order.csv"'

        writer = csv.writer(response)
        writer.writerow([u'订单号'.encode('utf8'), u'购买产品'.encode('utf8'), u'客户姓名'.encode('utf8'), u'客户手机'.encode('utf8'), u'客户地址'.encode('utf8'), u'其它附言'.encode('utf8'), u'创建时间'.encode('utf8'), u'订单状态'.encode('utf8')])
        for row in queryset.all():
            products_txt = ''
            for p in row.products_in.all():
                products_txt += "%s*%s=%s, " % (p.product.title, p.count, p.price)

            writer.writerow([row.order_txt, products_txt[:-2], row.realname, row.phone, row.address, row.message, row.create_at, row.status])

        return response

    export_selected_ojects.short_description = u'导出所选数据'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'realname', 'phone', 'point', 'register_at')
    list_filter = ('sex',)

    date_hierarchy = 'register_at'

class CustomerPointLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'opertor', 'event_name', 'opertion', 'score', 'create_at')
    list_filter = ('create_at', 'opertion', 'event_name')

    date_hierarchy = 'create_at'

    def has_delete_permission(self, request, obj=None):
        return False

class CustomerOperationLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'create_at', 'message')


class CustomerRelationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'upper', 'level', 'create_at')
    list_filter = ('create_at',)
    
class MessageListFilter(admin.SimpleListFilter):
    title = u'是否答复'
    parameter_name = 'message_type'

    def lookups(self, request, model_admin):
        return (
            ('close', u'已答复'),
            ('open', u'未答复')
        )

    def queryset(self, request, queryset):
        if self.value() == 'close':
            return queryset.filter(answer_text__isnull=False)

        if self.value() == 'open':
            return queryset.filter(answer_text__isnull=True)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'question_text', 'answer_html', 'create_at')
    list_filter = ('create_at', MessageListFilter)


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'create_at', 'status')
    list_filter = ('type', 'status')



admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerPointLog, CustomerPointLogAdmin)
admin.site.register(CustomerRelation, CustomerRelationAdmin)
admin.site.register(CustomerOperationLog, CustomerOperationLogAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(Message, MessageAdmin)
