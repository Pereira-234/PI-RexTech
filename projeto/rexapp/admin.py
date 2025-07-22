from django.contrib import admin
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
# Register your models here.

admin.site.register(Produto)
admin.site.register(Categoria)
admin.site.register(Fabricante)