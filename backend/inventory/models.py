from django.db import models
from django.contrib.auth.models import User  

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kitchen_items')
    name = models.CharField(max_length=100)
    initial_grams = models.DecimalField(max_digits=10, decimal_places=2) 
    current_grams = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"