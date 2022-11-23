from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import mainView
from census import views 

urlpatterns = [
    path('', login_required(mainView.as_view()), name='index'), 
    path('census_exported', export_csv),
    path('censo/', views.listar_censos, name = 'censo'),
    path('censo/crear', views.crear_censo, name = 'crear_censo'),
    path('censo/<int:votacion_id>', views.censo_details, name = 'censo_details'),
    path('borrar/censo/<int:votacion_id>', views.borrar_censo, name = 'borrar_censo'),
   

]
