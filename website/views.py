from datetime import date
from collections import OrderedDict
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
from .models import (
    Collaboration,
    Contribution,
    FoundersList,
    Article,
    Resource,
    Category,
    MagazineIssue,
    PopularArticle,
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
def home(request):
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

    latest_articles = Article.objects.filter(is_published=True).order_by("-published_date", "-created_at")[:3]
    featured_resources = Resource.objects.filter(published=True, is_featured=True).order_by("-created_at")[:3]

    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            FoundersList.objects.get_or_create(email=email)
            messages.success(request, "Thanks for joining the Call Soso founders list.")
            return redirect("website:home")

    context = {
        "hero_microcopy": hero_microcopy,
        "gardens_microcopy": gardens_microcopy,
        "latest_articles": latest_articles,
        "featured_resources": featured_resources,
    }

    return render(request, "website/home.html", context)


# ---------------------------
# About
# ---------------------------
def about(request):
    return render(request, 'website/about.html')

# ---------------------------
# Contact
# ---------------------------
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
            return redirect('website:contact')
        else:
            messages.error(request, "Please provide both your email and a message.")
    return render(request, 'website/contact.html')

# ---------------------------
# News View
# ---------------------------
def news(request):
    # Fetch all published articles
    articles_qs = Article.objects.filter(is_published=True).order_by("-published_date", "-created_at")

    # FIXED: the category filter pills in the template built a
    # ?category=<slug> URL, but this view never read or applied it —
    # clicking a category silently did nothing.
    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        articles_qs = articles_qs.filter(categories__slug=category_slug)

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
        "selected_category": category_slug,  # FIXED: template needs this to highlight the active pill
    }

    return render(request, "website/news.html", context)


# ---------------------------
# Article Detail View
# ---------------------------
def article_detail(request, slug):
    # Fetch the requested article
    article = get_object_or_404(Article, slug=slug, is_published=True)

    # Fetch related articles: same categories, exclude current article
    related_articles = Article.objects.filter(
        is_published=True,
        categories__in=article.categories.all()
    ).exclude(pk=article.pk).distinct().order_by('-published_date')[:4]

    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'website/article_detail.html', context)

# ---------------------------
# Sitewide Search
# ---------------------------
def search(request):
    """
    Single search box in the header searches across:
      - Magazine Issues (title, description)
      - Stories / Articles (title, excerpt, summary, body)
      - Services / Resources (title, description)
    Replaces the separate per-page search bars (e.g. the old Magazine
    page search) with one consistent, sitewide search experience.
    """
    query = request.GET.get("q", "").strip()

    issues = []
    articles = []
    resources = []

    if query:
        issues = (
            MagazineIssue.objects.filter(is_published=True)
            .filter(Q(title__icontains=query) | Q(description__icontains=query))
            .order_by("-published_date")[:12]
        )

        articles = (
            Article.objects.filter(is_published=True)
            .filter(
                Q(title__icontains=query)
                | Q(excerpt__icontains=query)
                | Q(summary__icontains=query)
                | Q(body__icontains=query)
            )
            .order_by("-published_date")[:12]
        )

        resources = (
            Resource.objects.filter(published=True)
            .filter(Q(title__icontains=query) | Q(description__icontains=query))
            .order_by("-created_at")[:12]
        )

    total_results = len(issues) + len(articles) + len(resources)

    context = {
        "query": query,
        "issues": issues,
        "articles": articles,
        "resources": resources,
        "total_results": total_results,
    }
    return render(request, "website/search_results.html", context)


# ---------------------------
# Directory Home (private)
# ---------------------------
@login_required(login_url=settings.LOGIN_URL)
def directory_home(request):
    return render(request, 'directory/index.html')

# ---------------------------
# Insights
# ---------------------------
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
def knowledge_center(request):
    """
    Knowledge Center

    Features
    --------
    • Category filtering (?category=slug)
    • Featured resources
    • Resource cards
    • Recently published sidebar
    """

    # ---------------------------------------
    # Categories
    # ---------------------------------------
    categories = Category.objects.all().order_by("name")

    # Selected category from URL
    selected_category = request.GET.get("category")

    # ---------------------------------------
    # Base queryset
    # ---------------------------------------
    resources_qs = (
        Resource.objects.filter(published=True)
        .prefetch_related("categories")
        .order_by("-created_at")
    )

    # Filter by category if supplied
    if selected_category:
        resources_qs = resources_qs.filter(
            categories__slug=selected_category
        ).distinct()

    # ---------------------------------------
    # Featured + Regular Resources
    # ---------------------------------------
    highlights = []
    resources = []

    for resource in resources_qs:

        category_list = list(resource.categories.all())

        resource_data = {
            "title": resource.title,
            "published_date": resource.created_at,
            "description": resource.description,
            "link": resource.link,
            "display_image": resource.display_image,
            "resource_type": resource.get_resource_type_display(),

            # template helpers
            "categories": [c.name for c in category_list],
            "category_ids": [str(c.id) for c in category_list],
            "category_slugs": [c.slug for c in category_list],
        }

        if resource.is_featured:
            highlights.append(resource_data)
        else:
            resources.append(resource_data)

    # ---------------------------------------
    # Sidebar
    # ---------------------------------------
    popular = []

    for resource in (
        Resource.objects.filter(published=True)
        .order_by("-created_at")[:5]
    ):
        popular.append({
            "title": resource.title,
            "published_date": resource.created_at,
            "link": resource.link,
        })

    # ---------------------------------------
    # Selected category name
    # ---------------------------------------
    selected_category_name = None

    if selected_category:
        category = Category.objects.filter(
            slug=selected_category
        ).first()

        if category:
            selected_category_name = category.name

    # ---------------------------------------
    # Context
    # ---------------------------------------
    context = {
        "categories": categories,

        "highlights": highlights,
        "resources": resources,
        "popular": popular,

        "selected_category": selected_category,
        "selected_category_name": selected_category_name,
    }

    return render(
        request,
        "website/knowledge_center.html",
        context,
    )


# ---------------------------
# Categories
# ---------------------------
def categories(request):
    """
    Categories hub — shows every real Category with counts of how much
    content exists under it across Stories (Articles), Services
    (Resources), and Magazine Issues, each linking into the right place.
    """
    all_categories = Category.objects.all().order_by("name")
 
    category_data = []
    for cat in all_categories:
        category_data.append({
            "category": cat,
            "story_count": cat.article_set.filter(is_published=True).count(),
            "service_count": cat.resource_set.filter(published=True).count(),
            "issue_count": cat.magazineissue_set.filter(is_published=True).count(),
        })
 
    context = {"category_data": category_data}
    return render(request, "website/categories.html", context)

# ---------------------------
# Magazine
# ---------------------------

def magazine(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    # 1. Base queryset with optimization
    issues = (
        MagazineIssue.objects.filter(is_published=True)
        .prefetch_related("categories")
        .order_by("-published_date", "-created_at")
    )

    # 2. Apply search filter if present
    if query:
        issues = issues.filter(title__icontains=query)

    # 3. Separate Featured Issues
    featured_issues = issues.filter(is_featured=True)[:4]
    regular_issues = issues.exclude(
        id__in=[issue.id for issue in featured_issues]
    )

    # 4. Determine which categories to display
    if category_slug:
        active_categories = Category.objects.filter(slug=category_slug)
    else:
        active_categories = Category.objects.all().order_by("name")

    # 5. Group regular issues into sections by Category
    issues_by_category = OrderedDict()
    for cat in active_categories:
        cat_issues = regular_issues.filter(categories=cat).distinct()
        # Display section if it has issues OR if the user explicitly clicked its filter
        if cat_issues.exists() or category_slug:
            issues_by_category[cat] = cat_issues

    # Handle uncategorized issues when viewing "All Issues"
    if not category_slug:
        uncategorized = regular_issues.filter(categories__isnull=True)
        if uncategorized.exists():
            issues_by_category["Uncategorized"] = uncategorized

    # 6. Sidebar data & metadata
    all_categories = Category.objects.all().order_by("name")
    selected_category_obj = active_categories.first() if category_slug else None
    popular_articles = PopularArticle.objects.all()[:5]

    context = {
        "featured_issues": featured_issues,
        "issues_by_category": (
            issues_by_category
        ),  # <-- Grouped sections dictionary
        "popular_articles": popular_articles,
        "search_query": query,
        "all_categories": all_categories,
        "selected_category": category_slug,
        "selected_category_name": (
            selected_category_obj.name if selected_category_obj else "All"
        ),
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
            return redirect('directory:directory_home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'website/signup.html', {'form': form})

def login_view(request):
    next_page = request.GET.get('next') or 'directory:directory_home'

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(resolve_url(next_page))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'website/login.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('website:home')

# ---------------------------
# Impact Tracker / Support / Loops / Tiers
# ---------------------------

@login_required(login_url=settings.LOGIN_URL)
def impact_tracker(request):
    collaborations = Collaboration.objects.all().order_by('-planted_date')

    # FIXED: the template needs summary.stage_1..stage_5 for the Forest Growth
    # Summary bars, but the original view never computed or passed this —
    # the bars were rendering with data-count="" (undefined), which the JS
    # parsed as NaN and multiplied into "NaNpx" widths.
    stage_counts = {row['growth_stage']: row['count'] for row in
                    Collaboration.objects.values('growth_stage').annotate(count=Count('id'))}
    summary = {f'stage_{i}': stage_counts.get(i, 0) for i in range(1, 6)}

    return render(request, 'website/impact_tracker.html', {
        'collaborations': collaborations,
        'summary': summary,
    })

@login_required(login_url=settings.LOGIN_URL)
def support(request):
    contributions = Contribution.objects.all().order_by('-date')
    return render(request, 'website/support.html', {'contributions': contributions})

@login_required(login_url=settings.LOGIN_URL)
def loops_detail(request):
    return render(request, 'website/loops.html')

@login_required(login_url=settings.LOGIN_URL)
def tiers(request):
    tiers_info = [
        {"title": "Creator", "description": "Access to circular community resources.", "price": "Free / $10"},
        {"title": "Business", "description": "Full directory access + features.", "price": "$50"},
        {"title": "Sponsor", "description": "Support the network & gain visibility.", "price": "$100"},
    ]
    return render(request, 'directory/tiers.html', {'tiers': tiers_info})
