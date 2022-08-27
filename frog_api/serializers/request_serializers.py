from rest_framework import serializers
from frog_api.models import AUTH_KEY_LEN


class ApiKeySerializer(serializers.CharField):
    required = True
    max_length = AUTH_KEY_LEN


# Classes for valdating requests to create new entries
class CreateEntrySerializer(serializers.Serializer):  # type:ignore
    timestamp = serializers.IntegerField()
    git_hash = serializers.CharField(max_length=40)
    categories = serializers.DictField(
        child=serializers.DictField(child=serializers.IntegerField())
    )


class CreateEntriesSerializer(serializers.Serializer):  # type:ignore
    api_key = ApiKeySerializer()
    entries = serializers.ListField(
        child=CreateEntrySerializer(), required=True, allow_empty=False
    )


class CreateCategoriesSerializer(serializers.Serializer):  # type:ignore
    api_key = ApiKeySerializer()
    categories = serializers.DictField(
        required=True, allow_empty=False, child=serializers.CharField()
    )
