from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthRegisterTests(APITestCase):
    def test_register_creates_driver_role_by_default(self):
        payload = {
            "email": "nuevo_driver@test.com",
            "first_name": "Nuevo",
            "last_name": "Driver",
            "address": "Quito",
            "birth_date": "2000-01-01",
            "password": "Driver1234!",
            "confirm_password": "Driver1234!",
        }

        response = self.client.post("/api/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["role"], User.Role.DRIVER)


class UserAdminCreationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin_users@test.com",
            password="Admin1234!",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin)

    def test_admin_cannot_create_invalid_role(self):
        payload = {
            "email": "badrole@test.com",
            "first_name": "Bad",
            "last_name": "Role",
            "role": "CLIENT",
            "is_active": True,
            "password": "Admin1234!",
            "confirm_password": "Admin1234!",
        }

        response = self.client.post("/api/users/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
