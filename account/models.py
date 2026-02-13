from django.db import models
from django.contrib.auth.models import User

# Lista de ciudades de Colombia
CIUDADES_COLOMBIA = [
    ("Bogotá", "Bogotá"),
    ("Medellín", "Medellín"),
    ("Cali", "Cali"),
    ("Barranquilla", "Barranquilla"),
    ("Cartagena", "Cartagena"),
    ("Bucaramanga", "Bucaramanga"),
    ("Pereira", "Pereira"),
    ("Santa Marta", "Santa Marta"),
    ("Manizales", "Manizales"),
    ("Cúcuta", "Cúcuta"),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    ciudad = models.CharField(max_length=50, choices=CIUDADES_COLOMBIA, blank=True, null=True)

    def __str__(self):
        return self.user.username
