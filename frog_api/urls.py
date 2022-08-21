from django.urls import path, re_path
from frog_api import views

urlpatterns = [
    path("projects/", views.ProjectView.as_view()),
    path(
        "data/",
        views.RootDigestView.as_view(),
    ),
    re_path(
        "data/(?P<project>.+)/$",
        views.ProjectDigestView.as_view(),
    ),
    # re_path(
    #     "data/(?P<project>.+)/(?P<version>.+)/$",
    #     views.EntryView.as_view(),
    # ),
    # re_path(
    #     "data/(?P<project>.+)/(?P<version>.+)/(?P<category>.+)/$",
    #     views.EntryView.as_view(),
    # ),
]
