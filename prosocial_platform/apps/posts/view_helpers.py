from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.posts.forms import PostForm
from apps.posts.services import create_post


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def handle_post_create(
    request: HttpRequest,
    *,
    redirect_view: str,
    redirect_with_post_id: bool = True,
) -> HttpResponse | None:
    """Shared POST handler for dashboard and dedicated post-create views."""
    if request.method != "POST":
        return None
    form = PostForm(request.POST, request.FILES)
    form.actor = request.user
    if form.is_valid():
        civility_event_id = request.POST.get("civility_event_id")
        kwargs = form.cleaned_post_kwargs()
        if civility_event_id:
            kwargs["civility_event_id"] = int(civility_event_id)
        post = create_post(author=request.user, **kwargs)
        if is_htmx(request):
            return render(request, "components/post_card.html", {"post": post})
        if redirect_with_post_id:
            return redirect(redirect_view, public_id=post.public_id)
        return redirect(redirect_view)
    if is_htmx(request):
        return render(
            request,
            "components/post_composer.html",
            {"form": form},
            status=422,
        )
    return None
