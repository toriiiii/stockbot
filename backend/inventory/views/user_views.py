from rest_framework import generics, permissions
from ..models import Item
from ..serializers import ItemSerializer
from django.contrib.auth import get_user_model

### ALL ENDPOINTS ARE PUBLIC DURING DEVELOPMENT

User = get_user_model()
class ItemListCreateView(generics.ListCreateAPIView):
    """Public GET + POST for dev/testing"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        #TO DO: Limit objects to authorized user
        return Item.objects.all()

    def perform_create(self, serializer):
        #TO DO: Get user by auth
        first_user = User.objects.order_by('id').first()
        serializer.save(user=first_user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Public GET, PUT, PATCH, DELETE for dev/testing"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        #TO DO: Limit objects to authorized user
        return Item.objects.all()

    def perform_update(self, serializer):
        #TO DO: Get user by auth
        first_user = User.objects.order_by('id').first()
        serializer.save(user=first_user)
