from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating new user with email successful"""
        email = 'smit@test.com'
        password = 'smit1111'

        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test new user is normalized"""
        email = 'test@LONDONAPPDEV.COM'
        user = get_user_model().objects.create_user(email,'smit1111')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test Creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'smit1111')

    def test_create_new_superuser(self):
        """Test Creating a new superuser"""
        user =get_user_model().objects.create_superuser(
            'smit@test.com',
            'smit1111'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
