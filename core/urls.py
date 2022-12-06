from django.urls import path
from .views import *


app_name = 'core'
urlpatterns = [
    path('', index, name='index'),
    path('categorias/', categories, name='categories'),
    path('categoria/<slug:slug>/', category_product, name='category_product'),
    path('produto/<slug:slug>/', product, name='product'),

    path('favorito-<int:id>/', favorite, name='favorite'),
    path('favoritos/', favorites, name='favorites'),
    
    path('carrinho-<int:id>/', cart, name='cart'),
    path('meu-carrinho/', my_cart, name='my_cart'),
    path('editar-carrinho/<int:id>/', edit_cart, name='edit_cart'),
    path('remover-carrinho/', remove_cart, name='remove_cart'),
    path('comprar/', buy, name='buy'),
    path('entregar/', delivery, name='delivery'),
    
    path('registrar-cliente/', register_client, name='register_client'),
    path('sair/', logout_account, name='logout_account'),
    path('entrar/', login_account, name='login_account'),
    
    path('minha-conta/', my_account, name='my_account'),
    path('minha-conta/detalhe-compra-<int:pk>/', detail_buy, name='detail_buy'),

    path('pesquisar/', search, name='search'),
]