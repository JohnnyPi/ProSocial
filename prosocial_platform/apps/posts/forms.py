from django import forms
from django.conf import settings

from apps.common.image_processing import ImageProcessingError, process_uploaded_image
from apps.posts.constants import ACTION_POST_KINDS, COMPOSER_KIND_CHOICES
from apps.posts.models import Post, ThreadType


def _parse_tag_slugs(raw: str) -> list[str]:
    slugs = [t.strip().lower().replace(" ", "-") for t in raw.split(",") if t.strip()]
    if len(slugs) > 5:
        raise forms.ValidationError("At most 5 tags allowed.")
    return slugs[:5]


class PostForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=200,
        required=False,
        help_text="Comma-separated tags (max 5)",
    )

    class Meta:
        model = Post
        fields = ("kind", "thread_type", "title", "body", "image", "image_alt_text")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Share an update…"}),
            "title": forms.TextInput(attrs={"placeholder": "Optional thread title"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kind"].choices = COMPOSER_KIND_CHOICES
        self.fields["thread_type"].choices = ThreadType.choices
        if self.instance and self.instance.pk:
            tag_names = [
                pt.tag.name
                for pt in self.instance.post_tags.select_related("tag").order_by("tag__name")
            ]
            self.fields["tags"].initial = ", ".join(tag_names)

    def clean_body(self) -> str:
        body = self.cleaned_data.get("body", "")
        if len(body) > settings.POST_BODY_MAX_LENGTH:
            raise forms.ValidationError(
                f"Post text must be at most {settings.POST_BODY_MAX_LENGTH} characters."
            )
        return body

    def clean_tags(self) -> list[str]:
        return _parse_tag_slugs(self.cleaned_data.get("tags", ""))

    def clean_kind(self) -> str:
        kind = self.cleaned_data.get("kind")
        if kind in ACTION_POST_KINDS:
            if self.instance.pk and self.instance.kind == kind:
                return kind
            raise forms.ValidationError(
                "Help requests and action posts must be created from the Actions module."
            )
        return kind

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

    def cleaned_post_kwargs(self) -> dict:
        if not self.is_valid():
            raise ValueError("Form must be valid before extracting post fields.")
        return {
            "body": self.cleaned_data["body"],
            "image": self.cleaned_data.get("image"),
            "image_alt_text": self.cleaned_data.get("image_alt_text", ""),
            "kind": self.cleaned_data["kind"],
            "thread_type": self.cleaned_data["thread_type"],
            "title": self.cleaned_data.get("title", ""),
            "tag_slugs": self.cleaned_data.get("tags", []),
        }


class PostDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Yes, delete this post",
    )
