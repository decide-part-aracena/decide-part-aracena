from django.forms import ModelForm
from django.contrib.auth.models import User

class UsersForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirmation']