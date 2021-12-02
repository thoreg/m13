
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


@login_required
def index(request):
    return render(request, 'm13/index.html', {})
