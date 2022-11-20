from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms

class UsersForm(ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=40)
    last_name = forms.CharField(required=False, max_length=40)
    username = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username','email','first_name', 'last_name','is_staff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['is_staff'].widget.attrs['class'] = 'form-check-label'
            

        
