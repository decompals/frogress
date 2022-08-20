from rest_framework import serializers

from frog_api.models import Entry, Project, Version


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
        model = Entry
        fields = [
            "timestamp",
            "git_hash",
            "total_chunks",
            "decompiled_chunks",
            "matching_chunks",
            "total_bytes",
            "decompiled_bytes",
            "matching_bytes",
        ]
