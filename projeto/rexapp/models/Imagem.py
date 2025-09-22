from django.db import models
from rexapp.models.Produto import Produto
class Imagem(models.Model):
    imagem = models.ImageField(null = False, blank= True)
    produto = models.ForeignKey(Produto, on_delete=models.RESTRICT, related_name='imagens', null=True, blank=True)