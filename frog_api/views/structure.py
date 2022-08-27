from typing import Any

from django.db import models
from frog_api.exceptions import AlreadyExistsException
from frog_api.models import Category, Project
from frog_api.serializers.model_serializers import ProjectSerializer
from frog_api.serializers.request_serializers import CreateCategoriesSerializer
from frog_api.views.common import get_project, get_version, validate_api_key
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ProjectStructureView(APIView):
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


class CategoryStructureView(APIView):
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
                    f"Category {cat} already exists for project '{project_slug}', version '{version_slug}'"
                )
            to_save.append(Category(version=version, slug=cat, name=name))

        for s in to_save:
            s.save()

        return len(to_save)

    def post(self, request: Request, project_slug: str, version_slug: str) -> Response:
        result = CategoryStructureView.create_categories(
            request.data, project_slug, version_slug
        )

        success_data = {
            "result": "success",
            "wrote": result,
        }

        return Response(success_data, status=status.HTTP_201_CREATED)
