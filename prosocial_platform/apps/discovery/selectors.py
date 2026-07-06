from django.db.models import Count

from apps.posts.models import Post


def get_most_clipped_posts(*, limit: int = 20):
    return (
        Post.objects.visible()
        .annotate(clip_count=Count("clips"))
        .filter(clip_count__gt=0)
        .order_by("-clip_count")[:limit]
    )


def get_sentiment_boosted_posts(*, limit: int = 20):
    from apps.ai_coach.models import SentimentLabel, SentimentSnapshot

    positive_post_ids = (
        SentimentSnapshot.objects.filter(label=SentimentLabel.POSITIVE, post__isnull=False)
        .values_list("post_id", flat=True)
        .distinct()
    )
    return (
        Post.objects.visible()
        .filter(pk__in=positive_post_ids)
        .select_related("author", "author__profile")
        .order_by("-created_at")[:limit]
    )


def get_prosocial_ranked_feed(*, user, page: int = 1, per_page: int = 20):
    from django.core.paginator import Paginator

    from apps.trust.services import get_or_create_trust_profile

    profile = get_or_create_trust_profile(user=user)
    queryset = (
        Post.objects.visible()
        .select_related("author", "author__profile")
        .annotate(clip_count=Count("clips"))
        .order_by("-clip_count", "-created_at")
    )
    return Paginator(queryset, per_page).get_page(page), profile
