from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from frog_api.models import Category, Entry, Project, Version
from frog_api.serializers import (
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


def get_latest_entry(project, version, category) -> dict:
    if not Project.objects.filter(slug=project).exists():
        raise APIException(
            f"Project {project} not found", code=status.HTTP_404_NOT_FOUND
        )

    if not Version.objects.filter(slug=version, project__slug=project).exists():
        raise APIException(
            f"Version '{version}' not found for project '{project}'",
            code=status.HTTP_404_NOT_FOUND,
        )

    if not Category.objects.filter(
        slug=category, version__slug=version, version__project__slug=project
    ).exists():
        raise APIException(
            f"Category '{category}' not found for project '{project}' and version '{version}'",
            code=status.HTTP_404_NOT_FOUND,
        )

    entry = Entry.objects.filter(
        category__slug=category,
        category__version__slug=version,
        category__version__project__slug=project,
    ).first()

    if entry is None:
        raise APIException("Entry is None", code=status.HTTP_404_NOT_FOUND)

    # Re-format the measures (TODO: DRF-ify this?)
    entry_data = TerseEntrySerializer(entry).data
    entry_data["measures"] = {m["type"]: m["value"] for m in entry_data["measures"]}
    return entry_data


def get_versions_digest_for_project(project) -> dict:
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

    def get(self, request):
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

    def get(self, request, project):
        """
        Return the most recent entry for overall progress for each version of a project.
        """

        if not Project.objects.filter(slug=project).exists():
            return Response(
                f"Project {project} not found", status=status.HTTP_404_NOT_FOUND
            )

        projects = {}

        versions = get_versions_digest_for_project(project)
        if len(versions) > 0:
            projects[project] = versions

        return Response({"progress": projects})


class VersionDigestView(APIView):
    """
    API endpoint that returns the most recent entry for overall progress for a version of a project.
    """

    def get(self, request, project, version):
        """
        Return the most recent entry for overall progress for a version of a project.
        """

        entry = get_latest_entry(project, version, "total")

        return Response(entry)


class CategoryDigestView(APIView):
    """
    API endpoint that returns the most recent entry for a specific cagory and a version of a project.
    """

    def get(self, request, project, version, category):
        """
        Return the most recent entry for a specific cagory and a version of a project.
        """

        entry = get_latest_entry(project, version, category)

        return Response(entry)
