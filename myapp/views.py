from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

##Class Based View##
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

def index(request):
   return HttpResponse("Hello World!")

def products(request):
   page_obj = products = Product.objects.all()

   #search
   product_name = request.GET.get('product_name')
   if product_name != '' and product_name is not None:
      page_obj = products.filter(name__icontains=product_name)

   #paginator
   paginator = Paginator(page_obj, 3)
   page_number = request.GET.get('page')
   page_obj = paginator.get_page(page_number) #pega os objetos dessa página

   context = {'page_obj': page_obj}
   return render(request, 'myapp/index.html', context)

#Class based views for above products views [ListView]
""" class ProductListView(ListView):
   model = Product
   template_name = 'myapp/index.html'
   context_object_name = 'products'
   paginate_by = 3
 """
def product_detail(request, id):
   product = Product.objects.get(id=id)
   context = {'product': product}
   return render(request, 'myapp/detail.html', context)

#Class based views for above product detail view [DetailView]
""" class ProductDetailView(DetailView):
   model = Product
   template_name = 'myapp/detail.html'
   context_object_name = 'product' """

@login_required
def product_add(request):
   if request.method == 'POST':
      name = request.POST.get('name')
      price = request.POST.get('price')
      desc = request.POST.get('desc')
      image = request.FILES['upload']
      seller_name = request.user
      product = Product(name=name, price=price, desc=desc, images=image, seller_name=seller_name)
      product.save()
      return redirect('/myapp/products')
   return render(request, 'myapp/addproduct.html')

#Class based view for creating a product
""" class ProductCreateView(CreateView):
   model = Product
   fields = ['name', 'price', 'desc', 'images', 'seller_name'] """


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

#class based view for update a product
""" class ProductUpdateView(UpdateView):
   model = Product
   fields = ['name', 'price', 'desc', 'images', 'seller_name']
   template_name = 'myapp/product_update_form.html' """

def product_delete(request, id):
   product = Product.objects.get(id=id)
   context = {
      'product': product
   }
   if request.method == 'POST':
      product.delete()
      return redirect('/myapp/products')
   return render(request, 'myapp/delete.html', context)

#class based view for delete a product
""" class ProductDelete(DeleteView):
   product = Product
   template_name = 'myapp/product_confirm_delete.html' """

@login_required
def my_listings(request):
   products = Product.objects.filter(seller_name=request.user)
   context = {
      'products': products
   }
   return render(request, 'myapp/mylistings.html', context)