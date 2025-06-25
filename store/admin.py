from django.contrib import admin
from .models import Product
from django.contrib.auth.admin import UserAdmin
from store import models


#to prepoluate slug
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('product_name',)}
    list_display=('product_name','price','stock','category','modified_date','is_available')
    

admin.site.register(Product,ProductAdmin)