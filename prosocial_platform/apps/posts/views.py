import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

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
            post = create_post(
                author=request.user,
                body=form.cleaned_data["body"],
                image=form.cleaned_data.get("image"),
                image_alt_text=form.cleaned_data.get("image_alt_text", ""),
            )
            if _is_htmx(request):
                return render(request, "components/post_card.html", {"post": post})
            return redirect("posts:detail", public_id=post.public_id)
    else:
        form = PostForm()

    return render(request, "posts/create.html", {"form": form})


def post_detail(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=public_id)
    return render(request, "posts/detail.html", {"post": post})


@login_required
def post_edit(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    post = get_owned_post(public_id=public_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        form.actor = request.user
        if form.is_valid():
            update_post(
                post=post,
                body=form.cleaned_data["body"],
                image=form.cleaned_data.get("image"),
                image_alt_text=form.cleaned_data.get("image_alt_text", ""),
            )
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
