from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

    def test_user_can_register(self):
        response = self.client.post(self.register_url, {
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_cannot_register_with_weak_password(self):
        response = self.client.post(self.register_url, {
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'weak'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_login(self):
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@1234'
        )
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_cannot_login_with_wrong_password(self):
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@1234'
        )
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)