from django.db import models
from django.conf import settings # Importa a configuração para User Model

class Avaliacao(models.Model):
    # Relacionamento com o Produto que está sendo avaliado
    produto = models.ForeignKey(
        'Produto', 
        on_delete=models.CASCADE, 
        related_name='avaliacoes' # Usado para acessar as avaliações do produto
    )
    
    # Relacionamento com o Usuário que fez a avaliação
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Campo para a nota (1 a 5 estrelas)
    NOTA_CHOICES = [
        (1, '1 Estrela'),
        (2, '2 Estrelas'),
        (3, '3 Estrelas'),
        (4, '4 Estrelas'),
        (5, '5 Estrelas'),
    ]
    nota = models.IntegerField(choices=NOTA_CHOICES)
    
    # Comentário (opcional)
    comentario = models.TextField(blank=True, null=True)
    
    # Data da criação
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que um usuário só pode avaliar o mesmo produto uma vez
        unique_together = ('produto', 'usuario') 
        ordering = ['-data_avaliacao'] # Ordena pela mais recente

    def __str__(self):
        return f'{self.produto.nome} - {self.nota} estrelas por {self.usuario.username}'