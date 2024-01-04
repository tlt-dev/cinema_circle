"""
URL configuration for cinema_circle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cinema_circle/', views.index, name='index'),
    path('cinema_circle/register', views.register_page, name='register_page'),
    path('cinema_circle/login', views.login_page, name='login_page'),
    path('cinema_circle/recommendations', views.login, name='login'),
    path('cinema_circle/recommendations', views.recommendations, name='recommendations'),
    path('cinema_circle/movies/<str:id>', views.movie_details, name='movie_details'),
    path('cinema_cirlce/user/<str:id>', views.get_user, name='view_user_page'),
    path('cinema_circle/movies/<str:id>/reviews/add', views.add_review, name='add_review'),
    path('cinema_circle/user/recommanded_users', views.get_recommanded_users, name='get_recommanded_users'),
    path('cinema_circle/user/profile', views.get_user_profile, name='get_user_profile'),
]
