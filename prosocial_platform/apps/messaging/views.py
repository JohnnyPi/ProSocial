from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.messaging.forms import MessageForm
from apps.messaging.selectors import (
    get_conversation_for_user,
    get_conversation_messages,
    get_user_conversations,
)
from apps.messaging.services import MessagingError, mark_messages_read, send_message

User = get_user_model()


@login_required
def conversation_list(request: HttpRequest) -> HttpResponse:
    conversations = get_user_conversations(user=request.user)
    conversation_rows = [
        {"conversation": conversation, "other": conversation.other_participant(request.user)}
        for conversation in conversations
    ]
    return render(
        request,
        "messaging/conversation_list.html",
        {"conversation_rows": conversation_rows},
    )


@login_required
def conversation_detail(request: HttpRequest, public_id) -> HttpResponse:
    conversation = get_conversation_for_user(public_id=public_id, user=request.user)
    mark_messages_read(conversation=conversation, reader=request.user)
    messages = get_conversation_messages(conversation=conversation)
    other = conversation.other_participant(request.user)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            try:
                send_message(
                    sender=request.user,
                    recipient=other,
                    body=form.cleaned_data["body"],
                )
                return redirect("messaging:detail", public_id=conversation.public_id)
            except MessagingError as exc:
                form.add_error("body", str(exc))
    else:
        form = MessageForm()
    return render(
        request,
        "messaging/conversation_detail.html",
        {"conversation": conversation, "messages": messages, "other": other, "form": form},
    )


@login_required
def start_conversation(request: HttpRequest, handle: str) -> HttpResponse:
    recipient = get_object_or_404(User, profile__handle=handle)
    from apps.messaging.services import get_or_create_conversation

    try:
        conversation = get_or_create_conversation(user_a=request.user, user_b=recipient)
    except MessagingError:
        return redirect("profiles:detail", handle=handle)
    return redirect("messaging:detail", public_id=conversation.public_id)
