from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Item

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
        )
        read_only_fields = ("user", "created_at")

class ServerSerializer(serializers.Serializer):
    """AI server sends botID, name and weight"""
    botID = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_botID(self, value):
        if not User.objects.filter(botID=value).exists():
            raise serializers.ValidationError("Invalid botID — no matching user found.")
        return value

    def create(self, validated_data):
        botID = validated_data.pop("botID")
        user = User.objects.get(botID=botID)

        return Item.objects.create(
            user=user,
            name=validated_data["name"],
            initial_grams=validated_data["weight"],
            current_grams=validated_data["weight"],
        )
