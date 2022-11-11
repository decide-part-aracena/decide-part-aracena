from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView, magic_link_via_email, authenticate_via_magic_link


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('magic-login/', magic_link_via_email, name='magic_login'),
    path('magic-link/<str:token>', authenticate_via_magic_link, name='magic_link')
]
