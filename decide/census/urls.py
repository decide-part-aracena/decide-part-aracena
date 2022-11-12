from django.urls import path, include
from . import views
from census import views


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('censo/', views.listar_censos, name = 'censo'),
    path('censo/crear', views.crear_censo, name = 'crear_censo'),
    path('censo/<int:votacion_id>', views.censo_details, name = 'censo_details'),
    path('borrar/censo/<int:votacion_id>', views.borrar_censo, name = 'borrar_censo'),
]
