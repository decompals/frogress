from typing import Any

from django.db import models
from frog_api.exceptions import (
    InvalidDataException,
    NoEntriesException,
)
from frog_api.models import Entry, Measure, Project, Version
from frog_api.serializers.model_serializers import EntrySerializer
from frog_api.serializers.request_serializers import CreateEntriesSerializer
from frog_api.views.common import (
    get_category,
    get_project,
    get_version,
    validate_api_key,
)
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

DEFAULT_CATEGORY_SLUG = "default"
DEFAULT_CATEGORY_NAME = "Default"


def get_latest_entry(
    project_slug: str, version_slug: str, category_slug: str
) -> dict[str, Any]:
    project = get_project(project_slug)
    version = get_version(version_slug, project)
    category = get_category(category_slug, version)

    entry = Entry.objects.filter(category=category).first()

    if entry is None:
        raise NoEntriesException(project_slug, version_slug, category_slug)

    return EntrySerializer(entry).data


def get_versions_digest_for_project(project: Project) -> dict[Any, Any]:
    versions = {}
    for version in Version.objects.filter(project=project):
        category_slug = DEFAULT_CATEGORY_SLUG
        entry = get_latest_entry(project.slug, version.slug, category_slug)
        if entry is not None:
            versions[version.slug] = {"default": [entry]}
    return versions


class RootDataView(APIView):
    """
    API endpoint that returns the most recent entry for overall progress of each version of each project.
    """

    def get(self, request: Request) -> Response:
        """
        Return the most recent entry for overall progress of each version of each project.
        """

        projects = {}
        for project in Project.objects.all():
            projects[project.slug] = get_versions_digest_for_project(project)

        return Response(projects)


class ProjectDataView(APIView):
    """
    API endpoint that returns the most recent entry for each version of a project.
    """

    def get(self, request: Request, project_slug: str) -> Response:
        """
        Return the most recent entry for overall progress for each version of a project.
        """

        project = get_project(project_slug)
        versions = get_versions_digest_for_project(project)

        return Response({project_slug: versions})


class VersionDataView(APIView):
    """
    API endpoint that returns the most recent entry for overall progress for a version of a project.
    """

    @staticmethod
    def create_entries(
        req_data: dict[str, Any], project_slug: str, version_slug: str
    ) -> int:
        request_ser = CreateEntriesSerializer(data=req_data)
        request_ser.is_valid(raise_exception=True)
        data = request_ser.data

        project = get_project(project_slug)

        validate_api_key(data["api_key"], project)

        version = get_version(version_slug, project)

        to_save: list[models.Model] = []
        for entry in data["entries"]:
            timestamp = entry["timestamp"]
            git_hash = entry["git_hash"]
            categories = entry["categories"]
            for cat in categories:
                category = get_category(cat, version)

                entry = Entry(category=category, timestamp=timestamp, git_hash=git_hash)

                to_save.append(entry)

                for measure_type in categories[cat]:
                    value = categories[cat][measure_type]
                    if type(value) != int:
                        raise InvalidDataException(
                            f"{cat}:{measure_type} must be an integer"
                        )
                    to_save.append(Measure(entry=entry, type=measure_type, value=value))

        for s in to_save:
            s.save()

        return len(to_save)

    def get(self, request: Request, project_slug: str, version_slug: str) -> Response:
        """
        Return the most recent entry for overall progress for a version of a project.
        """

        category_slug = DEFAULT_CATEGORY_SLUG

        entry = get_latest_entry(project_slug, version_slug, category_slug)

        response_json = {project_slug: {version_slug: {category_slug: [entry]}}}

        return Response(response_json)

    def post(self, request: Request, project_slug: str, version_slug: str) -> Response:

        result = VersionDataView.create_entries(
            request.data, project_slug, version_slug
        )

        success_data = {
            "result": "success",
            "wrote": result,
        }

        return Response(success_data, status=status.HTTP_201_CREATED)


class CategoryDataView(APIView):
    """
    API endpoint that returns data for a specific category and a version of a project.
    """

    def get(
        self, request: Request, project_slug: str, version_slug: str, category_slug: str
    ) -> Response:
        """
        Return data for a specific category and a version of a project.
        """

        entry = get_latest_entry(project_slug, version_slug, category_slug)

        response_json = {project_slug: {version_slug: {category_slug: [entry]}}}

        return Response(response_json)
