from django.db import models
from rexapp.models.Usuario import Usuario
from rexapp.models.Produto import Produto

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.IntegerField(default=1)
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processando')
    data_pedido = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.nome} - {self.produto.nome if self.produto else 'Produto removido'}"
    
    class Meta:
        ordering = ['-data_pedido']  # Ordena por data mais recente
