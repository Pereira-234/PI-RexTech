import uuid
from django.db import models
from rexapp.models.Produto import Produto
from rexapp.models.Usuario import Usuario

class Item(models.Model):
    produto_id = models.ForeignKey(Produto, on_delete=models.RESTRICT, related_name='produto')
    quantidade = models.PositiveIntegerField(default = 1)    
    usuario_id = models.ForeignKey(Usuario, on_delete=models.RESTRICT, related_name='usuario')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def subtotal(self):
        return self.produto.preco * self.quantidade
    
    def __str__(self):
        return self.nome
