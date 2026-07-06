import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.interactions.selectors import get_post_replies
from apps.posts.forms import PostDeleteForm, PostForm
from apps.posts.selectors import get_owned_post, get_post_for_display
from apps.posts.services import create_post, soft_delete_post, update_post


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        form.actor = request.user
        if form.is_valid():
            post = create_post(author=request.user, **form.cleaned_post_kwargs())
            if _is_htmx(request):
                return render(request, "components/post_card.html", {"post": post})
            return redirect("posts:detail", public_id=post.public_id)
    else:
        form = PostForm()

    return render(request, "posts/create.html", {"form": form})


def post_detail(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=public_id)
    replies = get_post_replies(post=post)
    from apps.interactions.models import ThankYou
    thank_count = ThankYou.objects.filter(post=post).count()
    user_thanked = (
        request.user.is_authenticated
        and ThankYou.objects.filter(sender=request.user, post=post).exists()
    )
    is_following_post = False
    if request.user.is_authenticated:
        from apps.follows.selectors import is_following_post as check_following_post

        is_following_post = check_following_post(user=request.user, post=post)
    context = {
        "post": post,
        "replies": replies,
        "thank_count": thank_count,
        "user_thanked": user_thanked,
        "is_following_post": is_following_post,
    }
    if _is_htmx(request):
        return render(request, "components/post_card.html", context)
    return render(request, "posts/detail.html", context)


@login_required
def post_edit(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_owned_post(public_id=public_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        form.actor = request.user
        if form.is_valid():
            update_post(post=post, **form.cleaned_post_kwargs())
            return redirect("posts:detail", public_id=post.public_id)
    else:
        form = PostForm(instance=post)

    return render(request, "posts/edit.html", {"form": form, "post": post})


@login_required
def post_delete(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_owned_post(public_id=public_id, author=request.user)

    if request.method == "POST":
        form = PostDeleteForm(request.POST)
        if form.is_valid():
            soft_delete_post(post=post)
            if _is_htmx(request):
                return HttpResponse("")
            return redirect("dashboard:index")
    else:
        form = PostDeleteForm()

    template = "components/post_delete_confirm.html" if _is_htmx(request) else "posts/confirm_delete.html"
    return render(request, template, {"form": form, "post": post})
