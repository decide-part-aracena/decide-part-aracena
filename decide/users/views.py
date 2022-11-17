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
from django.contrib.auth.models import User


class UsersDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, user_id, *args, **kwargs):
        user = User.objects.filter(user_id=user_id)
        user.delete()
        return Response('User deleted', status=ST_204)

    def retrieve(self, request, user_id, *args, **kwargs):
        user = request.GET.get('user_id')
        try:
            User.objects.get(user_id=user)
        except ObjectDoesNotExist:
            return Response('Invalid user', status=ST_401)
        return Response('Valid user')


def users_list(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})


def users_details(request, user_id):
    if request.method == 'GET':
        user = get_object_or_404(User, pk=user_id)
        form = UsersForm(instance=user)
        return render(request, 'users_details.html', {'user': user, 'form': form})
    else:
        try:
            user = get_object_or_404(User, pk=user_id)
            form = UsersForm(request.POST, instance=user)
            form.save()
            return redirect('user')
        except ValueError:
            return render(request, 'users_details.html', {'user': user, 'form': UsersForm,
                                                          'error': form.errors})

def users_delete(request, user_id):
    user = User.objects.get(id = user_id)
    user.delete()
    return redirect('user')
    

