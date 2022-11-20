import json

from base import mods
from census.models import Census
from store.models import Vote
from voting.models import Question

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView


class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)
    
        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])
            num_census, num_votes, participation = 0,0,'0%'

            if r[0].get('start_date'):
                print(".............................")
                num_census = Census.objects.filter(voting_id=vid).count()
                num_votes = Vote.objects.filter(voting_id=vid).count()

                # TODO: Al añadir la funcionalidad de más preguntas por votación:
                # num_questions = len(r[0].get('questions'))
                # participation = (f'{((num_votes/num_questions)/num_census)*100}')+'%'

                if num_census != 0:
                    participation = (f'{(num_votes/num_census)*100}')+'%'    
            
            realtimedata = {'num_census':num_census, 'num_votes':num_votes, 'participation':participation}
            context['realtimedata'] = realtimedata
        except:
            raise Http404
            
        return context

