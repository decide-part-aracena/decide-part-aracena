from django.urls import reverse
from .models import Census
from base.tests import BaseTestCase

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



