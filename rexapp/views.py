from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
from rexapp.models.Imagem import Imagem
from rexapp.models.Usuario import Usuario
from django.contrib.auth import logout
from .forms import UsuarioPerfilForm, AvaliacaoForm
from django.conf import settings
import requests
from django.db.models import Avg # Importa para calcular a média
from .models import Avaliacao
from .forms import (
    UsuarioPerfilForm, 
    AvaliacaoForm, 
    ProdutoAdminForm,
    UsuarioAdminCreationForm,  
    UsuarioAdminChangeForm,
    CategoriaAdminForm

)
import re

# Create your views here.

def home(request):
    produto = request.GET.get("produto")
    produtos = Produto.objects.all()
    print(produtos)
    categorias = Categoria.objects.all()
    fabricantes = Fabricante.objects.all()

    context = {
        'produtos': produtos,
        'categorias': categorias,
        'fabricantes': fabricantes,
        'Título': 'RexApp - Home',
    }
    return render(request, "home.html", context = context)

def detalhar(request, id):
    produto = get_object_or_404(Produto, pk=id)
    imagens = produto.imagens.all()  
    return render(request, "detalhar_produto.html", {'produto': produto, 'imagens': imagens})

def hardware(request):
    
    try:
        # Busca a Categoria 'Hardware' no banco de dados
        categoria_hardware = Categoria.objects.get(nome='Hardware')
        
        # Inicializa a queryset APENAS com produtos dessa categoria
        produtos = Produto.objects.filter(Categoria_id=categoria_hardware)
        
    except Categoria.DoesNotExist:
        # Se a categoria 'Hardware' não existir, a lista de produtos é vazia
        produtos = Produto.objects.none()

    fabricantes_selecionados_ids = request.GET.getlist('fabricante')
    categorias_selecionadas_ids = request.GET.getlist('categoria')
    
    # Aplica o filtro de Fabricantes, se houver
    if fabricantes_selecionados_ids:
        produtos = produtos.filter(Fabricante_id__id__in=fabricantes_selecionados_ids)

    # Aplica o filtro de Categorias, se houver
    if categorias_selecionadas_ids:
        produtos = produtos.filter(Categoria_id__id__in=categorias_selecionadas_ids)


    # 3. RECUPERAÇÃO DE DADOS PARA O TEMPLATE
    todas_categorias = Categoria.objects.filter(id__in=produtos.values('Categoria_id').distinct())
    todos_fabricantes = Fabricante.objects.filter(id__in=produtos.values('Fabricante_id').distinct())

    # Se você preferir manter a lista COMPLETA de categorias/fabricantes (para filtros mais amplos), use:
    # todas_categorias = Categoria.objects.all()
    # todos_fabricantes = Fabricante.objects.all()

    context = {
        'produtos': produtos,
        'todas_categorias': todas_categorias,
        'todos_fabricantes': todos_fabricantes,
        'categorias_selecionadas': [int(id) for id in categorias_selecionadas_ids],
        'fabricantes_selecionados': [int(id) for id in fabricantes_selecionados_ids],
        'Título': 'RexApp - Hardware'
    }

    return render(request, "hardware.html", context=context)
    
def verificar_hcaptcha(request):
    resposta_token = request.POST.get('h-captcha-response')
    if not resposta_token:
        return False

    data = {
        'secret': settings.HCAPTCHA_SECRET,
        'response': resposta_token
    }

    resp = requests.post('https://hcaptcha.com/siteverify', data=data).json()
    return resp.get('success', False)


def login_view(request):
    if request.method == 'POST':

        # --- Validação hCaptcha ---
        if not verificar_hcaptcha(request):
            messages.error(request, "Confirme que você não é um robô.")
            return render(request, 'login.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })

        email = request.POST.get('email')
        senha = request.POST.get('senha')
        lembrar = request.POST.get('captcha')

        user = authenticate(request, username=email, password=senha)
        if user is None:
            user = authenticate(request, email=email, password=senha)

        if user is not None:
            login(request, user)
            request.session.set_expiry(1209600 if lembrar else 0)
            return redirect('home')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'login.html', {
        "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
    })


def sign_up_view(request):
    if request.method == 'POST':

        # --- Validação hCaptcha ---
        if not verificar_hcaptcha(request):
            messages.error(request, "Confirme que você não é um robô.")
            return render(request, 'sign_up.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        email_confirm = request.POST.get('email_confirm')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')
        captcha = request.POST.get('captcha')
        foto = request.FILES.get('foto')

        # --- Captura e Limpa o CPF (remove pontos e traços) ---
        cpf_formatado = request.POST.get('cpf')
        cpf_apenas_digitos = re.sub(r'\D', '', cpf_formatado) # Remove caracteres não-dígitos
        
        # Validação de 11 dígitos no backend
        if len(cpf_apenas_digitos) != 11:
            messages.error(request, "O CPF deve conter 11 dígitos.")
            return render(request, 'sign_up.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })
        # ---------------------------------

        if not captcha:
            messages.error(request, "Confirme que você não é um robô.")
            return render(request, 'sign_up.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })

        if email != email_confirm:
            messages.error(request, "Os e-mails não conferem.")
            return render(request, 'sign_up.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })

        if senha != senha_confirm:
            messages.error(request, "As senhas não conferem.")
            return render(request, 'sign_up.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Já existe uma conta com esse e-mail.")
            return render(request, 'sign_up.html', {
                "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
            })

        usuario = Usuario.objects.create_user(
            email=email,
            password=senha,
            nome=nome,
            cpf=cpf_apenas_digitos, 
            foto=foto
        )
        usuario.save()
        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('login')

    return render(request, 'sign_up.html', {
        "HCAPTCHA_SITEKEY": settings.HCAPTCHA_SITEKEY
    })

def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    avaliacoes = produto.avaliacoes.all() # Pega todas as avaliações do produto
    
    # Calcula a média das notas
    media_avaliacoes = avaliacoes.aggregate(Avg('nota'))['nota__avg']

    form = AvaliacaoForm() # Formulário vazio para o método GET

    # Verifica se o usuário já avaliou o produto
    pode_avaliar = not request.user.is_authenticated or \
               not Avaliacao.objects.filter(produto=produto, usuario=request.user).exists()
    
    contexto = {
        'produto': produto,
        'avaliacoes': avaliacoes,
        'media_avaliacoes': media_avaliacoes,
        'form': form,
        'pode_avaliar': pode_avaliar,
    }
    
    return render(request, 'seu_app/detalhe_produto.html', contexto)

# Função separada para lidar com a submissão da avaliação (POST)
@login_required
def avaliar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    # 1. Verifica se o usuário já avaliou (segurança extra)
    if Avaliacao.objects.filter(produto=produto, usuario=request.user).exists():
        messages.error(request, 'Você já avaliou este produto.')
        return redirect('detalhe_produto', produto_id=produto_id)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.produto = produto
            avaliacao.usuario = request.user
            avaliacao.save()
            
            messages.success(request, 'Sua avaliação foi enviada com sucesso!')
            return redirect('detalhe_produto', produto_id=produto_id)
        else:
            # Se o formulário for inválido, redireciona e mostra erro
            messages.error(request, 'Erro ao enviar avaliação. Verifique a nota.')
            
    # Se não for POST ou se o formulário falhar, volta para a página de detalhes
    return redirect('detalhe_produto', produto_id=produto_id)


@login_required
def editar_perfil_view(request):
    # O objeto 'request.user' é o objeto Usuario logado
    usuario = request.user 
    
    if request.method == 'POST':
        # Instancia o formulário com os dados POST e a instância do usuário logado
        # request.FILES é necessário para processar o upload da foto
        form = UsuarioPerfilForm(request.POST, request.FILES, instance=usuario)
        
        if form.is_valid():
            # Salva as alterações no objeto usuario, que atualiza o banco de dados
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso! 🎉')
            return redirect('perfil') # Redireciona para a página de visualização do perfil
        else:
            # Se o formulário for inválido (ex: email repetido)
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os dados.')
            
    else:
        # GET request: cria o formulário preenchido com os dados atuais do usuário
        form = UsuarioPerfilForm(instance=usuario)

    return render(request, 'editar_perfil.html', {
        'form': form,
        'Título': 'Editar Perfil'
    })

@login_required
def perfil_view(request):
    # mostra perfil e permite navegação para editar
    return render(request, 'perfil.html', {
        'usuario': request.user
    })

@login_required
def logout_view(request):
    logout(request)  # encerra a sessão do usuário
    return redirect('login')  # redireciona pra página de login

def is_admin_user(user):
    # Verifica se o usuário está logado E tem a flag is_staff
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin_user, login_url='/login/')
def admin_dashboard(request):
    """
    View principal do Painel de Administração.
    Exibe métricas e atua como centro de navegação.
    """
    try:
        # Busca a contagem de produtos e usuários para exibição no dashboard
        total_produtos = Produto.objects.count()
        total_usuarios = Usuario.objects.count()
        total_categorias = Categoria.objects.count()
    except Exception as e:
        # Em caso de erro (ex: tabelas ainda não migradas), use 0
        total_produtos = 0
        total_usuarios = 0

    context = {
        'total_produtos': total_produtos,
        'total_usuarios': total_usuarios,
        'total_categorias' : total_categorias,
        'Título': 'Painel de Administração',
    }
    return render(request, "admin_dashboard.html", context)




@user_passes_test(is_admin_user, login_url='/login/')
def admin_produto_add(request):
    """View para adicionar um novo produto."""
    # Como o modelo Produto tem ImageField (imagem_url), o enctype="multipart/form-data" 
    # no template e o request.FILES na view são cruciais.
    if request.method == 'POST':
        form = ProdutoAdminForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('admin_produtos_list')
        else:
            messages.error(request, 'Erro ao adicionar produto. Verifique os dados e o upload da imagem.')
    else:
        form = ProdutoAdminForm()
        
    context = {
        'form': form, 
        'Título': 'Adicionar Produto',
        'is_edit': False 
    }
    return render(request, 'admin_produto_form.html', context)


@user_passes_test(is_admin_user, login_url='/login/')
def admin_produto_edit(request, pk):
    """View para editar um produto existente."""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        # Ao editar um objeto com upload de arquivo, passe request.FILES e a instância
        form = ProdutoAdminForm(request.POST, request.FILES, instance=produto) 
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso! 🎉')
            return redirect('admin_produtos_list')
        else:
            messages.error(request, 'Erro ao atualizar produto. Verifique os dados.')
    else:
        form = ProdutoAdminForm(instance=produto)

    context = {
        'form': form, 
        'Título': f'Editar Produto: {produto.nome}',
        'produto': produto,
        'is_edit': True
    }
    return render(request, 'admin_produto_form.html', context)


@user_passes_test(is_admin_user, login_url='/login/')
def admin_produto_delete(request, pk):
    """View para exclusão de produto."""
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        nome_produto = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome_produto}" excluído permanentemente.')
        return redirect('admin_produtos_list')
    
    return redirect('admin_produtos_list')

@user_passes_test(is_admin_user, login_url='/login/')
def admin_produtos_list(request):
    """Lista todos os produtos no painel administrativo."""
    
    # 1. Busca todos os produtos (READ)
    produtos = Produto.objects.all().order_by('id')
    
    context = {
        'produtos': produtos,
        'Título': 'Gerenciar Produtos',
    }
    # 2. Renderiza o template de listagem
    return render(request, "admin_produtos_list.html", context)



@user_passes_test(is_admin_user, login_url='/login/')
def admin_usuarios_list(request):
    """View para listar todos os usuários (READ)."""
    usuarios = Usuario.objects.all().order_by('id')
    
    context = {
        'usuarios': usuarios,
        'Título': 'Gerenciar Usuários',
    }
    return render(request, "admin_usuarios_list.html", context)


@user_passes_test(is_admin_user, login_url='/login/')
def admin_usuario_add(request):
    """View para adicionar um novo usuário (CREATE)."""
    if request.method == 'POST':
        form = UsuarioAdminCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('admin_usuarios_list')
        else:
            messages.error(request, 'Erro ao criar usuário. Verifique os dados.')
    else:
        form = UsuarioAdminCreationForm()
        
    return render(request, 'admin_usuario_form.html', {'form': form, 'Título': 'Adicionar Usuário', 'is_edit': False})


@user_passes_test(is_admin_user, login_url='/login/')
def admin_usuario_edit(request, pk):
    """View para editar um usuário existente (UPDATE)."""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioAdminChangeForm(request.POST, request.FILES, instance=usuario) 
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário "{usuario.nome}" atualizado com sucesso!')
            return redirect('admin_usuarios_list')
        else:
            messages.error(request, 'Erro ao atualizar usuário. Verifique os dados.')
    else:
        form = UsuarioAdminChangeForm(instance=usuario)

    return render(request, 'admin_usuario_form.html', {
        'form': form, 
        'Título': f'Editar Usuário: {usuario.nome}',
        'usuario': usuario,
        'is_edit': True
    })


@user_passes_test(is_admin_user, login_url='/login/')
def admin_usuario_delete(request, pk):
    """View para exclusão de usuário (DELETE)."""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        if usuario == request.user:
             messages.error(request, 'Você não pode excluir sua própria conta de administrador por aqui.')
             return redirect('admin_usuarios_list')

        nome_usuario = usuario.nome
        usuario.delete()
        messages.success(request, f'Usuário "{nome_usuario}" excluído permanentemente.')
        return redirect('admin_usuarios_list')
    
    return redirect('admin_usuarios_list')



# Assumindo que a função is_admin_user está definida...

# ----------------------------------------------------
# CRUD de Categorias
# ----------------------------------------------------

@user_passes_test(is_admin_user, login_url='/login/')
def admin_categorias_list(request):
    """View para listar todas as categorias (READ)."""
    categorias = Categoria.objects.all().order_by('id')
    
    context = {
        'categorias': categorias,
        'Título': 'Gerenciar Categorias',
    }
    return render(request, "admin_categorias_list.html", context)


@user_passes_test(is_admin_user, login_url='/login/')
def admin_categoria_add(request):
    """View para adicionar uma nova categoria (CREATE)."""
    if request.method == 'POST':
        form = CategoriaAdminForm(request.POST) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria adicionada com sucesso! 🎉')
            return redirect('admin_categorias_list')
        else:
            messages.error(request, 'Erro ao adicionar categoria. Verifique os dados.')
    else:
        form = CategoriaAdminForm()
        
    context = {
        'form': form, 
        'Título': 'Adicionar Categoria',
        'is_edit': False 
    }
    return render(request, 'admin_categoria_form.html', context)


@user_passes_test(is_admin_user, login_url='/login/')
def admin_categoria_edit(request, pk):
    """View para editar uma categoria existente (UPDATE)."""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaAdminForm(request.POST, instance=categoria) 
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
            return redirect('admin_categorias_list')
        else:
            messages.error(request, 'Erro ao atualizar categoria. Verifique os dados.')
    else:
        form = CategoriaAdminForm(instance=categoria)

    context = {
        'form': form, 
        'Título': f'Editar Categoria: {categoria.nome}',
        'categoria': categoria,
        'is_edit': True
    }
    return render(request, 'admin_categoria_form.html', context)


@user_passes_test(is_admin_user, login_url='/login/')
def admin_categoria_delete(request, pk):
    """View para exclusão de categoria (DELETE)."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nome_categoria = categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria "{nome_categoria}" excluída permanentemente.')
        return redirect('admin_categorias_list')
    
    # Se for GET, redireciona para a lista para evitar exclusão acidental
    return redirect('admin_categorias_list')

def ver_carrinho_view(request):
    if request.user.is_authenticated:
        itens = Item.objects.filter(usuario=request.user)
    else:
        session_key = request.session.session_key
        if session_key:
            itens = Item.objects.filter(session_key=session_key)
        else: itens = []
    total = sum([item.subtotal() for item in itens])

    return render(request, 'carrinho.html', {'itens': itens, 'total': total})    

@login_required(login_url='/login/')
def adicionar_carrinho_view(request, produto_id):
    # 1. Buscamos o produto pelo ID que veio da URL (produto_id)
    # Se você colocar 'id=request.user' aqui, dará o erro que você viu.
    produto = get_object_or_404(Produto, id=produto_id) 

    # 2. Verificamos se já existe um Item deste produto para este Usuário
    # O erro 'Field id expected a number' acontece se você usar 'id=request.user' aqui embaixo.
    # O correto é usar 'usuario=request.user'.
    item, created = Item.objects.get_or_create(
        produto=produto,
        usuario=request.user, 
        defaults={'quantidade': 1}
    )

    # 3. Se o item já existia, aumentamos a quantidade
    if not created:
        item.quantidade += 1
        item.save()

    return redirect('ver_carrinho')

@login_required(login_url='/login/')
def diminuir_carrinho_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    # Busca o item do usuário para esse produto
    item = Item.objects.filter(usuario=request.user, produto=produto).first()
    
    if item:
        if item.quantidade > 1:
            item.quantidade -= 1
            item.save()
        else:
            # Se a quantidade for 1 e clicar em menos, removemos o item
            item.delete()
            
    return redirect('ver_carrinho')

def remover_carrinho_view(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, id = item_id, usuario = request.user)
    else:
        session_key = request.session.session_key
        item = get_object_or_404(Item, id=item_id, session_key=session_key)
    item.delete()
    return redirect('ver_carrinho')
