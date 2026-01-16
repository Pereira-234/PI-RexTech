from django import forms
from .models.Avaliacao import Avaliacao
from .models.Usuario import Usuario
from .models.Produto import Produto
from .models.Categoria import Categoria
from .models.Fabricante import Fabricante
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


    def __init__(self, *args, **kwargs):
            # 1. Captura a instância (o objeto Usuario logado)
            instance = kwargs.get('instance', None)
            
            # Chama o construtor original do ModelForm
            super().__init__(*args, **kwargs)

            # 2. Itera sobre os campos e define o placeholder
            if instance:
                # Campos que você quer definir o placeholder com o valor atual
                placeholder_fields = ['nome', 'email', 'endereco']
                
                for field_name in placeholder_fields:
                    # Obtém o valor atual do campo na instância
                    current_value = getattr(instance, field_name, '')
                    
                    # Certifica-se de que o valor é tratado como string
                    placeholder_text = str(current_value)
                    
                    # Se o valor atual não estiver vazio, use-o como placeholder
                    if placeholder_text:
                        self.fields[field_name].widget.attrs['placeholder'] = placeholder_text
                        
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


class AvaliacaoForm(forms.ModelForm):
    # Personaliza o widget da nota para ser mais fácil de estilizar (opcional)
    nota = forms.ChoiceField(
        choices=Avaliacao.NOTA_CHOICES,
        widget=forms.HiddenInput() # Oculta o input padrão, pois usaremos estrelas no CSS/JS
    )
    
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deixe seu comentário (opcional)'})
        }
        labels = {
            'comentario': 'Comentário',
        }

class ProdutoAdminForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 
            'imagem_url', 
            'preco', 
            'especificacoes', 
            'Categoria_id', 
            'Fabricante_id',
        ]
        widgets = {
            # Recomendado usar um Textarea para campos de texto longo como 'especificacoes'
            'especificacoes': forms.Textarea(attrs={'rows': 5}),
        }

class UsuarioAdminCreationForm(forms.ModelForm):
    """
    Formulário para o Admin criar um novo usuário. 
    Exige senha e confirmação.
    """
    password = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput,
        help_text="Digite uma senha segura."
    )
    password_confirm = forms.CharField(
        label="Confirmação de Senha", 
        widget=forms.PasswordInput,
        help_text="Digite a mesma senha novamente."
    )

    class Meta:
        model = Usuario
        # Inclua todos os campos que devem ser definidos na criação
        fields = (
            'email', 'nome', 'cpf', 'nascimento', 'foto', 'endereco',
            'is_active', 'is_staff', 'is_superuser'
        )

    def clean(self):
        """Verifica se as senhas conferem."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("As senhas informadas não conferem.")
        
        return cleaned_data

    def save(self, commit=True):
        """Cria o usuário e define a senha hash."""
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario

# ----------------------------------------------------
# Formulário de Edição de Usuário (Admin)
# ----------------------------------------------------
class UsuarioAdminChangeForm(forms.ModelForm):
    """
    Formulário para o Admin editar um usuário existente.
    Não inclui a senha, que deve ser tratada separadamente.
    """
    class Meta:
        model = Usuario
        # Inclua todos os campos editáveis
        fields = (
            'email', 'nome', 'cpf', 'nascimento', 'foto', 'endereco',
            'is_active', 'is_staff', 'is_superuser'
        )
        
    def clean_password(self):
        # Impedir que a senha seja salva como texto simples se o campo não for explicitamente editado
        return self.initial.get("password")




class CategoriaAdminForm(forms.ModelForm):
    class Meta:
        model = Categoria
        # Se seu modelo Categoria tiver apenas 'nome' e 'descricao', use-os.
        # Ajuste esta lista para os campos exatos do seu modelo Categoria.
        fields = ['nome']

class FabricanteAdminForm(forms.ModelForm):
    class Meta:
        model = Fabricante
        # Se seu modelo Categoria tiver apenas 'nome' e 'descricao', use-os.
        # Ajuste esta lista para os campos exatos do seu modelo Categoria.
        fields = ['nome']