from django.urls import path
from . import views
from . import views as voting
from django.urls import include

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('voting/<int:voting_id>', voting.voting_details, name = 'voting_details'),
    path('voting/create', voting.create_voting, name = 'create_voting'),
    path('votingList/', voting.list_voting, name = 'voting_list'),
    path('delete/voting/<int:voting_id>/', voting.delete_voting, name='delete_voting'),
    path('start/voting/<int:voting_id>/', voting.start_voting, name='start_voting'),
    path('stop/voting/<int:voting_id>/', voting.stop_voting, name='stop_voting'),
    path('tally/voting/<int:voting_id>/', voting.tally_voting, name='tally_voting'),
    
]
