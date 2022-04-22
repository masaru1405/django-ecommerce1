from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product

def index(request):
   return HttpResponse("Hello World!")

def products(request):
   products = Product.objects.all()
   context = {'products': products}
   return render(request, 'myapp/index.html', context)

def product_detail(request, id):
   product = Product.objects.get(id=id)
   context = {'product': product}
   return render(request, 'myapp/detail.html', context)

def product_add(request):
   if request.method == 'POST':
      name = request.POST.get('name')
      price = request.POST.get('price')
      desc = request.POST.get('desc')
      image = request.FILES['upload']
      product = Product(name=name, price=price, desc=desc, images=image)
      product.save()
      return redirect('/myapp/products')
   return render(request, 'myapp/addproduct.html')


def product_update(request, id):
   product = Product.objects.get(id=id)
   if request.method == 'POST':
      product.name = request.POST.get('name')
      product.price = request.POST.get('price')
      product.desc = request.POST.get('desc')
      product.images = request.FILES['upload'] #dá erro se não der upload de uma imagem
      product.save()
      return redirect('/myapp/products') #é a url e não o arquivo html
   context = {
      'product': product
   }
   return render(request, 'myapp/updateproduct.html', context)

def product_delete(request, id):
   product = Product.objects.get(id=id)
   context = {
      'product': product
   }
   if request.method == 'POST':
      product.delete()
      return redirect('/myapp/products')
   return render(request, 'myapp/delete.html', context)