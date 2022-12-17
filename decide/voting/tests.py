import random
import itertools
import time
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase



class VotingModelTestCase(BaseTestCase): 
    
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v
    
    def create_question(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()

        return q

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        
        response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')
    
    def test_create_onequestion_voting(self):
        q1 = Question(desc='question1')
        q1.save()
        for i in range(5):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q1)
        self.assertEqual(v.question.all().count(), 1)


    def test_create_multiquestion_voting(self):
        q1 = Question(desc='question1')
        q1.save()
        for i in range(5):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()
        q2 = Question(desc='question2')
        q2.save()
        for i in range(5):
            opt = QuestionOption(question=q2, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)
        a = v.question.all().count() == 2
        self.assertTrue(a)

    def test_deleting_question_from_voting_multiquestion(self):
        q1 = Question(desc="test question1")
        q1.save()
        q2 = Question(desc="test question2")
        q2.save()
        QuestionOption(question=q1,option="option1")
        QuestionOption(question=q1,option="option2")
        QuestionOption(question=q2,option="option3")
        QuestionOption(question=q2,option="option4")
        v=Voting(name="Votacion")
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)
        self.assertEquals(v.question.all().count(), 2)
        v.question.remove(q2)
        self.assertEquals(v.question.all().count(),1)

    def test_adding_question_to_voting_multiquestion(self):
        q1 = Question(desc="test question1")
        q1.save()
        q2 = Question(desc="test question2")
        q2.save()
        QuestionOption(question=q1,option="option1")
        QuestionOption(question=q1,option="option2")
        QuestionOption(question=q2,option="option3")
        QuestionOption(question=q2,option="option4")
        v=Voting(name="Votacion")
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        v.auths.add(a)
        v.question.add(q1)
        self.assertEquals(v.question.all().count(), 1)
        v.question.add(q2)
        self.assertEquals(v.question.all().count(),2)

# Test de frontend Auth 
class AuthModelTestCase(BaseTestCase): 

    def setUp(self):
        super().setUp()

    def test_list(self):

        response = self.client.get('/auth_list/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed('auth_list.html')

        self.login()
        response = self.client.get('/auth_list/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed('auth_list.html')



    def test_create_positive(self):
        url = reverse('create_auth')
        response = self.client.post(url, {
            'name': 'test auth',
            'url': 'http://127.0.0.1:8000/'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('voting_create.html')

    def test_create_negative(self):
        Auth.objects.create(
            name = 'test auth',
            url = 'perro'
        )
        url = reverse('create_auth')
        self.client.post(url, {
            'name' : 'test auth',
            'url' : 'perro'
        })
        self.assertTemplateNotUsed('voting_create.html')

    def test_create_negative2(self):
        Auth.objects.create(
            name = "",
            url = ""
        )
        url = reverse('create_auth')
        response = self.client.post(url, {
            'name' : '',
            'url' : ''
        })
        self.assertTemplateNotUsed('voting_create.html')  

    def test_show_positive(self):
        auth = Auth.objects.create(
            name = 'test auth',
            url = 'http://127.0.0.1:8000/'
        )
        response = self.client.get(f'/auth/{auth.pk}')
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed('auth_details.html')


    def test_show_negative(self):
        url = 'auth/22'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed('voting_details.html')

    def test_update_positive(self):
        auth = Auth.objects.create(
            name = 'test auth',
            url = 'http://127.0.0.1:8000/'
        )
        response = self.client.post(f'/auth/{auth.pk}', {
            'name' :'test auth',
            'url' : 'http://127.0.0.1:8000/'
        })

        self.assertNotEqual(response.status_code, 301)
        self.assertTemplateUsed('auth_details.html')


    def test_update_negative(self):
        auth = Auth.objects.create(
            name = 'test auth',
            url = 'http://127.0.0.1:8000/'
        )
        url = reverse('auth_details', args=[auth.pk])
        response = self.client.post(url, {
            'name' :'test auth',
            'url' : ' sdfsf'
        })
        self.assertTemplateNotUsed('auth_list.html')
        self.assertTemplateUsed('auth_details.html')

    def test_delete_positive(self):
        auth =  Auth.objects.create(
            name = 'test auth',
            url = 'http://127.0.0.1:8000/'
        )
        auth.delete()
        self.assertTrue(Auth.objects.count() == 0)


    def test_delete_negative(self):
        Auth.objects.create(
            name = 'test auth',
            url = 'http://127.0.0.1:8000/'
        )
        self.assertTrue(Auth.objects.count() != 0)


class TestSortVoting(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        u = User(username='seleniumVoter')
        u.set_password('123')
        u.save()
        self.base.login()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.base.tearDown()
        self.vars = {}
        self.client = None
  
    def test_sortByName(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.set_window_size(1386, 752)

        self.driver.find_element(By.LINK_TEXT, "Order by:").click()
        self.driver.find_element(By.LINK_TEXT, "Title").click() 
        self.assertTemplateUsed('sorted_by_param.html')
    
    def test_sortByStartDate(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.set_window_size(1386, 752)
        
        self.driver.find_element(By.LINK_TEXT, "Order by:").click()
        self.driver.find_element(By.LINK_TEXT, "Start date").click() 
        self.assertTemplateUsed('sorted_by_param.html')
     
    def test_sortByEndDate(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.set_window_size(1386, 752)
        
        self.driver.find_element(By.LINK_TEXT, "Order by:").click()
        self.driver.find_element(By.LINK_TEXT, "End date").click() 
        self.assertTemplateUsed('sorted_by_param.html')
        
class TestCrudNegative(BaseTestCase):

    def setUp(self):
        self.logout()
        super().setUp()

    def test_list_name(self):
        self.logout()
        response = self.client.get('/voting/name/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed('voting_details.html')
    
    def test_list_startDate(self):
        self.logout()
        response = self.client.get('/voting/startDate/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed('voting_details.html')
    
    def test_list_endDate(self):
        self.logout()
        response = self.client.get('/voting/endDate/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed('voting_details.html')
    

# Test de frontend voting 
class TestVotingSelenium(StaticLiveServerTestCase):
    
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        u = User(username='seleniumVoter')
        u.set_password('123')
        u.save()
        self.base.login()

        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
              
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth','url':'http://127.0.0.1:8000'})
        a.save()
        v = Voting(name='test voting')
        v.save()
        v.auths.add(a)
        v.question.add(q)

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.base.tearDown()
        self.vars = {}
        self.client = None

    def test_crear_voting(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.set_window_size(1846, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.find_element(By.LINK_TEXT, "Create voting").click()
        self.driver.find_element(By.ID, "id_name").send_keys("prueba")
        self.driver.find_element(By.ID, "id_desc").send_keys("prueba")
        self.driver.find_element(By.ID, "id_question").send_keys('test question')  
        self.driver.find_element(By.ID, "id_auths").send_keys('http://127.0.0.1:8000')  
        self.driver.find_element(By.LINK_TEXT, "Create").click()
        self.driver.switch_to.alert.accept()

    def test_start(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.set_window_size(1846, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.get(f'{self.live_server_url}/voting/start/voting/'+'id_voting'+'/')


    def test_stop(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.set_window_size(1846, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.get(f'{self.live_server_url}/voting/stop/voting/'+'id_voting'+'/')

    def test_delete(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.set_window_size(1846, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.get(f'{self.live_server_url}/voting/delete/voting/'+'id_voting'+'/')

    def test_tally(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.set_window_size(1846, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/voting/votingList/')
        self.driver.get(f'{self.live_server_url}/voting/tally/voting/'+'id_voting'+'/')

      
   



class TestCrud(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_list(self):
        response = self.client.get('/voting/votingList/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed('voting_list.html')

        self.login()
        response = self.client.get('/voting/votingList/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('voting_list.html')

    def test_create_positive(self):
        url = reverse('create_voting')
        response = self.client.post(url, {
            'name': '¿Te gusta el chocolate?',
            'desc': 'Hablamos del chocolate',
            'question': '',
            'auths': 'http://127.0.0.1:8000/'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('create_voting.html')

    def test_create_negative(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting.objects.create(
            desc='Hablamos del chocolate',
        )
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        url = reverse('create_voting')
        response = self.client.post(url, {
        })

        self.assertTemplateNotUsed('voting_list.html')

    def test_show_negative(self):
        url = 'voting/2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed('voting_details.html')

    def test_show_positive(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
           opt = QuestionOption(question=q, option='option {}'.format(i+1))
           opt.save()
        v = Voting.objects.create(
           desc='Hablamos del chocolate',
        )
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        response = self.client.get(f'/voting/{v.id}')
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed('voting_details.html')

    def test_update_positive(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
           opt = QuestionOption(question=q, option='option {}'.format(i+1))
           opt.save()
        v = Voting.objects.create(
           desc='Hablamos del chocolate',
        )
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        response = self.client.post(f'/voting/{v.id}', {
            'name' : 'test',
        })
        self.assertEqual(response.status_code, 301)
        self.assertTemplateUsed('voting_details.html')

    def test_update_negative(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
           opt = QuestionOption(question=q, option='option {}'.format(i+1))
           opt.save()
        v = Voting.objects.create(
           desc='Hablamos del chocolate',
        )
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        url = 'voting/2'
        response = self.client.post(url, {
            'name' : 'test',
        })
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed('voting_details.html')

    def test_delete_positive(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
           opt = QuestionOption(question=q, option='option {}'.format(i+1))
           opt.save()
        v = Voting.objects.create(
           desc='Hablamos del chocolate',
        )
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                         defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        v.delete()
        self.assertTrue(Voting.objects.count() == 0)

    def test_delete_negative(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
           opt = QuestionOption(question=q, option='option {}'.format(i+1))
           opt.save()
        v = Voting.objects.create(
           desc='Hablamos del chocolate',
        )
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                         defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        self.assertTrue(Voting.objects.count() != 0)

# Test de frontend Auth 
class TestAuthSelenium(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        

        u = User(username='seleniumVoter')
        u.set_password('123')
        u.save()
        self.base.login()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.base.tearDown()
        self.vars = {}
        self.client = None

    def test_create_auth(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.set_window_size(1846, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/auth_list/')
        self.driver.find_element(By.LINK_TEXT, "Create auth").click()
        self.driver.find_element(By.ID, "id_name").send_keys("prueba1")
        self.driver.find_element(By.ID, "id_url").send_keys('http://127.0.0.1:8000')  
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, "form > .btn").click()
        assert self.driver.switch_to.alert.text == "Are you sure you want to create a auth??"
        self.driver.switch_to.alert.accept()
