# pages/urls.py
from django.urls import path
from .views import (
    AboutView,
    RulesView,
    SignUpView,
    EditProfileView,
    ProfileView
)

app_name = 'pages'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('rules/', RulesView.as_view(), name='rules'),
    path('auth/registration/', SignUpView.as_view(), name='signup'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
]
