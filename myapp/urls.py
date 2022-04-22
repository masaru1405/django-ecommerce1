from django.urls import path
from . import views

app_name = 'myapp'
urlpatterns = [
   path('', views.index, name='index'),
   path('products/', views.products, name='products'),
   path('products/<int:id>/', views.product_detail, name='product_detail'),
   path('products/add/', views.product_add, name='product_add'),
   path('products/update/<int:id>/', views.product_update, name='product_update'),
   path('products/delete/<int:id>/', views.product_delete, name='product_delete')
]