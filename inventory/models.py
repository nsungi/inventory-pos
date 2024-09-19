from django.db import models
from django.utils import timezone    


class Stock(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # Set default to current time

    def __str__(self):
        return self.name