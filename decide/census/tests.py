from rest_framework.test import APIClient
from rest_framework.test import APIClient
from base import mods
from django.urls import reverse
from .models import Census
from base.tests import BaseTestCase

from django.contrib.auth.models import User


#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APITestCase
from .models import Census, ExcelFile
from pandas.testing import assert_frame_equal
import pandas as pd
import os.path

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

#Tests Exportación
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
        response = self.client.get('/census/census/census_exported_html', format='html')
        self.assertEqual(response.status_code, 200)
    
    def test_export_pdf(self):
        response = self.client.get('/census/census/census_exported_pdf', format='pdf')
        self.assertEqual(response.status_code, 200)

class CensusTestCaseExportacionSelenium(StaticLiveServerTestCase):
    #Selenium tests de exportación
    def setUp(self):
        self.client = APIClient()
        self.base = BaseTestCase()
        self.base.setUp()

        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        self.client = None
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()          

    def test_testJSON(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("exporta")
        self.driver.find_element(By.ID, "id_password").send_keys("porta1234")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+'/census/census')
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to JSON").click()
        self.assertTrue(
            self.live_server_url+"/census/census/census_exported_json" == self.driver.current_url)

    def test_testHTML(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("exporta")
        self.driver.find_element(By.ID, "id_password").send_keys("porta1234")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+'/census/census')
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to HTML").click()
        self.assertTrue(
            self.live_server_url+"/census/census/census_exported_html" == self.driver.current_url)
        
    def test_testPDF(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("exporta")
        self.driver.find_element(By.ID, "id_password").send_keys("porta1234")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+'/census/census')
        self.driver.find_element(By.LINK_TEXT, "Export to:").click()
        self.driver.find_element(By.LINK_TEXT, "Export to PDF").click()
        self.assertTrue(
        self.live_server_url+"/census/census/census_exported_pdf" == self.driver.current_url)

class ImportTestCase(APITestCase):

    # Básicas de configuración

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

        admin = User(username='admin5')
        admin.set_password('12345')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)

    def tearDown(self):
        self.census = None
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
        self.assertEqual(user['username'], 'voter1')

    # Concretos para importación de excel

    def test_import_positive(self):

        response = self.client.get('/census/import_datadb')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excel.html')

        # POST data
        input_format = 'file'
        filename = os.path.join(
            os.path.dirname(__file__),
            'testImport.xlsx')

        with open(filename, "rb") as f:
            data = {'file': f,}
            response = self.client.post('/census/import_datadb', data)
        self.assertEqual(response.status_code, 200)

    def test_import_negative(self):

        response = self.client.get('/census/import_datadb')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excel.html')

        # Not POST DATA
        input_format = 'file'
        filename = os.path.join(
            os.path.dirname(__file__),
            'testImport.xlsx')

        with open(filename, "rb") as f:
            data = {}
            response = self.client.post('/census/import_datadb', data)
        self.assertContains(response, "¡Cuidado! No has cargado ningún archivo.")
    
    def test_same_voters(self):

        response = self.client.get('/census/import_datadb')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excel.html')

        # Not POST DATA
        input_format = 'file'
        filename = os.path.join(
            os.path.dirname(__file__),
            'testImport.xlsx')

        with open(filename, "rb") as f:
            data = {'file': f,}
            response = self.client.post('/census/import_datadb', data)
        self.assertEqual(response.status_code, 200)


    def test_import_emptyvalues(self):

        response = self.client.get('/census/import_datadb')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excel.html')

        # Not POST DATA
        input_format = 'file'
        filename = os.path.join(
            os.path.dirname(__file__),
            'testImport4.xlsx')

        with open(filename, "rb") as f:
            data = {'file': f,}
            response = self.client.post('/census/import_datadb', data)
        self.assertEqual(response.status_code, 200)

    def test_import_emptykeys(self):

        response = self.client.get('/census/import_datadb')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excel.html')

        # Not POST DATA
        input_format = 'file'
        filename = os.path.join(
            os.path.dirname(__file__),
            'testImport6.xlsx')

        with open(filename, "rb") as f:
            data = {'file': f,}
            response = self.client.post('/census/import_datadb', data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_census_filtered(self):

        response = self.client.get('/census/import_datadb')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excel.html')

        # POST data
        input_format = 'file'
        filename = os.path.join(
            os.path.dirname(__file__),
            'testImport3.xlsx')

        with open(filename, "rb") as f:
            data = {'file': f,}
            response = self.client.post('/census/import_datadb', data)
        self.assertEqual(response.status_code, 200)



    ##TEST UNITARIOS CRUD CENSO

class TestCrud(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_list(self):
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 401)
        self.assertTemplateNotUsed('censo.html')

        self.login(user='noadmin')
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateNotUsed('censo.html')

        self.login()
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('censo.html')


    def test_create_positive(self):
        url = reverse('crear_censo')
        response = self.client.post(url, {
            'voting_id' : 5,
            'voter_id' : 7
        })
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('crear_censo.html')
    

    def test_create_negative(self):
        Census.objects.create(
            voting_id = 1,
            voter_id = 1
        )
        url = reverse('crear_censo')
        response = self.client.post(url, {
            'voting_id' : 1,
            'voter_id' : 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('crear_censo.html')


    def test_show_negative(self):
        url = reverse('censo_details', args=['1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed('censo_details.html')

    def test_show_positive(self):
        censo =  Census.objects.create(
            voting_id = 1,
            voter_id = 1
        )
        response = self.client.get(f'/census/{censo.voting_id}')
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed('censo_details.html')


    def test_update_positive(self):
        censo =  Census.objects.create(
            voting_id = 1,
            voter_id = 1
        )
        response = self.client.post(f'/census/{censo.voting_id}', {
            'voting_id' : 1,
            'voter_id' : 4
        })
        self.assertEqual(response.status_code, 301)
        self.assertTemplateUsed('censo_details.html')


    def test_update_negative(self):
        censo =  Census.objects.create(
            voting_id = 1,
            voter_id = 1
        )
        url = reverse('censo_details', args=[censo.voting_id])
        response = self.client.post(url, {
            'voting_id' : 1,
            'voter_id' : 1
        })
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed('censo_details.html')


    def test_delete_positive(self):
        censo =  Census.objects.create(
            voting_id = 1,
            voter_id = 1
        )
        censo.delete()
        self.assertTrue(Census.objects.count() == 0)


    def test_delete_negative(self):
        Census.objects.create(
            voting_id = 1,
            voter_id = 1
        )
        self.assertTrue(Census.objects.count() != 0)

##TEST UNITARIOS filtros y ordenacion

class TestSortedVoting(BaseTestCase):

    def setUp(self):
        super().setUp()
    
    def test_list_positive(self):
        self.login()
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('censo.html')

        response2 = self.client.get('/census/sortedByVoting/')
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed('sorting_by_voting.html')

    
    def test_list_negative(self):
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed('censo.html')

        response2 = self.client.get('/census/sortedByVoting/')
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed('sorting_by_voting.html')

class TestPaginacionCensus(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_paginator_positive(self):
        self.login()
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('censo.html')

        response2 = self.client.get('/census/?page=2/')
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed('censo.html')

    def test_paginator_negative(self):

        response2 = self.client.get('/census/?page=2/')
        self.assertEqual(response2.status_code, 401)
        self.assertTemplateUsed('censo.html')

class TestSortedVoter(BaseTestCase):

    def setUp(self):
        super().setUp()
    
    def test_list_positive(self):
        self.login()
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('censo.html')

        response2 = self.client.get('/census/sortedByVoter/')
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed('sorting_by_voter.html')
    
    def test_list_negative(self):
        response = self.client.get('/census/')
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed('censo.html')

        response2 = self.client.get('/census/sortedByVoter/')
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed('sorting_by_voter.html')

