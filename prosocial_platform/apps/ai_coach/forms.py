from django import forms


class JournalEntryForm(forms.Form):
    body = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "Write your reflection…"}),
    )
