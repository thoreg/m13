from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import FeedUpload
from .forms import PriceToolForm
from .services import update_prices


@login_required
def index(request):
    feed_uploads = FeedUpload.objects.all().order_by('-created')[:13]
    ctx = {
        'feed_uploads': feed_uploads
    }

    if request.method == 'POST':
        form = PriceToolForm(request.POST)
        if form.is_valid():
            update_prices(form.cleaned_data['z_factor'])
            return HttpResponseRedirect(reverse('zalando_index'))
    else:
        form = PriceToolForm()

    ctx['form'] = form
    return render(request, 'zalando/index.html', ctx)
