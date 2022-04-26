from django.contrib import admin
from .models import Product


admin.site.site_header = "Buy & Sell Website"
admin.site.site_title = "ABC Buying"
admin.site.index_title = "Manage ABC Buying"

class ProductAdmin(admin.ModelAdmin):
   list_display = ('name', 'price', 'desc')


admin.site.register(Product, ProductAdmin)