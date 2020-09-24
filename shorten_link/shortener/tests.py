from django.test import TestCase, Client
from parameterized import parameterized
from .models import Link


class DatabaseTestCase(TestCase):
    @parameterized.expand([
        ('wrong_url', 'preferred', None),
        ('https://example.com', 'https://kek.ru', None),
        ('https://example.com', 'my-short-link', 'http://127.0.0.1:8000/my-short-link'),
    ])
    def test_making_preferred_url(self, url, preferred, result):
        preferred_url = Link.objects.create_preferred_link(
            url,
            preferred,
            'localhost'
        )
        self.assertEqual(preferred_url, result)

    @parameterized.expand([
        ('example.com',),
        ('website.com.ru/',),
        ('https://example.com',),
        ('ftp://mywrong.url',),
    ])
    def test_making_short_url(self, url):
        new_url = Link.objects.write_new_link(url, 'localhost')
        self.assertIsNotNone(new_url)

    @parameterized.expand([
        ('wrong_url',),
        ('wrong/url/haha')
    ])
    def test_making_wrong_short_url(self, url):
        new_url = Link.objects.write_new_link(url, 'localhost')
        self.assertIsNone(new_url)


class ClientTestCase(TestCase):

    def test_index(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    @parameterized.expand([
        ('example.com',),
        ('https://example.com',),
        ('http://topwar.ru',),
    ])
    def test_making_short_url(self, url):
        client = Client()
        response = client.get(f'/shorten?url={url}')
        self.assertEqual(response.status_code, 200)
