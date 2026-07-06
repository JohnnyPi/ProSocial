from apps.posts.constants import FEED_KIND_FILTERS


def feed_filters(_request):
    return {"feed_kind_filters": FEED_KIND_FILTERS}
