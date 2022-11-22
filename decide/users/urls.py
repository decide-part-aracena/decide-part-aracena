from django.urls import path
from . import views

urlpatterns = [
    path('', views.users_list, name = 'users'),
    path('delete/<int:user_id>', views.users_delete, name = 'delete_user'),
    path('<int:user_id>', views.users_details, name = 'update_user'),
]