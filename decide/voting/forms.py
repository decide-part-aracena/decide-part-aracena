from voting.models import Question
from django.forms import ModelForm
from voting.models import Voting
from voting.models import QuestionOption
from base.models import Auth

class QuestionForm(ModelForm):
    class Meta: 
        model= Question
        fields = ['desc', 'optionSiNo']

class QuestionOptionsForm(ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['number', 'option']

class VotingForm(ModelForm):
    class Meta:
        model = Voting
        fields = ['name', 'desc', 'question','auths']

class AuthForm(ModelForm):
    class Meta:
        model = Auth
        fields = ['name', 'url']