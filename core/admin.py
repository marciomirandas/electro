from django.contrib import admin

from .models import *


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'address', 'modified')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'modified')


@admin.register(Maker)
class MakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'modified')


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'active', 'modified')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'detail', 'price', 'amount', 'slug', 'image', 'category', 'maker', 'color', 'active', 'modified')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'client', 'total', 'modified')


@admin.register(CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    list_display = ('id','__str__', 'cart', 'product', 'quantity', 'total', 'modified')


@admin.register(Buy)
class BuyAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'cart', 'email', 'total', 'created', 'status')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'quantity')


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'favorite', 'product')
