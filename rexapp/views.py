from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
