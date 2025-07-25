from django.shortcuts import get_object_or_404, render
from rexapp.models.Produto import Produto
from rexapp.models.Categoria import Categoria
from rexapp.models.Fabricante import Fabricante



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

def detalhar(request, id: int):
    produto = get_object_or_404(Produto, pk=id)
    return render(request, "detalhar_produto.html", {'produto': produto})