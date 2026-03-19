from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SensorIngestionEvent, Item
from .services.ingestion import try_resolve_event

User = get_user_model()

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            "id",
            "user",
            "name",
            "initial_grams",
            "current_grams",
            "expires_at",
            "created_at",
            "image",
        )
        read_only_fields = ("user", "created_at")

# AI Server Ingestion
class ClassificationIngestionSerializer(serializers.Serializer):
    bot_id = serializers.IntegerField()
    image_id = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False)
    classification = serializers.CharField(max_length=255)
    expires_at = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], allow_null=True, required=False)

# Force Sensor (FSR) Ingestion
class FSRIngestionSerializer(serializers.Serializer):
    bot_id = serializers.IntegerField()
    image_id = serializers.CharField(max_length=255)
    weight_grams = serializers.FloatField()

