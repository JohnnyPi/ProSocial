from django import forms

from apps.posts.models import PostKind
from apps.prosocial_actions.models import VerificationMode


class ActionOpportunityForm(forms.Form):
    kind = forms.ChoiceField(choices=[(k, l) for k, l in PostKind.choices if k != PostKind.GENERAL])
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    location_label = forms.CharField(required=False, max_length=200)
    starts_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    ends_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    capacity = forms.IntegerField(required=False, min_value=1)
    verification_mode = forms.ChoiceField(choices=VerificationMode.choices)
    completion_instructions = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))


class CommitmentForm(forms.Form):
    commit_now = forms.BooleanField(required=False, initial=True, label="Commit now")
    scheduled_for = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    reminder_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    reminders_enabled = forms.BooleanField(required=False, initial=True, label="Send reminder")
    private_note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    is_public = forms.BooleanField(required=False, initial=False, label="Show participation publicly")


class CompletionForm(forms.Form):
    participant_note = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)


class InvitationForm(forms.Form):
    invitee_username = forms.CharField(max_length=150, label="Username")
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), max_length=280)


class AcknowledgementForm(forms.Form):
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), max_length=280)


class RejectCompletionForm(forms.Form):
    reviewer_note = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), max_length=500)
