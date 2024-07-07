from rest_framework import serializers
from .models import RenderTask

class RenderTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenderTask
        fields = '__all__'
