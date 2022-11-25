from django.urls import path
from .views import GraphicView


urlpatterns = [
    path('<int:voting_id>/', GraphicView.as_view()),
]
