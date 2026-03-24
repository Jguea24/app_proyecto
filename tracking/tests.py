from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Tracking


class TrackingOfflineTests(APITestCase):
    def setUp(self):
        self.driver = User.objects.create_user(
            email="driver_tracking@test.com",
            password="Driver1234!",
            role=User.Role.DRIVER,
        )
        self.client.force_authenticate(user=self.driver)

    def test_driver_create_tracking_offline_idempotent(self):
        payload = {
            "latitude": "-2.170998",
            "longitude": "-79.922359",
            "offline_id": "trk-000001",
            "device_recorded_at": (timezone.now() - timezone.timedelta(minutes=1)).isoformat(),
        }

        first = self.client.post("/api/tracking/", payload, format="json")
        second = self.client.post("/api/tracking/", payload, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(Tracking.objects.count(), 1)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertTrue(first.data["synced_from_offline"])

    def test_synced_from_offline_requires_offline_id(self):
        payload = {
            "latitude": "-2.170998",
            "longitude": "-79.922359",
            "synced_from_offline": True,
        }

        response = self.client.post("/api/tracking/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
