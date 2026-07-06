from django import forms
from django.conf import settings

from apps.common.image_processing import ImageProcessingError, process_uploaded_image
from apps.posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("body", "image", "image_alt_text")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Share an update…"}),
        }

    def clean_body(self) -> str:
        body = self.cleaned_data.get("body", "")
        if len(body) > settings.POST_BODY_MAX_LENGTH:
            raise forms.ValidationError(
                f"Post text must be at most {settings.POST_BODY_MAX_LENGTH} characters."
            )
        return body

    def clean(self):
        cleaned = super().clean()
        body = (cleaned.get("body") or "").strip()
        image = cleaned.get("image")
        has_existing_image = bool(self.instance.pk and self.instance.image)
        has_new_image = bool(image and hasattr(image, "read"))

        if not body and not has_new_image and not has_existing_image:
            raise forms.ValidationError("A post must contain text, an image, or both.")

        cleaned["body"] = body
        if not body and has_existing_image:
            cleaned["body"] = self.instance.body
        return cleaned

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            if self.instance.pk and self.instance.image:
                return self.instance.image
            return image
        try:
            return process_uploaded_image(image, actor=getattr(self, "actor", None))
        except ImageProcessingError as exc:
            raise forms.ValidationError(str(exc)) from exc


class PostDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Yes, delete this post",
    )
