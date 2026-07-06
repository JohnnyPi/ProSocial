from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

from apps.follows.services import FollowError, toggle_post_follow, toggle_user_follow
from apps.posts.selectors import get_post_for_display

User = get_user_model()


@login_required
def toggle_follow_user(request: HttpRequest, handle: str) -> HttpResponse:
    target = get_object_or_404(User, profile__handle=handle)
    try:
        toggle_user_follow(follower=request.user, following=target)
    except FollowError:
        pass
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)


@login_required
def toggle_follow_post(request: HttpRequest, post_id) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    toggle_post_follow(user=request.user, post=post)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)
