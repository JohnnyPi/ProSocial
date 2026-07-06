from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.ai_coach.models import ContentReviewSurface
from apps.ai_coach.review_validation import enforce_content_review, parse_review_event_id
from apps.posts.forms import PostForm
from apps.posts.services import create_post


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def handle_post_create(
    request: HttpRequest,
    *,
    redirect_view: str,
    redirect_with_post_id: bool = True,
    review_surface: str = ContentReviewSurface.POST,
) -> HttpResponse | None:
    """Shared POST handler for dashboard and dedicated post-create views."""
    if request.method != "POST":
        return None
    form = PostForm(request.POST, request.FILES)
    form.actor = request.user
    if form.is_valid():
        kwargs = form.cleaned_post_kwargs()
        civility_event_id = request.POST.get("civility_event_id")
        if civility_event_id:
            kwargs["civility_event_id"] = int(civility_event_id)
        review_event_id = parse_review_event_id(request.POST.get("review_event_id"))
        try:
            enforce_content_review(
                user=request.user,
                text=kwargs["body"],
                review_event_id=review_event_id,
                surface=review_surface,
            )
        except ValidationError as exc:
            form.add_error(None, exc.messages[0])
        else:
            if review_event_id:
                kwargs["review_event_id"] = review_event_id
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
