from enum import unique
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name=forms.CharField(required=False,max_length=40)
    last_name=forms.CharField(required=False,max_length=40)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        help_texts = {
            'password1' : 'Ejemplo',
        }

    def save(self, commit=True):
        user = super(NewUserForm,self).save(commit=False)
        user.email= self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        self.fields['password1'].help_text='Ejemplo'

        if commit:
            user.save()
        return user

class MagicLinkForm(forms.Form):
    email = forms.EmailField()
