from rest_framework.response import Response
from rest_framework.views import APIView

from frog_api.models import Project
from frog_api.serializers import ProjectSerializer


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
