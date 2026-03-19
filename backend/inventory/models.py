from django.db import models
from django.conf import settings

# Stores kitchen items with complete data. This data is displayed to the app
class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kitchen_items'
    )
    name = models.CharField(max_length=100)
    initial_grams = models.FloatField()
    current_grams = models.FloatField()
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="item_images/", null=True, blank=True) 

    # Notification flags - prevent repeat notifs
    notified_expiring_soon = models.BooleanField(default=False)  # 7 days
    notified_expiry_day = models.BooleanField(default=False)    # today
    notified_low_stock = models.BooleanField(default=False)    # < 10% of initial weight

    # Tracks whether a logged item has been removed from the fridge
    # Items removed for longer than 5hrs will be considered consumed
    status = models.CharField(
        max_length=20,
        choices=[
            ("in_fridge", "In Fridge"),
            ("removed", "Removed"),
        ],
        default="in_fridge"
    )
    last_removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


# Stores incomplete item data. Accepts asynchronous sensor POST requests until rows are completed.
class SensorIngestionEvent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sensor_ingestion_events"
    )
    image_id = models.CharField(max_length=128)

    # Partial data (nullable)
    classification = models.CharField(max_length=100, null=True, blank=True)
    weight_grams = models.FloatField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    # Resolution
    created_at = models.DateTimeField(auto_now_add=True)

    # (user, image_id) should be unique 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "image_id"],
                name="unique_ingestion_event_per_user_image"
            )
        ]

    def __str__(self):
        return f"{self.user_id}:{self.image_id}"