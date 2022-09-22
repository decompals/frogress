from django.urls import path, re_path
from frog_api.views import data, structure

urlpatterns = [
    # structure (/project)
    re_path(
        "projects/(?P<project_slug>.+)/(?P<version_slug>.+)/(?P<category_slug>.+)/$",
        structure.CategoryStructureView.as_view(),
        name="category-structure",
    ),
    re_path(
        "projects/(?P<project_slug>.+)/(?P<version_slug>.+)/$",
        structure.VersionStructureView.as_view(),
        name="version-structure",
    ),
    re_path(
        "projects/(?P<project_slug>.+)/$",
        structure.ProjectStructureView.as_view(),
        name="project-structure",
    ),
    path(
        "projects/",
        structure.RootStructureView.as_view(),
        name="root-structure",
    ),
    # data (/data)
    re_path(
        "data/(?P<project_slug>.+)/(?P<version_slug>.+)/(?P<category_slug>.+)/$",
        data.CategoryDataView.as_view(),
        name="category-data",
    ),
    re_path(
        "data/(?P<project_slug>.+)/(?P<version_slug>.+)/$",
        data.VersionDataView.as_view(),
        name="version-data",
    ),
    re_path(
        "data/(?P<project_slug>.+)/$",
        data.ProjectDataView.as_view(),
        name="project-data",
    ),
    path(
        "data/",
        data.RootDataView.as_view(),
        name="root-data",
    ),
]
