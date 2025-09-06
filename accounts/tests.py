from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token

class UserCreationsTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = "/accounts/register/"
        self.data ={
            "username": "Giorgio",
            "password": "Password123",
            "password2": "Password123"
            }

    def test_user_token_password_created(self):
        # Url
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Username
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, "Giorgio")
        #Token
        token = Token.objects.get(user=user)
        self.assertIsNotNone(token)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["token"], token.key)
        # Password
        self.assertNotEqual(user.password, "Password123")
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password("Password123"))