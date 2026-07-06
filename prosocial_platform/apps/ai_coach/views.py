from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.ai_coach.forms import JournalEntryForm
from apps.ai_coach.models import ReflectionJournalEntry
from apps.ai_coach.services import create_journal_entry, pre_send_prompt


@login_required
@require_POST
def pre_send_check(request: HttpRequest) -> HttpResponse:
    prompt = pre_send_prompt(text=request.POST.get("text", ""))
    return render(request, "ai_coach/pre_send_prompt.html", {"prompt": prompt})


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
