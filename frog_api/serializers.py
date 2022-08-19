from rest_framework import serializers

from frog_api.models import Project, Version


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ["slug", "name"]


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        fields = ["project", "slug", "name"]


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        fields = [
            "version",
            "timestamp",
            "git_hash",
            "total_functions",
            "decompiled_functions",
            "matching_functions",
            "total_bytes",
            "decompiled_bytes",
            "matching_bytes",
            "other_data",
        ]
