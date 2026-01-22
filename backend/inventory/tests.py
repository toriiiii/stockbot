from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import StockBotUser
from inventory.models import SensorIngestionEvent, Item

class IngestionBaseTest(APITestCase):
    """
    Base class that sets up a user and common helpers.
    """

    def setUp(self):
        self.user = StockBotUser.objects.create_user(
            username="testbot",
            password="password",
            botID=123,
        )

        self.camera_url = "/api/inventory/ingestion/camera/"
        self.classification_url = "/api/inventory/ingestion/classification/"
        self.weight_url = "/api/inventory/ingestion/fsr/"


class CameraIngestionTests(IngestionBaseTest):
    def test_camera_creates_event(self):
        response = self.client.post(
            self.camera_url,
            {
                "bot_id": 123,
                "image_id": "img-1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(SensorIngestionEvent.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 0)

    def test_camera_is_idempotent(self):
        self.client.post(
            self.camera_url,
            {"bot_id": 123, "image_id": "img-1"},
            format="json",
        )

        self.client.post(
            self.camera_url,
            {"bot_id": 123, "image_id": "img-1"},
            format="json",
        )

        self.assertEqual(SensorIngestionEvent.objects.count(), 1)


class ClassificationIngestionTests(IngestionBaseTest):
    def test_classification_creates_event(self):
        response = self.client.post(
            self.classification_url,
            {
                "bot_id": 123,
                "image_id": "img-2",
                "classification": "milk",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(SensorIngestionEvent.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 0)

    def test_classification_updates_existing_event(self):
        SensorIngestionEvent.objects.create(
            user=self.user,
            image_id="img-2",
        )

        response = self.client.post(
            self.classification_url,
            {
                "bot_id": 123,
                "image_id": "img-2",
                "classification": "eggs",
            },
            format="json",
        )

        event = SensorIngestionEvent.objects.get()
        self.assertEqual(event.classification, "eggs")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


class WeightIngestionTests(IngestionBaseTest):
    def test_weight_creates_event(self):
        response = self.client.post(
            self.weight_url,
            {
                "bot_id": 123,
                "image_id": "img-3",
                "weight_grams": 500,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(SensorIngestionEvent.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 0)


class ResolutionTests(IngestionBaseTest):
    def test_event_resolves_when_all_data_present(self):
        """
        Classification + weight (order should not matter)
        """
        self.client.post(
            self.classification_url,
            {
                "bot_id": 123,
                "image_id": "img-4",
                "classification": "cheese",
            },
            format="json",
        )

        self.client.post(
            self.weight_url,
            {
                "bot_id": 123,
                "image_id": "img-4",
                "weight_grams": 250,
            },
            format="json",
        )

        self.assertEqual(SensorIngestionEvent.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 1)

        item = Item.objects.get()
        self.assertEqual(item.name, "cheese")
        self.assertEqual(item.initial_grams, 250)
        self.assertEqual(item.current_grams, 250)

    def test_resolution_is_order_independent(self):
        """
        Weight first, then classification
        """
        self.client.post(
            self.weight_url,
            {
                "bot_id": 123,
                "image_id": "img-5",
                "weight_grams": 1000,
            },
            format="json",
        )

        self.client.post(
            self.classification_url,
            {
                "bot_id": 123,
                "image_id": "img-5",
                "classification": "yogurt",
            },
            format="json",
        )

        self.assertEqual(SensorIngestionEvent.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 1)


class ErrorHandlingTests(IngestionBaseTest):
    def test_invalid_bot_id_rejected(self):
        response = self.client.post(
            self.weight_url,
            {
                "bot_id": 999,
                "image_id": "img-6",
                "weight_grams": 100,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields_rejected(self):
        response = self.client.post(
            self.weight_url,
            {
                "bot_id": 123,
                "image_id": "img-7",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
