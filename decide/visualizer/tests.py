from base.tests import BaseTestCase
from census.models import Census
from voting.models import Question, Voting
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from base import mods

from voting.tests import VotingModelTestCase

class VisualizerTestCase(StaticLiveServerTestCase):
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
        
    def test_visualizer_not_started(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Voting not started")
    
    def test_visualizer_started_no_census(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting', start_date=timezone.now())
        v.save()
        v.question.add(q)

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        assert self.driver.find_element(By.ID, "participation").text == "-"

    def test_visualizer_started_no_noted(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting', start_date=timezone.now())
        v.save()
        v.question.add(q)

        c1 = Census(voter_id=1, voting_id=v.id)
        c1.save()
        c2 = Census(voter_id=2, voting_id=v.id)
        c2.save()
        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        assert self.driver.find_element(By.ID, "participation").text == "0.0%"

    def test_visualizer_census_change(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting', start_date=timezone.now())
        v.save()
        v.question.add(q)
        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')

        census_before = self.driver.find_element(By.ID, "census").text

        c1 = Census(voter_id=1, voting_id=v.id)
        c1.save()
        c2 = Census(voter_id=2, voting_id=v.id)
        c2.save()
        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')

        census_after = self.driver.find_element(By.ID, "census").text

        assert census_before != census_after

    def test_visualizer_participation_change(self): 

        v = self.voting.create_voting()
        self.voting.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        participation_before = self.driver.find_element(By.ID, "participation").text

        self.store_votes_multiquestion(v)
        
        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        participation_after = self.driver.find_element(By.ID, "participation").text
        assert participation_after != participation_before

