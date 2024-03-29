from enum import Enum
from typing import Any, Optional

from django.db import IntegrityError, models, transaction
from django.template.defaultfilters import title
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from frog_api.cache import (
    get_entries_cache,
    invalidate_entries_cache,
    set_entries_cache,
)
from frog_api.exceptions import (
    InvalidDataException,
    EmptyCategoryException,
    NonexistentCategoryException,
    NonexistentProjectException,
    NonexistentVersionException,
)
from frog_api.models import Category, Entry, Measure, Project, Version
from frog_api.serializers.model_serializers import EntrySerializer
from frog_api.serializers.request_serializers import CreateEntriesSerializer
from frog_api.views.common import (
    get_category,
    get_project,
    get_version,
    validate_api_key,
)

EntryT = dict[str, Any]


def get_latest_entry(
    project_slug: str, version_slug: str, category_slug: str
) -> Optional[EntryT]:
    project = get_project(project_slug)
    version = get_version(version_slug, project)
    category = get_category(category_slug, version)

    entry = Entry.objects.filter(category=category).first()

    if entry is None:
        return None

    return EntrySerializer(entry).data


def get_all_entries(
    project_slug: str, version_slug: str, category_slug: str
) -> list[EntryT]:
    data = get_entries_cache(project_slug, version_slug, category_slug)
    if data:
        return data  # type: ignore

    project = get_project(project_slug)
    version = get_version(version_slug, project)
    category = get_category(category_slug, version)

    entries = Entry.objects.filter(category=category).prefetch_related("measures")

    data = EntrySerializer(entries, many=True).data
    set_entries_cache(project_slug, version_slug, category_slug, data)
    return data  # type: ignore


def get_versions_digest_for_project(project: Project) -> dict[Any, Any]:
    versions = {}
    for version in Version.objects.filter(project=project):
        category_entries: dict[str, list[EntryT]] = {}

        for category in Category.objects.filter(version=version):
            entry = get_latest_entry(project.slug, version.slug, category.slug)
            if entry is not None:
                category_entries[category.slug] = [entry]

        if len(category_entries) > 0:
            versions[version.slug] = category_entries

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


def get_progress_shield(
    request: Request, project_slug: str, version_slug: str, category_slug: str
) -> dict[str, Any]:
    latest = get_latest_entry(project_slug, version_slug, category_slug)

    if latest is None:
        raise EmptyCategoryException(project_slug, version_slug, category_slug)

    latest_measures = latest["measures"]

    project = get_project(project_slug)
    version = get_version(version_slug, project)
    category = get_category(category_slug, version)

    params = request.query_params
    if not params:
        raise InvalidDataException("No measure specified")

    if "measure" in params:
        measure = params["measure"]
    else:
        raise InvalidDataException("No measure specified")
    if measure not in latest_measures:
        raise InvalidDataException(f"Measure '{measure}' not found")
    numerator = latest_measures[measure]

    label = params.get(
        "label",
        " ".join(
            [
                version.name,
                category.name,
                title(str(measure)),
            ]
        ),
    )

    if "total" in params:
        total = params["total"]
    elif f"{measure}/total" in latest_measures:
        total = f"{measure}/total"
    else:
        raise InvalidDataException("No total specified")
    if total not in latest_measures:
        raise InvalidDataException(f"Measure '{total}' not found")
    denominator = latest_measures[total]

    fraction = float(numerator) / float(denominator)
    message = f"{fraction:.2%}"

    color = params.get("color", "informational" if fraction < 1.0 else "success")

    return {"schemaVersion": 1, "label": label, "message": message, "color": color}


class Mode(Enum):
    LATEST = "latest"
    ALL = "all"
    SHIELD = "shield"


class VersionDataView(APIView):
    """
    API endpoint that returns data for overall progress for a version of a project.
    """

    @staticmethod
    def create_entries(
        req_data: dict[str, Any], project_slug: str, version_slug: str
    ) -> int:
        request_ser = CreateEntriesSerializer(data=req_data)
        request_ser.is_valid(raise_exception=True)
        data = request_ser.data

        try:
            project = get_project(project_slug)
        except NonexistentProjectException:
            raise InvalidDataException(f"Project '{project_slug}' does not exist")

        validate_api_key(data["api_key"], project)

        try:
            version = get_version(version_slug, project)
        except NonexistentVersionException:
            raise InvalidDataException(f"Version '{version_slug}' does not exist")

        to_save: list[models.Model] = []
        for entry in data["entries"]:
            timestamp = entry["timestamp"]
            git_hash = entry["git_hash"]
            categories = entry["categories"]
            for cat in categories:
                try:
                    category = get_category(cat, version)
                except NonexistentCategoryException:
                    raise InvalidDataException(f"Category '{cat}' does not exist")

                entry = Entry(category=category, timestamp=timestamp, git_hash=git_hash)

                to_save.append(entry)

                for measure_type in categories[cat]:
                    value = categories[cat][measure_type]
                    if type(value) != int:
                        raise InvalidDataException(
                            f"{cat}:{measure_type} must be an integer, not {type(value): {value}}"
                        )
                    to_save.append(Measure(entry=entry, type=measure_type, value=value))

        try:
            with transaction.atomic():
                for s in to_save:
                    s.save()
        except IntegrityError as e:
            raise InvalidDataException(f"Integrity error: {e}")

        invalidate_entries_cache(project_slug, version_slug, data)

        return len(to_save)

    def get(self, request: Request, project_slug: str, version_slug: str) -> Response:
        """
        Return the most recent entry for overall progress for a version of a project.
        """

        mode_str = self.request.query_params.get("mode", Mode.LATEST.value)

        try:
            mode: Mode = Mode(mode_str)
        except ValueError:
            raise InvalidDataException(f"Invalid mode specified: {mode_str}")

        project = get_project(project_slug)
        version = get_version(version_slug, project)

        categories_data: dict[str, list[EntryT]]

        match mode:
            case Mode.LATEST:
                categories_data = {}
                for category in Category.objects.filter(version=version):
                    entry = get_latest_entry(project_slug, version_slug, category.slug)
                    if entry is not None:
                        categories_data[category.slug] = [entry]
                response_json = {project_slug: {version_slug: categories_data}}
                return Response(response_json)
            case Mode.ALL:
                categories_data = {}
                for category in Category.objects.filter(version=version):
                    entries = get_all_entries(project_slug, version_slug, category.slug)
                    categories_data[category.slug] = entries
                response_json = {project_slug: {version_slug: categories_data}}
                return Response(response_json)
            case Mode.SHIELD:
                raise InvalidDataException(
                    "Category must be specified for shield output"
                )

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

        mode_str = self.request.query_params.get("mode", Mode.LATEST.value)

        try:
            mode: Mode = Mode(mode_str)
        except ValueError:
            raise InvalidDataException(f"Invalid mode specified: {mode_str}")

        match mode:
            case Mode.LATEST:
                entry = get_latest_entry(project_slug, version_slug, category_slug)
                entries = [entry] if entry is not None else []
                response_json = {project_slug: {version_slug: {category_slug: entries}}}
                return Response(response_json)
            case Mode.ALL:
                entries = get_all_entries(project_slug, version_slug, category_slug)
                response_json = {project_slug: {version_slug: {category_slug: entries}}}
                return Response(response_json)
            case Mode.SHIELD:
                return Response(
                    get_progress_shield(
                        self.request, project_slug, version_slug, category_slug
                    )
                )
