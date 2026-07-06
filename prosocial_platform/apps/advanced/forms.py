from django import forms

from apps.advanced.models import DonationCampaign, SkillOffering


class DonationCampaignForm(forms.ModelForm):
    class Meta:
        model = DonationCampaign
        fields = ("title", "organization_name", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class DonationForm(forms.Form):
    amount_dollars = forms.DecimalField(min_value=1, max_digits=8, decimal_places=2)
    is_anonymous = forms.BooleanField(required=False, initial=True)


class SkillOfferingForm(forms.ModelForm):
    class Meta:
        model = SkillOffering
        fields = ("skill_name", "description", "is_remote")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
