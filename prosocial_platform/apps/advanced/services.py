from django.db import transaction
from django.utils import timezone

from apps.advanced.export_builders import build_export_payload
from apps.advanced.models import DataExportRequest, Donation, DonationCampaign, DonationStatus


@transaction.atomic
def create_donation_campaign(
    *, creator, title: str, organization_name: str, description: str = ""
) -> DonationCampaign:
    return DonationCampaign.objects.create(
        created_by=creator,
        title=title.strip(),
        organization_name=organization_name.strip(),
        description=description.strip(),
    )


@transaction.atomic
def record_donation(
    *, donor, campaign: DonationCampaign, amount_cents: int, is_anonymous: bool = True
) -> Donation:
    fee = int(amount_cents * 0.029) + 30
    return Donation.objects.create(
        donor=donor,
        campaign=campaign,
        amount_cents=amount_cents,
        processing_fee_cents=fee,
        status=DonationStatus.COMPLETED,
        is_anonymous=is_anonymous,
    )


@transaction.atomic
def request_data_export(*, user) -> DataExportRequest:
    export = DataExportRequest.objects.create(user=user, status="PROCESSING")
    data = build_export_payload(user=user)
    export.file_path = f"exports/{user.pk}_{export.pk}.json"
    export.status = "COMPLETED"
    export.completed_at = timezone.now()
    export.save()
    export._payload = data  # noqa: SLF001 - attached for view response
    return export
