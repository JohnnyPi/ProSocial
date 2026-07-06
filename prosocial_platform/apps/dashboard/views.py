from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.posts.forms import PostForm
from apps.posts.selectors import get_dashboard_feed
from apps.posts.services import create_post


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


@login_required
def dashboard_index(request: HttpRequest) -> HttpResponse:
    page_number = request.GET.get("page", 1)
    feed_page = get_dashboard_feed(page=page_number)

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
            return redirect("dashboard:index")
        elif _is_htmx(request):
            return render(
                request,
                "components/post_composer.html",
                {"form": form},
                status=422,
            )
    else:
        form = PostForm()

    return render(
        request,
        "dashboard/index.html",
        {
            "form": form,
            "feed_page": feed_page,
            "profile": request.user.profile,
        },
    )
