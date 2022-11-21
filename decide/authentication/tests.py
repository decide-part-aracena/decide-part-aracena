from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from base import mods

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from base.tests import BaseTestCase
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post(
            '/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post(
            '/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(
            user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post(
            '/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(
            user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post(
            '/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(
            user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post(
            '/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post(
            '/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post(
            '/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post(
            '/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post(
            '/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )


class TestRegisterLoginUser(StaticLiveServerTestCase):

    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        u = User(username='seleniumVoter')
        u.set_password('123')
        u.save()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.base.tearDown()
        self.vars = {}
        self.client = None

    def test_register_user(self):
        self.driver.get(self.live_server_url+"/authentication/registeruser/")
        self.driver.set_window_size(1366, 836)
        self.driver.find_element(
            By.ID, "id_username").send_keys("usuarioSeleniumTest")
        self.driver.find_element(By.ID, "id_first_name").send_keys("usuario")
        self.driver.find_element(By.ID, "id_last_name").send_keys("selenium")
        self.driver.find_element(By.ID, "id_email").send_keys(
            "usuarioSelenium@gmail.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("fire1234")
        self.driver.find_element(By.ID, "id_password2").send_keys(
            "fire1234", Keys.ENTER)

        print(self.driver.current_url)
        print(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.assertTrue(
            self.live_server_url+"/authentication/loginuser/?next=/base/" == self.driver.current_url)

    def test_register_user_already_exists(self):
        self.driver.get(self.live_server_url+"/authentication/registeruser/")
        self.driver.set_window_size(1366, 836)
        self.driver.find_element(
            By.ID, "id_username").send_keys("seleniumVoter")
        self.driver.find_element(By.ID, "id_first_name").send_keys("usuario")
        self.driver.find_element(By.ID, "id_last_name").send_keys("selenium")
        self.driver.find_element(By.ID, "id_email").send_keys(
            "usuarioSelenium@gmail.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("fire1234")
        self.driver.find_element(By.ID, "id_password2").send_keys(
            "fire1234", Keys.ENTER)
        self.assertTrue(
            self.live_server_url+"/authentication/registeruser/" == self.driver.current_url)

    def test_login(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/")
        self.driver.set_window_size(1366, 836)
        self.driver.find_element(
            By.ID, "id_username").send_keys("seleniumVoter")
        self.driver.find_element(By.ID, "id_password").send_keys(
            "123", Keys.ENTER)
        self.assertTrue(
            self.live_server_url+"/base/" == self.driver.current_url)

    def test_login_fail(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/")
        self.driver.set_window_size(1366, 836)
        self.driver.find_element(
            By.ID, "id_username").send_keys("seleniumVoter")
        self.driver.find_element(By.ID, "id_password").send_keys(
            "1234", Keys.ENTER)
        self.assertTrue(
            self.live_server_url+"/authentication/loginuser/" == self.driver.current_url)
