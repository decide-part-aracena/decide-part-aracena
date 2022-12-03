from django.urls import path, re_path
from . import views
from . import views as voting
from django.urls import include

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('sortedByName/', views.sort_by_name, name = 'sorted_by_name'),
    path('sortedByStartDate/', views.sort_by_startDate, name = 'sorted_by_startDate'),
    path('sortedByEndDate/', views.sort_by_endDate, name = 'sorted_by_endDate'),
    path('voting/<int:voting_id>', voting.voting_details, name = 'voting_details'),
    path('voting/create', voting.create_voting, name = 'create_voting'),
    path('votingList/', voting.list_voting, name = 'voting_list'),
    path('delete/voting/<int:voting_id>/', voting.delete_voting, name='delete_voting'),
    path('start/voting/<int:voting_id>/', voting.start_voting, name='start_voting'),
    path('stop/voting/<int:voting_id>/', voting.stop_voting, name='stop_voting'),
    re_path(r'^question/(?P<pk>\d+)/delete', views.QuestionDelete.as_view(), name='delete_question'),
  
]
