from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta

import urllib.request as urllib2
import http.cookiejar as cookielib
import  xml.etree
import xmltodict
import pprint
import json
import requests

from .models import *
from .forms import *


# Método que salva o usuário logado no carrinho de compra
def save_client(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)

        if request.user.is_authenticated and request.user.client:
            cart_obj.client = request.user.client
            cart_obj.save()


# Método que retorna os dados do link 
def file_get_contents(url):
    url = str(url).replace(" ", "+") # just in case, no space in url
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    try:
        page = urllib2.urlopen(req)
        return page.read()
    except urllib2.HTTPError as e:
        print(e.fp.read())
    return ''


# Exibe a quantidade de produtos no carrinho
def cart_quantity(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = None
    return cart


# Exibe a quantidae de produtos nos favoritos
def favorites_quantity(request):
    if request.user.is_authenticated and request.user.client:
        client = request.user.client
    else:
        client = None
    return client


# Página principal do site
def index(request): 
    context = {
        'products': Product.objects.all(),
        'categories': Category.objects.all(),
        'colors': Color.objects.all(),
        'makers': Maker.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
        
        # Seleciona os produtos adicionados em até cinco dias atrás
        'news': Product.objects.filter(created__gte=datetime.now() - timedelta(days=5)),
        'views': Product.objects.all().order_by('-views')[:7]
    }
    return render(request, 'index.html', context)

    
# Página de categorias do produtos
def categories(request):
    context = {
        'categories': Category.objects.all(), 

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)), 
    }
    return render(request, 'categories.html', context)


# Página de categorias do produtos
def category_product(request, slug):
    category = get_object_or_404(Category, slug=slug)

    context = {
        'category': category,
        'categories': Category.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
    }
    return render(request, 'category_product.html', context)


# Página do produto
def product(request, slug):
    # Seleciona o produto através do slug
    product = get_object_or_404(Product, slug=slug)
    product.views += 1
    product.save()

    context = {
        'product': product,
        'categories': Category.objects.all(),
        'views': Product.objects.all().order_by('-views')[:7],

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
    }
    return render(request, 'product.html', context)


# Método que cria e atualiza o carrrinho de compras 
def favorite(request, id):
    if request.user.is_authenticated and request.user.client:
        pass
    else:
        return redirect(f'/entrar/?next=/favoritos-{id}')

    favorite = Favorite.objects.get(client=request.user.client)
    product = get_object_or_404(Product, id=id)
    product_in_favorite = favorite.favoriteproduct_set.filter(product=product)

    # Se o produto já existe no carrinho 
    if product_in_favorite.exists():
        messages.error(request, 'Produto já estava adicinado aos favoritos')      

    # Se o produto não existe no carrinho 
    else:
        favoriteproduct = FavoriteProduct.objects.create(favorite=favorite, product=product)
        favoriteproduct.save()
        messages.error(request, 'Produto adicinado aos favoritos')

    return redirect('core:favorites')


# Método que cria e atualiza o carrrinho de compras 
def cart(request, id):
    product = get_object_or_404(Product, id=id)
    
    # Recupera a sessão ou atribui 'None', caso ela não exista
    cart_id = request.session.get('cart_id', None)
    
    # Se a sessão existe
    if cart_id:

        # Salva o usuário logado no carrinho de compras
        save_client(request)

        # Pega o carrinho e filtra pelo produto selecionado
        cart_obj = Cart.objects.get(id=cart_id)
        product_in_cart = cart_obj.cartproduct_set.filter(product=product)

        # Se o produto já existe no carrinho 
        if product_in_cart.exists():
            cartproduct = product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.total += product.price
            cartproduct.save()

            cart_obj.total += product.price
            cart_obj.save()
            

        # Se o produto não existe no carrinho 
        else:
            cartproduct = CartProduct.objects.create(
                cart = cart_obj,
                product = product,
                quantity = 1,
                total = product.price
            )

            cart_obj.total += product.price
            cart_obj.save()
            
    # Se a sessão não existe
    else:
        cart_obj = Cart.objects.create(total = 0)
        request.session['cart_id'] = cart_obj.id

        cartproduct = CartProduct.objects.create(
                cart = cart_obj,
                product = product,
                quantity = 1,
                total = product.price
        )

        cart_obj.total += product.price
        cart_obj.save()

        # Salva o usuário logado no carrinho de compras
        save_client(request)

    return redirect('core:my_cart')


# Página que exibe os produtos no carrinho de compras
def my_cart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)

        # Salva o usuário logado no carrinho de compras
        save_client(request)
    else:
        cart = None

    context = {
        'cart': cart,
        'categories': Category.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
    }
    return render(request, 'my_cart.html', context)


# Método que realiza alterações no carrinho de compras
def edit_cart(request, id):
    action = request.GET.get('action')
    cart_product = CartProduct.objects.get(id=id)
    cart = cart_product.cart

    # Salva o usuário logado no carrinho de compras
    save_client(request)

    if action == 'inc':
        cart_product.quantity += 1
        cart_product.total += cart_product.product.price
        cart_product.save()

        cart.total += cart_product.product.price
        cart.save()

    elif action == 'dec':
        cart_product.quantity -= 1
        cart_product.total -= cart_product.product.price
        cart_product.save()

        cart.total -= cart_product.product.price
        cart.save()

        if cart_product.total == 0:
            cart_product.delete()

    elif action == 'del':
        cart.total -= cart_product.total
        cart.save()

        cart_product.delete()

    else:
        pass
    
    return redirect('core:my_cart')


# Método que apaga o carrinho
def remove_cart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        cart.cartproduct_set.all().delete()
        cart.total = 0
        cart.save()

    return redirect('core:my_cart')


# Método que exibe a página de compra ou salva seus dados no banco
def buy(request):
    if str(request.method) == 'POST':
        form = BuyModelForm(request.POST)
        cart_id = request.session.get('cart_id')

        if cart_id:
            cart = Cart.objects.get(id=cart_id)

            form.instance.cart = cart
            form.instance.total = cart.total
            form.instance.status = "Pedido Recebido"

            if form.is_valid():
                form.save()
                del request.session['cart_id']

                messages.success(request, 'Compra efetuada com sucesso!')
                return redirect('core:index')

            else:
                messages.error(request, 'Erro com os dados do formulário')
                return redirect('core:index')
                       
        else:
            messages.error(request, 'Erro ao efetuar a compra!')
            return redirect('core:index')

    else:
        # Salva o usuário logado no carrinho de compras
        save_client(request)
        
        if request.user.is_authenticated and request.user.client:
            pass
        else:
            return redirect('/entrar/?next=/comprar')


        cart_id = request.session.get('cart_id', None)
        form = BuyModelForm()
        form_delivery = DeliveryForm()

        if cart_id:

            # Exibe a quantidade de produtos no carrinho
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None

            # Exibe a quantidade de produtos nos favoritos
            if request.user.is_authenticated and request.user.client:
                client = request.user.client
            else:
                client = None

            cart = Cart.objects.get(id=cart_id)

            context = {
            'cart': cart,
            'form': form,
            'form_delivery': form_delivery,
            'categories': Category.objects.all(),

            'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
            'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
            }
            return render(request, 'buy.html', context)
        else:
            messages.error(request, 'Erro ao efetuar a compra!')
            return redirect('core:index')


# Página de registro do usuário
def register_client(request):
    if str(request.method) == 'POST':
        form = RegisterClientModelForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')

            user = User.objects.create_user(username, email, password)
            form.instance.user = user
            form.save()

            Favorite.objects.create(client=user.client, quantity=0)

            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('core:index')

        else:
            # Exibe a quantidade de produtos no carrinho
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None

            # Exibe a quantidade de produtos nos favoritos
            if request.user.is_authenticated and request.user.client:
                client = request.user.client
            else:
                client = None

            context = {
                'form': form,
                'categories': Category.objects.all(),

                'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
                'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
            }        
            return render(request, 'register_client.html', context)

    else:
        # Exibe a quantidade de produtos no carrinho
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None

        # Exibe a quantidade de produtos nos favoritos
        if request.user.is_authenticated and request.user.client:
            client = request.user.client
        else:
            client = None

        form = RegisterClientModelForm()
        context = {
            'form': form,
            'categories': Category.objects.all(),

            'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
            'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
        }       
        return render(request, 'register_client.html', context)


# Página de login
def login_account(request):
    if str(request.method) == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            page = form.cleaned_data.get('page')

            authenticated = authenticate(username=username, password=password)

            if authenticated:
                try:
                    if(authenticated.client):
                        login(request, authenticated)
                        if page:
                            return redirect(page)
                        else:
                            return redirect('core:index')
                except:
                    messages.error(request, 'Este usuário não tem permissão para entrar!')
                    return redirect('core:login_account')
            else:
                messages.error(request, 'Usuário e/ou Senha incorretos!')
                return redirect('core:login_account')
                 
        else:
            # Exibe a quantidade de produtos no carrinho
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None

            # Exibe a quantidade de produtos nos favoritos
            if request.user.is_authenticated and request.user.client:
                client = request.user.client
            else:
                client = None

            context = {
                'form': form,
                'categories': Category.objects.all(),

                'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
                'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
            }        
            return render(request, 'login.html', context)

    else:
        if 'next' in request.GET:
            # Exibe a quantidade de produtos no carrinho
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None

            # Exibe a quantidade de produtos nos favoritos
            if request.user.is_authenticated and request.user.client:
                client = request.user.client
            else:
                client = None

            next_url = request.GET.get('next')

            form = LoginForm()
            context = {
                'form': form,
                'next_url': next_url,
                'categories': Category.objects.all(),

                'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
                'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
            }       
            return render(request, 'login.html', context)

        else:
            # Exibe a quantidade de produtos no carrinho
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None

            # Exibe a quantidade de produtos nos favoritos
            if request.user.is_authenticated and request.user.client:
                client = request.user.client
            else:
                client = None

            form = LoginForm()
            context = {
                'form': form,
                'categories': Category.objects.all(),
                'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
                'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
            }       
            return render(request, 'login.html', context)


# Método de logout
def logout_account(request):
    logout(request)
    return redirect('core:index')


# Página de dados do usuário
def my_account(request):
    if request.user.is_authenticated and request.user.client:
        pass
    else:
        return redirect('/entrar/?next=/minha-conta')

    client = request.user.client
    buy = Buy.objects.filter(cart__client=client).order_by('-id')

    context = {
        'client': client,
        'buy': buy,
        'categories': Category.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
    }
    return render(request, 'my_account.html', context)


# Página de detalhes das compras
def detail_buy(request, pk):
    buy = get_object_or_404(Buy, id=pk)

    if request.user.is_authenticated:
        if request.user.client != buy.cart.client:
            messages.error(request, 'Você não pode acessar as compras de outro usuário!')
            return redirect('core:index')
    else:
        return redirect(f'/entrar/?next=/minha-conta/detalhe-compra-{pk}')
    
    context = {
        'buy': buy,
        'categories': Category.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
    }
    return render(request, 'detail_buy.html', context)


# Página que exibe os produtos procurados
def search(request):
    search = request.GET.get('search')
    category = request.GET.get('category')

    if category == 'Todos':
        results = Product.objects.filter(Q(name__icontains=search) | Q(detail__icontains=search))
    else:
        results = Product.objects.filter(Q(name__icontains=search) | Q(detail__icontains=search), category__slug=category)
 
    context = {
        'results': results,
        'categories': Category.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),
    }
    return render(request, 'search.html', context)


# Página de produtos favoritos
def favorites(request):
    context = {
        'favorites': FavoriteProduct.objects.filter(favorite__client=request.user.client),
        'categories': Category.objects.all(),

        'cart_product': CartProduct.objects.filter(cart=cart_quantity(request)),
        'favorite_product': FavoriteProduct.objects.filter(favorite__client=favorites_quantity(request)),  
    }
    return render(request, 'favorites.html', context)


# Página de dados de entrega da compra
def delivery(request):
    if str(request.method) == 'POST':
        form = DeliveryForm(request.POST)

        if form.is_valid():
            cep = form.cleaned_data.get('cep')
            xml = file_get_contents(f"http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?nCdEmpresa=&sDsSenha=&sCepOrigem=49072000&sCepDestino={cep}&nVlPeso=1&nCdFormato=1&nVlComprimento=20&nVlAltura=5&nVlLargura=15&sCdMaoPropria=s&nVlValorDeclarado=200&sCdAvisoRecebimento=n&nCdServico=41106&nVlDiametro=0&StrRetorno=xml")
            my_dict = xmltodict.parse(xml)
            
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)

                # Salva o usuário logado no carrinho de compras
                save_client(request)

                if cart.delivery == None:
                    cart.delivery = float(my_dict['Servicos']['cServico']['Valor'].replace(',', '.', 1))
                    cart.total = float(cart.total) + cart.delivery
                    cart.save()

                else:
                    old_delivery = cart.delivery
                    cart.delivery = float(my_dict['Servicos']['cServico']['Valor'].replace(',', '.', 1))
                    cart.total = float(cart.total) - float(old_delivery) + cart.delivery
                    cart.save()

                    return redirect('core:buy')
        else: 
            messages.error(request, 'O CEP deve conter oito dígitos e apenas números!')

            return redirect('core:buy')     
            

# Página não encontrada          
def error404(request, ex):
    template = loader.get_template('404.html')
    return HttpResponse(content=template.render(), content_type='text/html; charset=utf8', status=404)
    
    