from django.urls import path
from django.contrib.auth.decorators import login_required
from users import views as v1

urlpatterns = [
    path('', v1.users_list, name = 'users'),
    path('delete/<int:user_id>', v1.users_delete, name = 'delete_user'),
    path('<int:user_id>', v1., name = 'update_user'),
]
