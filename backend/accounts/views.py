from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model

from .models import DeviceToken
from .serializers import RegisterSerializer, UserSerializer, DeviceTokenSerializer

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=201)
        return Response(serializer.errors, status=400)


class MeView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)
        
        return Response(UserSerializer(user).data)

class DeviceTokenListCreateView(generics.ListCreateAPIView):
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return tokens belonging to the authenticated user
        return DeviceToken.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        token = request.data.get('token')
        platform = request.data.get('platform', 'android')

        if not token:
            return Response({'error': 'token is required'}, status=400)

        obj, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'platform': platform,
            },
        )

        return Response({
            'status': 'registered' if created else 'updated',
            'platform': platform,
        })