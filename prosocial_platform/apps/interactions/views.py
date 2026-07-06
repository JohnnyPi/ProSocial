import uuid

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.ai_coach.models import ContentReviewSurface
from apps.ai_coach.review_validation import enforce_content_review, parse_review_event_id
from apps.common.http import is_htmx
from apps.interactions.forms import (
    BlockConfirmForm,
    MuteConfirmForm,
    ReplyDeleteForm,
    ReplyForm,
    ReportForm,
)
from apps.interactions.models import Notification
from apps.interactions.selectors import (
    get_hidden_posts,
    get_owned_reply,
    get_post_replies,
    get_unread_notification_count,
    get_user_notifications,
    is_blocked,
)
from apps.interactions.services import (
    BlockedInteractionError,
    InteractionError,
    block_user,
    create_context_note,
    create_reply,
    delete_reply,
    hide_post,
    mark_all_notifications_read,
    mark_notification_read,
    mute_user,
    rate_context_note,
    submit_report,
    toggle_prosocial_reaction,
    unblock_user,
    unhide_post,
    unmute_user,
    update_reply,
)
from apps.posts.models import Post
from apps.posts.selectors import get_post_for_display
from apps.profiles.selectors import get_public_profile


@login_required
def reply_create(request: HttpRequest, post_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    parent_id = request.GET.get("parent") or request.POST.get("parent")
    parent = None
    if parent_id:
        from apps.interactions.models import Reply

        parent = get_object_or_404(Reply.objects.visible(), public_id=parent_id, post=post)

    if is_blocked(user_a=request.user, user_b=post.author):
        return HttpResponseForbidden("This interaction is not available.")

    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            try:
                civility_event_id = request.POST.get("civility_event_id")
                review_event_id = parse_review_event_id(request.POST.get("review_event_id"))
                body = form.cleaned_data["body"]
                enforce_content_review(
                    user=request.user,
                    text=body,
                    review_event_id=review_event_id,
                    surface=ContentReviewSurface.REPLY,
                )
                create_reply(
                    post=post,
                    author=request.user,
                    body=body,
                    parent=parent,
                    civility_event_id=int(civility_event_id) if civility_event_id else None,
                    review_event_id=review_event_id,
                )
            except BlockedInteractionError:
                return HttpResponseForbidden("This interaction is not available.")
            except ValidationError as exc:
                form.add_error(None, exc.messages[0])
            except InteractionError as exc:
                form.add_error(None, str(exc))
            else:
                if is_htmx(request):
                    replies = get_post_replies(post=post)
                    return render(
                        request,
                        "interactions/reply_list.html",
                        {"post": post, "replies": replies},
                    )
                return redirect("posts:detail", public_id=post.public_id)
    else:
        form = ReplyForm()

    return render(
        request,
        "interactions/reply_form.html",
        {"form": form, "post": post, "parent": parent},
    )


@login_required
def reply_edit(request: HttpRequest, reply_id: uuid.UUID) -> HttpResponse:
    reply = get_owned_reply(public_id=reply_id, author=request.user)
    if request.method == "POST":
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            civility_event_id = request.POST.get("civility_event_id")
            review_event_id = parse_review_event_id(request.POST.get("review_event_id"))
            body = form.cleaned_data["body"]
            try:
                enforce_content_review(
                    user=request.user,
                    text=body,
                    review_event_id=review_event_id,
                    surface=ContentReviewSurface.EDIT,
                )
                update_reply(
                    reply=reply,
                    body=body,
                    civility_event_id=int(civility_event_id) if civility_event_id else None,
                    review_event_id=review_event_id,
                )
            except BlockedInteractionError:
                return HttpResponseForbidden("This interaction is not available.")
            except ValidationError as exc:
                form.add_error(None, exc.messages[0])
            except InteractionError as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("posts:detail", public_id=reply.post.public_id)
    else:
        form = ReplyForm(instance=reply)
    return render(
        request, "interactions/reply_form.html", {"form": form, "post": reply.post, "reply": reply}
    )


@login_required
def reply_delete(request: HttpRequest, reply_id: uuid.UUID) -> HttpResponse:
    reply = get_owned_reply(public_id=reply_id, author=request.user)
    if request.method == "POST":
        form = ReplyDeleteForm(request.POST)
        if form.is_valid():
            delete_reply(reply=reply)
            if is_htmx(request):
                replies = get_post_replies(post=reply.post)
                return render(
                    request,
                    "interactions/reply_list.html",
                    {"post": reply.post, "replies": replies},
                )
            return redirect("posts:detail", public_id=reply.post.public_id)
    else:
        form = ReplyDeleteForm()
    return render(request, "interactions/reply_confirm_delete.html", {"form": form, "reply": reply})


@login_required
def notification_list(request: HttpRequest) -> HttpResponse:
    notifications = get_user_notifications(user=request.user)
    if is_htmx(request) and request.GET.get("fragment") == "count":
        return render(
            request,
            "interactions/notification_count.html",
            {"count": get_unread_notification_count(user=request.user)},
        )
    return render(request, "interactions/notification_list.html", {"notifications": notifications})


@login_required
def notification_read(request: HttpRequest, notification_id: int) -> HttpResponse:
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    if request.method == "POST":
        mark_notification_read(notification=notification, user=request.user)
    return redirect("interactions:notifications")


@login_required
def notification_read_all(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        mark_all_notifications_read(user=request.user)
    return redirect("interactions:notifications")


@login_required
def hide_post_view(request: HttpRequest, post_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    if request.method == "POST":
        hide_post(user=request.user, post=post)
        return redirect("dashboard:index")
    return redirect("posts:detail", public_id=post.public_id)


@login_required
def hidden_posts_list(request: HttpRequest) -> HttpResponse:
    hidden = get_hidden_posts(user=request.user)
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        if post_id:
            post = get_object_or_404(Post, pk=post_id)
            unhide_post(user=request.user, post=post)
            return redirect("interactions:hidden_posts")
    return render(request, "interactions/hidden_posts.html", {"hidden_posts": hidden})


@login_required
def mute_user_view(request: HttpRequest, handle: str) -> HttpResponse:
    profile = get_public_profile(handle=handle)
    if request.method == "POST":
        form = MuteConfirmForm(request.POST)
        if form.is_valid():
            mute_user(muting_user=request.user, muted_user=profile.user)
            return redirect("profiles:detail", handle=profile.handle)
    else:
        form = MuteConfirmForm()
    return render(request, "interactions/mute_confirm.html", {"form": form, "profile": profile})


@login_required
def block_user_view(request: HttpRequest, handle: str) -> HttpResponse:
    profile = get_public_profile(handle=handle)
    if request.method == "POST":
        form = BlockConfirmForm(request.POST)
        if form.is_valid():
            block_user(blocking_user=request.user, blocked_user=profile.user)
            return redirect("dashboard:index")
    else:
        form = BlockConfirmForm()
    return render(request, "interactions/block_confirm.html", {"form": form, "profile": profile})


@login_required
def unmute_user_view(request: HttpRequest, handle: str) -> HttpResponse:
    profile = get_public_profile(handle=handle)
    if request.method == "POST":
        unmute_user(muting_user=request.user, muted_user=profile.user)
    return redirect("profiles:detail", handle=profile.handle)


@login_required
def unblock_user_view(request: HttpRequest, handle: str) -> HttpResponse:
    profile = get_public_profile(handle=handle)
    if request.method == "POST":
        unblock_user(blocking_user=request.user, blocked_user=profile.user)
    return redirect("profiles:detail", handle=profile.handle)


@login_required
def report_post(request: HttpRequest, post_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            submit_report(
                reporter=request.user,
                post=post,
                reason=form.cleaned_data["reason"],
                details=form.cleaned_data.get("details", ""),
            )
            return redirect("posts:detail", public_id=post.public_id)
    else:
        form = ReportForm()
    return render(request, "interactions/report_form.html", {"form": form, "post": post})


@login_required
def report_reply(request: HttpRequest, reply_id: uuid.UUID) -> HttpResponse:
    from apps.interactions.models import Reply

    reply = get_object_or_404(Reply.objects.visible(), public_id=reply_id)
    if is_blocked(user_a=request.user, user_b=reply.author) or is_blocked(
        user_a=request.user, user_b=reply.post.author
    ):
        return HttpResponseForbidden("This interaction is not available.")
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            submit_report(
                reporter=request.user,
                reply=reply,
                reason=form.cleaned_data["reason"],
                details=form.cleaned_data.get("details", ""),
            )
            return redirect("posts:detail", public_id=reply.post.public_id)
    else:
        form = ReportForm()
    return render(request, "interactions/report_form.html", {"form": form, "reply": reply})


@login_required
def react_post(request: HttpRequest, post_id: uuid.UUID) -> HttpResponse:
    from apps.interactions.models import ProsocialReactionKind

    post = get_post_for_display(public_id=post_id)
    if request.method != "POST":
        return redirect("posts:detail", public_id=post.public_id)
    kind = request.POST.get("kind", ProsocialReactionKind.HELPFUL)
    try:
        toggle_prosocial_reaction(sender=request.user, post=post, kind=kind)
    except (InteractionError, BlockedInteractionError):
        return HttpResponseForbidden("This interaction is not available.")
    if is_htmx(request):
        return _render_reactions(request, post=post)
    return redirect("posts:detail", public_id=post.public_id)


@login_required
def react_reply(request: HttpRequest, reply_id: uuid.UUID) -> HttpResponse:
    from apps.interactions.models import ProsocialReactionKind, Reply

    reply = get_object_or_404(Reply.objects.visible(), public_id=reply_id)
    if is_blocked(user_a=request.user, user_b=reply.author) or is_blocked(
        user_a=request.user, user_b=reply.post.author
    ):
        return HttpResponseForbidden("This interaction is not available.")
    if request.method != "POST":
        return redirect("posts:detail", public_id=reply.post.public_id)
    kind = request.POST.get("kind", ProsocialReactionKind.HELPFUL)
    try:
        toggle_prosocial_reaction(sender=request.user, reply=reply, kind=kind)
    except (InteractionError, BlockedInteractionError):
        return HttpResponseForbidden("This interaction is not available.")
    if is_htmx(request):
        return _render_reactions(request, reply=reply)
    return redirect("posts:detail", public_id=reply.post.public_id)


def _render_reactions(request, post=None, reply=None) -> HttpResponse:
    from apps.interactions.selectors import get_reaction_summary

    summary = get_reaction_summary(post=post, reply=reply, user=request.user)
    return render(
        request,
        "interactions/prosocial_reactions.html",
        {"post": post, "reply": reply, "summary": summary},
    )


@login_required
def context_note_create(request: HttpRequest, post_id: uuid.UUID) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    if request.method == "POST":
        body = request.POST.get("body", "")
        try:
            create_context_note(author=request.user, post=post, body=body)
            return redirect("posts:detail", public_id=post.public_id)
        except InteractionError as exc:
            return render(
                request,
                "interactions/context_note_form.html",
                {"post": post, "error": str(exc)},
            )
    return render(request, "interactions/context_note_form.html", {"post": post})


@login_required
def context_note_rate(request: HttpRequest, note_id: int) -> HttpResponse:
    from apps.interactions.models import ContextNote

    note = get_object_or_404(ContextNote, pk=note_id)
    if request.method == "POST":
        is_helpful = request.POST.get("helpful") == "1"
        try:
            rate_context_note(rater=request.user, note=note, is_helpful=is_helpful)
        except (BlockedInteractionError, InteractionError):
            return HttpResponseForbidden("This interaction is not available.")
    return redirect("posts:detail", public_id=note.post.public_id)
