from django.db import transaction
from django.utils.text import slugify

from apps.common.models import ActivityEventType
from apps.common.services import record_activity_event
from apps.guilds.models import Guild, GuildMembership, GuildRole


class GuildError(Exception):
    pass


@transaction.atomic
def create_guild(*, creator, name: str, description: str = "", guild_type: str = "CAUSE") -> Guild:
    base_slug = slugify(name)[:90] or "guild"
    slug = base_slug
    counter = 1
    while Guild.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    guild = Guild.objects.create(
        name=name.strip(),
        slug=slug,
        description=description.strip(),
        guild_type=guild_type,
        created_by=creator,
    )
    GuildMembership.objects.create(guild=guild, user=creator, role=GuildRole.LEADER)
    record_activity_event(
        event_type=ActivityEventType.GUILD_JOINED,
        actor=creator,
        object_type="guild",
        object_public_id=guild.public_id,
        metadata={"action": "created"},
    )
    return guild


@transaction.atomic
def join_guild(*, user, guild: Guild) -> GuildMembership:
    membership, created = GuildMembership.objects.get_or_create(
        guild=guild, user=user, defaults={"role": GuildRole.MEMBER}
    )
    if created:
        record_activity_event(
            event_type=ActivityEventType.GUILD_JOINED,
            actor=user,
            object_type="guild",
            object_public_id=guild.public_id,
            metadata={"action": "joined"},
        )
    return membership


@transaction.atomic
def leave_guild(*, user, guild: Guild) -> None:
    membership = GuildMembership.objects.filter(guild=guild, user=user).first()
    if not membership:
        return
    if membership.role == GuildRole.LEADER:
        other = GuildMembership.objects.filter(guild=guild).exclude(user=user).first()
        if other:
            other.role = GuildRole.LEADER
            other.save(update_fields=["role"])
        elif GuildMembership.objects.filter(guild=guild).count() <= 1:
            guild.delete()
            return
    membership.delete()
