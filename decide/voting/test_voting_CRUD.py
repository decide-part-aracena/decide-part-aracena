
from django.urls import reverse
from .models import Voting, Question, QuestionOption, Auth
from base.tests import BaseTestCase
from django.conf import settings


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
