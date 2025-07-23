from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('matiere/<int:matiere_id>/chapitres/', views.chapitres_par_matiere, name='chapitres'),
    path('chapitre/<int:chapitre_id>/cours/', views.cours_detail, name='cours_detail'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
]

