
import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render, redirect
from base.serializers import KeySerializer

from voting.forms import QuestionForm
from .models import Voting
from base.models import Key
from .filters import StartedFilter
from django.utils.crypto import get_random_string
from base import mods
from base.models import Auth, Key


from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth
from django.shortcuts import get_object_or_404, redirect, render
from .forms import VotingForm
from .forms import QuestionOptionsForm



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
        for data in ['name', 'desc', 'question', 'question_opt']:
            if not data in request.data:
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

def listaPreguntas(request):
    preguntas = Question.objects.all()
    return render(request, 'preguntas.html', {'preguntas':preguntas})

def crearPreguntas(request):
    if request.method == 'GET':
        v = range(0,3)
        return render(request, 'crearPreguntas.html', {'form':QuestionForm, 'form2':QuestionOptionsForm, 'v':v})
    else:
        try: 
            form = QuestionForm(request.POST)
            nuevaPregunta = form.save(commit = False)
            nuevaPregunta.save()
            return redirect('preguntas')
        except ValueError:
            v = range(0,3) 
            return render(request, 'preguntas.html', {'form':QuestionForm, 'form2':QuestionOptionsForm,'v':v,'error': form.errors})

def borrarPreguntas(request, question_id):
    question = Question.objects.get(id = question_id)
    question.delete()
    return redirect('preguntas')

def showUpdateQuestions(request, question_id):
    if request.method == 'GET':
        question = get_object_or_404(Question, pk=question_id)
        form = QuestionForm(instance = question)
        return render(request, 'showUpdateQuestions.html', {'pregunta': question, 'form':form})
    else:
        try:
            question = get_object_or_404(Question, pk=question_id)
            form = QuestionForm(request.POST, instance = question)
            form.save()
            return redirect('preguntas')
        except ValueError:
            return render(request, 'showUpdateQuestions.html', {'pregunta': question, 'form':QuestionForm, 'error': form.errors})



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
                                                  

def create_voting(request):
    if request.method == 'GET':
        return render(request, 'create_voting.html', {'form': VotingForm})
    else:
        try:
            form = VotingForm(request.POST)
            nuevo_question = form.save(commit=False)
            nuevo_question.save()
            return redirect('voting_list')
        except ValueError:
            return render(request, 'create_voting.html', {'form': VotingForm, 'error': form.errors})


def list_voting(request):
    voting = Voting.objects.all()
    return render(request, 'voting_list.html',{
        'voting':voting
    })

def delete_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    voting.delete()
    return redirect('voting_list')

def start_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    #voting.create_pubkey()
    voting.start_date = timezone.now()
    voting.save()
    return redirect('voting_list')

def stop_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    voting.end_date = timezone.now()
    voting.save()
    return redirect('voting_list')

def tally_voting(request, voting_id):
    voting = Voting.objects.get(id = voting_id)
    token = request.session.get('auth-token', '')
    voting.tally_votes(token)
    return redirect('voting_list')

