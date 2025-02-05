import csv
from import_export import resources
from http.client import HTTPResponse
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
from .models import Census, ExcelFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
import pandas as pd 
from voting.models import Voting
import operator
from django.core.paginator import Paginator
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
import random
from django.contrib.auth.decorators import user_passes_test

from django.template.loader import render_to_string

from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


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

def staff_required(login_url):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)

@staff_required(login_url="/base")
def listar_censos(request):

    censos = Census.objects.all()
    page = request.GET.get('page',1)
    try:
        paginator = Paginator(censos,5)
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

# Creada para la task de Importación de Censo -----------------------------------------------------------------

def randletter(a,b):
    return chr(random.randint(ord(a),ord(b)))

def generar_nombre():

    newUser = "user"
    letraMin = randletter('a','z')
    letraMayusc = randletter('A', 'Z')
    letraRand = (letraMin, letraMayusc)[random.randint(0,1)]

    newUser = newUser + letraMin + letraMayusc + letraRand
    print(newUser)
    
    try:
        User.objects.get(username=newUser)
        return generar_nombre()
    except User.DoesNotExist:
        return newUser

def import_datadb(request):

    if request.method == 'POST':

        # Importación del archivo excel:
        try:
            file = request.FILES['file']
            
            obj = ExcelFile.objects.create( file = file )
            path = str(obj.file)
        
            df = pd.read_excel(path)
            
            # Ids de los usuarios de la bbdd:
            users = User.objects.all()
            users_id = []
            for us in users:
                user_id = us.id
                users_id.append(user_id)

            # Ids de las votaciones de la bbdd:
            votings = Voting.objects.all()
            votings_id = []
            for vid in votings:
                voting_id = vid.id
                votings_id.append(voting_id)
            
            try:
                cols = [col for col in df.columns if col.startswith('Unnamed:')]
                filas = [f for f in df.values if ( len(list(v for v in f if str(v).startswith('nan'))) > 0 ) ]
                print(filas)
                if not len(cols) > 0 and not len(filas) > 0:

                    for i in range(df.shape[0]):
                        
                        if df['voter_id'][i] not in users_id and str(df['voter_id'][i]) != 'nan':
                        
                        # Crear un nuevo usuario con el votante no registrado en bbdd:
                            newUsername =  generar_nombre()
                            newUser = User(username=newUsername)
                            newUser.set_password('newUser')
                            newUser.pk =  (df['voter_id'][i])
                            newUser.save()

                        # Añadirlo a la lista de ids de usuarios en bbdd:
                            users_id.append(df['voter_id'][i])
                            
                        if df['voter_id'][i] in users_id and df['voting_id'][i] in votings_id and len(str(df['voting_id'][i])) > 0:
                            
                            try:
                                
                                census = Census(voting_id=df['voting_id'][i], voter_id=df['voter_id'][i])
                                census.save()

                            except IntegrityError:
                                print('Entra en error Duplicated key')
                                messages.add_message(request,  messages.ERROR, "Duplicated Key")
            except KeyError:
                   messages.add_message(request,  messages.ERROR, "Key Error")
        except MultiValueDictKeyError:
                messages.add_message(request, messages.ERROR, 
                    "¡Cuidado! No has cargado ningún archivo.")

    return render(request, 'excel.html')


def excel(request):
   return render(request, 'excel.html')

def sort_by_voting(request):
    census = Census.objects.all()
    dic = {}
    for c in census:
        voting_id = c.voting_id
        dic[c] = voting_id
    
    sorted_dic = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'sorting_by_voting.html', {'sorted_census_voting_id':sorted_dic.keys})

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

def export_xls(request):

    census_resource = resources.modelresource_factory(model=Census)()
    dataset = census_resource.export()

    response = HttpResponse(dataset.xls, content_type='text/xls')
    response['Content_Disposition'] = 'atachment; filename="census.xls"'
    
    return response

def export_json(request):
    
    census_resource = resources.modelresource_factory(model=Census)()
    dataset = census_resource.export()

    response = HttpResponse(dataset.json, content_type='text/json')
    response['Content_Disposition'] = 'atachment; filename="census.json"'
    
    return response

def export_yaml(request):
    
    census_resource = resources.modelresource_factory(model=Census)()
    dataset = census_resource.export()

    response = HttpResponse(dataset.yaml, content_type='text/yaml')
    response['Content_Disposition'] = 'atachment; filename="census.yaml"'
    
    return response

def export_html(request):
    
    census_resource = resources.modelresource_factory(model=Census)()
    dataset = census_resource.export()

    response = HttpResponse(dataset.html, content_type='text/html')
    response['Content_Disposition'] = 'atachment; filename="census.html"'
    
    return response

def export_ods(request):

    census_resource = resources.modelresource_factory(model=Census)()
    dataset = census_resource.export()

    response = HttpResponse(dataset.ods, content_type='text/ods')
    response['Content_Disposition'] = 'atachment; filename="census.ods"'
    
    return response

def export_pdf(request):

    censos = Census.objects.all()
    html = render_to_string("censoToPDF.html", {'censos':censos})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; attachment; census.pdf"
    response["Content-Transfer-Encoding"] = 'binary'

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response

def sort_by_voter(request):
    census = Census.objects.all()
    dic = {}
    for c in census:
        voter_id = c.voter_id
        dic[c] = voter_id
    
    sorted_dic = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'sorting_by_voter.html', {'sorted_census_voter_id':sorted_dic.keys})

