from rest_framework import generics, permissions, status
from rest_framework.response import Response

from accounts.models import StockBotUser
from inventory.models import SensorIngestionEvent
from ..serializers import ClassificationIngestionSerializer, FSRIngestionSerializer
from inventory.services.ingestion import try_resolve_event

import logging

logger = logging.getLogger(__name__)

class ClassificationIngestionView(generics.CreateAPIView):
    serializer_class = ClassificationIngestionSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        logger.info(f'Classification data received — bot_id={data["bot_id"]} image_id={data["image_id"]}')

        try:
            user = StockBotUser.objects.get(botID=data["bot_id"])
        except StockBotUser.DoesNotExist:
            logger.error(f'Classification update failed — bot id user not found')
            return Response(
                {"error": "Invalid bot_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        event, _ = SensorIngestionEvent.objects.get_or_create(
            user=user,
            image_id=data["image_id"],
        )

        event.classification = data["classification"]
        event.expires_at = data.get("expires_at")
        if "image" in data:
            event.image = data["image"]
        event.save()

        event.refresh_from_db()
        resolved = try_resolve_event(event)

        logger.info(f'Classification data processed — bot_id={data["bot_id"]} image_id={data["image_id"]}')

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

        logger.info(f'FSR data received — bot_id={data["bot_id"]} image_id={data["image_id"]}')

        try:
            user = StockBotUser.objects.get(botID=data["bot_id"])
        except StockBotUser.DoesNotExist:
            logger.error(f'Camera update failed — bot id user not found')
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

        event.refresh_from_db()
        resolved = try_resolve_event(event)

        logger.info(f'FSR data processed — bot_id={data["bot_id"]} image_id={data["image_id"]}')

        return Response(
            {
                "status": "accepted",
                "image_id": data["image_id"],
                "resolved": resolved,
            },
            status=status.HTTP_202_ACCEPTED,
        )
