from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.ai_coach.forms import JournalEntryForm
from apps.ai_coach.models import ContentReviewSurface, ReflectionJournalEntry
from apps.ai_coach.sentiment.constants import CONDUCT_LABELS, EMOTION_LABELS
from apps.ai_coach.services import (
    ContentReviewError,
    classify_civility,
    create_civility_prompt_event,
    create_content_review_event,
    create_journal_entry,
    record_civility_action,
)


def _emotion_display_context(event) -> dict:
    top = sorted(event.emotion_scores.items(), key=lambda item: item[1], reverse=True)
    labeled_emotions = [
        {
            "name": name,
            "label": EMOTION_LABELS.get(name, name.replace("_", " ").title()),
            "score": score,
            "percent": int(round(score * 100)),
        }
        for name, score in top
        if score >= 0.15
    ][:5]
    conduct_messages = [CONDUCT_LABELS[f] for f in event.conduct_flags if f in CONDUCT_LABELS]
    return {
        "labeled_emotions": labeled_emotions,
        "conduct_messages": conduct_messages,
    }


@login_required
@require_POST
def content_review(request: HttpRequest) -> HttpResponse:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("content_review"):
        return HttpResponse("", status=204)
    text = request.POST.get("text", "")
    surface = request.POST.get("surface", ContentReviewSurface.POST)
    if surface not in ContentReviewSurface.values:
        surface = ContentReviewSurface.POST
    try:
        event = create_content_review_event(user=request.user, text=text, surface=surface)
    except ContentReviewError as exc:
        return render(
            request,
            "ai_coach/content_review_panel.html",
            {"event": None, "error": str(exc)},
            status=422,
        )
    context = {"event": event, **_emotion_display_context(event)}
    return render(request, "ai_coach/content_review_panel.html", context)


@login_required
@require_POST
def pre_send_check(request: HttpRequest) -> HttpResponse:
    text = request.POST.get("text", "")
    result = classify_civility(text=text)
    event = None
    if result.message:
        event = create_civility_prompt_event(user=request.user, text=text)
    return render(
        request,
        "ai_coach/pre_send_prompt.html",
        {"prompt": result.message, "event": event, "prompt_type": result.prompt_type},
    )


@login_required
@require_POST
def record_civility_action_view(request: HttpRequest) -> HttpResponse:
    event_id = request.POST.get("event_id")
    user_action = request.POST.get("user_action", "")
    text = request.POST.get("text", "")
    if not event_id:
        return JsonResponse({"ok": False}, status=400)
    record_civility_action(
        event_id=int(event_id),
        user=request.user,
        user_action=user_action,
        text=text,
    )
    return JsonResponse({"ok": True})


@login_required
def journal_list(request: HttpRequest) -> HttpResponse:
    entries = ReflectionJournalEntry.objects.filter(user=request.user).order_by("-created_at")[:50]
    return render(request, "ai_coach/journal_list.html", {"entries": entries})


@login_required
def journal_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            create_journal_entry(user=request.user, body=form.cleaned_data["body"])
            return redirect("ai_coach:journal_list")
    else:
        form = JournalEntryForm()
    return render(request, "ai_coach/journal_form.html", {"form": form})
