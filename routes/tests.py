from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Route


class RoutePermissionsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@test.com", password="Admin1234!", role=User.Role.ADMIN)
        self.driver = User.objects.create_user(email="driver@test.com", password="Driver1234!", role=User.Role.DRIVER)
        self.other_driver = User.objects.create_user(
            email="other@test.com",
            password="Other1234!",
            role=User.Role.DRIVER,
        )

    def test_driver_cannot_create_route(self):
        self.client.force_authenticate(user=self.driver)
        payload = {
            "name": "Ruta no autorizada",
            "date": str(timezone.localdate()),
            "status": "pending",
            "driver": str(self.driver.id),
            "delivery_points": [
                {"address": "A", "latitude": "-2.170998", "longitude": "-79.922359", "order": 1, "status": "pending"},
                {"address": "B", "latitude": "-2.171100", "longitude": "-79.920000", "order": 2, "status": "pending"},
            ],
        }

        response = self.client.post("/api/routes/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_driver_can_start_own_route(self):
        route = Route.objects.create(
            name="Ruta propia",
            date=timezone.localdate(),
            status=Route.Status.PENDING,
            driver=self.driver,
        )
        self.client.force_authenticate(user=self.driver)

        response = self.client.post(f"/api/routes/{route.id}/start/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        route.refresh_from_db()
        self.assertEqual(route.status, Route.Status.IN_PROGRESS)

    def test_driver_cannot_start_foreign_route(self):
        route = Route.objects.create(
            name="Ruta ajena",
            date=timezone.localdate(),
            status=Route.Status.PENDING,
            driver=self.other_driver,
        )
        self.client.force_authenticate(user=self.driver)

        response = self.client.post(f"/api/routes/{route.id}/start/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
