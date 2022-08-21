from rest_framework import serializers

from frog_api.models import Entry, Project, Version


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        fields = ["slug", "name"]


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    versions = VersionSerializer(many=True)

    class Meta:
        model = Project
        fields = ["slug", "name", "versions"]


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


class TerseEntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entry
        fields = [
            "timestamp",
            "total_bytes",
            "matching_bytes",
        ]
