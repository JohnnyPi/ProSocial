"""Trust cluster assignment via guild membership and follow graph."""

from collections import defaultdict, deque

from apps.follows.models import UserFollow
from apps.guilds.models import GuildMembership
from apps.trust.models import TrustCluster


def _build_adjacency() -> dict[int, set[int]]:
    adjacency: dict[int, set[int]] = defaultdict(set)
    for follower_id, following_id in UserFollow.objects.values_list("follower_id", "following_id"):
        adjacency[follower_id].add(following_id)
        adjacency[following_id].add(follower_id)
    guild_members: dict[int, set[int]] = defaultdict(set)
    for user_id, guild_id in GuildMembership.objects.values_list("user_id", "guild_id"):
        guild_members[guild_id].add(user_id)
    for members in guild_members.values():
        for user_id in members:
            adjacency[user_id].update(members - {user_id})
    return adjacency


def compute_trust_clusters() -> dict[int, str]:
    adjacency = _build_adjacency()
    user_to_cluster: dict[int, str] = {}
    cluster_index = 0
    for user_id in adjacency:
        if user_id in user_to_cluster:
            continue
        cluster_id = f"cluster_{cluster_index}"
        cluster_index += 1
        queue = deque([user_id])
        user_to_cluster[user_id] = cluster_id
        while queue:
            current = queue.popleft()
            for neighbor in adjacency.get(current, set()):
                if neighbor not in user_to_cluster:
                    user_to_cluster[neighbor] = cluster_id
                    queue.append(neighbor)
    return user_to_cluster


def sync_trust_clusters() -> int:
    mapping = compute_trust_clusters()
    updated = 0
    for user_id, cluster_id in mapping.items():
        TrustCluster.objects.update_or_create(
            user_id=user_id,
            defaults={"cluster_id": cluster_id},
        )
        updated += 1
    return updated


def get_user_cluster_id(*, user) -> str:
    cluster = TrustCluster.objects.filter(user=user).first()
    if cluster:
        return cluster.cluster_id
    return f"solo_{user.pk}"


def get_cluster_ids_for_users(*, user_ids: set[int]) -> dict[int, str]:
    if not user_ids:
        return {}
    clusters = dict(
        TrustCluster.objects.filter(user_id__in=user_ids).values_list("user_id", "cluster_id")
    )
    for user_id in user_ids:
        clusters.setdefault(user_id, f"solo_{user_id}")
    return clusters
