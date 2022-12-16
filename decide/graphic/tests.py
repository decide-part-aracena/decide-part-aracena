from base.tests import BaseTestCase
from census.models import Census
from voting.models import Question, Voting
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from base import mods

from voting.tests import VotingModelTestCase

class GraphicTestCase(StaticLiveServerTestCase):
    
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        self.voting = VotingModelTestCase()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def store_votes_multiquestion(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        question = v.question.all()
        for q in question:
            options = q.options.all()
            for opt in options:
                clear[opt.number] = 0
                for i in range(4):
                    a, b = self.voting.encrypt_msg(opt.number, v)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user = self.voting.get_or_create_user(voter.voter_id)
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
        return clear
                 
    #enter URL
    def test_graphicEntry(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)

        self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"info-title").text
        self.assertTrue(vState, "Graphs with voting results")

    #votation without tally -> show advise
    def test_graphic_not_tally(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)

        self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"advertisement").text
        self.assertTrue(vState, "Count not complete")

    # button graphic -> visualizer
    def test_graphic_buttonGraphicVisualizer(self):
        print("Creating voting")
        v = self.voting.create_voting()

        self.voting.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        self.store_votes_multiquestion(v)

        self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')

        self.driver.implicitly_wait(5)
        self.driver.find_element(By.ID, "return-button").click()
        actualUrl = self.driver.current_url
        expectedUrl = f'{self.live_server_url}/visualizer/{v.pk}/'
        
        self.assertTrue(actualUrl, expectedUrl)

    # button visualizer -> graphic
    def test_graphic_buttonVisualizerGraphic(self):
        print("Creating voting")
        v = self.voting.create_voting()

        self.voting.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        self.store_votes_multiquestion(v)

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')

        self.driver.implicitly_wait(5)
        self.driver.find_element(By.ID, "button-graphic").click()
        actualUrl = self.driver.current_url
        expectedUrl = f'{self.live_server_url}/graphic/{v.pk}/'
        
        self.assertTrue(actualUrl, expectedUrl)

    # show graphic -> bar type
    def test_graphic_BarType(self):        
        print("Creating voting")
        v = self.voting.create_voting()

        self.voting.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        self.store_votes_multiquestion(v)

        self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"graphic-title-1").text
        self.assertTrue(vState, "Bar type")

    # show graphic -> donut type
    def test_graphic_DonutType(self):        
        print("Creating voting")
        v = self.voting.create_voting()

        self.voting.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        print("Storing votes")
        self.store_votes_multiquestion(v)

        self.driver.get(f'{self.live_server_url}/graphic/{v.pk}/')
        vState= self.driver.find_element(By.ID,"graphic-title-2").text
        self.assertTrue(vState, "Donut type")
    
