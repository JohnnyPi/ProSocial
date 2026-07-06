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
        password = self.cleaned_data.get("password2")
        if password:
            validate_password(password, user=self.instance)
        return super().clean_password2()


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Invalid username or password.",
        "inactive": "This account is inactive.",
    }


class ProsocialPasswordChangeForm(PasswordChangeForm):
    pass
