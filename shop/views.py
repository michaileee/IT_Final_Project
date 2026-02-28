from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Min, Max, Avg
from django.contrib import messages
from .models import Product, Review

from django.contrib.auth import login, logout
from .forms import CustomRegisterForm, CustomLoginForm

def home(request):
    products = Product.objects.annotate(avg_rating=Avg('reviews__rating'))

    categories = Product.objects.values_list('category', flat=True).distinct()
    brands = Product.objects.values_list('brand', flat=True).distinct()

    price_range = products.aggregate(Min('price'), Max('price'))
    min_price = int(price_range['price__min'] or 0)
    max_price = int(price_range['price__max'] or 1000)

    search_query = request.GET.get('q') 
    category_query = request.GET.get('category')
    brand_query = request.GET.get('brand')
    price_query = request.GET.get('price')
    rating_query = request.GET.get('rating')

    if search_query:
        products = products.filter(title__icontains=search_query) 
    
    if category_query and category_query != 'ყველა':
        products = products.filter(category=category_query)
        
    if brand_query and brand_query != 'ყველა':
        products = products.filter(brand=brand_query)
        
    if price_query:
        products = products.filter(price__lte=price_query) 
        
    if rating_query:
        products = products.filter(avg_rating__gte=rating_query) 

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'min_price': min_price,
        'max_price': max_price,

        'selected_category': category_query,
        'selected_brand': brand_query,
        'selected_price': price_query or max_price,
    }
    
    return render(request, 'home.html', context)

# ნივთის დეტალური გვერდი
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # 1. ვამოწმებთ, ფორმა ხომ არ გამოგზავნა მომხმარებელმა (POST მოთხოვნა)
    if request.method == 'POST':
        # 2. დამატებითი ბექენდ დაცვა: ვამოწმებთ, ნამდვილად ავტორიზებულია თუ არა
        if request.user.is_authenticated:
            # მოგვაქვს HTML ფორმიდან 'rating' ველში ჩაწერილი რიცხვი
            rating_value = request.POST.get('rating')
            
            if rating_value:
                # 3. ვინახავთ ან ვაახლებთ შეფასებას ბაზაში
                Review.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={'rating': rating_value} # თუ უკვე არსებობს, განაახლებს ამ მნიშვნელობით
                )
                
                # 4. ვაგზავნით წარმატების შეტყობინებას და ვაბრუნებთ იგივე გვერდზე
                messages.success(request, "თქვენი შეფასება წარმატებით შენახულია!")
                return redirect('product_detail', pk=product.id)
        else:
            messages.error(request, "შეფასებისთვის აუცილებელია ავტორიზაციის გავლა.")
            return redirect('login')
            
    # GET მოთხოვნის შემთხვევაში (უბრალოდ გვერდის გახსნისას) ვაჩვენებთ პროდუქტს
    context = {
        'product': product
    }
    return render(request, 'detail.html', context)

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    request.session['cart'] = cart
    
    # ვქმნით შეტყობინებას
    product = get_object_or_404(Product, id=product_id)
    messages.success(request, f"{product.title} წარმატებით დაემატა კალათაში!")
    
    # ვბრუნდებით იმავე გვერდზე
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# კალათის გვერდი
def cart(request):
    cart_session = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    # სესიაში შენახული ID-ებით ბაზიდან მოგვაქვს პროდუქტები
    for product_id, quantity in cart_session.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        except Product.DoesNotExist:
            pass # თუ პროდუქტი ბაზიდან წაიშალა, უბრალოდ გამოვტოვებთ
            
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    
    return render(request, 'cart.html', context)

# კალათაში რაოდენობის შეცვლა
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    action = request.POST.get('action')

    if product_id_str in cart:
        if action == 'increase':
            cart[product_id_str] += 1
        elif action == 'decrease':
            cart[product_id_str] -= 1
            # თუ რაოდენობა 0 გახდა, ნივთს საერთოდ ვშლით კალათიდან
            if cart[product_id_str] <= 0:
                del cart[product_id_str]

    request.session['cart'] = cart
    return redirect('cart')

# კალათიდან ნივთის სრულად წაშლა
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        messages.info(request, "ნივთი წაიშალა კალათიდან.")

    request.session['cart'] = cart
    return redirect('cart')


# რეგისტრაცია
def register_view(request):
    if request.method == 'POST':
        # თუ მომხმარებელმა მონაცემები გამოაგზავნა, ვაწვდით მათ ფორმას
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save() # ვინახავთ ახალ იუზერს ბაზაში
            login(request, user) # რეგისტრაციისთანავე ავტომატურად ვაკეთებთ ავტორიზაციას
            messages.success(request, "რეგისტრაცია წარმატებით დასრულდა!")
            return redirect('home')
    else:
        # თუ უბრალოდ გვერდზე შემოვიდა, ვაჩვენებთ ცარიელ ფორმას
        form = CustomRegisterForm()
        
    return render(request, 'register.html', {'form': form})

# 6. ავტორიზაცია
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) # ვრთავთ იუზერს სისტემაში
            messages.success(request, f"გამარჯობა, {user.username}!")
            return redirect('home')
    else:
        form = CustomLoginForm()
        
    return render(request, 'login.html', {'form': form})

# 7. სისტემიდან გამოსვლა
def logout_view(request):
    logout(request)
    messages.info(request, "თქვენ გამოხვედით სისტემიდან.")
    return redirect('home')