"""decide URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from base import views as v1
from census import views as v2

schema_view = get_swagger_view(title='Decide API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', v1.home, name = 'home'),
    path('doc/', schema_view),
    path('censo/', v2.listar_censos, name = 'censo'),
    path('censo/crear', v2.crear_censo, name = 'crear_censo'),
    path('censo/<int:votacion_id>', v2.censo_details, name = 'censo_details'),
    path('borrar/censo/<int:votacion_id>', v2.borrar_censo, name = 'borrar_censo'),
    path('gateway/', include('gateway.urls')),
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]
