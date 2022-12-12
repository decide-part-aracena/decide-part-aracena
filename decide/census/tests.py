import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from base import mods
from base.tests import BaseTestCase

#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

    def test_export_csv(self):
        response = self.client.get('/census/census/census_exported_csv', format='json')
        self.assertEqual(response.status_code, 200)

    def test_export_xls(self):
        response = self.client.get('/census/census/census_exported_xls', format='json')
        self.assertEqual(response.status_code, 200)

    def test_export_yaml(self):
        response = self.client.get('/census/census/census_exported_yaml', format='json')
        self.assertEqual(response.status_code, 200)

    def test_export_json(self):
        response = self.client.get('/census/census/census_exported_json', format='json')
        self.assertEqual(response.status_code, 200)

    def test_export_ods(self):
        response = self.client.get('/census/census/census_exported_ods', format='json')
        self.assertEqual(response.status_code, 200)

    def test_export_html(self):
        response = self.client.get('/census/census/census_exported_html', format='json')
        self.assertEqual(response.status_code, 200)

class CensusTestCaseSelenium(StaticLiveServerTestCase):
    #Selenium tests de exportación
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
  
    def test_testCSV(self):
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to CSV").click()
    
    def test_testXLS(self):
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to XLS").click()

    def test_testODS(self):
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to ODS").click()

    def test_testYAML(self):
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to YAML").click()

    def test_testJSON(self):
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to JSON").click()

    def test_testHTML(self):
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to HTML").click()