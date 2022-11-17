from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name=forms.CharField(required=False,max_length=40)
    last_name=forms.CharField(required=False,max_length=40)
    username=forms.CharField(required=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super(NewUserForm,self).save(commit=False)
        user.email= self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        

        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


