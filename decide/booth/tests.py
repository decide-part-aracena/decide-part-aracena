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
from selenium.webdriver.common.by import By
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
        a.save()
        v.auths.add(au)
        v.question.add(q1)
        v.question.add(q2)

        #Create user
        u = User(username='voter1')
        u.set_password('complexpassword')
        u.is_staff = True
        u.save()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
    
    def test_vote_multiple_questions(self):
        voting = Voting.objects.get(name="test voting")
        user = User.objects.get(username="voter1")

        census = Census(voting_id=voting.pk, voter_id=user.pk)
        census.save()

        #Start voting
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("voter1")
        self.driver.find_element(By.ID, "id_password").send_keys("complexpassword")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+'/voting/votingList/')
        self.driver.find_element(By.LINK_TEXT, "Start").click()

        #Try to vote
        self.driver.find_element(By.LINK_TEXT, "booth").click()
        self.driver.find_element(By.ID, "username").send_keys('voter1')
        self.driver.find_element(By.ID, "password").send_keys('complexpassword')
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "#\\__BVID__9 .custom-control-label").click()
        self.driver.find_element(By.CSS_SELECTOR, "#\\__BVID__19 .custom-control-label").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
    
    
    def selenium_test_vote_multiple_questions_not_started(self):
        votingId = Voting.objects.get(name="test voting").pk
        
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("voter1")
        self.driver.find_element(By.ID, "id_password").send_keys("complexpassword")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
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
    
    ### SELENIUM TESTS 
    def selenium_test_vote_multiple_questions_not_started(self):
        votingId = Voting.objects.get(name="test voting").pk
        
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("voter1")
        self.driver.find_element(By.ID, "id_password").send_keys("complexpassword")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+'/voting/votingList/')
        self.driver.find_element(By.LINK_TEXT, "booth").click()
        self.assertTrue(
            self.live_server_url+"/booth/{}/".format(votingId) == self.driver.current_url)
        self.assertTrue(
            self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Not Found")
    
    def selenium_test_vote_multiple_questions_incorrect_login(self):

        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("voter1")
        self.driver.find_element(By.ID, "id_password").send_keys("complexpassword")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        #Start voting
        self.driver.get(self.live_server_url+'/voting/votingList/')
        self.driver.find_element(By.LINK_TEXT, "Start").click()

        #Try to vote
        self.driver.find_element(By.LINK_TEXT, "booth").click()
        self.driver.find_element(By.ID, "username").send_keys('incorrectVoter')
        self.driver.find_element(By.ID, "password").send_keys('incorrectPassword')
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(1)
        self.assertTrue(
            self.driver.find_element(By.CSS_SELECTOR, "div.alert.alert-dismissible.alert-danger").text == "× Error: Bad Request")
    