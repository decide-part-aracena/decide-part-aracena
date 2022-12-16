from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from voting import views


schema_view = get_swagger_view(title='Decide API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doc/', schema_view),
    path('gateway/', include('gateway.urls')),
    path('census/', include('census.urls')),
    path('voting/', include('voting.urls')),
    path('question/', views.listaPreguntas, name='preguntas'),
    path('question/create/', views.crearPreguntas, name='crear_preguntas'),
    path('question/createYesNo/', views.create_question_YesNo, name='create_questionYesNo'),
    path('borrar/question/<int:question_id>/', views.borrarPreguntas, name='borrar_preguntas'),
    path('', include('base.urls')),     
    path('auth/create', views.create_auth, name = 'create_auth'),
    path('auth_list/', views.list_auth, name='auth_list'),
    path('auth/<int:auth_id>', views.auth_details, name = 'auth_details'),
    path('delete/auth/<int:auth_id>/', views.delete_auth, name='delete_auth')


]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]
    