from rest_framework import serializers
from frog_api.models import AUTH_KEY_LEN


class ApiKeySerializer(serializers.CharField):
    required = True
    max_length = AUTH_KEY_LEN


class CreateCategoriesSerializer(serializers.Serializer):  # type:ignore
    api_key = ApiKeySerializer()
    categories = serializers.DictField(
        required=True, allow_empty=False, child=serializers.CharField()
    )
