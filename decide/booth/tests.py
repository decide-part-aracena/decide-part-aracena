from django.test import TestCase
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.conf import settings

class BoothTestCase(BaseTestCase):

    def test_vote_multiple_questions_without_permission(self):
        #First we create the questions
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
        
        #Second we create the voting and add the questions to it
        v = Voting(name='test voting')
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'url':'http://127.0.0.1:8000', 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)
        v.start_date
        a = v.question.all().count() == 2
        self.assertTrue(a)

        votingId = v.pk
        self.login()
        #Start the voting
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
        
        
 