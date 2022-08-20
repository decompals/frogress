from typing import Any
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from frog_api.models import Entry, Project
from frog_api.serializers import EntrySerializer, ProjectSerializer


class ProjectView(APIView):
    """
    API endpoint that allows projects to be viewed or edited.
    """

    def get(self, request, format=None):
        """
        Return a list of all projects.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
