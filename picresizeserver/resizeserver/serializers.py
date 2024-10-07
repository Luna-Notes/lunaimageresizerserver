from rest_framework import serializers


class ResizeImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    width = serializers.IntegerField(required=True, min_value=100)
    height = serializers.IntegerField(required=True, min_value=100)
