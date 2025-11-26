from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Item

User = get_user_model()

class ServerEndpointTests(APITestCase):
    def setUp(self):
        # Create a StockBotUser with botID 0
        self.user = User.objects.create_user(
            username="bot_user",
            password="testpass123",
            botID=0
        )
        self.url = reverse("server-add") 

    def test_create_item_success(self):
        """
        Ensure the server endpoint creates an Item successfully.
        """
        payload = {
            "botID": 0,
            "name": "Zucchini",
            "weight": 550.25
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify item is created in database
        item = Item.objects.get(name="Zucchini")
        self.assertEqual(item.user, self.user)
        self.assertEqual(item.initial_grams, 550.25)
        self.assertEqual(item.current_grams, 550.25)

    def test_invalid_botID(self):
        """
        Returns 400 if the botID does not exist.
        """
        payload = {
            "botID": 999,
            "name": "Tomato",
            "weight": 200.0
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("botID", response.data)

    def test_missing_fields(self):
        """
        Returns 400 if required fields are missing.
        """
        payload = {
            "botID": 0
            # name and weight missing
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("weight", response.data)
