from http.client import HTTPResponse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
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
from .models import Census, ExcelFile
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
import pandas as pd 



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
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})

#Creada para la task -----------------------------------------------------------------
    def list_user_create(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        for voter in voters:
            usuario = User.create_user(voter)
            usuario.save()
        return Response({'voters': voters})

class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')

#Creada para la task -----------------------------------------------------------------

def import_datadb(request):
    if request.method == 'POST':
            file = request.FILES['file']
            obj = ExcelFile.objects.create(
                file = file
            )
            path = file.file
            print('{settings.BASE_DIR)/{path}')
            df = pd.read_excel(path)
            print(df)

    return render(request, 'excel.html')

def get_or_create_user_to_import(self, voter_id):
        user, _ = User.objects.get_or_create(pk=voter_id)
        user.username = 'user{}'.format(voter_id)
        user.set_password('qwerty')
        user.save()
        return user

def imprimir(request):
    votaciones = Census.objects.all().values()
    output = ""
    for vt in votaciones:
        output += vt
    return HTTPResponse(output)

def excel(request):
   return render(request, 'excel.html')