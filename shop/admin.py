# coding:utf8
from django.contrib import admin
from .models import *

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'display_order')


class ProductItemInline(admin.TabularInline):
    model = ProductItem
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'type', 'price', 'stock', 'status')
    list_filter = ('type', 'status')

    inlines = (ProductItemInline, )


class ItemAdmin(admin.ModelAdmin):
    inlines = (ProductItemInline, )


class OrderAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ('type', 'status')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ()


class CustomerPointLogAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ()


class CustomerRelationAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ()


class DoctorAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ()


class NoticeAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ()


class SettingAdmin(admin.ModelAdmin):
    list_display = ()
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
