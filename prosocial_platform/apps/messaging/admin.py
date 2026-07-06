from django.contrib import admin

from apps.messaging.models import Conversation, Message

admin.site.register(Conversation)
admin.site.register(Message)
