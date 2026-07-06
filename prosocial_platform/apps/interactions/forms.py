from django import forms

from apps.interactions.models import Reply as ReplyModel
from apps.interactions.models import ReportReason


class ReplyForm(forms.ModelForm):
    class Meta:
        model = ReplyModel
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a reply…"})}

    def clean_body(self) -> str:
        body = self.cleaned_data.get("body", "").strip()
        if not body:
            raise forms.ValidationError("Reply cannot be empty.")
        return body


class ReplyDeleteForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Yes, delete this reply")


class ReportForm(forms.Form):
    reason = forms.ChoiceField(choices=ReportReason.choices)
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Optional details…"}),
        max_length=1000,
    )


class MuteConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Yes, mute this user")


class BlockConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Yes, block this user")
