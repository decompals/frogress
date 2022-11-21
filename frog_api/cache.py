from django.core.cache import cache
from rest_framework.utils.serializer_helpers import ReturnDict

ENTRIES_CACHE_TIMEOUT = 7200  # 2 hours


def _entries_cache_key(project_slug: str, version_slug: str, category_slug: str) -> str:
    return f"entries_{project_slug}_{version_slug}_{category_slug}"


def get_entries_cache(
    project_slug: str, version_slug: str, category_slug: str
) -> ReturnDict | None:
    """
    Fetches cached entries data.
    """
    return cache.get(_entries_cache_key(project_slug, version_slug, category_slug))


def set_entries_cache(
    project_slug: str, version_slug: str, category_slug: str, data: ReturnDict
):
    """
    Updates cached entries data.
    """
    return cache.set(_entries_cache_key(project_slug, version_slug, category_slug), data, ENTRIES_CACHE_TIMEOUT)


def invalidate_entries_cache(project_slug: str, version_slug: str, data: ReturnDict):
    """
    Invalidates all affected entries caches.
    """
    all_categories = set()
    for entry in data["entries"]:
        for category in entry["categories"]:
            all_categories.add(category)
    for category_slug in all_categories:
        cache.delete(_entries_cache_key(project_slug, version_slug, category_slug))
