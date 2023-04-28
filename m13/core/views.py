import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .models import Job
from .services.article_stats import get_article_stats

LOG = logging.getLogger(__name__)


@login_required
def return_shipments_stats(request):
    """Overview of all zalando calculator values."""
    return render(request, "core/return_shipments_stats.html", {})


@login_required()
def api_return_shipments_stats(request) -> JsonResponse:
    """Return the article stats as JSON."""
    start_date = request.GET.get("start")
    if not start_date:
        start_date = date.today() - timedelta(weeks=4)

    end_date = request.GET.get("end")
    if not end_date:
        end_date = date.today()

    marketplace = request.GET.get("marketplace")
    if not marketplace:
        return JsonResponse(
            {
                "status": "false",
                "message": "No marketplace name - do you know what you are doing?",
            },
            status=500,
        )

    article_stats = get_article_stats(marketplace, start_date, end_date)
    article_keys = list(article_stats.keys())
    article_keys.sort()
    sorted_article_stats = {i: article_stats[i] for i in article_keys}

    return JsonResponse(sorted_article_stats, safe=False)


@login_required
def status(request):
    """Overview of the system status."""

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
                }
            )

        return grouped_jobs

    green_jobs = Job.objects.filter(successful=True).order_by("-start")
    red_jobs = Job.objects.filter(successful=False).order_by("-start")

    grouped_green_jobs = _group_jobs(green_jobs)
    grouped_red_jobs = _group_jobs(red_jobs)

    return render(
        request,
        "core/status.html",
        {"green_jobs": grouped_green_jobs, "red_jobs": grouped_red_jobs},
    )
