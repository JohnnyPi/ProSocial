from django import forms

from apps.guilds.models import Guild, GuildType


class GuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = ("name", "description", "guild_type")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 3:
            raise forms.ValidationError("Guild name must be at least 3 characters.")
        return name
