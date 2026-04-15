from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Car(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cars")

    make = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1950), MaxValueValidator(2100)])
    price = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    mileage_km = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    city = models.CharField(max_length=80, blank=True, default="")
    description = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.make} {self.model} {self.year} - {self.price}"
    
    def get_url(self):
        return reverse('cars:car_detail', args=[str(self.id)])



def car_image_upload_to(instance, filename: str) -> str:
    return f"cars/{instance.car_id}/{filename}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=car_image_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} for Car {self.car_id}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CarViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="view_history")
    car = models.ForeignKey("Car", on_delete=models.CASCADE, related_name="viewed_by")
    first_viewed_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(default=timezone.now)
    times_viewed = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "car")
        ordering = ["-last_viewed_at"]

    def __str__(self):
        return f"{self.user.username} vio {self.car}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "car"], name="unique_user_car_favorite")
        ]

    def __str__(self):
        return f"{self.user_id} ❤️ {self.car_id}"