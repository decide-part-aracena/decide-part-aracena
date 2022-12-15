import random
from base.tests import BaseTestCase
from census.models import Census
from base.models import Auth, Key
from voting.models import Question, QuestionOption, Voting
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from base import mods
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt

class VisualizerTestCase(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
        
    def test_visualizer_not_started(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.question.add(q)

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Voting not started")
    
    def test_Visualizer_Started_No_Census(self):        
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

        print("Creating voting")
        v = self.create_voting()

        self.create_voters(v)

        print("Creating pubkey")
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        participation_before = self.driver.find_element(By.ID, "participation").text
        print(participation_before)

        print("Storing votes")
        self.store_votes(v)
        
        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        participation_after = self.driver.find_element(By.ID, "participation").text
        print(participation_after)
        assert participation_after != participation_before


    def create_question(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        return q

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(2):
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

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()
    
    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voters(self, v):
        for i in range(10):
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
        question = v.question.all()
        for q in question:
            options = q.options.all()
            for opt in options:
                clear[opt.number] = 0
                for i in range(4):
                    a, b = self.encrypt_msg(opt.number, v)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user = self.get_or_create_user(voter.voter_id)
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
        return clear
