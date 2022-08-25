from typing import Any, List
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.db import models
import json

from frog_api.models import Category, Entry, Measure, Project, Version
from frog_api.serializers import (
    ProjectSerializer,
    TerseEntrySerializer,
)


class MissingModelException(APIException):
    status_code = status.HTTP_404_NOT_FOUND


class InvalidAPIKeyException(APIException):
    status_code = status.HTTP_403_FORBIDDEN


class InvalidDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


# Maybe?
class AlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


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
        entry = get_latest_entry(project, version.slug, "default")
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


def write_new_entries(request: Request, project: str, version: str) -> List[Any]:
    found_project = Project.objects.filter(slug=project).first()
    if not found_project:
        raise MissingModelException(f"Project {project} not found")

    found_version = Version.objects.filter(slug=version, project__slug=project).first()
    if not found_version:
        raise MissingModelException(
            f"Version '{version}' not found for project '{project}'"
        )

    print(request.data)
    input = request.data

    if "api_key" not in input:
        raise InvalidAPIKeyException(f"No api_key provided, cannot POST.")
    if input["api_key"] != found_project.auth_key:
        raise InvalidAPIKeyException(
            f"Provided api_key does not match authorization, cannot POST."
        )

    to_save: List[models.Model] = []
    for row in input["data"]:
        timestamp = row["timestamp"]
        git_hash = row["git_hash"]
        for cat in row:
            if cat in ["timestamp", "git_hash"]:
                continue
            if type(row[cat]) is not dict:
                continue

            category = Category.objects.filter(
                slug=cat, version__slug=version, version__project__slug=project
            ).first()
            if not category:
                raise MissingModelException(
                    f"Attempted to write to Category '{cat}' not found in project '{project}', version '{version}'"
                )

            entry = Entry(category=category, timestamp=timestamp, git_hash=git_hash)
            print(entry)
            to_save.append(entry)

            for measure_type in row[cat]:
                value = row[cat][measure_type]
                if type(value) != int:
                    raise InvalidDataException(f"{cat}:{measure_type} must be an int")
                to_save.append(Measure(entry=entry, type=measure_type, value=value))

    for s in to_save:
        s.save()

    return []


class VersionDigestView(APIView):
    """
    API endpoint that returns the most recent entry for overall progress for a version of a project.
    """

    def get(self, request: Request, project: str, version: str) -> Response:
        """
        Return the most recent entry for overall progress for a version of a project.
        """

        entry = get_latest_entry(project, version, "default")

        return Response(entry)

    def post(self, request: Request, project: str, version: str) -> Response:

        result = write_new_entries(request, project, version)

        return Response(result, status=status.HTTP_201_CREATED)


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


def add_new_category(request: Request, project: str, version: str) -> List[Any]:
    found_project = Project.objects.filter(slug=project).first()
    if not found_project:
        raise MissingModelException(f"Project {project} not found")

    found_version = Version.objects.filter(slug=version, project__slug=project).first()
    if not found_version:
        raise MissingModelException(
            f"Version '{version}' not found for project '{project}'"
        )

    print(request.data)
    input = request.data
    categories = input["data"]

    if "api_key" not in input:
        raise InvalidAPIKeyException(f"No api_key provided, cannot POST.")
    if input["api_key"] != found_project.auth_key:
        raise InvalidAPIKeyException(
            f"Provided api_key does not match authorization, cannot POST."
        )

    to_save = []
    for cat in categories:
        if Category.objects.filter(
            slug=cat, version__slug=version, version__project__slug=project
        ).exists():
            raise AlreadyExistsException(
                f"Category {cat} already exists for project '{project}', version '{version}'"
            )
        to_save.append(Category(version=found_version, slug=cat, name=categories[cat]))

    for s in to_save:
        s.save()

    return []


class AddNewCategoryView(APIView):
    """
    API endpoint for adding new categories
    """

    def post(self, request: Request, project: str, version: str) -> Response:

        result = add_new_category(request, project, version)

        return Response(result, status=status.HTTP_201_CREATED)
