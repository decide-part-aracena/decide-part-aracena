from django.urls import path
from django.contrib.auth.decorators import login_required
from census import views
from .views import mainView
from .views import export_csv

urlpatterns = [
    path('', login_required(mainView.as_view()), name='index'),
   # path('import_datadb', views.excel, name='import_datadb'),
   path('census_exported', export_csv),
]
