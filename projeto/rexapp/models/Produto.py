from django.db import models
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
class Produto(models.Model):
    nome = models.CharField(max_length = 100)
    imagem_url = models.ImageField(null = False, blank= True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    especificacoes = models.TextField(blank=True)
    Categoria_id = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='categoria')
    Fabricante_id = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='fabricante')
    
    def __str__(self):
        return self.nome