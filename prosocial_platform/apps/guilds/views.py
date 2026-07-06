from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.guilds.forms import GuildForm
from apps.guilds.models import Guild
from apps.guilds.selectors import (
    get_guild_by_slug,
    get_guild_feed,
    get_user_guild_ids,
    get_user_guilds,
    is_guild_member,
)
from apps.guilds.services import create_guild, join_guild, leave_guild


@login_required
def guild_list(request: HttpRequest) -> HttpResponse:
    user_guilds = get_user_guilds(user=request.user, limit=50)
    browse_guilds = Guild.objects.exclude(pk__in=get_user_guild_ids(user=request.user)).order_by(
        "name"
    )[:20]
    return render(
        request,
        "guilds/guild_list.html",
        {"user_guilds": user_guilds, "browse_guilds": browse_guilds},
    )


@login_required
def guild_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = GuildForm(request.POST)
        if form.is_valid():
            guild = create_guild(
                creator=request.user,
                name=form.cleaned_data["name"],
                description=form.cleaned_data.get("description", ""),
                guild_type=form.cleaned_data["guild_type"],
            )
            return redirect("guilds:detail", slug=guild.slug)
    else:
        form = GuildForm()
    return render(request, "guilds/guild_form.html", {"form": form})


def guild_detail(request: HttpRequest, slug: str) -> HttpResponse:
    guild = get_guild_by_slug(slug=slug)
    feed_page = get_guild_feed(guild=guild, page=request.GET.get("page", 1))
    member = request.user.is_authenticated and is_guild_member(user=request.user, guild=guild)
    return render(
        request,
        "guilds/guild_detail.html",
        {"guild": guild, "feed_page": feed_page, "is_member": member},
    )


@login_required
def guild_join(request: HttpRequest, slug: str) -> HttpResponse:
    guild = get_guild_by_slug(slug=slug)
    join_guild(user=request.user, guild=guild)
    return redirect("guilds:detail", slug=guild.slug)


@login_required
def guild_leave(request: HttpRequest, slug: str) -> HttpResponse:
    guild = get_guild_by_slug(slug=slug)
    leave_guild(user=request.user, guild=guild)
    return redirect("guilds:list")
