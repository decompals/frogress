from django.urls import path, re_path
from frog_api import views

urlpatterns = [
    path("projects/", views.ProjectView.as_view()),
    re_path(
        "projects/(?P<project>.+)/(?P<version>.+)/$",
        views.AddNewCategoryView.as_view(),
    ),
    re_path(
        "data/(?P<project>.+)/(?P<version>.+)/(?P<category>.+)/$",
        views.CategoryDigestView.as_view(),
    ),
    re_path(
        "data/(?P<project>.+)/(?P<version>.+)/$",
        views.VersionDigestView.as_view(),
    ),
    re_path(
        "data/(?P<project>.+)/$",
        views.ProjectDigestView.as_view(),
    ),
    path(
        "data/",
        views.RootDigestView.as_view(),
    ),
]
