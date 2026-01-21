# website/urls.py
from django.urls import path
from . import views

app_name = "website"   # ✅ ADD THIS (does NOT break anything)

urlpatterns = [
    # Core pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # News / Articles
    path('news/', views.news, name='news'),
    path('news/<slug:slug>/', views.article_detail, name='article_detail'),

    # Content
    path('insights/', views.insights, name='insights'),
    path('knowledge/', views.knowledge_center, name='knowledge'),
    path('categories/', views.categories, name='categories'),
    path('magazine/', views.magazine, name='magazine'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Features
    path('impact-tracker/', views.impact_tracker, name='impact_tracker'),
    path('support/', views.support, name='support'),
    path('loops/', views.loops_detail, name='loops_detail'),
    path('tiers/', views.tiers, name='tiers'),
]
