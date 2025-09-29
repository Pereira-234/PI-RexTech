from django.db import models
from django.db import models
from django.contrib.auth.models import User  # Import correto para o modelo User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_nascimento = models.DateField(default =None, null = True, blank=True)
    cpf = models.TextField(max_length = 11)
    email = models.CharField(max_length = 200)


    def __str__(self):
        return '{}'.format(self.user.username)
    @receiver(post_save, sender=User)

    def create_user_usuario(sender, instance, created, **kwargs):
        try:
            if created:
                Usuario.objects.create(user=instance)
        except:
            pass
    @receiver(post_save, sender=User)
    def save_user_usuario(sender, instance, **kwargs):
        try:
            if hasattr(instance, 'usuario'):
                instance.usuario.save()
        except:
            pass