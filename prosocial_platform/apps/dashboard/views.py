from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.posts.forms import PostForm
from apps.posts.selectors import get_dashboard_feed
from apps.posts.view_helpers import handle_post_create


@login_required
def dashboard_index(request: HttpRequest) -> HttpResponse:
    from apps.ai_coach.services import get_undismissed_interventions

    page_number = request.GET.get("page", 1)
    feed_mode = request.GET.get("feed", "all")
    feed_page = get_dashboard_feed(
        page=page_number,
        user=request.user,
        kind=request.GET.get("kind"),
        feed_mode=feed_mode,
    )

    form = PostForm()
    if request.method == "POST":
        response = handle_post_create(
            request,
            redirect_view="dashboard:index",
            redirect_with_post_id=False,
        )
        if response is not None:
            return response
        form = PostForm(request.POST, request.FILES)
        form.actor = request.user

    return render(
        request,
        "dashboard/index.html",
        {
            "form": form,
            "feed_page": feed_page,
            "profile": request.user.profile,
            "feed_mode": feed_mode,
            "ai_interventions": list(get_undismissed_interventions(user=request.user)[:3]),
        },
    )


@login_required
def knowledge_hub(request: HttpRequest) -> HttpResponse:
    from apps.engagement.models import Challenge
    from apps.follows.models import PostFollow
    from apps.gamification.models import LevelTier
    from apps.gamification.selectors import get_gamification_profile
    from apps.knowledge.selectors import get_user_collections, get_user_vault
    from apps.posts.models import Post

    followed_post_ids = PostFollow.objects.filter(user=request.user).values_list(
        "post_id", flat=True
    )
    followed_threads = (
        Post.objects.visible()
        .filter(pk__in=followed_post_ids)
        .select_related("author", "author__profile")[:10]
    )
    from apps.follows.selectors import get_followed_user_ids

    followed_user_ids = get_followed_user_ids(user=request.user)
    activity_feed = (
        Post.objects.visible()
        .filter(author_id__in=followed_user_ids)
        .select_related("author", "author__profile")[:15]
        if followed_user_ids
        else Post.objects.none()
    )
    collections = get_user_collections(user=request.user, limit=5)
    collections_count = get_user_collections(user=request.user).count()
    vault_page = get_user_vault(user=request.user, page=1, per_page=5)
    active_challenges = Challenge.objects.filter(is_active=True).order_by("period", "title")[:3]
    gamification_profile = get_gamification_profile(user=request.user)
    level = gamification_profile.level
    prev_xp = (level - 1) * 100
    next_xp = level * 100
    xp_in_level = gamification_profile.total_xp - prev_xp
    xp_needed = next_xp - prev_xp
    xp_progress_pct = min(100, int(xp_in_level * 100 / xp_needed)) if xp_needed else 100
    tier_label = dict(LevelTier.choices).get(gamification_profile.tier, gamification_profile.tier)
    return render(
        request,
        "dashboard/knowledge_hub.html",
        {
            "activity_feed": activity_feed,
            "collections": collections,
            "collections_count": collections_count,
            "followed_threads": followed_threads,
            "vault_recent": vault_page.object_list,
            "vault_count": vault_page.paginator.count,
            "active_challenges": active_challenges,
            "gamification_profile": gamification_profile,
            "tier_label": tier_label,
            "xp_in_level": xp_in_level,
            "xp_needed": xp_needed,
            "xp_progress_pct": xp_progress_pct,
        },
    )
