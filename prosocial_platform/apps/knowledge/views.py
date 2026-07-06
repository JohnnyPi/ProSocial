from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.knowledge.forms import CollectionForm
from apps.knowledge.models import ClipKind
from apps.knowledge.selectors import (
    get_collection_for_display,
    get_collection_for_owner,
    get_popular_tags,
    get_tag_by_slug,
    get_tagged_posts,
    get_user_collections,
    get_user_vault,
    search_knowledge,
)
from apps.knowledge.services import (
    KnowledgeError,
    add_clip_to_collection,
    add_post_to_collection,
    create_clip,
    create_collection,
)
from apps.posts.models import Post
from apps.posts.selectors import get_post_for_display


@login_required
def vault_list(request: HttpRequest) -> HttpResponse:
    page = get_user_vault(user=request.user, page=request.GET.get("page", 1))
    return render(request, "knowledge/vault_list.html", {"page": page})


@login_required
@require_POST
def clip_post(request: HttpRequest, post_id) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    clip_kind = request.POST.get("clip_kind", ClipKind.WHOLE_POST)
    try:
        create_clip(owner=request.user, post=post, clip_kind=clip_kind)
    except KnowledgeError as exc:
        return render(
            request,
            "components/flash_messages.html",
            {"messages": [("error", str(exc))]},
            status=422,
        )
    return redirect("posts:detail", public_id=post.public_id)


@login_required
@require_POST
def clip_selection(request: HttpRequest, post_id) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    try:
        selection_start = int(request.POST.get("selection_start", 0))
        selection_end = int(request.POST.get("selection_end", 0))
    except (TypeError, ValueError):
        return render(
            request,
            "components/flash_messages.html",
            {"messages": [("error", "Invalid selection.")]},
            status=422,
        )
    quoted_text = request.POST.get("quoted_text", "").strip()
    try:
        create_clip(
            owner=request.user,
            post=post,
            clip_kind=ClipKind.SELECTION,
            quoted_text=quoted_text,
            selection_start=selection_start,
            selection_end=selection_end,
        )
    except KnowledgeError as exc:
        return render(
            request,
            "components/flash_messages.html",
            {"messages": [("error", str(exc))]},
            status=422,
        )
    return redirect("knowledge:vault")


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "")
    page, tags = search_knowledge(query=query, page=request.GET.get("page", 1))
    return render(
        request,
        "knowledge/search.html",
        {"query": query, "page": page, "tags": tags},
    )


@login_required
def collection_list(request: HttpRequest) -> HttpResponse:
    collections = get_user_collections(user=request.user)
    return render(request, "knowledge/collection_list.html", {"collections": collections})


@login_required
def collection_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = create_collection(
                owner=request.user,
                title=form.cleaned_data["title"],
                description=form.cleaned_data.get("description", ""),
                visibility=form.cleaned_data.get("visibility"),
            )
            return redirect("knowledge:collection_detail", public_id=collection.public_id)
    else:
        form = CollectionForm()
    return render(request, "knowledge/collection_form.html", {"form": form})


def collection_detail(request: HttpRequest, public_id) -> HttpResponse:
    user = request.user if request.user.is_authenticated else None
    collection = get_collection_for_display(public_id=public_id, user=user)
    return render(request, "knowledge/collection_detail.html", {"collection": collection})


@login_required
def collection_add_clip(request: HttpRequest, public_id, clip_id) -> HttpResponse:
    collection = get_collection_for_owner(public_id=public_id, owner=request.user)
    clip = get_object_or_404(collection.owner.clips, public_id=clip_id)
    try:
        add_clip_to_collection(collection=collection, clip=clip, owner=request.user)
    except KnowledgeError as exc:
        return redirect("knowledge:collection_detail", public_id=collection.public_id)
    return redirect("knowledge:collection_detail", public_id=collection.public_id)


@login_required
def collection_add_post(request: HttpRequest, public_id, post_id) -> HttpResponse:
    collection = get_collection_for_owner(public_id=public_id, owner=request.user)
    post = get_post_for_display(public_id=post_id)
    try:
        add_post_to_collection(collection=collection, post=post, owner=request.user)
    except KnowledgeError:
        pass
    return redirect("knowledge:collection_detail", public_id=collection.public_id)


def tag_browse(request: HttpRequest) -> HttpResponse:
    tags = get_popular_tags()
    return render(request, "knowledge/tag_browse.html", {"tags": tags})


def tag_detail(request: HttpRequest, slug: str) -> HttpResponse:
    tag = get_tag_by_slug(slug=slug)
    page = get_tagged_posts(tag=tag, page=request.GET.get("page", 1))
    return render(request, "knowledge/tag_detail.html", {"tag": tag, "page": page})
