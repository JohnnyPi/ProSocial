from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to the platform terms",
        error_messages={"required": "You must agree to the platform terms."},
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_username(self) -> str:
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        if password2:
            validate_password(
                password2,
                user=User(
                    username=self.cleaned_data.get("username", ""),
                    email=self.cleaned_data.get("email", ""),
                ),
            )
        return password2


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Invalid username or password.",
        "inactive": "This account is inactive.",
    }


class ProsocialPasswordChangeForm(PasswordChangeForm):
    pass


class AccountDeletionForm(forms.Form):
    password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    confirm = forms.BooleanField(
        required=True,
        label="I understand my account will be permanently deleted after the grace period.",
        error_messages={"required": "You must confirm account deletion."},
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self) -> str:
        password = self.cleaned_data.get("password", "")
        if self.user and not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password
