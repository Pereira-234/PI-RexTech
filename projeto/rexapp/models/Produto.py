import uuid
from django.db import models
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante

def rename_image(instance, filename):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Generate a new unique filename
    new_filename = f"{uuid.uuid4()}.{ext}"
    # Define the upload path
    return new_filename

class Produto(models.Model):
    nome = models.CharField(max_length = 100)
    imagem_url = models.ImageField(null = False, blank= True, upload_to=rename_image)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    especificacoes = models.TextField(blank=True)
    Categoria_id = models.ForeignKey(Categoria, on_delete=models.RESTRICT, related_name='categoria')
    Fabricante_id = models.ForeignKey(Fabricante, on_delete=models.RESTRICT, related_name='fabricante')
    
    def __str__(self):
        return self.nome