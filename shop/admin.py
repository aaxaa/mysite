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

    fieldsets = (
        (None, {
            'fields': ('model', 'name', 'category', 'type', 'price', 'stock', 'cover', 'description', 'content', 'status', 'open_at', 'close_at',),
        }),

        (u'产品图片', {
            'classes': ('collapse', ),
            'fields': ('image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'image9'),
        }),
    )

    inlines = (ProductItemInline, )


class ItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'display_order')
    fields = ('category', 'name', 'display_order')

    #inlines = (ProductItemInline, )


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer',  'type', 'products', 'total_price', 'create_at', 'status')
    list_filter = ('type', 'status')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'realname', 'phone', 'point', 'register_at')
    list_filter = ()


class CustomerPointLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'opertor', 'event_name', 'opertion', 'score', 'create_at')
    list_filter = ()


class CustomerRelationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'upper', 'level', 'create_at')
    list_filter = ()


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
