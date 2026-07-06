import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.prosocial_actions.exceptions import ProsocialActionError
from apps.prosocial_actions.forms import (
    AcknowledgementForm,
    ActionOpportunityForm,
    CommitmentForm,
    CompletionForm,
    InvitationForm,
    RejectCompletionForm,
)
from apps.prosocial_actions.models import Commitment
from apps.prosocial_actions.selectors import (
    get_action_detail,
    get_open_actions,
    get_pending_invitations,
    get_pending_verifications,
    get_user_commitments,
)
from apps.prosocial_actions.services import (
    accept_invitation,
    cancel_action,
    commit_to_action,
    create_action_post,
    decline_invitation,
    invite_user,
    reject_completion,
    save_action,
    send_acknowledgement,
    submit_completion,
    verify_completion,
    withdraw_commitment,
)

User = get_user_model()


@login_required
def action_list(request: HttpRequest) -> HttpResponse:
    actions = get_open_actions(kind=request.GET.get("kind"))
    return render(request, "prosocial_actions/action_list.html", {"actions": actions})


@login_required
def action_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ActionOpportunityForm(request.POST)
        if form.is_valid():
            action = create_action_post(
                creator=request.user,
                kind=form.cleaned_data["kind"],
                body=form.cleaned_data["body"],
                location_label=form.cleaned_data.get("location_label", ""),
                starts_at=form.cleaned_data.get("starts_at"),
                ends_at=form.cleaned_data.get("ends_at"),
                capacity=form.cleaned_data.get("capacity"),
                verification_mode=form.cleaned_data["verification_mode"],
                completion_instructions=form.cleaned_data.get("completion_instructions", ""),
            )
            return redirect("prosocial_actions:action_detail", public_id=action.public_id)
    else:
        form = ActionOpportunityForm()
    return render(request, "prosocial_actions/action_form.html", {"form": form})


@login_required
def action_detail(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    user_commitment = Commitment.objects.filter(action=action, participant=request.user).first()
    return render(
        request,
        "prosocial_actions/action_detail.html",
        {"action": action, "user_commitment": user_commitment},
    )


@login_required
def action_cancel(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    if request.method == "POST":
        try:
            cancel_action(action=action, actor=request.user)
        except ProsocialActionError as exc:
            return HttpResponseForbidden(str(exc))
        return redirect("prosocial_actions:action_list")
    return render(request, "prosocial_actions/action_cancel_confirm.html", {"action": action})


@login_required
def action_save(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    if request.method == "POST":
        try:
            save_action(action=action, participant=request.user)
        except ProsocialActionError as exc:
            return HttpResponseForbidden(str(exc))
    return redirect("prosocial_actions:action_detail", public_id=action.public_id)


@login_required
def action_commit(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    if request.method == "POST":
        form = CommitmentForm(request.POST)
        if form.is_valid():
            try:
                commit_to_action(
                    action=action,
                    participant=request.user,
                    scheduled_for=form.cleaned_data.get("scheduled_for"),
                    reminder_at=form.cleaned_data.get("reminder_at"),
                    private_note=form.cleaned_data.get("private_note", ""),
                    is_public=form.cleaned_data.get("is_public", False),
                )
            except ProsocialActionError as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("prosocial_actions:action_detail", public_id=action.public_id)
    else:
        form = CommitmentForm()
    return render(
        request,
        "prosocial_actions/commitment_form.html",
        {"form": form, "action": action},
    )


@login_required
def action_withdraw(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    commitment = get_object_or_404(Commitment, action=action, participant=request.user)
    if request.method == "POST":
        try:
            withdraw_commitment(commitment=commitment, participant=request.user)
        except ProsocialActionError as exc:
            return HttpResponseForbidden(str(exc))
    return redirect("prosocial_actions:action_detail", public_id=action.public_id)


@login_required
def action_complete(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    commitment = get_object_or_404(Commitment, action=action, participant=request.user)
    if request.method == "POST":
        form = CompletionForm(request.POST)
        if form.is_valid():
            try:
                submit_completion(
                    commitment=commitment,
                    participant=request.user,
                    note=form.cleaned_data.get("participant_note", ""),
                )
            except ProsocialActionError as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("prosocial_actions:commitment_detail", public_id=commitment.public_id)
    else:
        form = CompletionForm()
    return render(
        request,
        "prosocial_actions/completion_form.html",
        {"form": form, "action": action, "commitment": commitment},
    )


@login_required
def commitment_list(request: HttpRequest) -> HttpResponse:
    commitments = get_user_commitments(user=request.user)
    return render(request, "prosocial_actions/commitment_list.html", {"commitments": commitments})


@login_required
def commitment_detail(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    commitment = get_object_or_404(
        Commitment.objects.select_related("action", "action__post"),
        public_id=public_id,
    )
    if commitment.participant_id != request.user.pk and commitment.action.creator_id != request.user.pk:
        if not commitment.is_public:
            return HttpResponseForbidden("This commitment is private.")
    return render(request, "prosocial_actions/commitment_detail.html", {"commitment": commitment})


@login_required
def commitment_verify(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    commitment = get_object_or_404(Commitment, public_id=public_id)
    if request.method == "POST":
        try:
            verify_completion(commitment=commitment, reviewer=request.user)
        except ProsocialActionError as exc:
            return HttpResponseForbidden(str(exc))
    return redirect("prosocial_actions:verification_queue")


@login_required
def commitment_reject(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    commitment = get_object_or_404(Commitment, public_id=public_id)
    if request.method == "POST":
        form = RejectCompletionForm(request.POST)
        if form.is_valid():
            try:
                reject_completion(
                    commitment=commitment,
                    reviewer=request.user,
                    note=form.cleaned_data.get("reviewer_note", ""),
                )
            except ProsocialActionError as exc:
                return HttpResponseForbidden(str(exc))
            return redirect("prosocial_actions:verification_queue")
    else:
        form = RejectCompletionForm()
    return render(
        request,
        "prosocial_actions/verification_detail.html",
        {"form": form, "commitment": commitment},
    )


@login_required
def commitment_acknowledge(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    commitment = get_object_or_404(Commitment, public_id=public_id)
    if request.method == "POST":
        form = AcknowledgementForm(request.POST)
        if form.is_valid():
            try:
                send_acknowledgement(
                    commitment=commitment,
                    sender=request.user,
                    message=form.cleaned_data.get("message", ""),
                )
            except ProsocialActionError as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("prosocial_actions:commitment_detail", public_id=commitment.public_id)
    else:
        form = AcknowledgementForm()
    return render(
        request,
        "prosocial_actions/acknowledgement_form.html",
        {"form": form, "commitment": commitment},
    )


@login_required
def action_invite(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    action = get_action_detail(public_id=public_id)
    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitee = get_object_or_404(User, username=form.cleaned_data["invitee_username"])
            try:
                invite_user(
                    action=action,
                    inviter=request.user,
                    invitee=invitee,
                    message=form.cleaned_data.get("message", ""),
                )
            except ProsocialActionError as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("prosocial_actions:action_detail", public_id=action.public_id)
    else:
        form = InvitationForm()
    return render(
        request,
        "prosocial_actions/invitation_form.html",
        {"form": form, "action": action},
    )


@login_required
def invitation_list(request: HttpRequest) -> HttpResponse:
    invitations = get_pending_invitations(user=request.user)
    return render(request, "prosocial_actions/invitation_list.html", {"invitations": invitations})


@login_required
def invitation_accept(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    from apps.prosocial_actions.models import ActionInvitation
    invitation = get_object_or_404(ActionInvitation, public_id=public_id, invitee=request.user)
    if request.method == "POST":
        try:
            commitment = accept_invitation(invitation=invitation, invitee=request.user)
        except ProsocialActionError as exc:
            return HttpResponseForbidden(str(exc))
        return redirect("prosocial_actions:commitment_detail", public_id=commitment.public_id)
    return redirect("prosocial_actions:invitations")


@login_required
def invitation_decline(request: HttpRequest, public_id: uuid.UUID) -> HttpResponse:
    from apps.prosocial_actions.models import ActionInvitation
    invitation = get_object_or_404(ActionInvitation, public_id=public_id, invitee=request.user)
    if request.method == "POST":
        decline_invitation(invitation=invitation, invitee=request.user)
    return redirect("prosocial_actions:invitations")


@login_required
def verification_queue(request: HttpRequest) -> HttpResponse:
    pending = get_pending_verifications(creator=request.user)
    return render(request, "prosocial_actions/verification_queue.html", {"pending": pending})
