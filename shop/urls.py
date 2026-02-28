from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # გზა დეტალური გვერდისკენ
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # გზა კალათისკენ
    path('cart/', views.cart, name='cart'),
    # გზა კალათაში დამატებისკენ
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # წაშლა/რედაქტირება
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    # ავტორიზაციის მარშრუტები
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]