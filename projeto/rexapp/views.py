from django.shortcuts import get_object_or_404, render
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante
from rexapp.models.Imagem import Imagem
from rexapp.models.Usuario import Usuario

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
        lembrar = request.POST.get('captcha')

        user = authenticate(request, email=email, password=senha)
        if user is not None:
            if lembrar:  # checkbox "não sou um robô" (apenas exemplo)
                login(request, user)
                return redirect('home')  # redireciona para a página inicial
            else:
                messages.error(request, 'Confirme que você não é um robô.')
        else:
            messages.error(request, 'Email ou senha inválidos.')

    return render(request, 'login.html')

def sign_up_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        email_confirm = request.POST.get('email_confirm')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')
        captcha = request.POST.get('captcha')

        
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

       
        usuario = Usuario.objects.create_user(email=email, password=senha, nome=nome)
        usuario.save()

        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('login')

    return render(request, 'sign_up.html')
