import csv
from census.models import Census
from voting.models import Voting
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse



class mainView(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        votings_ids = Census.objects.all().filter(voter_id=user.id).values_list('voting_id', flat=True)
        user_votings = Voting.objects.filter(id__in=votings_ids)

        on_going_votings = user_votings.filter(tally__isnull=True, end_date__isnull=True, start_date__isnull=False)
        finished_votings = user_votings.filter(tally__isnull=True, end_date__isnull=False)
        tally_votings = user_votings.filter(tally__isnull=False)

        context['on_going_votings'] = on_going_votings
        context['finished_votings'] = finished_votings
        context['tally_votings'] = tally_votings
        return context

#Creada para la task -----------------------------------------------------------------
def export_csv(request):

    queryset = Census.objects.all()

    options = Census._meta
    fields = [field.name for field in options.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content_Disposition'] = 'atachment; filename="census.csv"'

    writer = csv.writer(response)

    writer.writerow([options.get_field(field).verbose_name for field in fields])

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    
    return response

