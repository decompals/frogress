from typing import Optional
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from frog_api.models import Entry, Project, Version
from frog_api.serializers import (
    EntrySerializer,
    ProjectSerializer,
    TerseEntrySerializer,
)


class ProjectView(APIView):
    """
    API endpoint that allows projects to be viewed.
    """

    def get(self, request, format=None):
        """
        Return a list of all projects.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


def get_latest_entry(project, version, category) -> Optional[Entry]:
    return Entry.objects.filter(
        category__slug=category,
        category__version__slug=version,
        category__version__project__slug=project,
    ).first()


def get_versions_digest_for_project(project) -> dict:
    versions = {}
    for version in Version.objects.filter(project__slug=project):
        entry = get_latest_entry(project, version.slug, "total")
        if entry is not None:
            versions[version.slug] = TerseEntrySerializer(entry).data
    return versions


class RootDigestView(APIView):
    """
    API endpoint that returns the most recent entry for each version of each project.
    """

    def get(self, request):
        """
        Return the most recent entry for ovreall progress for each version of each project.
        """

        projects = {}
        for project in Project.objects.all():
            versions = get_versions_digest_for_project(project.slug)
            if len(versions) > 0:
                projects[project.slug] = versions

        entry = get_latest_entry(project=None, version=None, category="total")

        return Response({"progress": projects})


class ProjectDigestView(APIView):
    """
    API endpoint that returns the most recent entry for each version of a project.
    """

    def get(self, request, project):
        """
        Return the most recent entry for ovreall progress for each version of a project.
        """

        if Project.objects.get(slug=project) is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        projects = {}

        versions = get_versions_digest_for_project(project)
        if len(versions) > 0:
            projects[project] = versions

        entry = get_latest_entry(project=None, version=None, category="total")

        return Response({"progress": projects})
