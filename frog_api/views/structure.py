from typing import Any

from django.db import models
from frog_api.exceptions import AlreadyExistsException
from frog_api.models import Category, Project, Version
from frog_api.serializers.model_serializers import ProjectSerializer
from frog_api.serializers.request_serializers import (
    CreateCategoriesSerializer,
    CreateProjectSerializer,
    CreateVersionSerializer,
)
from frog_api.views.common import (
    get_project,
    get_version,
    validate_api_key,
    validate_ultimate_api_key,
)
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from frog_api.views.data import DEFAULT_CATEGORY_NAME, DEFAULT_CATEGORY_SLUG


class RootStructureView(APIView):
    """
    API endpoint that allows the structure of the database to be viewed or edited.
    """

    def get(self, request: Request) -> Response:
        """
        Return a digest of the database structure.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """
        Create a new project.
        """
        request_ser = CreateProjectSerializer(data=request.data)

        validate_ultimate_api_key(request_ser.data["api_key"])

        if request_ser.is_valid():
            request_ser.project.save()
            return Response(request_ser.project.data, status=status.HTTP_201_CREATED)
        return Response(request_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectStructureView(APIView):
    """
    API endpoint for adding a new version
    """

    def post(self, request: Request, project_slug: str) -> Response:
        request_ser = CreateVersionSerializer(data=request.data)

        project = get_project(project_slug)

        validate_api_key(request_ser.data["api_key"], project)

        if request_ser.is_valid():
            if Version.objects.filter(
                slug=request_ser.data["version"]["slug"], project=project
            ).exists():
                raise AlreadyExistsException(
                    f"Version with slug {request_ser.data['version']['slug']} already exists"
                )

            version = Version(
                project=project,
                slug=request_ser.data["version"]["slug"],
                name=request_ser.data["version"]["name"],
            )
            version.save()

            # Create the default category
            default_cat = Category(
                version=version,
                slug=DEFAULT_CATEGORY_SLUG,
                name=DEFAULT_CATEGORY_NAME,
            )
            default_cat.save()
            return Response(request_ser.version.data, status=status.HTTP_201_CREATED)
        return Response(request_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class VersionStructureView(APIView):
    """
    API endpoint for adding new categories
    """

    @staticmethod
    def create_categories(
        req_data: dict[str, Any], project_slug: str, version_slug: str
    ) -> int:
        request_ser = CreateCategoriesSerializer(data=req_data)
        request_ser.is_valid(raise_exception=True)
        data = request_ser.data

        project = get_project(project_slug)

        validate_api_key(request_ser.data["api_key"], project)

        version = get_version(version_slug, project)

        categories: dict[str, str] = data["categories"]

        to_save: list[models.Model] = []
        for cat, name in categories.items():
            if Category.objects.filter(slug=cat, version=version).exists():
                raise AlreadyExistsException(
                    f"Category '{cat}' already exists for project '{project_slug}', version '{version_slug}'"
                )
            to_save.append(Category(version=version, slug=cat, name=name))

        for s in to_save:
            s.save()

        return len(to_save)

    def post(self, request: Request, project_slug: str, version_slug: str) -> Response:
        result = VersionStructureView.create_categories(
            request.data, project_slug, version_slug
        )

        success_data = {
            "result": "success",
            "wrote": result,
        }

        return Response(success_data, status=status.HTTP_201_CREATED)
