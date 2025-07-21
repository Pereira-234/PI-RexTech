from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, "home.html")

def detalhar(request):
    return render(request, "detalhar_produto.html")