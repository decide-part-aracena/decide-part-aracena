from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED as ST_201,
    HTTP_204_NO_CONTENT as ST_204,
    HTTP_400_BAD_REQUEST as ST_400,
    HTTP_401_UNAUTHORIZED as ST_401,
    HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from .models import Census
from .forms import CensusForm
from django.core.paginator import Paginator
from django.http import Http404


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(
            voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(
            voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')


def listar_censos(request):
    censos = Census.objects.all()
    page = request.GET.get('page',1)
    try:
        paginator = Paginator(censos,2)
        censos = paginator.page(page)
    except:
        raise Http404

    return render(request, 'censo.html', {'censos': censos, 'paginator':paginator})


def crear_censo(request):
    if request.method == 'GET':
        return render(request, 'crear_censo.html', {'form': CensusForm})
    else:
        try:
            form = CensusForm(request.POST)
            nuevo_censo = form.save(commit=False)
            nuevo_censo.save()
            return redirect('censo')
        except ValueError:
            return render(request, 'crear_censo.html', {'form': CensusForm, 'error': form.errors})


def censo_details(request, votacion_id):
    if request.method == 'GET':
        censo = get_object_or_404(Census, pk=votacion_id)
        form = CensusForm(instance=censo)
        return render(request, 'censo_details.html', {'censo': censo, 'form': form})
    else:
        try:
            censo = get_object_or_404(Census, pk=votacion_id)
            form = CensusForm(request.POST, instance=censo)
            form.save()
            return redirect('censo')
        except ValueError:
            return render(request, 'censo_details.html', {'censo': censo, 'form': CensusForm,
                                                          'error': form.errors})

def borrar_censo(request, votacion_id):
    censo = Census.objects.get(id = votacion_id)
    censo.delete()
    return redirect('censo')
