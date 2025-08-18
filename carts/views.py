from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from store.models import Product,Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

#to return the session key from website for to assign it to cart_id
def  _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart    

    
#add cart item
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    # Collect product variations from POST
    product_variation = []
    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    # If the user is authenticated
    if current_user.is_authenticated:
        cart_item_qs = CartItem.objects.filter(product=product, user=current_user)

        if cart_item_qs.exists():
            ex_var_list = []
            ids = []
            for cart_item in cart_item_qs:
                existing_variation = cart_item.variations.all()
                ex_var_list.append(list(existing_variation))
                ids.append(cart_item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = ids[index]
                cart_item = CartItem.objects.get(product=product, id=item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if product_variation:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            if product_variation:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

    # If the user is not authenticated
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        cart_item_qs = CartItem.objects.filter(product=product, cart=cart)

        if cart_item_qs.exists():
            ex_var_list = []
            ids = []
            for cart_item in cart_item_qs:
                existing_variation = cart_item.variations.all()
                ex_var_list.append(list(existing_variation))
                ids.append(cart_item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = ids[index]
                cart_item = CartItem.objects.get(product=product, id=item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if product_variation:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

    return redirect('cart')
  
            
                
                                 


#to remove items---minus button
def remove_cart(request,product_id,cart_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
            
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))   
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass        
    return redirect('cart') 


#remove total cart
def remove_cart_item(request,product_id,cart_item_id):
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:   
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()    
    return redirect('cart') 
  



#to render the cart page and show the all fileds dynamically
def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True) 
        else:  
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        #to get total items, quantity of added items, and cart_items
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity+=cart_item.quantity
        tax=int(0.02*total)
        grand_total=total+tax    
    except ObjectDoesNotExist:
        pass 
    
    context={
        'total':total ,
        'quantity': quantity,
        'cart_items':cart_items ,
        'tax':tax,
        'grand_total':grand_total,
    }        
    
    return render(request,'store/cart.html',context)


@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True) 
        else:  
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        #to get total items, quantity of added items, and cart_items
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity+=cart_item.quantity
        tax=int(0.02*total)
        grand_total=total+tax    
    except ObjectDoesNotExist:
        pass 
    
    context={
        'total':total ,
        'quantity': quantity,
        'cart_items':cart_items ,
        'tax':tax,
        'grand_total':grand_total,
    }        
    
    return render(request,'store/checkout.html',context)