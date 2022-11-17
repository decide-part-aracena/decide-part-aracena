from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics
from rest_framework.response import Response
from .forms import NewUserForm
from django.views.generic

from rest_framework.status import (
    HTTP_201_CREATED as ST_201,
    HTTP_204_NO_CONTENT as ST_204,
    HTTP_400_BAD_REQUEST as ST_400,
    HTTP_401_UNAUTHORIZED as ST_401,
    HTTP_409_CONFLICT as ST_409
)
from rest_framework.views import APIView
from base.perms import UserIsStaff
from django.contrib.auth.models import User


def users_list(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})


def users_delete(request, user_id):
    user = User.objects.get(id = user_id)
    user.delete()
    return redirect('/users')


    

