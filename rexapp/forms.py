from django import forms
from .models.Usuario import Usuario

class UsuarioPerfilForm(forms.ModelForm):
    # Campos que o usuário pode editar no perfil
    
    # 1. Torne o campo 'nome' não obrigatório no formulário
    nome = forms.CharField(
        max_length=150, 
        required=False, 
        label='Nome Completo'
    )
    
    # O email DEVE ser obrigatório (se for o caso)
    email = forms.EmailField(required=True, label='E-mail')
    
    # Endereço já está correto (required=False)
    endereco = forms.CharField(
        max_length=255, 
        required=False, 
        label='Endereço (Rua, Número, Bairro, Cidade)'
    )
    foto = forms.ImageField(required=False, label='Foto de Perfil')
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'endereco', 'foto']

    # 2. Adicione este método para preservar dados existentes se campos opcionais forem vazios
    def save(self, commit=True):
        # Obtém a instância do modelo sem salvá-la no banco (commit=False)
        instance = super().save(commit=False)
        
        # Lista de campos que devem ser preservados se submetidos vazios
        # Adicione todos os seus campos opcionais aqui (exceto ImageField, que é tratado diferente)
        fields_to_preserve = ['nome', 'endereco'] 
        
        for field_name in fields_to_preserve:
            # Verifica se o campo está no cleaned_data (foi processado)
            # E se o valor submetido é uma string vazia ou None
            if self.cleaned_data.get(field_name) in ('', None):
                # Se estiver vazio, removemos o atributo da instância.
                # Isso impede que o save() do Django sobrescreva o valor do banco de dados 
                # com uma string vazia ('').
                if hasattr(instance, field_name):
                    delattr(instance, field_name)

        if commit:
            instance.save()
            
        return instance