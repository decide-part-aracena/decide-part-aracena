from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('import_datadb', import_datadb, name='import'),
    path('census/', views.listar_censos, name = 'censo'),
    path('censo/census_exported', views.export_csv),
    path('census/create', views.crear_censo, name = 'crear_censo'),
    path('census/<int:votacion_id>', views.censo_details, name = 'censo_details'),
    path('delete/census/<int:votacion_id>', views.borrar_censo, name = 'borrar_censo'),
    path('sortedByVoting/', views.sort_by_voting, name = 'sorted_by_voting'),
]
