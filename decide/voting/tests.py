import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption



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

    
    def create_question_sino(self):
        q = Question(desc='Test Pregunta Sí/No', sino=True)
        q.save()
        opt = QuestionOption(question=q)
        opt.save()
        v = Voting(name='Test Votación', desc='Realicemos pregunta Sí/No', question=q)
        v.save()
        a,_=Auth.objects.get_or_create(url=settings.BASEURL,
                                        defaults={'me':True, 'name':'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def test_question_sino_validacion(self):
        q = Question(desc='Test Pregunta Sí/No con más de 2 opciones', sino=True)
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            self.assertRaises(ValidationError, opt.clean)

    def test_delete_question_sino(self):
        q = Question.objects.create(
            desc='Test Pregunta Sí/No',
            sino=True,
        )
        url = reverse('delete_question', kwargs={'pk':q.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
    
    def test_voting_question_sino(self):
        q = Question(desc='Test Votación Pregunta Sí/No', sino=True)
        q.save()
        v = Voting(name='Test Votación Pregunta Sí/No')
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        self.assertEqual(v.question.all().count(), 1)
    

    def test_empty_question_to_sino(self):
        q = Question(desc='Test Convertir Votación Pregunta Vacía a Pregunta Sí/No', sino=False)
        q.save()
        self.assertFalse(q.sino)
        q.sino=True
        self.assertTrue(q.sino)
    

    def test_filled_question_to_sino(self):
        q = Question(desc='Test Convertir Votación Pregunta Rellena a Pregunta Sí/No', sino=False)
        q.save()
        opt = QuestionOption(question=q, number= '3', option='Opción 3')
        opt.save()
        self.assertTrue(q.sino == False)
        q.sino=True
        self.assertTrue(q.sino == True)
        self.assertRaises(ValidationError, opt.clean)
    
    
    def test_create_multiquestion_sino_voting(self):
        q1 = Question(desc='Pregunta con diferentes opciones')
        q1.save()
        for i in range(5):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()
        q2 = Question(desc='Pregunta Sí/No', sino=True)
        q2.save()
        v = Voting(name='Test Votación de todo tipo')
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)
        a = v.question.all().count() == 2
        b = v.question.all()[1].sino
        self.assertTrue(a)
        self.assertTrue(b)

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
