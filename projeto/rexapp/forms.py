from django import forms
from .models.Usuario import Usuario

class UsuarioPerfilForm(forms.ModelForm):
    # Campos que o usuário pode editar no perfil
    nome = forms.CharField(max_length=150, required=True, label='Nome Completo')
    email = forms.EmailField(required=True, label='E-mail')
    endereco = forms.CharField(max_length=255, required=False, label='Endereço (Rua, Número, Bairro, Cidade)')
    foto = forms.ImageField(required=False, label='Foto de Perfil')
    
    class Meta:
        model = Usuario
        # Inclua apenas os campos que você quer permitir a edição
        fields = ['nome', 'email', 'endereco', 'foto']