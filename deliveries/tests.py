from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from routes.models import DeliveryPoint, Route
from users.models import User


class DeliveryProofPermissionsTests(APITestCase):
    def setUp(self):
        self.driver = User.objects.create_user(email="driver@test.com", password="Driver1234!", role=User.Role.DRIVER)
        self.other_driver = User.objects.create_user(
            email="other@test.com",
            password="Other1234!",
            role=User.Role.DRIVER,
        )

        self.own_route = Route.objects.create(
            name="Ruta propia",
            date=timezone.localdate(),
            status=Route.Status.PENDING,
            driver=self.driver,
        )
        self.own_point = DeliveryPoint.objects.create(
            route=self.own_route,
            address="Mi punto",
            latitude="-2.170998",
            longitude="-79.922359",
            order=1,
            status=DeliveryPoint.Status.PENDING,
        )

        self.foreign_route = Route.objects.create(
            name="Ruta ajena",
            date=timezone.localdate(),
            status=Route.Status.PENDING,
            driver=self.other_driver,
        )
        self.foreign_point = DeliveryPoint.objects.create(
            route=self.foreign_route,
            address="Punto ajeno",
            latitude="-2.171100",
            longitude="-79.920000",
            order=1,
            status=DeliveryPoint.Status.PENDING,
        )

    def _file(self, name="proof.png"):
        return SimpleUploadedFile(name, b"fake-image-content", content_type="image/png")

    def test_driver_cannot_create_proof_for_foreign_route(self):
        self.client.force_authenticate(user=self.driver)

        response = self.client.post(
            "/api/delivery-proofs/",
            {
                "delivery_point": str(self.foreign_point.id),
                "status": "pending",
                "image": self._file("foreign.png"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_driver_can_create_proof_for_own_route(self):
        self.client.force_authenticate(user=self.driver)

        response = self.client.post(
            "/api/delivery-proofs/",
            {
                "delivery_point": str(self.own_point.id),
                "status": "pending",
                "image": self._file("own.png"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
