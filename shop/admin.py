from django.contrib import admin
from .models import Product, Review

# ვარეგისტრირებთ ჩვენს მოდელებს
admin.site.register(Product)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at' if hasattr(Review, 'created_at') else 'rating')
    list_filter = ('rating', 'product')
