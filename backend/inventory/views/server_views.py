from rest_framework import generics, permissions
from ..serializers import ServerSerializer, ItemSerializer

from rest_framework.response import Response
from rest_framework import status

class ServerView(generics.CreateAPIView):
    serializer_class = ServerSerializer
    permission_classes = [permissions.AllowAny] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        # respond with ItemSerializer as ServerSerializer has custom fields
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)