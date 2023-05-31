from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from core.models import Error, Job, Price
from zalando.models import FeedUpload


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


@login_required
def index(request):
    now = timezone.now()
    feed_upload = FeedUpload.objects.latest("created")

    delta = now - feed_upload.created

    if delta > timedelta(hours=1):
        messages.error(request, f"Last feed upload to Z {delta} ago")
    else:
        messages.success(request, f"Last feed upload to Z {delta} ago")

    def _group_jobs(jobs):
        grouped_jobs = {}

        for job in jobs:
            if job.cmd not in grouped_jobs:
                grouped_jobs[job.cmd] = []

            duration = 0
            if job.end:
                duration = job.end - job.start

            grouped_jobs[job.cmd].append(
                {
                    "start": job.start,
                    "duration": duration,
                    "success": job.successful,
                    "end": job.end,
                    "description": job.description,
                }
            )

        for job, result_list in grouped_jobs.items():
            grouped_jobs[job] = result_list[:5]

        return grouped_jobs

    green_jobs = Job.objects.filter(successful=True).order_by("-start")
    red_jobs = Job.objects.filter(successful=False).order_by("-start")

    grouped_green_jobs = _group_jobs(green_jobs)
    grouped_red_jobs = _group_jobs(red_jobs)

    prices_without_category = Price.objects.filter(category__isnull=True).order_by(
        "sku"
    )

    errors = Error.objects.filter(cleared=False)

    return render(
        request,
        "m13/index.html",
        {
            "errors": errors,
            "green_jobs": grouped_green_jobs,
            "prices_without_category": prices_without_category,
            "red_jobs": grouped_red_jobs,
        },
    )
