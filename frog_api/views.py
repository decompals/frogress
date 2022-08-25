from typing import Any
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from frog_api.models import Category, Entry, Project, Version
from frog_api.serializers import (
    ProjectSerializer,
    TerseEntrySerializer,
)


class MissingModelException(APIException):
    status_code = status.HTTP_404_NOT_FOUND


class ProjectView(APIView):
    """
    API endpoint that allows projects to be viewed.
    """

    def get(self, request: Request) -> Response:
        """
        Return a list of all projects.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


def get_latest_entry(project: str, version: str, category: str) -> dict[Any, Any]:
    if not Project.objects.filter(slug=project).exists():
        raise MissingModelException(f"Project {project} not found")

    if not Version.objects.filter(slug=version, project__slug=project).exists():
        raise MissingModelException(
            f"Version '{version}' not found for project '{project}'"
        )

    if not Category.objects.filter(
        slug=category, version__slug=version, version__project__slug=project
    ).exists():
        raise MissingModelException(
            f"Category '{category}' not found for project '{project}' and version '{version}'"
        )

    entry = Entry.objects.filter(
        category__slug=category,
        category__version__slug=version,
        category__version__project__slug=project,
    ).first()

    if entry is None:
        raise MissingModelException(
            f"No data exists for project '{project}', version '{version}', and category '{category}'"
        )

    # Re-format the measures (TODO: DRF-ify this?)
    entry_data = TerseEntrySerializer(entry).data
    entry_data["measures"] = {m["type"]: m["value"] for m in entry_data["measures"]}
    return entry_data


def get_versions_digest_for_project(project: str) -> dict[Any, Any]:
    versions = {}
    for version in Version.objects.filter(project__slug=project):
        entry = get_latest_entry(project, version.slug, "total")
        if entry is not None:
            versions[version.slug] = entry
    return versions


class RootDigestView(APIView):
    """
    API endpoint that returns the most recent entry for each version of each project.
    """

    def get(self, request: Request) -> Response:
        """
        Return the most recent entry for ovreall progress for each version of each project.
        """

        projects = {}
        for project in Project.objects.all():
            versions = get_versions_digest_for_project(project.slug)
            if len(versions) > 0:
                projects[project.slug] = versions

        return Response({"progress": projects})


class ProjectDigestView(APIView):
    """
    API endpoint that returns the most recent entry for each version of a project.
    """

    def get(self, request: Request, project: str) -> Response:
        """
        Return the most recent entry for overall progress for each version of a project.
        """

        if not Project.objects.filter(slug=project).exists():
            raise MissingModelException(f"Project {project} not found")

        projects = {}

        versions = get_versions_digest_for_project(project)
        if len(versions) > 0:
            projects[project] = versions

        return Response({"progress": projects})


class VersionDigestView(APIView):
    """
    API endpoint that returns the most recent entry for overall progress for a version of a project.
    """

    def get(self, request: Request, project: str, version: str) -> Response:
        """
        Return the most recent entry for overall progress for a version of a project.
        """

        entry = get_latest_entry(project, version, "total")

        return Response(entry)


class CategoryDigestView(APIView):
    """
    API endpoint that returns the most recent entry for a specific cagory and a version of a project.
    """

    def get(
        self, request: Request, project: str, version: str, category: str
    ) -> Response:
        """
        Return the most recent entry for a specific cagory and a version of a project.
        """

        entry = get_latest_entry(project, version, category)

        return Response(entry)
