# coding:utf8
from django.contrib import admin
from .models import *

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'display_order')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'type', 'price', 'stock', 'status')
    list_filter = ('type', 'status')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(CustomerPointLog)
admin.site.register(CustomerRelation)
admin.site.register(Doctor)
admin.site.register(Notice)
admin.site.register(Setting)
admin.site_title = 'Shop'
