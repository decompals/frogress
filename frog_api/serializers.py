from rest_framework import serializers

from frog_api.models import Entry, Measure, Project, Version


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        fields = ["slug", "name"]


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    versions = VersionSerializer(many=True)

    class Meta:
        model = Project
        fields = ["slug", "name", "versions"]


class MeasureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measure
        fields = ["type", "value"]


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    measures = MeasureSerializer(many=True)

    class Meta:
        model = Entry
        fields = [
            "timestamp",
            "git_hash",
            "measures",
        ]


class TerseEntrySerializer(serializers.HyperlinkedModelSerializer):
    measures = MeasureSerializer(many=True)

    class Meta:
        model = Entry
        fields = [
            "timestamp",
            "measures",
        ]
