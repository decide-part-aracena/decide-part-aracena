from django.urls import path
from . import views
from . import views as voting

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('votingSorted/', views.sort_by_name, name = 'sorted_by_name'),
    path('votingSorted/', views.sort_by_startDate, name = 'sorted_by_startDate'),
    path('votingSorted/', views.sort_by_endDate, name = 'sorted_by_endDate'),
    path('voting/<int:voting_id>', voting.voting_details, name = 'voting_details'),
    path('voting/create', voting.create_voting, name = 'create_voting'),
    path('votingList/', voting.list_voting, name = 'voting_list'),
    path('delete/voting/<int:voting_id>/', voting.delete_voting, name='delete_voting'),
]
