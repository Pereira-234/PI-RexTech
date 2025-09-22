from django.db import models
from rexapp.models.Produto import Produto
import os
import uuid 


def rename_image(instance, filename):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Generate a new unique filename
    new_filename = f"{uuid.uuid4()}.{ext}"
    # Define the upload path
    return new_filename

class Imagem(models.Model):
    imagem = models.ImageField(null = False, blank= True, upload_to=rename_image)
    produto = models.ForeignKey(Produto, on_delete=models.RESTRICT, related_name='imagens', null=True, blank=True)

