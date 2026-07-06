from django.contrib import admin

from apps.trust.models import PeerRating, TrustEvent, UserTrustProfile

admin.site.register(UserTrustProfile)
admin.site.register(PeerRating)
admin.site.register(TrustEvent)
