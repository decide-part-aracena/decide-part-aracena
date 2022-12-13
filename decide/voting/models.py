from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from base import mods
from base.models import Auth, Key


class Question(models.Model):
    desc = models.TextField()
    optionSiNo = models.BooleanField(default=False, help_text="Marca esta casilla para que las opciones sean Si o No. No podrás añadir más opciones")

    def __str__(self):
        return self.desc

@receiver(post_save, sender=Question)
def post_SiNo_Option(sender, instance, **kwargs):
    options = instance.options.all()
    if instance.optionSiNo and options.count() == 0:
        op1 = QuestionOption(question=instance, number=1, option="Sí")
        op1.save()
        op2 = QuestionOption(question=instance, number=2, option="No")
        op2.save()


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)
    
    def clean(self):
        if self.question.optionSiNo and self.question.options.all().count() != 2:
            raise ValidationError('Las Preguntas Sí/No no deben tener opciones extras. Borre todas las opciones añadidas para poder crear la pregunta')


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ManyToManyField(Question, related_name='votings')
    typepostproc = models.CharField(max_length=8,help_text='Método de recuento',choices=(('IDENTITY','IDENTITY'),('DHONT','DHONT')),default='IDENTITY')
    seats = models.PositiveIntegerField(default=0, help_text='Introduzca número de escaños a repartir en caso de elegir DHONT')

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)
 
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

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [[i['a'], i['b']] for i in votes]

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''
        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        
        question = self.question.all()
        opts = []

        for q in question:
            options = q.options.all()
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })
            

        data = { 'type': self.typepostproc, 'options': opts, 'seats': self.seats }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
