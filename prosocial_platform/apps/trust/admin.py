from django.contrib import admin

from apps.trust.models import (
    DomainReputation,
    PeerRating,
    PrivilegeDefinition,
    TrustCluster,
    TrustEvent,
    UserPrivilege,
    UserTrustProfile,
)

admin.site.register(UserTrustProfile)
admin.site.register(PeerRating)
admin.site.register(TrustEvent)
admin.site.register(DomainReputation)
admin.site.register(TrustCluster)
admin.site.register(PrivilegeDefinition)
admin.site.register(UserPrivilege)
