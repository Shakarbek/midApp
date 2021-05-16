from django.contrib import admin

from django.contrib import admin
from .models import Seller,  User, Profile
from main.models import Order, Product, Category
#


class UserAdmin(admin.ModelAdmin):
    list_filter = ['is_seller', 'location']


admin.site.register(Seller)
admin.site.register(User, UserAdmin)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Profile)