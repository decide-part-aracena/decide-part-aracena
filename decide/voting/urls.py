from django.urls import path
from . import views
from . import views as voting

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('voting/<int:voting_id>', voting.voting_details, name = 'voting_details'),
    path('voting/create', voting.create_voting, name = 'create_voting'),
    path('votingList/', voting.list_voting, name = 'voting_list'),
]
