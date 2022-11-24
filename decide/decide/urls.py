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
    path('question/', views.listaPreguntas, name='preguntas'),
    path('question/create/', views.crearPreguntas, name='crear_preguntas'),
    path('question/<int:question_id>/', views.showUpdateQuestions, name='showUpdateQuestions'),
    path('borrar/question/<int:question_id>/', views.borrarPreguntas, name='borrar_preguntas'),
    path('', include('base.urls'))
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]
    