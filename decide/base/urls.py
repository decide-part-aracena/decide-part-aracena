from django.urls import include, path
from django.contrib.auth.decorators import login_required

from .views import mainView

urlpatterns = [
    path('', login_required(mainView.as_view()), name='index'),
]
