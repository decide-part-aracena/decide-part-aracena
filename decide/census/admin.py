from django.contrib import admin
from import_export.admin import ImportExportMixin
from django.contrib.auth.models import User
from census import views
from django.contrib.auth.forms import UserCreationForm
from .models import Census


class CensusAdmin(ImportExportMixin,admin.ModelAdmin):

    #v = views.get_or_create_user_to_import(User, int('voter_id'))


    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )

    

admin.site.register(Census, CensusAdmin)

