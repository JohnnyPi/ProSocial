import uuid

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from apps.guilds.models import Guild, GuildMembership


def get_guild_list(*, user=None):
    return Guild.objects.all().order_by("name")


def get_guild_by_slug(*, slug: str) -> Guild:
    return get_object_or_404(Guild, slug=slug)


def get_guild_by_public_id(*, public_id: uuid.UUID) -> Guild:
    return get_object_or_404(Guild, public_id=public_id)


def is_guild_member(*, user, guild: Guild) -> bool:
    return GuildMembership.objects.filter(guild=guild, user=user).exists()


def get_user_guild_ids(*, user) -> list[int]:
    return list(GuildMembership.objects.filter(user=user).values_list("guild_id", flat=True))


def get_user_guilds(*, user, limit: int = 5):
    return Guild.objects.filter(memberships__user=user).order_by("name")[:limit]


def get_guild_feed(*, guild: Guild, page: int = 1, per_page: int = 20):
    from apps.posts.models import Post

    queryset = (
        Post.objects.visible()
        .filter(guild=guild)
        .select_related("author", "author__profile")
        .order_by("-created_at")
    )
    return Paginator(queryset, per_page).get_page(page)
