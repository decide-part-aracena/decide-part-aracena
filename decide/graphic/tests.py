import random

from base.tests import BaseTestCase
from census.models import Census
from base.models import Auth
from voting.models import Question, QuestionOption, Voting
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import User

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from voting.tests import VotingModelTestCase

from selenium.webdriver.common.by import By

class AdminTestCase(StaticLiveServerTestCase, VotingModelTestCase):

    #enter URL
    def test_graphicEntry(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)
        response =self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"info-title").text
        self.assertTrue(vState, "Graphs with voting results")

    #votation without tally
    def test_graphic_not_tally(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)

        response =self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"advertisement").text
        self.assertTrue(vState, "Count not complete")

    # button graphic -> visualizer
    def test_graphic_buttonGraphicVisualizer(self):
        print("Creating voting")
        v = self.create_voting()

        self.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        clear = self.store_votes(v)

        response =self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')

        self.driver.find_element(By.ID, "return-button").click()
        actualUrl = self.driver.current_url
        expectedUrl = f'{self.live_server_url}/visualizer/{v.pk}/'
        
        self.assertTrue(actualUrl, expectedUrl) 

    # button visualizer -> graphic
    def test_graphic_buttonVisualizerGraphic(self):
        print("Creating voting")
        v = self.create_voting()

        self.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        clear = self.store_votes(v)

        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')

        self.driver.find_element(By.ID, "button-graphic").click()
        actualUrl = self.driver.current_url
        expectedUrl = f'{self.live_server_url}/graphic/{v.pk}/'
        
        self.assertTrue(actualUrl, expectedUrl)

    # show graphic -> bar type
    def test_graphic_BarType(self):        
        print("Creating voting")
        v = self.create_voting()

        self.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        clear = self.store_votes(v)

        response =self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"graphic-title-1").text
        self.assertTrue(vState, "Bar type")

    # show graphic -> donut type
    def test_graphic_DonutType(self):        
        print("Creating voting")
        v = self.create_voting()

        self.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        clear = self.store_votes(v)

        print(v.postproc)

        response =self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"graphic2")
        self.assertTrue(vState, True)
    
