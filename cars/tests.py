from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Car


class CompareCarsViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="testpass123",
        )

        self.car_1 = Car.objects.create(
            owner=self.owner,
            make="Mazda",
            model="CX-5",
            year=2019,
            price=85000000,
            mileage_km=45000,
            city="Bogota",
            description="SUV familiar",
        )
        self.car_2 = Car.objects.create(
            owner=self.owner,
            make="Toyota",
            model="Corolla Cross",
            year=2021,
            price=98000000,
            mileage_km=25000,
            city="Medellin",
            description="Camioneta compacta",
        )
        self.car_3 = Car.objects.create(
            owner=self.owner,
            make="Renault",
            model="Duster",
            year=2018,
            price=62000000,
            mileage_km=70000,
            city="Cali",
            description="Uso diario",
        )
        self.car_4 = Car.objects.create(
            owner=self.owner,
            make="Kia",
            model="Sportage",
            year=2020,
            price=93000000,
            mileage_km=30000,
            city="Barranquilla",
            description="Buena para viajes",
        )

    def test_compare_view_renders_selected_cars(self):
        response = self.client.get(
            reverse("cars:compare_cars"),
            {"cars": [self.car_1.id, self.car_2.id]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mazda")
        self.assertContains(response, "CX-5")
        self.assertContains(response, "Toyota")
        self.assertContains(response, "Corolla Cross")
        self.assertContains(response, "Kilometraje")
        self.assertEqual(len(response.context["comparison_rows"]), 9)

    def test_compare_view_requires_at_least_two_active_cars(self):
        self.car_2.is_active = False
        self.car_2.save(update_fields=["is_active"])

        response = self.client.get(
            reverse("cars:compare_cars"),
            {"cars": [self.car_1.id, self.car_2.id]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecciona al menos 2 vehículos activos para compararlos.")
        self.assertEqual(response.context["comparison_rows"], [])

    def test_compare_view_limits_selection_to_three_cars(self):
        response = self.client.get(
            reverse("cars:compare_cars"),
            {"cars": [self.car_1.id, self.car_2.id, self.car_3.id, self.car_4.id]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puedes comparar hasta 3 vehículos al mismo tiempo.")
        self.assertEqual(response.context["comparison_rows"], [])
