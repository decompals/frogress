from django.urls import path, re_path
from frog_api.views import data, structure

urlpatterns = [
    # structure (/project)
    path(
        "projects/",
        structure.ProjectStructureView.as_view(),
    ),
    re_path(
        "projects/(?P<project_slug>.+)/(?P<version_slug>.+)/$",
        structure.CategoryStructureView.as_view(),
        name="category-structure",
    ),
    # data (/data)
    re_path(
        "data/(?P<project_slug>.+)/(?P<version_slug>.+)/(?P<category_slug>.+)/$",
        data.CategoryDataView.as_view(),
    ),
    re_path(
        "data/(?P<project_slug>.+)/(?P<version_slug>.+)/$",
        data.VersionDataView.as_view(),
        name="version-data",
    ),
    re_path(
        "data/(?P<project_slug>.+)/$",
        data.ProjectDataView.as_view(),
    ),
    path(
        "data/",
        data.RootDataView.as_view(),
    ),
]
