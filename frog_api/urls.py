from django.urls import path, re_path
from frog_api.views import data, structure

urlpatterns = [
    # structure (/project)
    path(
        "projects/",
        structure.ProjectStructureView.as_view(),
    ),
    re_path(
        "projects/(?P<project>.+)/(?P<version>.+)/$",
        structure.CategoryStructureView.as_view(),
    ),
    # data (/data)
    re_path(
        "data/(?P<project>.+)/(?P<version>.+)/(?P<category>.+)/$",
        data.CategoryDataView.as_view(),
    ),
    re_path(
        "data/(?P<project>.+)/(?P<version>.+)/$",
        data.VersionDataView.as_view(),
    ),
    re_path(
        "data/(?P<project>.+)/$",
        data.ProjectDataView.as_view(),
    ),
    path(
        "data/",
        data.RootDataView.as_view(),
    ),
]
