from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the user API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating the user with valid payload is successful"""
        payload = {
                    'email': 'testuser1@gmail.com',
                    'password': 'test123',
                    'name': 'Test User1'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test user already exists"""
        payload = {
                    'email': 'testuser1@gmail.com',
                    'password': 'test123',
                    'name': 'Test User1'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password too short"""
        payload = {
                    'email': 'testuser1@gmail.com',
                    'password': '123',
                    'name': 'Test User1'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
                                                      email=payload['email']
                                                      ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test create token for user"""
        payload = {'email': 'testuser1@gmail.com', 'password': 'password123'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_not_created_with_invalid_credentials(self):
        """Test the token is not created with invalid credentials"""
        create_user(email='testuser@gmail.com', password='password123')
        payload = {'email': 'testuser@gmail.com', 'password': 'password'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_a_user(self):
        """Test the token is not created without a user"""
        payload = {'email': 'without@gmail.com', 'password': 'password'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_password(self):
        """Test the token is not created if the password is not provided"""
        create_user(email='testuser@gmail.com', password='password123')
        payload = {'email': 'testuser@gmail.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
