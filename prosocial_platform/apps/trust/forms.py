from django import forms

from apps.trust.models import HelperStyle, ScoreVisibility


class HelperStyleOnboardingForm(forms.Form):
    helper_style = forms.ChoiceField(choices=HelperStyle.choices, widget=forms.RadioSelect)


class ScoreVisibilityForm(forms.Form):
    score_visibility = forms.ChoiceField(choices=ScoreVisibility.choices, widget=forms.RadioSelect)


class PeerRatingForm(forms.Form):
    dimension = forms.ChoiceField(
        choices=[
            ("HELPED_ME", "This helped me"),
            ("HELPFUL", "Helpful"),
            ("SUPPORTIVE", "Supportive"),
            ("INSIGHTFUL", "Insightful"),
        ]
    )
