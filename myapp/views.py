from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, OrderDetail
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import stripe

##Class Based View##
from django.views.generic import ListView, DetailView, TemplateView
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
   context = {
      'product': product,
      'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
      }
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

#checkout stripe
@csrf_exempt
def create_checkout_session(request, id):
   product = get_object_or_404(Product, pk=id)
   stripe.api_key = settings.STRIPE_SECRET_KEY
   checkout_session = stripe.checkout.Session.create(
      customer_email = request.user.email,
      payment_method_types = ['card'],
      line_items = [
         {
            'price_data':{
               'currency':'usd',
               'product_data':{
                  'name':product.name,
               },
               'unit_amount':int(product.price * 100),
            },
            'quantity':1,
         }
      ],
      mode = 'payment',
      success_url = request.build_absolute_uri(reverse('myapp:success'))+"?session_id={CHECKOUT_SESSION_ID}",
      cancel_url = request.build_absolute_uri(reverse('myapp:failed')),
   )

   order = OrderDetail()
   order.customer_username = request.user.username
   order.product = product
   order.stripe_payment_intent = checkout_session['payment_intent']
   order.amount = int(product.price * 100)
   order.save()
   return JsonResponse({'sessionId':checkout_session.id})

class PaymentSuccessView(TemplateView):
   template_name = 'myapp/payment_success.html'

   def get(self, request, *args, **kwargs):
      session_id = request.GET.get('session_id')
      if session_id is None:
         return HttpResponseNotFound()
      session = stripe.checkout.Session.retrieve(session_id)
      stripe.api_key = settings.STRIPE_SECRET_KEY
      order = get_object_or_404(OrderDetail, stripe_payment_intent=session.payment_intent)
      order.has_paid = True
      order.save()
      return render(request, self.template_name)

class PaymentFailedView(TemplateView):
   template_name = 'myapp/payment_failed.html'