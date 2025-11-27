from django.db import models
from django.db import models
from django.contrib.auth.models import User  # Import correto para o modelo User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)  


class UsuarioManager(BaseUserManager):

    def create_user(self, email,  password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail do usuário deve ser informado.')

        usuario = self.model(
            # normaliza os emails deixando tudo em minusculo
            email=self.normalize_email(email), 
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario


    def create_superuser(self, email, password):
        usuario = self.create_user(email, password)
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)

        return usuario



class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True ,blank=False, null=False, 
                              help_text='O e-mail informado será utilizado para fazer o login no sistema.')
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, blank=False,  null=True, default=True)
    nascimento = models.DateField()
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)
    is_staff = models.BooleanField(verbose_name='Administrador', default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.nome or self.email

    class Meta:
        db_table = 'usuario'