from django.urls import path, include
from . import views
from .views import *


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('import_datadb', import_datadb, name='import'),
    path('census/', views.listar_censos, name = 'censo'),
    path('census/census_exported_csv', views.export_csv,),
    path('census/census_exported_pdf', views.export_pdf,),
    path('census/census_exported_xls', views.export_xls,),
    path('census/census_exported_json', views.export_json,),
    path('census/census_exported_yaml', views.export_yaml,),
    path('census/census_exported_html', views.export_html,),
    path('census/census_exported_ods', views.export_ods,),
    path('census/create', views.crear_censo, name = 'crear_censo'),
    path('census/<int:votacion_id>', views.censo_details, name = 'censo_details'),
    path('delete/census/<int:votacion_id>', views.borrar_censo, name = 'borrar_censo'),
    path('sortedByVoting/', views.sort_by_voting, name = 'sorted_by_voting'),
]
