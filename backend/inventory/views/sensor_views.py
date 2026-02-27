from rest_framework import generics, permissions, status
from rest_framework.response import Response

from accounts.models import StockBotUser
from inventory.models import SensorIngestionEvent
from ..serializers import CameraIngestionSerializer, ClassificationIngestionSerializer, FSRIngestionSerializer
from inventory.services.ingestion import try_resolve_event

class CameraIngestionView(generics.CreateAPIView):
    serializer_class = CameraIngestionSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        try:
            user = StockBotUser.objects.get(botID=data["bot_id"])
        except StockBotUser.DoesNotExist:
            return Response(
                {"error": "Invalid bot_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        event, _ = SensorIngestionEvent.objects.get_or_create(
            user=user,
            image_id=data["image_id"],
        )

        if "image" in data:
            event.image = data["image"]
            event.save()

        resolved = try_resolve_event(event)

        return Response(
            {
                "status": "accepted",
                "image_id": data["image_id"],
                "resolved": resolved,
            },
            status=status.HTTP_202_ACCEPTED,
        )

class ClassificationIngestionView(generics.CreateAPIView):
    serializer_class = ClassificationIngestionSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        try:
            user = StockBotUser.objects.get(botID=data["bot_id"])
        except StockBotUser.DoesNotExist:
            return Response(
                {"error": "Invalid bot_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        event, _ = SensorIngestionEvent.objects.get_or_create(
            user=user,
            image_id=data["image_id"],
        )

        event.classification = data["classification"]
        event.expires_at = data["expires_at"]
        event.save()

        resolved = try_resolve_event(event)

        return Response(
            {
                "status": "accepted",
                "image_id": data["image_id"],
                "resolved": resolved,
            },
            status=status.HTTP_202_ACCEPTED,
        )

class FSRIngestionView(generics.CreateAPIView):
    serializer_class = FSRIngestionSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        try:
            user = StockBotUser.objects.get(botID=data["bot_id"])
        except StockBotUser.DoesNotExist:
            return Response(
                {"error": "Invalid bot_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event, _ = SensorIngestionEvent.objects.get_or_create(
            user=user,
            image_id=data["image_id"],
        )

        event.weight_grams = data["weight_grams"]
        event.save()

        resolved = try_resolve_event(event)

        return Response(
            {
                "status": "accepted",
                "image_id": data["image_id"],
                "resolved": resolved,
            },
            status=status.HTTP_202_ACCEPTED,
        )