from django.contrib import admin

from apps.follows.models import PostFollow, UserFollow

admin.site.register(UserFollow)
admin.site.register(PostFollow)
