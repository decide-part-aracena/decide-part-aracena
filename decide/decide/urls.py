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
    path('voting/<int:voting_id>', views.voting_details, name = 'voting_details'),
    path('voting/crear', views.crear_voting, name = 'crear_voting'),
    path('votingList/', views.listar_voting, name = 'voting_list'),
    path('', include('base.urls'))
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]
