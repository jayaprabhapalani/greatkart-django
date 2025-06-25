from .models import Category


#it will request data as an arg then return dict as a context

def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)