from django.forms import ModelForm
from census.models import Census

class CensusForm(ModelForm):
    class Meta:
        model = Census
        fields = ['voting_id', 'voter_id']