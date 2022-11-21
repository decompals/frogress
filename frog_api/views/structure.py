from typing import Any

from frog_api.exceptions import AlreadyExistsException
from frog_api.models import Category, Project, Version
from frog_api.serializers.model_serializers import ProjectSerializer
from frog_api.serializers.request_serializers import (
    CreateCategorySerializer,
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
    def get(self, request: Request, format: Any = None) -> Response:
        """
        Get a list of all projects
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


class ProjectStructureView(APIView):
    """
    API endpoint for modifying projects
    """

    def post(self, request: Request, project_slug: str) -> Response:
        """
        Create a new project.
        """
        request_ser = CreateProjectSerializer(data=request.data)
        request_ser.is_valid(raise_exception=True)

        validate_ultimate_api_key(request_ser.data["api_key"])

        if request_ser.is_valid():
            request_ser.project.save()
            return Response(request_ser.project.data, status=status.HTTP_201_CREATED)
        return Response(request_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class VersionStructureView(APIView):
    """
    API endpoint for modifying versions
    """

    def post(self, request: Request, project_slug: str, version_slug: str) -> Response:
        request_ser = CreateVersionSerializer(data=request.data)
        request_ser.is_valid(raise_exception=True)

        project = get_project(project_slug)

        validate_api_key(request_ser.data["api_key"], project)

        if Version.objects.filter(slug=version_slug, project=project).exists():
            raise AlreadyExistsException(
                f"Version {version_slug} already exists in project {project_slug}"
            )

        version = Version(
            project=project,
            slug=version_slug,
            name=request_ser.data["name"],
        )
        version.save()

        # Create the default category
        default_cat = Category(
            version=version,
            slug=DEFAULT_CATEGORY_SLUG,
            name=DEFAULT_CATEGORY_NAME,
        )
        default_cat.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(
        self, request: Request, project_slug: str, version_slug: str
    ) -> Response:
        project = get_project(project_slug)

        validate_api_key(request.data["api_key"], project)

        version = get_version(version_slug, project)

        version.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryStructureView(APIView):
    """
    API endpoint for modifying categories
    """

    @staticmethod
    def create_category(
        req_data: dict[str, Any],
        project_slug: str,
        version_slug: str,
        category_slug: str,
    ) -> int:
        request_ser = CreateCategorySerializer(data=req_data)
        request_ser.is_valid(raise_exception=True)
        data = request_ser.data

        project = get_project(project_slug)

        validate_api_key(request_ser.data["api_key"], project)

        version = get_version(version_slug, project)

        if Category.objects.filter(slug=category_slug, version=version).exists():
            raise AlreadyExistsException(
                f"Category '{category_slug}' already exists for project '{project_slug}', version '{version_slug}'"
            )

        category = Category(version=version, slug=category_slug, name=data["name"])
        category.save()

        return 1

    def post(
        self, request: Request, project_slug: str, version_slug: str, category_slug: str
    ) -> Response:
        result = CategoryStructureView.create_category(
            request.data, project_slug, version_slug, category_slug
        )

        return Response(status=status.HTTP_201_CREATED)

    def delete(
        self, request: Request, project_slug: str, version_slug: str, category_slug: str
    ) -> Response:
        project = get_project(project_slug)

        validate_api_key(request.data["api_key"], project)

        version = get_version(version_slug, project)

        category = Category.objects.get(slug=category_slug, version=version)

        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
