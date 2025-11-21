from rest_framework import generics, permissions
from .models import Item
from .serializers import ItemSerializer

from django.contrib.auth import get_user_model

##### User Views #####

## Temp public for testing
class ItemListCreateView(generics.ListCreateAPIView):
    """Public can list items, authenticated users can create items"""
    serializer_class = ItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Public GET returns all items (or adjust if desired)
        return Item.objects.all()

    def perform_create(self, serializer):
        first_user = User.objects.order_by('id').first()
        serializer.save(user=first_user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User can modify their inventory items"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Prevent users from accessing or editing others' items
        return Item.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure user cannot change ownership
        serializer.save(user=self.request.user)

##### AI Server Views #####
