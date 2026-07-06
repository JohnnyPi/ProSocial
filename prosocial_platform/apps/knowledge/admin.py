from django.contrib import admin

from apps.knowledge.models import Clip, Collection, CollectionItem, PostTag, Tag

admin.site.register(Tag)
admin.site.register(PostTag)
admin.site.register(Clip)
admin.site.register(Collection)
admin.site.register(CollectionItem)
