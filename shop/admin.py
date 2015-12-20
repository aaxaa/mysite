# coding:utf8
from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'display_order')


class ProductItemInline(admin.TabularInline):
    model = ProductItem
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'type', 'price', 'stock', 'status')
    list_filter = ('type', 'status')

    date_hierarchy = 'create_at'

    inlines = (ProductItemInline, )


class ItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'display_order')
    fields = ('category', 'name', 'display_order')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer',  'type', 'products', 'total_price', 'create_at', 'status')
    list_filter = ('type', 'status')

    date_hierarchy = 'create_at'

    def has_delete_permission(self, request, obj=None):
        return False


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


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'product')
    list_filter = ()


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'create_at', 'public_at', 'status')
    list_filter = ('type', 'status')


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'values')
    list_filter = ()


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerPointLog, CustomerPointLogAdmin)
admin.site.register(CustomerRelation, CustomerRelationAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(Setting, SettingAdmin)
