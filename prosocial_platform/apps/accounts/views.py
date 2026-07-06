from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from apps.accounts.forms import (
    AccountDeletionForm,
    LoginForm,
    ProsocialPasswordChangeForm,
    RegistrationForm,
)
from apps.accounts.services import (
    AccountDeletionError,
    cancel_account_deletion,
    get_pending_deletion_request,
    register_user,
    request_account_deletion,
)
from apps.common.rate_limit import is_rate_limited, rate_limit_key
from apps.common.services import ActivityEventType, record_activity_event


class ProsocialLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm

    def _login_rate_limited(self, identifier: str) -> bool:
        key = rate_limit_key("login", f"{identifier}:{self.request.META.get('REMOTE_ADDR', '')}")
        return is_rate_limited(
            key=key,
            limit=settings.LOGIN_RATE_LIMIT,
            window_seconds=settings.LOGIN_RATE_WINDOW_SECONDS,
        )

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("username", "")
        if self._login_rate_limited(identifier):
            form = self.get_form()
            form.add_error(None, "Too many login attempts. Please try again later.")
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        record_activity_event(
            event_type=ActivityEventType.LOGIN_SUCCEEDED,
            actor=self.request.user,
            object_type="user",
            object_public_id=self.request.user.public_id,
        )
        return response

    def form_invalid(self, form):
        username = self.request.POST.get("username", "")
        record_activity_event(
            event_type=ActivityEventType.LOGIN_FAILED,
            metadata={"username_attempt": username[:64]},
        )
        return super().form_invalid(form)


class ProsocialLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        key = rate_limit_key("register", request.META.get("REMOTE_ADDR", "unknown"))
        if is_rate_limited(
            key=key,
            limit=settings.REGISTRATION_RATE_LIMIT,
            window_seconds=settings.REGISTRATION_RATE_WINDOW_SECONDS,
        ):
            messages.error(request, "Too many registration attempts. Please try again later.")
            return render(request, "registration/register.html", {"form": RegistrationForm()})

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = register_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("dashboard:index")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


class ProsocialPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change_form.html"
    form_class = ProsocialPasswordChangeForm
    success_url = reverse_lazy("accounts:password_change_done")


class ProsocialPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "registration/password_change_done.html"


class ProsocialPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class ProsocialPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class ProsocialPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class ProsocialPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


@login_required
def password_change_redirect(request: HttpRequest) -> HttpResponse:
    return redirect("accounts:password_change")


@login_required
def account_delete(request: HttpRequest) -> HttpResponse:
    pending = get_pending_deletion_request(user=request.user)
    if request.method == "POST":
        if pending:
            messages.error(request, "Account deletion is already scheduled.")
            return redirect("accounts:account_delete")
        form = AccountDeletionForm(user=request.user, data=request.POST)
        if form.is_valid():
            try:
                deletion_request = request_account_deletion(
                    user=request.user,
                    password=form.cleaned_data["password"],
                )
            except AccountDeletionError as exc:
                form.add_error(None, str(exc))
            else:
                logout(request)
                messages.success(
                    request,
                    "Your account is scheduled for deletion on "
                    f"{deletion_request.scheduled_for:%B %d, %Y}. "
                    "Sign in before then if you want to cancel.",
                )
                return redirect("accounts:login")
    else:
        form = AccountDeletionForm(user=request.user)

    return render(
        request,
        "registration/account_delete.html",
        {
            "form": form,
            "pending": pending,
            "grace_days": settings.ACCOUNT_DELETION_GRACE_DAYS,
        },
    )


@login_required
@require_POST
def account_delete_cancel(request: HttpRequest) -> HttpResponse:
    try:
        cancel_account_deletion(user=request.user)
    except AccountDeletionError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Your account deletion request has been cancelled.")
    return redirect("accounts:account_delete")
