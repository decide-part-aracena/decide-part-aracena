from voting.models import Question
from django.forms import ModelForm
from voting.models import Voting

class QuestionForm(ModelForm):
    class Meta: 
        model= Question
        fields = ['desc']

class VotingForm(ModelForm):
    class Meta:
        model = Voting
        fields = ['name', 'desc', 'question', 'start_date', 'end_date','auths']