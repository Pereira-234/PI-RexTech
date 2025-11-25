from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
from rexapp.models.Imagem import Imagem
from rexapp.models.Usuario import Usuario
from rexapp.models.Itens import Item
from django.contrib.auth import logout

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
    

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        lembrar = request.POST.get('captcha')  # seu checkbox no template é "captcha"

        user = authenticate(request, username=email, password=senha)
        if user is None:
            # tenta usar email kwarg (alguns backends aceitam)
            user = authenticate(request, email=email, password=senha)

        if user is not None:
            login(request, user)
            if lembrar:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # expira ao fechar o browser
            return redirect('home')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'login.html')


def sign_up_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        email_confirm = request.POST.get('email_confirm')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')
        captcha = request.POST.get('captcha')
        foto = request.FILES.get('foto')

        if not captcha:
            messages.error(request, "Confirme que você não é um robô.")
            return render(request, 'sign_up.html')

        if email != email_confirm:
            messages.error(request, "Os e-mails não conferem.")
            return render(request, 'sign_up.html')

        if senha != senha_confirm:
            messages.error(request, "As senhas não conferem.")
            return render(request, 'sign_up.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Já existe uma conta com esse e-mail.")
            return render(request, 'sign_up.html')

        usuario = Usuario.objects.create_user(email=email, password=senha, nome=nome, foto=foto)
        usuario.save()
        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('login')

    return render(request, 'sign_up.html')

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

def adicionar_carrinho_view(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    
    if request.user.is_authenticated:
        usuario = request.user
        chave_sessao = None     
    else:
        usuario = None
        if not request.session.session_key:
            request.session.create()
        chave_sessao = request.session.session_key

    filtro = {'produto' : produto}
    if usuario:
        filtro['usuario'] = usuario
    else:
        filtro['session_key'] = chave_sessao

    item_existente = Item.objects.filter(**filtro).first()

    if item_existente:
        item_existente.quantidade += 1
        item_existente.save()
    else:
        novo_item = Item(produto = produto, quantidade = 1)
        if usuario:
            novo_item.usuario_id = usuario
        else:
            novo_item.session_key = chave_sessao
        novo_item.save()
    return redirect('ver_carrinho')

def remover_carrinho_view(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, id = item_id, usuario = request.user)
    else:
        session_key = request.session.session_key
        item = get_object_or_404(Item, id=item_id, session_key=session_key)
    item.delete()
    return redirect('ver_carrinho')


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
