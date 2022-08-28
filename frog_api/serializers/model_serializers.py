from rest_framework import serializers

from frog_api.models import Entry, Measure, Project, Version


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        fields = ["slug", "name"]


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    versions = VersionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "slug",
            "name",
            "versions",
            "repository",
            "discord",
            "website",
        ]


class MeasureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measure
        fields = ["type", "value"]


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    measures = serializers.SerializerMethodField()

    def get_measures(self, instance: Entry) -> dict[str, int]:
        return {m.type: m.value for m in instance.measures.all()}

    class Meta:
        model = Entry
        fields = [
            "timestamp",
            "git_hash",
            "measures",
        ]
