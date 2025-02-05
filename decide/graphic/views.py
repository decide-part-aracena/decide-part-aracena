import json
from django.views.generic import TemplateView
from django.http import Http404

from base import mods


class GraphicView(TemplateView):
    template_name = 'graphic/graphic.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        return context

    
