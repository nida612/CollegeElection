"""election URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from college_election import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('staff_login/', views.staff_login, name='staff_login'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff_dashboard/<int:election_id>/', views.staff_election_dashboard, name='staff_election_dashboard'),
    path('election/', views.election, name='election'),
    path('approval/<int:candidate_id>/<int:app_id>/', views.candidate_approval, name='candidate_approval'),
    path('activate_election/<int:election_id>/', views.activate_election, name='activate_election'),
    path('deactivate_election/<int:election_id>/', views.deactivate_election, name='deactivate_election'),


    # student urls
    path('student_login/', views.student_login, name='student_login'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student_dashboard/<int:election_id>/', views.student_election_dashboard, name='student_election_dashboard'),
    path('register_candidate/<int:position_id>/', views.register_candidate, name='register_candidate'),
    path('submit_vote/', views.submit_vote, name='submit_vote'),

    path('logout/', views.logoutUser, name='logout'),
    path('results/<int:election_id>/', views.results, name='results'),

]
