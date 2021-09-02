from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import FeedUpload


@login_required
def index(request):
    feed_uploads = FeedUpload.objects.all().order_by('-created')[:100]
    context = {
        'feed_uploads': feed_uploads
    }
    return render(request, 'zalando/index.html', context)
