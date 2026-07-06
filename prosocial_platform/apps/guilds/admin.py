from django.contrib import admin

from apps.guilds.models import Guild, GuildMembership

admin.site.register(Guild)
admin.site.register(GuildMembership)
