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

        #df1 = pd.DataFrame({'voting_id'=1, voter_id=1})
        """data = {'voting_id': [1,2,3,4,5],
                'username': ['Marina', 'Juanjo', 'Laura', 'Rubén', 'Nico'],
                'sexo': ['F', 'M','F', 'M','M'],
                'voter_id': [2,3,4,1,5]}
        df = pd.DataFrame(data)
        """

        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

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
        self.assertEqual(user['id'], 11)
        self.assertEqual(user['username'], 'voter1')

    # Concretos para importación de excel

    # ---- Creación de excel

    def generate_excel(self):
        file = open('testImport.xlsx', 'wb')
        obj = ExcelFile.objects.create( file = file )
        return obj
    
    def generate_dataFrame(self):
        data = {'voting_id': [1,2,3,4,5],
                'username': ['Marina', 'Juanjo', 'Laura', 'Rubén', 'Nico'],
                'sexo': ['F', 'M','F', 'M','M'],
                'voter_id': [2,3,4,1,5]}
        df = pd.DataFrame(data)
        return data

    def test_import_ok(self):
        #data = {'voting_id': 2, 'voter_id':1}
        #data = self.generate_excel()
        data = self.generate_dataFrame()
        response = self.client.get('/census/import_datadb')
        response = self.client.post(
            '/census/import_datadb', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_invalid_import(self):
        #data = {}
        data = self.generate_dataFrame()
        data = data.clear
        response = self.client.get('/census/import_datadb')
        response = self.client.post(
            '/census/import_datadb', data, format='json')
        self.assertEqual(response.status_code, 500)

    def test_import_duplicated(self):
        #data = {'voting_id': 2, 'voter_id':1}
        data = self.generate_excel()
        response = self.client.get('/census/import_datadb')
        response = self.client.post(
            '/census/import_datadb', data, format='json')
        self.assertEqual(response.status_code, 500)

