from django import forms
from django.conf import settings

from apps.accounts.validators import validate_handle
from apps.common.image_processing import ImageProcessingError, process_uploaded_image
from apps.profiles.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("handle", "display_name", "biography", "profile_image", "header_image")
        widgets = {
            "biography": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_handle(self) -> str:
        handle = validate_handle(self.cleaned_data["handle"])
        queryset = Profile.objects.filter(handle__iexact=handle)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("This handle is already taken.")
        return handle

    def clean_biography(self) -> str:
        biography = self.cleaned_data.get("biography", "")
        if len(biography) > settings.PROFILE_BIO_MAX_LENGTH:
            raise forms.ValidationError(
                f"Biography must be at most {settings.PROFILE_BIO_MAX_LENGTH} characters."
            )
        return biography

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if not image:
            return image
        if hasattr(image, "file") and image.size == 0:
            return self.instance.profile_image
        try:
            processed = process_uploaded_image(image, actor=getattr(self, "actor", None))
            return processed
        except ImageProcessingError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def clean_header_image(self):
        image = self.cleaned_data.get("header_image")
        if not image:
            return image
        if hasattr(image, "file") and image.size == 0:
            return self.instance.header_image
        try:
            processed = process_uploaded_image(image, actor=getattr(self, "actor", None))
            return processed
        except ImageProcessingError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def save(self, commit=True):
        profile = super().save(commit=False)
        processed = self.cleaned_data.get("profile_image")
        if processed and hasattr(processed, "read"):
            profile.profile_image.save(processed.name, processed, save=False)
        header = self.cleaned_data.get("header_image")
        if header and hasattr(header, "read"):
            profile.header_image.save(header.name, header, save=False)
        if commit:
            profile.save()
        return profile
