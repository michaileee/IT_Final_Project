from .models import Product

def cart_processor(request):
    cart_session = request.session.get('cart', {})
    nav_cart_items = []
    nav_total_price = 0
    nav_total_quantity = 0

    for product_id, quantity in cart_session.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            nav_total_price += item_total
            nav_total_quantity += quantity
            nav_cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        except Product.DoesNotExist:
            pass

    return {
        'nav_cart_items': nav_cart_items,
        'nav_total_price': nav_total_price,
        'nav_total_quantity': nav_total_quantity
    }