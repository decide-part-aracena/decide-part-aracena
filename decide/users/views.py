from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics
from rest_framework.response import Response

from django.contrib.auth.models import User
from .forms import UsersForm
from django.contrib import messages

class UsersDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, user_id, *args, **kwargs):
        user = User.objects.filter(id=user_id)
        user.delete()
        return Response('User deleted', status=ST_204)

    def retrieve(self, request, user_id, *args, **kwargs):
        try:
            User.objects.get(id=user_id)
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
            messages.info(request, 'The profile has been update')
            return redirect('/users/'+str(user_id))
        except ValueError:
            return render(request, 'users_details.html', {'user': user, 'form': UsersForm,
                                                          'error': form.errors})

def users_delete(request, user_id):
    user = User.objects.get(id = user_id)
    user.delete()
    return redirect('/users')
    

