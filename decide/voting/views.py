
import django_filters.rest_framework
import operator

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response

from base.serializers import KeySerializer

from django.shortcuts import render, redirect, get_object_or_404
from voting.forms import QuestionForm
#from .models import Voting
from base.models import Key
from .filters import StartedFilter
from django.utils.crypto import get_random_string
from base import mods
from base.models import Auth, Key
from voting.forms import QuestionForm, QuestionOptionsForm
from django.shortcuts import render, redirect, get_object_or_404

from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth
from .forms import VotingForm, AuthForm
from django.contrib.auth.decorators import user_passes_test

def staff_required(login_url):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)

class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', )

    def get(self, request, *args, **kwargs):
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'question', 'question_opt','typepostproc', 'seats']:
            if data not in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('question'))
        question.save()
        voting.question.add(question)
        for idx, q_opt in enumerate(request.data.get('question_opt')):
            opt = QuestionOption(question=question, option=q_opt, number=idx)
            opt.save()
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),
                question=question)
        voting.save()

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)


class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)

@staff_required(login_url="/base")        
def listaPreguntas(request):
    preguntas = Question.objects.all() 
    return render(request, 'preguntas.html', {'preguntas':preguntas})

@staff_required(login_url="/base")        
def crearPreguntas(request):
    if request.method == 'GET':
        return render(request, 'crearPreguntas.html', {'form':QuestionForm, 'form2':QuestionOptionsForm})
    else:
        try: 
       
            form = QuestionForm(request.POST)
            q = form.save()

            e = dict(request.POST)
            numbers = e.pop('number')
            options = e.pop('option')

            for i  in range(len(numbers)):
                form2 = QuestionOption(question=q, option=options[i], number=numbers[i])
                form2.save()

            return redirect('create_voting')
        except ValueError:
            return render(request, 'preguntas.html', {'form':QuestionForm, 'form2':QuestionOption,'error': form.errors})

@staff_required(login_url="/base")        
def borrarPreguntas(request, question_id):
    question = Question.objects.get(id = question_id)
    question.delete()
    return redirect('preguntas')

@staff_required(login_url="/base")
def voting_details(request, voting_id):
    if request.method == 'GET':
        voting = get_object_or_404(Voting, pk=voting_id)
        form = VotingForm(instance=voting)
        return render(request, 'voting_details.html', {'voting': voting, 'form': form})
    else:
        try:
            voting = get_object_or_404(Voting, pk=voting_id)
            form = VotingForm(request.POST, instance=voting)
            form.save()
            return redirect('voting_list')
        except ValueError:
            return render(request, 'voting_details.html', {'voting': voting, 'form': VotingForm,
                                                          'error': form.errors})
                                                  

@staff_required(login_url="/base")
def create_voting(request):
    if request.method == 'GET':
        return render(request, 'create_voting.html', {'form': VotingForm})
    else:
        try:
            form = VotingForm(request.POST)
            nuevo_question = form.save(commit=True)
            nuevo_question.save()
            return redirect('voting_list')
        except ValueError:
            return render(request, 'create_voting.html', {'form': VotingForm, 'error': form.errors})

@staff_required(login_url="/base")
def sort_by_param(request):
    cadena = str(request)
    spliter = cadena.split(sep = '/')
    param = spliter[-2]
    voting = Voting.objects.all()
    dic = {}
    
    for v in voting:
        if(param == 'name'):
            name = v.name
            dic[v] = name
        elif(param == 'startDate'):
            date = v.start_date
            if date is not None:      
                dic[v] = date
        else: 
            date = v.end_date  
            if date is not None:      
                dic[v] = date

    sorted_dic = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'sorted_by_param.html', {'sorted_voting':sorted_dic.keys})
    

@staff_required(login_url="/base")
def list_voting(request):
    voting = Voting.objects.all()
    return render(request, 'voting_list.html',{
        'voting':voting
    })
@staff_required(login_url="/base")
def delete_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    voting.delete()
    return redirect('voting_list')
@staff_required(login_url="/base")  
def start_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)

    Voting.create_pubkey(voting)
    voting.start_date = timezone.now()
    voting.save()
    return redirect('voting_list')
@staff_required(login_url="/base")
def stop_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    voting.end_date = timezone.now()
    voting.save()
    return redirect('voting_list')

@staff_required(login_url="/base")
def tally_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    token = request.session.get('auth-token', '')
    voting.tally_votes(token)
    return redirect('voting_list')

@staff_required(login_url="/base")        
def create_auth(request):
    if request.method == 'GET':
        return render(request, 'create_auth.html', {'form': AuthForm})
    else:
        try:
            form = AuthForm(request.POST)
            new_auth = form.save(commit=True)
            new_auth.save()
            return redirect('create_voting')
        except ValueError:
            return render(request, 'create_auth.html', {'form':AuthForm, 'error':form.errors})

@staff_required(login_url="/base")        
def list_auth(request):
    auth = Auth.objects.all()
    return render(request, 'auth_list.html',{'auth':auth})

@staff_required(login_url="/base")        
def delete_auth(request, auth_id):
    auth = Auth.objects.get(id = auth_id)
    auth.delete()
    return redirect('auth_list')

@staff_required(login_url="/base")        
def auth_details(request, auth_id):
    if request.method == 'GET':
        auth = get_object_or_404(Auth, pk=auth_id)
        form = AuthForm(instance=auth)
        return render(request, 'auth_details.html', {'auth': auth, 'form':form})
    else:
        try:
            auth = get_object_or_404(Auth, pk=auth_id)
            form = AuthForm(request.POST, instance=auth)
            form.save()
            return redirect('auth_list')
        except ValueError:
            return render(request, 'auth_details.html', {'auth': auth, 'form': AuthForm,
                                                          'error': form.errors})

