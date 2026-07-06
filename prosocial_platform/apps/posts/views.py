import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.ai_coach.models import ContentReviewSurface
from apps.ai_coach.review_validation import parse_review_event_id
from apps.interactions.selectors import get_post_replies
from apps.posts.forms import PostDeleteForm, PostForm
from apps.posts.selectors import get_owned_post, get_post_for_display
from apps.posts.services import soft_delete_post, update_post
from apps.posts.view_helpers import handle_post_create, is_htmx


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        response = handle_post_create(
            request,
            redirect_view="posts:detail",
            redirect_with_post_id=True,
        )
        if response is not None:
            return response
        form = PostForm(request.POST, request.FILES)
        form.actor = request.user
        return render(request, "posts/create.html", {"form": form})
    form = PostForm()
    return render(request, "posts/create.html", {"form": form})


def post_detail(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=public_id)
    replies = get_post_replies(post=post)
    from apps.interactions.selectors import get_reaction_summary, get_visible_context_notes

    reaction_summary = get_reaction_summary(
        post=post, user=request.user if request.user.is_authenticated else None
    )
    if request.user.is_authenticated:
        for reply in replies:
            reply.reaction_summary = get_reaction_summary(reply=reply, user=request.user)
            for child in reply.children.all():
                child.reaction_summary = get_reaction_summary(reply=child, user=request.user)
    context_notes = get_visible_context_notes(post=post)
    is_following_post = False
    if request.user.is_authenticated:
        from apps.follows.selectors import is_following_post as check_following_post

        is_following_post = check_following_post(user=request.user, post=post)
    context = {
        "post": post,
        "replies": replies,
        "is_following_post": is_following_post,
        "reaction_summary": reaction_summary,
        "context_notes": context_notes,
        "post_card_clickable": False,
    }
    if is_htmx(request):
        return render(request, "components/post_card.html", context)
    return render(request, "posts/detail.html", context)


@login_required
def post_edit(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_owned_post(public_id=public_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        form.actor = request.user
        if form.is_valid():
            from django.core.exceptions import ValidationError

            from apps.ai_coach.review_validation import enforce_content_review

            civility_event_id = request.POST.get("civility_event_id")
            review_event_id = parse_review_event_id(request.POST.get("review_event_id"))
            kwargs = form.cleaned_post_kwargs()
            try:
                enforce_content_review(
                    user=request.user,
                    text=kwargs["body"],
                    review_event_id=review_event_id,
                    surface=ContentReviewSurface.EDIT,
                )
                update_post(
                    post=post,
                    civility_event_id=int(civility_event_id) if civility_event_id else None,
                    review_event_id=review_event_id,
                    **kwargs,
                )
            except ValidationError as exc:
                form.add_error(None, exc.messages[0])
            else:
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
            if is_htmx(request):
                return HttpResponse("")
            return redirect("dashboard:index")
    else:
        form = PostDeleteForm()

    template = (
        "components/post_delete_confirm.html" if is_htmx(request) else "posts/confirm_delete.html"
    )
    return render(request, template, {"form": form, "post": post})
