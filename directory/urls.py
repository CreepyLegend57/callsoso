# directory/urls.py
from django.urls import path
from . import views

app_name = "directory"   # ✅ ADD THIS

urlpatterns = [
    path('', views.index, name='directory_home'),

    path('surplus/', views.surplus_list, name='surplus_list'),
    path('surplus/create/', views.surplus_create, name='surplus_create'),

    path('demand/', views.demand_list, name='demand_list'),
    path('demand/create/', views.demand_create, name='demand_create'),

    path('matches/', views.match_list, name='match_list'),
    path('match/suggest/<int:surplus_id>/<int:demand_id>/', views.suggest_match, name='suggest_match'),


    # New Pages / Features
    #path('tiers/', views.tiers, name='tiers'),                   # Tiers & Pricing page
    #path('impact-tracker/', views.impact_tracker, name='impact_tracker'),
    #path('support/', views.support, name='support'),
    #path('loops/', views.loops_detail, name='loops_detail'),
]
