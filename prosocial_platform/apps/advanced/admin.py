from django.contrib import admin

from apps.advanced.models import (
    DataExportRequest,
    Donation,
    DonationCampaign,
    SkillOffering,
    Workshop,
)

admin.site.register(DonationCampaign)
admin.site.register(Donation)
admin.site.register(SkillOffering)
admin.site.register(Workshop)
admin.site.register(DataExportRequest)
