import random

from base.tests import BaseTestCase
from census.models import Census
from base.models import Auth
from voting.models import Question, QuestionOption, Voting
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import User

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from base.tests import BaseTestCase
from voting.models import Question, Voting
from base import mods
from base.models import Auth, Key
from django.contrib.auth.models import User
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt

class AdminTestCase(StaticLiveServerTestCase):


    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

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

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        question = v.question.all()
        for q in question:
            options = q.options.all()
            for opt in options:
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
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
        return clear
        
    ####### TESTS

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
