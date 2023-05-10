# from django.test import TestCase

import unittest
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.test import RequestFactory
from . import views

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from .models import FriendRequest, User, Friendship





class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_context(self):
        user_id = 1
        context = views.get_context(user_id)
        self.assertIsInstance(context, dict)
        self.assertIn('user', context)
        self.assertIn('users', context)
        self.assertIn('friends', context)
        self.assertIn('requests_to_user', context)
        self.assertIn('requests_from_user', context)

    def test_welcome_page(self):
        request = self.factory.get('/')
        response = views.welcome_page(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, render)

    def test_log_in_user(self):
        # Test POST request
        request = self.factory.post('/', {'username': 'testuser'})
        response = views.log_in_user(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, render)

        # Test GET request
        request = self.factory.get('/')
        response = views.log_in_user(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, render)

    # Add more tests for other functions...

    def test_page_not_found(self):
        request = self.factory.get('/')
        response = views.page_not_found(request, None)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_server_error(self):
        request = self.factory.get('/')
        response = views.server_error(request)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response, HttpResponseNotFound)


if __name__ == '__main__':
    unittest.main()

