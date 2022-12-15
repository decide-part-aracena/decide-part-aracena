from django.test import TestCase
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.conf import settings
from census.models import Census
from django.contrib.auth.models import User
from base import mods
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class BoothTestCase(StaticLiveServerTestCase):
   
    def setUp(self):
        self.client = APIClient()
        self.base = BaseTestCase()  
        self.base.setUp()
        self.vars={}
        mods.mock_query(self.client)
        
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        #Create questions
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
        
        #Create voting and add the questions to it
        v = Voting(name='test voting')
        v.save()
        au = Auth(name='test auth', url=self.live_server_url, me=True)
        au.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'url':self.live_server_url, 'name': 'test auth'})
        print(self.live_server_url)
        a.save()
        v.auths.add(au)
        v.question.add(q1)
        v.question.add(q2)

        #Create user
        u = User(username='voter1')
        u.set_password('complexpassword')
        u.save()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def selenium_test_voting_multiple_questions_not_started(self):
        votingId = Voting.objects.get(name="test voting").pk
        
        self.driver.get(self.live_server_url+'/voting/votingList/')
        self.driver.find_element(By.LINK_TEXT, "booth").click()
        self.assertTrue(
            self.live_server_url+"/booth/{}/".format(votingId) == self.driver.current_url)
        self.assertTrue(
            self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Not Found")
    
    def test_voting_multiple_questions_not_started(self):
        votingId = Voting.objects.get(name="test voting").pk

        response = self.client.get('/booth/{}/'.format(votingId), format='json')
        self.assertEqual(response.status_code, 404)
    
    def test_vote_multiple_questions_without_permission(self):
        #Start the voting
        votingId = Voting.objects.get(name="test voting").pk
        response = self.client.get('/voting/start/voting/{}/'.format(votingId))
        self.assertEqual(response.status_code, 302)

        #Access the booth
        response = self.client.get('/booth/{}/'.format(votingId), format='json')
        self.assertEqual(response.status_code, 200)
        
        #Try to vote
        response = self.client.get('/census/{}/?voter_id={}'.format(votingId,1), format='json')
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/store/')
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/gateway/store/')
        self.assertEqual(response.status_code, 401)