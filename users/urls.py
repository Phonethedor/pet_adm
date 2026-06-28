from django.urls import path
from .api_views import (
    SignUpAPIView, 
    LoginAPIView, 
    LogoutAPIView, 
    UserProfileAPIView, 
    RoleListAPIView, 
    UserListAPIView
)

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='api_signup'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('me/', UserProfileAPIView.as_view(), name='api_user_profile'),
    path('roles/', RoleListAPIView.as_view(), name='api_role_list'),
    path('', UserListAPIView.as_view(), name='api_user_list'),
]