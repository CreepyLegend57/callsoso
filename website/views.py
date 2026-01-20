from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from collections import OrderedDict

from .models import (
    Collaboration,
    Contribution,
    FoundersList,
    Article,
    Resource,
    Category,
    MagazineIssue, 
    PopularArticle
)


# ---------------------------
# Magazine / Popular Data
# ---------------------------
MAGAZINE_ISSUES = [
    {"title": "Circular Autumn 2025", "url": "#"},
    {"title": "Circular Summer 2025", "url": "#"},
    {"title": "Circular Spring 2025", "url": "#"},
    {"title": "Circular Winter 2024", "url": "#"},
    {"title": "Circular Autumn 2024", "url": "#"},
    {"title": "Circular Summer 2024", "url": "#"},
    {"title": "Circular Spring 2024", "url": "#"},
    {"title": "Circular November/December 2023", "url": "#"},
    {"title": "Circular September/October 2023", "url": "#"},
    {"title": "Circular July/August 2023", "url": "#"},
    {"title": "Circular May/June 2023", "url": "#"},
    {"title": "Circular March/April 2023", "url": "#"},
    {"title": "Circular January/February 2023", "url": "#"},
    {"title": "Circular November/December 2022", "url": "#"},
]

POPULAR_ARTICLES = [
    {"title": "WRAP shines a spotlight on toothpaste tubes this Recycle Week", "date": "September 23, 2025", "url": "#"},
    {"title": "Encyclis to develop ‘UK’s first’ carbon capture project for EfW", "date": "September 25, 2025", "url": "#"},
    {"title": "EU adopts new rules to reduce textile and food waste", "date": "September 10, 2025", "url": "#"},
    {"title": "UK post-consumer plastic exports rely on ‘a broken system full of criminality and death’, investigation finds", "date": "September 26, 2025", "url": "#"},
]

# ---------------------------
# Home View
# ---------------------------
@login_required(login_url='login')
def home(request):
    # --- Microcopy arrays ---
    hero_microcopy = [
        "Every material has a second life.",
        "Surplus isn’t waste, it’s unrealised potential.",
        "Culture forms from what we choose to value.",
        "Circularity begins with attention.",
        "Creativity is a form of infrastructure.",
    ]

    gardens_microcopy = [
        "Ideas grow wherever they’re planted.",
        "Every material carries a history.",
        "Circularity begins with attention.",
    ]

    # --- Latest articles (News) ---
    latest_articles = (
        Article.objects
        .filter(is_published=True)
        .order_by("-published_date", "-created_at")[:3]
    )

    # --- Featured resources (from Knowledge Center system) ---
    featured_resources = (
        Resource.objects
        .filter(published=True, is_featured=True)
        .order_by("-created_at")[:3]
    )

    # --- Handle FoundersList form submission ---
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            FoundersList.objects.get_or_create(email=email)
            messages.success(request, "Thanks for joining the Call Soso founders list.")
            return redirect("home")

    context = {
        "hero_microcopy": hero_microcopy,
        "gardens_microcopy": gardens_microcopy,
        "latest_articles": latest_articles,
        "featured_resources": featured_resources,  # ✅ THIS WAS MISSING
    }

    return render(request, "website/home.html", context)




# ---------------------------
# About
# ---------------------------
@login_required(login_url='login')
def about(request):
    return render(request, 'website/about.html')

# ---------------------------
# Contact
# ---------------------------
@login_required(login_url='login')
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        organization = request.POST.get('organization')
        inquiry_type = request.POST.get('inquiry_type')
        message = request.POST.get('message')

        if email and message:
            send_mail(
                f"Contact Inquiry: {inquiry_type} from {name}",
                f"From: {name}\nEmail: {email}\nOrganization: {organization}\n\nMessage:\n{message}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully.")
            return redirect('contact')
        else:
            messages.error(request, "Please provide both your email and a message.")
    return render(request, 'website/contact.html')

# ---------------------------
# News View
# ---------------------------
@login_required(login_url='login')
def news(request):
    # Fetch all published articles
    articles_qs = Article.objects.filter(is_published=True).order_by("-published_date", "-created_at")

    # Featured and popular
    featured_articles = articles_qs.filter(is_featured=True)[:3]
    popular_articles = articles_qs[:4]

    # Pagination
    paginator = Paginator(articles_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # All categories for filter UI
    all_categories = Category.objects.all()

    context = {
        "articles": page_obj.object_list,
        "featured_articles": featured_articles,
        "popular_articles": popular_articles,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "all_categories": all_categories,
    }

    return render(request, "website/news.html", context)


# ---------------------------
# Article Detail View
# ---------------------------
@login_required(login_url='login')
def article_detail(request, slug):
    # Fetch the requested article
    article = get_object_or_404(Article, slug=slug, is_published=True)

    # Fetch related articles: same categories, exclude current article
    related_articles = Article.objects.filter(
        is_published=True,
        categories__overlap=article.categories
    ).exclude(pk=article.pk).order_by('-published_date')[:4]

    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'website/article_detail.html', context)


# ---------------------------
# Directory Home (private)
# ---------------------------
@login_required
def directory_home(request):
    return render(request, 'directory/index.html')

# ---------------------------
# Insights
# ---------------------------
@login_required(login_url='login')
def insights(request):
    """
    Insights page:
    - Groups published articles by category
    - Provides sidebar category filters
    - Provides 'popular' articles (most recent 5)
    - Uses Article.display_image property
    """

    # Fetch all published articles, newest first
    articles = Article.objects.filter(is_published=True).order_by('-published_date', '-created_at')

    # Build category → articles mapping
    categories_map = {}
    for article in articles:
        category_names = [cat.name for cat in article.categories.all()]
        if category_names:
            for category in category_names:
                categories_map.setdefault(category, []).append(article)
        else:
            categories_map.setdefault("Uncategorized", []).append(article)

    # Sort categories alphabetically
    categories_dict = OrderedDict(sorted(categories_map.items(), key=lambda item: item[0].lower()))
    categories_list = list(categories_dict.keys())

    # Popular articles: most recent 5
    popular_articles = articles[:5]

    # Ensure each article has display_image resolved
    for article in articles:
        article.display_image_url = article.display_image  # For template use

    context = {
        "categories_dict": categories_dict,   # Main grid: category -> articles
        "categories_list": categories_list,   # Sidebar filters
        "popular": popular_articles,          # Sidebar popular list
    }

    return render(request, "website/insights.html", context)


# ---------------------------
# Knowledge Center
# ---------------------------
@login_required(login_url='login')
def knowledge_center(request):
    """
    Knowledge Center:
    - Admin-managed categories
    - Separates 'Highlights' from other resources
    - Passes category IDs and names as strings for template
    """

    # Sidebar categories
    categories = Category.objects.all().order_by("name")

    # Fetch all published resources
    resources_qs = Resource.objects.filter(published=True).prefetch_related("categories").order_by("-created_at")

    highlights = []
    resources = []

    for r in resources_qs:
        cats = r.categories.all()
        resource_data = {
            "title": r.title,
            "published_date": r.created_at,
            "description": r.description,
            "link": r.link,
            "display_image": r.display_image,  # Uses model property
            "categories": [cat.name for cat in cats],
            "category_ids": [str(cat.id) for cat in cats],
        }

        if r.is_featured:
            highlights.append(resource_data)
        else:
            resources.append(resource_data)

    # Popular resources: top 5 newest
    popular_qs = resources_qs.order_by("-created_at")[:5]
    popular = [
        {
            "title": r.title,
            "published_date": r.created_at,
            "link": r.link,
        }
        for r in popular_qs
    ]

    context = {
        "categories": categories,
        "highlights": highlights,
        "resources": resources,
        "popular": popular,
    }

    return render(request, "website/knowledge_center.html", context)


# ---------------------------
# Categories
# ---------------------------
@login_required(login_url='login')
def categories(request):
    return render(request, 'website/categories.html')

# ---------------------------
# Magazine
# ---------------------------
@login_required(login_url='login')
def magazine(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    # Base queryset
    issues = MagazineIssue.objects.filter(is_published=True)

    # Filter by search
    if query:
        issues = issues.filter(title__icontains=query)

    # Filter by category
    if category_slug:
        issues = issues.filter(categories__slug=category_slug)

    # Featured vs regular
    featured_issues = issues.filter(is_featured=True)[:4]
    regular_issues = issues.exclude(id__in=[issue.id for issue in featured_issues])

    # Popular articles for sidebar
    popular_articles = PopularArticle.objects.all()[:5]

    # Categories for filter bar
    all_categories = Category.objects.all()

    context = {
        "issues": issues,
        "featured_issues": featured_issues,
        "regular_issues": regular_issues,
        "popular_articles": popular_articles,
        "search_query": query,
        "all_categories": all_categories,
        "selected_category": category_slug,
    }

    return render(request, "website/magazine.html", context)

# ---------------------------
# Signup / Login / Logout
# ---------------------------
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect('directory_home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'website/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('directory_home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'website/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# ---------------------------
# Impact Tracker / Support / Loops / Tiers
# ---------------------------
@login_required(login_url='login')
def impact_tracker(request):
    collaborations = Collaboration.objects.all().order_by('-planted_date')
    return render(request, 'website/impact_tracker.html', {'collaborations': collaborations})

@login_required(login_url='login')
def support(request):
    contributions = Contribution.objects.all().order_by('-date')
    return render(request, 'website/support.html', {'contributions': contributions})

@login_required(login_url='login')
def loops_detail(request):
    return render(request, 'website/loops.html')

@login_required(login_url='login')
def tiers(request):
    tiers_info = [
        {"title": "Creator", "description": "Access to circular community resources.", "price": "Free / $10"},
        {"title": "Business", "description": "Full directory access + features.", "price": "$50"},
        {"title": "Sponsor", "description": "Support the network & gain visibility.", "price": "$100"},
    ]
    return render(request, 'directory/tiers.html', {'tiers': tiers_info})
