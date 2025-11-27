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
from .forms import UsuarioPerfilForm
from django.conf import settings
import requests


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
    produtos = Produto.objects.all()
    fabricantes_selecionados_ids = request.GET.getlist('fabricante')
    categorias_selecionadas_ids = request.GET.getlist('categoria')
    
    if fabricantes_selecionados_ids:
        produtos = produtos.filter(Fabricante_id__id__in=fabricantes_selecionados_ids)

    if categorias_selecionadas_ids:
        produtos = produtos.filter(Categoria_id__id__in=categorias_selecionadas_ids)


    todas_categorias = Categoria.objects.all()
    todos_fabricantes = Fabricante.objects.all()

    context = {
        'produtos': produtos, # A lista de produtos já filtrada
        'todas_categorias': todas_categorias, # Para montar os checkboxes
        'todos_fabricantes': todos_fabricantes, # Para montar os checkboxes
        # Converte os IDs de string (da URL) para inteiros, para comparar no template
        'categorias_selecionadas': [int(id) for id in categorias_selecionadas_ids],
        'fabricantes_selecionados': [int(id) for id in fabricantes_selecionados_ids],
        'Título': 'RexApp - Hardware'
    }


    return render(request, "hardware.html", context= context)
    
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


from django.conf import settings

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


from django.conf import settings

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
    messages.success(request, "Você saiu da sua conta.")
    return redirect('login')  # redireciona pra página de login
