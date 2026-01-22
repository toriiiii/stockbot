from django.urls import path
from .views import ItemListCreateView, ItemDetailView
from .views import CameraIngestionView, ClassificationIngestionView, FSRIngestionView

urlpatterns = [
    path("items/", ItemListCreateView.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),

    path("ingestion/camera/", CameraIngestionView.as_view(), name="ingestion-camera"),
    path("ingestion/classification/", ClassificationIngestionView.as_view(), name="ingestion-classification",),
    path("ingestion/fsr/", FSRIngestionView.as_view(), name="ingestion-fsr"),
]
