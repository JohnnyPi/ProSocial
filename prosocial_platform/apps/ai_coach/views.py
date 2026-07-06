from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.ai_coach.forms import JournalEntryForm
from apps.ai_coach.models import ReflectionJournalEntry
from apps.ai_coach.services import (
    classify_civility,
    create_civility_prompt_event,
    create_journal_entry,
    record_civility_action,
)


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
