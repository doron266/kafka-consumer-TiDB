from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from api.models import User


class UserTestCase(APITestCase):
    """
    Test suite for User endpoints (new schema):
    username, email, password, auth_token, created_at
    """

    def setUp(self):
        self.client = APIClient()
        self.data = {
            "username": "JohnDoe",
            "email": "john@example.com",
            "password": "secret123",
            "auth_token": None,
        }

    def create_test_user(self, username="JohnDoe", email="john@example.com", password="secret123", auth_token=None):
        """
        Create dummy user for testing
        """
        data = {
            "username": username,
            "email": email,
            "password": password,
            "auth_token": auth_token,
        }
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    # ----------------- POST -----------------
    # Test /users/add endpoint

    def test_create_user(self):
        """
        Test API: Create new user with correct data.
        """
        response = self.client.post("/api/users/add", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get().username, "JohnDoe")

    def test_create_user_without_username(self):
        """
        Test API: Create new user when username is not in data.
        """
        data = self.data.copy()
        data.pop("username")
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_when_username_equals_blank(self):
        """
        Test API: Create new user when username is blank.
        """
        data = self.data.copy()
        data["username"] = ""
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_email(self):
        """
        Test API: Create new user when email is not in data.
        """
        data = self.data.copy()
        data.pop("email")
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_when_email_equals_blank(self):
        """
        Test API: Create new user when email is blank.
        """
        data = self.data.copy()
        data["email"] = ""
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password(self):
        """
        Test API: Create new user when password is not in data.
        """
        data = self.data.copy()
        data.pop("password")
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_when_password_equals_blank(self):
        """
        Test API: Create new user when password is blank.
        """
        data = self.data.copy()
        data["password"] = ""
        response = self.client.post("/api/users/add", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_same_email_again(self):
        """
        Test API: Create user twice with same email. Email should be unique.
        """
        response = self.client.post("/api/users/add", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

        response = self.client.post("/api/users/add", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    # ----------------- GET -----------------
    # Test /users endpoint

    def test_get_all_users_when_no_users(self):
        """
        Test API: Return all users when no users.
        """
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data, [])

    def test_get_all_users_when_one_user_exists(self):
        """
        Test API: Return all users when one user exists.
        """
        self.create_test_user()
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data[0]["username"], "JohnDoe")
        self.assertEqual(response.data[0]["email"], "john@example.com")

    def test_get_all_users_when_multiple_users_exist(self):
        """
        Test API: Return all users when multiple users exist.
        """
        self.create_test_user("JohnDoe", "john@example.com", "secret123")
        self.create_test_user("JaneDoe", "jane@example.com", "secret123")
        self.create_test_user("JamesDoe", "james@example.com", "secret123")

        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 4)

        # Order is not guaranteed unless you order_by in the view, so just check presence
        emails = {u["email"] for u in response.data}
        self.assertEqual(emails, {"john@example.com", "jane@example.com", "james@example.com"})

    def test_get_user_without_email_parameter(self):
        """
        Test API: Return error when email parameter is empty.
        """
        response = self.client.get("/api/users?email=")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_when_no_users(self):
        """
        Test API: Return 404 when requesting user by email but none exist.
        """
        response = self.client.get("/api/users?email=wrongemail@example.com")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_when_one_user_exists(self):
        """
        Test API: Return user by email when one user exists.
        """
        self.create_test_user()
        response = self.client.get("/api/users?email=john@example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "john@example.com")
        self.assertEqual(response.data["username"], "JohnDoe")

    def test_get_user_when_multiple_users_exist(self):
        """
        Test API: Return specific user by email when multiple users exist.
        """
        self.create_test_user("JohnDoe", "john@example.com", "secret123")
        self.create_test_user("JaneDoe", "jane@example.com", "secret123")

        response = self.client.get("/api/users?email=jane@example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "jane@example.com")
        self.assertEqual(response.data["username"], "JaneDoe")

    # ----------------- PUT -----------------
    # Test /users/update endpoint

    def test_update_user_without_email_parameter(self):
        response = self.client.put("/api/users/update", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_empty_email_parameter(self):
        response = self.client.put("/api/users/update?email=", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_when_no_users(self):
        response = self.client.put("/api/users/update?email=john@example.com", {"username": "NewName"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_when_one_user(self):
        self.create_test_user()
        response = self.client.put(
            "/api/users/update?email=john@example.com",
            {"username": "JohnUpdated", "auth_token": "t1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], "john@example.com")
        self.assertEqual(response.data["data"]["username"], "JohnUpdated")
        self.assertEqual(response.data["data"]["auth_token"], "t1")

    def test_update_user_when_wrong_email_used(self):
        self.create_test_user()
        response = self.client.put(
            "/api/users/update?email=wrong@example.com",
            {"username": "Nope"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------- DELETE -----------------
    # Test /users/delete endpoint

    def test_delete_user_without_email_parameter(self):
        response = self.client.delete("/api/users/delete")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user_when_no_users(self):
        response = self.client.delete("/api/users/delete?email=john@example.com")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_when_one_user(self):
        self.create_test_user()
        response = self.client.delete("/api/users/delete?email=john@example.com")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)

    def test_delete_user_when_multiple_users_exist(self):
        self.create_test_user("JohnDoe", "john@example.com", "secret123")
        self.create_test_user("JaneDoe", "jane@example.com", "secret123")

        response = self.client.delete("/api/users/delete?email=john@example.com")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(),21)

        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["email"], "jane@example.com")


class DocsTestCase(APITestCase):
    """
    Test suite for api documentation
    """

    def test_docs_return_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_docs_title(self):
        response = self.client.get("/")
        self.assertContains(response, "<title>Django REST API</title>")
