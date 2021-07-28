from django.shortcuts import render

from .models import OrderItem

def index(request):
    order_items = OrderItem.objects.all().order_by('-expected_delivery_date')
    context = {'order_items': order_items}
    return render(request, 'otto/index.html', context)