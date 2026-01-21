from django.urls import path
from . import views

app_name = "website"  # Keep this for your main website pages

# Core + namespaced pages
urlpatterns = [
    # Core pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # News / Articles
    path('news/', views.news, name='news'),
    path('news/<slug:slug>/', views.article_detail, name='article_detail'),

    # Content / Knowledge
    path('insights/', views.insights, name='insights'),
    path('knowledge/', views.knowledge_center, name='knowledge'),
    path('categories/', views.categories, name='categories'),
    path('magazine/', views.magazine, name='magazine'),

    # Features (some render templates in directory app, but routed via website)
    path('impact-tracker/', views.impact_tracker, name='impact_tracker'),
    path('support/', views.support, name='support'),
    path('loops/', views.loops_detail, name='loops_detail'),
    path('tiers/', views.tiers, name='tiers'),
]

# Auth URLs (outside namespace for simplicity)
auth_urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
