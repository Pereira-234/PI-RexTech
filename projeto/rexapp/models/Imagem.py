from django.db import models
from rexapp.models.Produto import Produto, rename_image
import os
import uuid 




class Imagem(models.Model):
    imagem_url = models.ImageField(null = False, blank= True, upload_to=rename_image)
    produto = models.ForeignKey(Produto, on_delete=models.RESTRICT, related_name='imagens', null=True, blank=True)
    


