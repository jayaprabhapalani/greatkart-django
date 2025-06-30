from django.shortcuts import render,get_object_or_404
from store.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import EmptyPage,Paginator
from django.db.models import Q # for complex queries
# Create your views here.

def store(request, category_slug=None):
    categories=None
    products=None
    
    if category_slug != None:
        categories=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.filter(category=categories,is_available=True)
        paginator=Paginator(products,6)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    else:    
        products=Product.objects.all().filter(is_available=True).order_by('id')
        # to show 6 products per page
        paginator=Paginator(products,3)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
        
    context={
        'products':paged_products,
        'product_count':product_count,
    }

    return render(request,'store/store.html',context)


#view for single prod page while clciking the name of that particular product
def product_detail(request,category_slug,product_slug):
    
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        # for cart--if it is added already--show that and also add a view cart button
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()# cart is the fk of CartItems model
       
    except Exception as e:
        raise e
    
    context={
        'single_product':single_product,
        'in_cart':in_cart
    }
    
    return render(request,'store/product_detail.html',context)


#search view
def search(request):
    #if keyword is present then return its corressponding value then show that cat /prod
    if "keyword" in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)) # if i use , then the filter will act as and operator so we need or operator--usnig Q()|Q()
            product_count=products.count()
        context={
            'products':products,
            'product_count':product_count,
        }    
    return render(request,'store/store.html',context)