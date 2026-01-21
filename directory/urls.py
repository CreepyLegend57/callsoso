from django.urls import path
from . import views

app_name = "directory"

urlpatterns = [
    path('', views.index, name='directory_home'),  # Main dashboard

    # Surplus
    path('surplus/', views.surplus_list, name='surplus_list'),
    path('surplus/create/', views.surplus_create, name='surplus_create'),

    # Demand
    path('demand/', views.demand_list, name='demand_list'),
    path('demand/create/', views.demand_create, name='demand_create'),

    # Matches
    path('matches/', views.match_list, name='match_list'),
    path('match/suggest/<int:surplus_id>/<int:demand_id>/', views.suggest_match, name='suggest_match'),
]
