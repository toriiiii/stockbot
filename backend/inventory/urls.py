from django.urls import path
from .views import ItemListCreateView, ItemDetailView
from .views import ClassificationIngestionView, FSRIngestionView
from .views import management_views

urlpatterns = [
    path("items/", ItemListCreateView.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),

    path("ingestion/classification/", ClassificationIngestionView.as_view(), name="ingestion-classification",),
    path("ingestion/fsr/", FSRIngestionView.as_view(), name="ingestion-fsr"),

    path("management/check-expiring-items/", management_views.cron_check_expiring_items),
    path("management/remove-absent-items/", management_views.cron_remove_absent_items),
]
