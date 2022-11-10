from django.forms import ModelForm
from voting.models import Voting

class VotingForm(ModelForm):
    class Meta:
        model = Voting
        fields = ['name', 'desc', 'question', 'start_date', 'end_date','auths']