from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.discovery.models import CommunitySpotlight, RippleLink
from apps.discovery.selectors import (
    get_most_clipped_posts,
    get_prosocial_ranked_feed,
    get_sentiment_boosted_posts,
)


@login_required
def discovery_home(request: HttpRequest) -> HttpResponse:
    most_clipped = get_most_clipped_posts()
    sentiment_boosted = get_sentiment_boosted_posts()
    ranked_page, _ = get_prosocial_ranked_feed(user=request.user, page=request.GET.get("page", 1))
    spotlights = CommunitySpotlight.objects.filter(is_published=True).select_related("user")[:5]
    return render(
        request,
        "discovery/home.html",
        {
            "most_clipped": most_clipped,
            "sentiment_boosted": sentiment_boosted,
            "ranked_page": ranked_page,
            "spotlights": spotlights,
        },
    )


@login_required
def ripple_effect(request: HttpRequest) -> HttpResponse:
    links = RippleLink.objects.filter(helper=request.user).select_related(
        "helped", "helped__profile"
    )
    received = RippleLink.objects.filter(helped=request.user).select_related(
        "helper", "helper__profile"
    )
    return render(
        request,
        "discovery/ripple.html",
        {"outgoing": links, "incoming": received},
    )
