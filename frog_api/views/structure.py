from typing import Any

from django.db import models
from frog_api.exceptions import AlreadyExistsException, MissingAPIKeyException
from frog_api.models import Category, Project
from frog_api.serializers import ProjectSerializer
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
        project = get_project(project_slug)
        version = get_version(version_slug, project)

        if "api_key" not in req_data:
            raise MissingAPIKeyException()

        validate_api_key(req_data["api_key"], project)

        categories = req_data["data"]

        to_save: list[models.Model] = []
        for cat in categories:
            if Category.objects.filter(slug=cat, version=version).exists():
                raise AlreadyExistsException(
                    f"Category {cat} already exists for project '{project_slug}', version '{version_slug}'"
                )
            to_save.append(Category(version=version, slug=cat, name=categories[cat]))

        for s in to_save:
            s.save()

        return len(to_save)

    def post(self, request: Request, project: str, version: str) -> Response:

        result = CategoryStructureView.create_categories(request.data, project, version)

        success_data = {
            "result": "success",
            "wrote": result,
        }

        return Response(success_data, status=status.HTTP_201_CREATED)
