"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
from django.urls import *
from django.contrib.auth.models import User

from .models import Printer 
from .forms import BootstrapUserCreationForm
from django.db import connection

# run tests with: python manage.py test

class ViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTest, cls).setUpClass()
            django.setup()

class HomePageTest(TestCase):
    def test_home_redirect_not_logged_in(self):
        """Tests the home page when the user is not logged in.
            It should give a redirect to the login page."""
        response = self.client.get('/')
        self.assertContains(response, '', 1, 302)

class CRUDTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_printer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    ip_address VARCHAR(45) NOT NULL,
                    mac_address VARCHAR(17) NOT NULL,
                    manufacture_date DATE NOT NULL,
                    comments TEXT
                );
            """)

    def setUp(self):
        """Set up test data."""
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')
        self.test_object = Printer.objects.create(
            brand="Test Brand",
            model="Test Model",
            location="Test Location",
            ip_address="192.168.1.1",
            mac_address="00:1A:2B:3C:4D:5E",
            manufacture_date="2025-06-20",
            comments="Test comments"
        )

    def test_create(self):
        """Test creating an object."""
        obj = Printer.objects.create(
            brand="Create Brand",
            model="Create Model",
            location="Create Location",
            ip_address="192.168.1.2",
            mac_address="00:1A:2B:3C:4D:5F",
            manufacture_date="2025-06-21",
            comments="Create comments"
        )
        self.assertEqual(obj.brand, "Create Brand")
        self.assertEqual(obj.model, "Create Model")
        self.assertEqual(obj.location, "Create Location")
        self.assertEqual(obj.ip_address, "192.168.1.2")
        self.assertEqual(obj.mac_address, "00:1A:2B:3C:4D:5F")
        self.assertEqual(obj.manufacture_date, "2025-06-21")
        self.assertEqual(obj.comments, "Create comments")

    def test_read(self):
        """Test reading an object."""
        obj = Printer.objects.get(brand='Test Brand')
        self.assertEqual(obj.brand, 'Test Brand')

    def test_update(self):
        """Test updating an object."""
        self.test_object.brand = 'Update Brand'
        self.test_object.save()
        self.assertEqual(self.test_object.brand, 'Update Brand')

    def test_delete(self):
        """Test deleting an object."""
        self.test_object.delete()
        with self.assertRaises(Printer.DoesNotExist):
            Printer.objects.get(brand='Test Brand')

class UserTests(ViewTest):
    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_printer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    ip_address VARCHAR(45) NOT NULL,
                    mac_address VARCHAR(17) NOT NULL,
                    manufacture_date DATE NOT NULL,
                    comments TEXT
                );
            """)

    def setUp(self):
        """Set up test user using BootstrapUserCreationForm."""
        user_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = BootstrapUserCreationForm(user_data)
        self.assertTrue(form.is_valid())
        self.test_user = form.save()

        admin_data = {
            'username': 'testadminuser',
            'password1': 'testadminpassword123',
            'password2': 'testadminpassword123'
        }
        admin_form = BootstrapUserCreationForm(admin_data)
        self.assertTrue(admin_form.is_valid())
        self.test_adminuser = admin_form.save()
        self.test_adminuser.is_superuser = True
        self.test_adminuser.is_staff = True
        self.test_adminuser.save()

        self.printer = Printer.objects.create(
            brand="Test Brand",
            model="Test Model",
            location="Test Location",
            ip_address="192.168.1.1",
            mac_address="00:1A:2B:3C:4D:5E",
            manufacture_date="2025-06-20",
            comments="Test comments"
        )

    def test_login(self):
        """Test user login."""
        login = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(login)

    def test_admin_login(self):
        """Test admin user login."""
        login = self.client.login(username='testadminuser', password='testadminpassword123')
        self.assertTrue(login)

    def test_logout(self):
        """Test user logout."""
        self.client.login(username='testuser', password='testpassword123')
        self.client.logout()
        response = self.client.get('/login/')
        self.assertNotContains(response, 'testuser')

    def test_regular_user_cannot_delete_printer(self):
        """Test that a regular user cannot delete a printer due to insufficient permissions."""
        self.client.login(username='testuser', password='testpassword123')
        self.client.post(f'/delete_printer/{self.printer.id}/')  # Simulate delete request 
        self.assertTrue(Printer.objects.filter(id=self.printer.id).exists())  # Printer should still exist

    def test_admin_user_can_delete_printer(self):
        """Test that an admin user can delete a printer."""
        self.client.login(username='testadminuser', password='testadminpassword123')
        self.client.post(f'/delete_printer/{self.printer.id}/') # Simulate delete request
        self.assertFalse(Printer.objects.filter(id=self.printer.id).exists())  # Printer should not exist
    
    def test_home_logged_in(self):
        """Tests the home page when the user is logged in.
            It should display the home page."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get('/')
        self.assertContains(response, 'Home - Printer Management', 1, 200)
