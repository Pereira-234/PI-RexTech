from django.db import models
from rexapp.models.Produto import Produto
class Imagem(models.Model):
    imagem = models.ImageField(null = False, blank= True)
    Produto_id = models.ForeignKey(Produto, on_delete=models.RESTRICT, related_name='fabricante')