from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('accounts/profile/', views.home, name='home'),
]
