from voting.models import Question
from django.forms import ModelForm
from voting.models import Voting
from voting.models import QuestionOption

class QuestionForm(ModelForm):
    class Meta: 
        model= Question
        fields = ['desc']

class QuestionOptionsForm(ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['number', 'option']

class VotingForm(ModelForm):
    class Meta:
        model = Voting
        fields = ['name', 'desc', 'question', 'start_date', 'end_date','auths']