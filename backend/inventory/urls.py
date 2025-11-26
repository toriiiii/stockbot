from django.urls import path
from .views import ItemListCreateView, ItemDetailView, ServerView

urlpatterns = [
    path("items/", ItemListCreateView.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),

    path("server/", ServerView.as_view(), name="server-add"),
]
