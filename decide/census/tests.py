import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from base import mods
from base.tests import BaseTestCase
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
            'testImport5.xlsx')

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

    
        
        