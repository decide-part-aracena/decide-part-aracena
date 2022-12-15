import json

from base import mods
from census.models import Census
from store.models import Vote

from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView


class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)
    
        # try:
        r = mods.get('voting', params={'id': vid})
        context['voting'] = json.dumps(r[0])
        num_census, num_votes, participation, num_questions = 0,0,'-', 1

        if r[0].get('start_date'):
            num_census = Census.objects.filter(voting_id=vid).count()
            num_votes = Vote.objects.filter(voting_id=vid).count()
            num_questions = len(r[0].get('question'))
            print(r[0])
            print(num_census)
            print(num_votes)
            print(num_questions)
            print("**********", (num_votes/num_questions)/num_census )
            if num_census != 0:
                participation = (f'{((num_votes/num_questions)/num_census)*100}')+'%'
            
            realtimedata = {'num_census':num_census, 'num_votes':num_votes, 'participation':participation}
            context['realtimedata'] = realtimedata
            
            postproc_list = r[0].get('postproc')
            context_results = {}
            if postproc_list:
                for i in range(len(postproc_list)):
                    posts = []    
                    post = postproc_list[i]
                    post_q_desc = post.get('question')

                    if not post_q_desc in context_results:

                        posts.append(post)
                        context_results[post_q_desc] = posts

                    else:

                        v = context_results.get(post_q_desc)    
                        v.append(post)
                        context_results[post_q_desc] = v

            print(context_results)
            context['results'] = context_results
            
        # except:
        #     raise Http404
            
        return context

