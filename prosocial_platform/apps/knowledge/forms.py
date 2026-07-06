from django import forms

from apps.knowledge.models import Collection, CollectionVisibility


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ("title", "description", "visibility")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_visibility(self):
        visibility = self.cleaned_data["visibility"]
        if visibility != CollectionVisibility.PRIVATE and not self.instance.pk:
            if visibility == CollectionVisibility.GUILD:
                pass
        return visibility


class ClipNoteForm(forms.Form):
    private_note = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Private note…"}),
    )
