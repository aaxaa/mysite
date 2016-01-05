# coding:utf8
from django.contrib import admin
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
    list_display = ('name', 'model', 'type', 'price', 'stock', 'status', 'recommend')
    list_filter = ('recommend', 'type', 'status')

    date_hierarchy = 'create_at'

    inlines = (ProductItemInline, )

class ShopcartProductInline(admin.TabularInline):
    model = ShopcartProduct

class ShopcartAdmin(admin.ModelAdmin):
    inlines = (ShopcartProductInline, )


class ItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'display_order')
    fields = ('category', 'name', 'display_order')

class OrderProductInline(admin.TabularInline):
    model = OrderProduct

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer',  'total_price', 'create_at', 'status')
    list_filter = ('status',)

    date_hierarchy = 'create_at'

    inlines = (OrderProductInline, )



class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'realname', 'phone', 'point', 'register_at')
    list_filter = ('sex',)

    date_hierarchy = 'register_at'

    def has_delete_permission(self, request, obj=None):
        return False


class CustomerPointLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'opertor', 'event_name', 'opertion', 'score', 'create_at')
    list_filter = ()

    date_hierarchy = 'create_at'

    def has_delete_permission(self, request, obj=None):
        return False


class CustomerRelationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'upper', 'level', 'create_at')
    list_filter = ()

    def has_delete_permission(self, request, obj=None):
        return False


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'create_at', 'public_at', 'status')
    list_filter = ('type', 'status')


class SettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'values')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerPointLog, CustomerPointLogAdmin)
admin.site.register(CustomerRelation, CustomerRelationAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(Shopcart, ShopcartAdmin)
