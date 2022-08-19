from django.urls import path
from frog_api import views

urlpatterns = [
    path("projects/", views.ProjectView.as_view()),
]
