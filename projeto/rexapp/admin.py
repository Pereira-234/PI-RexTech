from django.contrib import admin
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
from rexapp.models.Imagem import Imagem
from rexapp.models.Usuario import Usuario
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as transl
from django.utils.html import format_html
# Register your models here.
class UsuarioAdmin(UserAdmin):
    # define um botao para realizar a edicao
    def action_buttons(self, obj):
        ret = format_html('<a class="btn" href="/admin/core/usuario/{}/change/">Editar</a>', obj.id) + \
              format_html('&nbsp;&nbsp;') + \
              format_html('<a class="btn" href="/admin/core/usuario/{}/delete/">Excluir</a>', obj.id)
        return ret

    # define o titulo da coluna de acoes (editar, excluir) 
    action_buttons.short_description = 'Ações'

    # define a ordenacao default dos registros
    ordering = ['nome']
    # define os campos que serao exibidos na tela de listagem
    list_display = ['nome', 'email', 'is_active', 'is_staff', 'last_login', 'action_buttons']
    list_display_links = None #['nome', 'email']
    # define os campos somente de leitura
    readonly_fields = ['last_login']



    # define os campos que serao editados durante a inclusao ou alteracao.
    # Aqui tambem podem ser definidos grupos para agrupar campos
    fieldsets = (
        (
            None, # None = "Sem agrupamento"
            {'fields': ('nome', 'email', 'password')},
        ),
        (
            transl('Permissões'), # Nome do grupo de campos, usando metodo para fazer traducao
            {'fields': ('is_active', 'is_staff', 'is_superuser')},
        ),
        (
            transl('Outras Informações'), # Nome do grupo de campos, usando metodo para fazer traducao
            {'fields': ('last_login',)},
        ),
    )
    # define os campos utilizados na tela de inclusao
    add_fieldsets = (
        (
            # None = "Sem agrupamento"
            'Dados de Acesso', 
            {   
                # defincao das classes CSS para serem aplicadas
                'classes': (
                    'wide', # wide: insere um espacamento horizontal extra entre os elementos
                    # 'collapse', # collapse: o grupo aparece 'recolhido' e o usuario podera expandir se quiser
                    # 'your_custom_CSS_class', # pode utilizar outras classes definidas em CSS
                ),
                # campos
                'fields': (
                    'nome',
                    'email', 
                    'password1', # senha
                    'password2', # confirmação da senha
                )
            },
        ),
        (
            transl('Permissões'), # Nome do grupo de campos, usando metodo para fazer traducao
            {
                # pode ser inserida uma breve explicacao sobre o grupo de campos
                'description': ('Defina aqui as permissões de acesso deste usuário.'),
                # campos do grupo
                'fields': (
                    'is_active', 
                    'is_staff', 
                    'is_superuser'
                    )
                },
        ),
    )



"""
REGISTRA AS INTERFACES DE USUARIO DO MODULO ADMIN
"""
admin.site.disable_action("delete_selected")

admin.site.register(Usuario, UsuarioAdmin)

admin.site.register(Produto)
admin.site.register(Categoria)
admin.site.register(Fabricante)
admin.site.register(Imagem)
