import os
import shutil
from unittest.mock import patch, MagicMock
from django.test import TestCase
from log_downloader.views import download_via_sftp
from django.conf import settings
from django.test import Client
from django.urls import reverse


class TestSFTP(TestCase):
    def setUp(self):
        super(TestSFTP, self).setUp()

    @patch('paramiko.client.SSHClient', autospec=True)
    def test_sftp(self, mocked_ssh):
        mocked_ssh().connect('localhost').return_value = True
        download_via_sftp(settings.LOGS_PATH, {'host': 'localhost'})
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_PATH, 'localhost', 'foo.txt')))

    @patch('paramiko.client.SSHClient', autospec=True)
    def test_multiple_hosts(self, mocked_ssh):
        mocked_ssh().connect('127.0.0.1').return_value = True
        mocked_ssh().connect('localhost').return_value = True
        c = Client()
        response = c.post(reverse('download_logs'), {'hosts': ['127.0.0.1', 'localhost']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('success'), 'Files downloaded successfully')
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_PATH, '127.0.0.1', 'foo.txt')))
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_PATH, 'localhost', 'foo.txt')))

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_PATH)
