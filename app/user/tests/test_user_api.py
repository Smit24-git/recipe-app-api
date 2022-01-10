from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the users api (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'smit@test.com',
            'password': 'smit1111',
            'name': 'smit'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exits(self):
        """Test creating a user which already exists fails"""
        payload = {'email': "smit@test.com", 'password': 'smit1111', 'name': 'smit'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the paswword must be more than 5 chars"""
        payload = {'email': "smit@test.com", 'password': 'pw', 'name': 'smit'}
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for user"""
        payload = {'email': 'smit@test.com', 'password': 'smit1111'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        payload = {'email': 'smit@test.com', 'password': 'smit1111'}
        create_user(**payload)
        wrong_login_payload = {'email': 'smit@test.com',
                               'password': 'wrongpass'}
        res = self.client.post(TOKEN_URL,wrong_login_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exists"""
        payload = {'email': 'smit@test.com', 'password': 'smit1111'}

        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {'email': 'smit@test.com', 'password': ''}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorised(self):
        """Test that authenication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ required authentication"""

    def setUp(self):
        payload = {
            'email': 'smit@test.com',
            'password': 'smit1111',
            'name': 'smit'
        }

        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    def test_post_me_not_allowed(self):
        """Test that post is not allowed in me url"""

        res = self.client.post(ME_URL,{})

        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test updating the user profile for authenticatioed user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL,payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
