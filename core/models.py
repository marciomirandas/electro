from django.db import models
from stdimage.models import StdImageField
import uuid
from django.contrib.auth.models import User


STATUS = (
    ('Pedido Recebido', 'Pedido Recebido'),
    ('Pedido Processado', 'Pedido Processado'),
    ('Pedido a Caminho', 'Pedido a Caminho'),
    ('Pedido Entregue', 'Pedido Entregue'),
    ('Pedido Cancelado', 'Pedido Cancelado'),
)


def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return 'products/' + str(filename)


class Base(models.Model):
    created = models.DateField('Data de Criação', auto_now_add=True)
    modified = models.DateField('Data de Modificação', auto_now=True)
    active = models.BooleanField('Ativo', default=True)

    class Meta:
        abstract = True


class Client(Base):
    user = models.OneToOneField(User, verbose_name='Usuario', on_delete=models.CASCADE)
    name = models.CharField('Nome', max_length=100)
    address = models.CharField('Endereço', max_length=200)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name


class Category(Base):
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', unique=True)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name


class Maker(Base):
    name = models.CharField('Nome', max_length=100)
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.name


class Color(Base):
    name = models.CharField('Nome', max_length=100)
    code = models.CharField('Código', max_length=10)
    
    class Meta:
        verbose_name = 'Cor'
        verbose_name_plural = 'Cores'

    def __str__(self):
        return self.name


class Product(Base):
    name = models.CharField('Nome', max_length=100)
    detail = models.TextField('Detalhes')
    price = models.DecimalField('Preço', max_digits=8, decimal_places=2)
    amount = models.IntegerField('Estoque')
    slug = models.SlugField('Slug', unique=True)
    image = StdImageField('Imagem', upload_to=get_file_path, variations={'thumb': {'width': 480, 'height': 480, 'crop': True}})
    views = models.PositiveIntegerField()

    category = models.ForeignKey('core.Category', verbose_name='Categoria', on_delete=models.CASCADE)
    maker = models.ForeignKey('core.Maker', verbose_name='Marca', on_delete=models.CASCADE)
    color = models.ForeignKey('core.Color', verbose_name='Cor', on_delete=models.CASCADE)
    

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.name


class Cart(Base):
    client = models.ForeignKey(Client, verbose_name='Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    delivery = models.DecimalField('Entrega', max_digits=8, decimal_places=2, blank=True, null=True)
    total = models.DecimalField('Total', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return 'Carrinho: ' + str(self.id)


class CartProduct(Base):
    cart = models.ForeignKey(Cart, verbose_name='Carrinho', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Produto', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Quantidade')
    total = models.DecimalField('Total', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Produto no Carrinho'
        verbose_name_plural = 'Produtos no Carrinho'

    def __str__(self):
        return 'Carrinho: ' + str(self.cart.id) + ', Produto no Carrinho: ' + str(self.id)


class Buy(Base):
    cart = models.OneToOneField(Cart, verbose_name='Carrinho', on_delete=models.CASCADE)
    recipient = models.CharField('Destinatário', max_length=200)
    email = models.EmailField('Email')
    address = models.CharField('Endereço', max_length=200)
    total = models.DecimalField('Total', max_digits=8, decimal_places=2)
    status = models.CharField('Status', max_length=50, choices=STATUS)
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return 'Cliente: ' + str(self.cart.client) + ', Data: ' +  str(self.created)


class Favorite(Base):
    client = models.OneToOneField(Client, verbose_name='Cliente', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField('Quantidade')
    
    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return str(self.client)


class FavoriteProduct(Base):
    favorite = models.ForeignKey(Favorite, verbose_name='Favorito', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Produto', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Produto Favorito'
        verbose_name_plural = 'Produtos Favoritos'

