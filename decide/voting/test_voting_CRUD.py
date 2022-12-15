
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

    def test_show_negative(self):
         url = 'voting/2'
         response = self.client.get(url)
         self.assertEqual(response.status_code, 404)
         self.assertTemplateNotUsed('voting_details.html')

    def test_show_positive(self):
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
         response = self.client.get(f'/voting/{v.id}')
         self.assertNotEqual(response.status_code, 404)
         self.assertTemplateUsed('voting_details.html')

    def test_update_positive(self):
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
         response = self.client.post(f'/voting/{v.id}', {
             'name' : 'test',
         })
         self.assertEqual(response.status_code, 301)
         self.assertTemplateUsed('voting_details.html')

    def test_update_negative(self):
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
         url = 'voting/2'
         response = self.client.post(url, {
             'name' : 'test',
         })
         self.assertEqual(response.status_code, 404)
         self.assertTemplateNotUsed('voting_details.html')

    def test_delete_positive(self):
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
         v.delete()
         self.assertTrue(Voting.objects.count() == 0)

    def test_delete_negative(self):
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
         self.assertTrue(Voting.objects.count() != 0)