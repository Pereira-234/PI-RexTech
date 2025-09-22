from django.contrib import admin
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
from rexapp.models.Imagem import Imagem
# Register your models here.

admin.site.register(Produto)
admin.site.register(Categoria)
admin.site.register(Fabricante)
admin.site.register(Imagem)