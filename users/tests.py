import json
from unittest import TestCase
from django.urls import reverse
from users.models import CustomUser
from rest_framework.test import APIClient
from rest_framework import status


class AdminViewTestCase(TestCase):
    client = APIClient()

    def setUp(self):
        # Authenticate the client with the admin user
        login_data = {"username": "admin", "password": "admin"}
        self.login_url = reverse("login")
        response = self.client.post(self.login_url, login_data, format="json")
        content = json.loads(response.content)

        # Assert that the login was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extract the access token from the login response
        access_token = content["access"]

        # Set the Authorization header with the access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_admin_creates_user(self):
        request = {
            "username": "testuser",
            "password": "testpassword",
            "email": "testuser@chatconnect.com",
        }

        response = self.client.post(reverse("create-user"), request)
        content = json.loads(response.content)

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the user details in the response match the expected values
        self.assertEqual(content["username"], request["username"])
        self.assertEqual(content["email"], request["email"])

    def test_admin_updates_user(self):
        request = {
            "username": "testuser",
            "password": "testpassword",
            "email": "testuser@chatconnect.com",
        }

        response = self.client.post(reverse("create-user"), request)

        content = json.loads(response.content)
        request = {
            "password": "changedpassword",
        }

        response = self.client.put(
            reverse("update-user", args=(content["id"],)), request
        )
        content = json.loads(response.content)

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the user details in the response match the expected values
        self.assertEqual(content["password"], request["password"])

    def tearDown(self) -> None:
        super().tearDown()
        CustomUser.objects.get(username="testuser").delete()


class UserViewTestCase(TestCase):
    client = APIClient()

    def setUp(self):
        # Authenticate the client with the admin user and create a testuser
        login_data = {"username": "admin", "password": "admin"}
        self.login_url = reverse("login")
        response = self.client.post(self.login_url, login_data, format="json")

        content = json.loads(response.content)
        access_token = content["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_user_manages_user(self):
        # admin creates a testuser
        testuser = {
            "username": "testuser2",
            "password": "testpassword",
            "email": "testuser2@chatconnect.com",
        }
        response = self.client.post(reverse("create-user"), testuser)

        response = self.client.post(self.login_url, testuser)
        content = json.loads(response.content)
        access_token = content["access"]
        refresh_token = content["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # testuser creates a user
        testuser = {
            "username": "user",
            "password": "testpassword",
            "email": "user@chatconnect.com",
        }
        response = self.client.post(reverse("create-user"), testuser)

        # Assert that the response has a status code of 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        request = {
            "password": "changedpassword",
        }

        # testuser updates a user
        response = self.client.put(reverse("update-user", args=(1,)), request)

        # Assert that the response has a status code of 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # testuser is logged out
        self.logout_url = reverse("logout")
        response = self.client.post(self.logout_url, {"refresh_token": refresh_token})

    def tearDown(self) -> None:
        super().tearDown()
        CustomUser.objects.get(username="testuser2").delete()


# class to test the login logout functionality
class LoginLogoutTestCase(TestCase):
    client = APIClient()

    def setUp(self):
        pass

    def test_login_logout(self):
        # testuser logs in
        login_data = {"username": "admin", "password": "admin"}
        self.login_url = reverse("login")
        response = self.client.post(self.login_url, login_data, format="json")
        content = json.loads(response.content)

        # Assert that the login was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response has an access token
        self.assertTrue("access" in content)

        # Extract the access token from the login response
        access_token = content["access"]

        # Extract the refresh token from the login response
        refresh_token = content["refresh"]

        # Set the Authorization header with the access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # testuser logs out
        self.logout_url = reverse("logout")
        response = self.client.post(self.logout_url, {"refresh_token": refresh_token})

        # Assert that the logout was successful (status code 204)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
