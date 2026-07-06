from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.posts.forms import PostForm
from apps.posts.selectors import get_dashboard_feed
from apps.posts.view_helpers import handle_post_create


@login_required
def dashboard_index(request: HttpRequest) -> HttpResponse:
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
        },
    )


@login_required
def knowledge_hub(request: HttpRequest) -> HttpResponse:
    from apps.follows.models import PostFollow
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
    vault_recent = get_user_vault(user=request.user, page=1, per_page=5)
    return render(
        request,
        "dashboard/knowledge_hub.html",
        {
            "activity_feed": activity_feed,
            "collections": collections,
            "followed_threads": followed_threads,
            "vault_recent": vault_recent,
        },
    )
