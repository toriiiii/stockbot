from rest_framework import generics, permissions
from .models import Item
from .serializers import ItemSerializer
from django.contrib.auth import get_user_model

### ALL ENDPOINTS ARE PUBLIC DURING DEVELOPMENT

User = get_user_model()
class ItemListCreateView(generics.ListCreateAPIView):
    """Public GET + POST for dev/testing"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Item.objects.all()

    def perform_create(self, serializer):
        # Hardcode item owner to first user in the DB
        first_user = User.objects.order_by('id').first()
        serializer.save(user=first_user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Public GET, PUT, PATCH, DELETE for dev/testing"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Allow access to ALL items (dev mode only)
        return Item.objects.all()

    def perform_update(self, serializer):
        # Hardcode owner so user cannot be changed
        first_user = User.objects.order_by('id').first()
        serializer.save(user=first_user)
