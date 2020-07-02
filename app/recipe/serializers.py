from rest_framework import serializers
from core.models import Tag

class TagSerializer(serializers.ModelSerializer):
    # Serializer for tag object
    class Meta:
        model = Tag
        fields = ('id','name')
        ready_only_fields = ('id',)