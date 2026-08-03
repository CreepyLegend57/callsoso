from datetime import date
from collections import OrderedDict
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.http import Http404
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
from directory.models import SurplusListing, DemandListing, Match

# ---------------------------
# The Four Loops (Switchboard)
# Shared by home, loops_detail, and loop_detail.
# Each loop carries the same rich content shape as the directory's
# Material/Edible modules: lede, pathways, ecosystem, action hub, live feed.
# ---------------------------
LOOPS = [
    {
        "number": "01",
        "slug": "material",
        "name": "The Material Loop",
        "short_name": "Material",
        "icon": "fa-recycle",
        "image": "images/loop-material.jpg",
        "description": "Corporate surplus becomes creative potential. We divert materials before they become waste, redirecting them to makers, designers, and builders.",
        "lede": "Surplus becomes structure, substance, and new cultural value. Materials are treated as data, story, and infrastructure for an imaginative economy. Nothing is static. Everything circulates.",
        "cta_label": "Explore the Material Loop",
        "cta_url_name": "website:loop_detail",
        "highlighted": False,
        "live_feed": "surplus",
        "pathways": [
            ("Creative Reuse & Fabrication", "Installations, artworks, prototypes, furniture, and spatial elements."),
            ("Industrial Reprocessing", "Reprocessed materials, internal reuse streams, and cost-saving alternatives."),
            ("Education & Workshops", "Youth programmes, corporate team days, and skill-building labs."),
            ("Material Intelligence", "University R&D, product design studies, and material testing."),
        ],
        "ecosystem": [
            ("Businesses", "Reduce waste overheads and improve measurable ESG metrics."),
            ("Creators & Makers", "Source affordable materials and prototype scalable ideas."),
            ("Built Environment Teams", "Access unique finishes and offcuts for architectural builds."),
            ("Councils & Sponsors", "Fund and monitor regional circular economy impact."),
        ],
        "actions": [
            {"label": "Browse Surplus", "url_name": "website:browse", "primary": True},
            {"label": "List Your Surplus", "url_name": "directory:surplus_create"},
            {"label": "Post a Demand", "url_name": "directory:demand_create"},
        ],
    },
    {
        "number": "02",
        "slug": "edible",
        "name": "The Edible Loop",
        "short_name": "Edible",
        "icon": "fa-leaf",
        "image": "images/loop-edible.jpg",
        "description": "Food surplus becomes nourishment. We close the loop on edible waste, redirecting it back into the community before it's lost.",
        "lede": "Food becomes flavour, fuel, material, and future infrastructure. We treat food as material intelligence capable of nourishment, creativity, bio-production, and scientific transformation. Nothing is just waste. Everything has a next life.",
        "cta_label": "Explore the Edible Loop",
        "cta_url_name": "website:loop_detail",
        "highlighted": False,
        "live_feed": "demand",
        "pathways": [
            ("Culinary Play & Pop-ups", "Experimental menus, food art, pop-up kitchens, and edible installations."),
            ("Civic Nourishment", "Safe community meals, cooking literacy workshops, and youth access."),
            ("Biomaterial Innovation", "Bioplastics, organic dyes, natural pigments, compost, and fermentation substrates."),
            ("Circular Research", "Experimental kitchens prototyping sustainable packaging and food futures."),
        ],
        "ecosystem": [
            ("Food Businesses", "Save disposal costs and support ethical, circular redistribution."),
            ("Chefs & Creatives", "Source experimental ingredients and collaborative R&D space."),
            ("Community Partners", "Secure consistent ingredients for teaching, cooking, and preserving."),
            ("Scientific Researchers", "Experiment with biomaterial extraction and waste transformation."),
        ],
        "actions": [
            {"label": "Browse Food Surplus", "url_name": "website:browse", "primary": True},
            {"label": "Add Food Surplus", "url_name": "directory:surplus_create"},
            {"label": "Request Ingredients", "url_name": "directory:demand_create"},
        ],
    },
    {
        "number": "03",
        "slug": "strategic",
        "name": "The Strategic Loop",
        "short_name": "Strategic",
        "icon": "fa-chart-line",
        "image": "images/loop-strategy.jpg",
        "description": "For businesses ready to act. We audit surplus and waste streams, uncovering where your organisation's circularity — and cost savings — actually live.",
        "lede": "Realizing and diverting your Scope 3. We map your surplus and waste streams, then turn them into procurement savings, ESG wins, and funded circular programmes.",
        "cta_label": "Get an Audit",
        "cta_url_name": "website:contact",
        "highlighted": True,
        "live_feed": "resources",
        "pathways": [
            ("Circular Strategy", "Audits and roadmaps that locate circularity inside your business model."),
            ("Scope 3 Reduction", "Quantified diversion of your value chain's emissions and waste."),
            ("Circular Procurement", "Buying frameworks that prioritise reuse, repair, and regeneration."),
            ("Corporate Membership", "Tiered partnerships with custom activations and impact reporting."),
        ],
        "ecosystem": [
            ("Corporates", "Turn sustainability commitments into measurable, funded action."),
            ("ESG & Procurement Leads", "Credible data and reporting for your board and investors."),
            ("Councils & Public Bodies", "Meet net-zero and social value targets through local loops."),
            ("Investors & Sponsors", "Fund regional circular infrastructure with tracked outcomes."),
        ],
        "actions": [
            {"label": "Get an Audit", "url_name": "website:contact", "primary": True},
            {"label": "Explore Membership", "url_name": "website:tiers"},
            {"label": "Start a Conversation", "url_name": "website:contact"},
        ],
    },
    {
        "number": "04",
        "slug": "cultural",
        "name": "The Cultural Loop",
        "short_name": "Cultural",
        "icon": "fa-people-group",
        "image": "images/loop-culture.jpg",
        "description": "Circularity is a culture, not just a system. We work with teams and communities to build the behaviours that make the other loops last.",
        "lede": "Culture forms from what we choose to value. We build the behaviours, rituals, and creative habits that make every other loop last.",
        "cta_label": "Join the Pulse",
        "cta_url_name": "signup",
        "highlighted": False,
        "live_feed": "collaborations",
        "pathways": [
            ("Creative Projects", "Commissions, residencies, and installations built from surplus."),
            ("Makers & Networks", "Connecting artists, designers, and craftspeople with materials."),
            ("Cultural Activations", "Exhibitions, events, and public programming that shift perception."),
            ("Community Building", "Workshops and rituals that embed circular behaviour locally."),
        ],
        "ecosystem": [
            ("Artists & Makers", "Source materials and build work with cultural weight."),
            ("Cultural Institutions", "Programmes, exhibitions, and civic commissions."),
            ("Schools & Youth", "Learning experiences that normalise circular habits."),
            ("Communities", "Shared projects, skills, and local ownership."),
        ],
        "actions": [
            {"label": "Join the Pulse", "url_name": "signup", "primary": True},
            {"label": "Propose a Project", "url_name": "website:contact"},
            {"label": "Track Impact", "url_name": "website:impact_tracker"},
        ],
    },
]

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
        "loops": LOOPS,
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
# Public Marketplace (Browse)
# ---------------------------
def browse(request):
    """
    Public marketplace. Lists approved surplus and demand listings.
    No login required. Data lives in the directory app.
    """
    material_type = request.GET.get("material_type", "").strip()
    location = request.GET.get("location", "").strip()

    surpluses = SurplusListing.objects.filter(approved=True).order_by("-created_on")
    demands = DemandListing.objects.filter(approved=True).order_by("-created_on")

    if material_type:
        surpluses = surpluses.filter(material_type=material_type)
        demands = demands.filter(material_wanted=material_type)

    if location:
        surpluses = surpluses.filter(location__icontains=location)
        demands = demands.filter(location__icontains=location)

    context = {
        "surpluses": surpluses,
        "demands": demands,
        "material_type": material_type,
        "location": location,
        "total_listings": surpluses.count() + demands.count(),
    }
    return render(request, "website/browse.html", context)


# ---------------------------
# Insights
# ---------------------------
def insights(request):
    """
    Stories page — the merged home for both editorial stories (Articles)
    and knowledge resources (Resources / "Services").

    Unified, date-sorted feed with two filter axes:
      • ?type=all|stories|resources  — what kind of content
      • ?category=slug               — which category

    Replaces the old separate Insights + Knowledge Center pages.
    """

    # Categories, annotated with live combined counts
    categories = Category.objects.annotate(
        story_count=Count("article", filter=Q(article__is_published=True), distinct=True),
        resource_count=Count("resource", filter=Q(resource__published=True), distinct=True),
    ).order_by("name")

    selected_type = request.GET.get("type", "all")
    if selected_type not in ("all", "stories", "resources"):
        selected_type = "all"
    selected_category = request.GET.get("category")

    # Base querysets
    articles_qs = Article.objects.filter(is_published=True).order_by(
        "-published_date", "-created_at"
    )
    resources_qs = Resource.objects.filter(published=True).prefetch_related(
        "categories"
    ).order_by("-created_at")

    if selected_category:
        articles_qs = articles_qs.filter(categories__slug=selected_category).distinct()
        resources_qs = resources_qs.filter(categories__slug=selected_category).distinct()

    # Build a single date-sorted feed of items
    items = []
    if selected_type in ("all", "stories"):
        for a in articles_qs:
            cats = list(a.categories.all())
            items.append({
                "kind": "story",
                "kind_label": "Story",
                "title": a.title,
                "date": a.published_date or a.created_at.date(),
                "category": cats[0].name if cats else "",
                "image": a.display_image,
                "excerpt": a.excerpt or a.summary or a.body,
                "url": a.get_absolute_url(),
                "target": False,
            })
    if selected_type in ("all", "resources"):
        for r in resources_qs:
            cats = list(r.categories.all())
            items.append({
                "kind": "resource",
                "kind_label": r.get_resource_type_display(),
                "title": r.title,
                "date": r.created_at.date(),
                "category": cats[0].name if cats else "",
                "image": r.display_image,
                "excerpt": r.description,
                "url": r.link or "#",
                "target": bool(r.link),
            })
    items.sort(key=lambda item: item["date"], reverse=True)

    # Popular / recently published sidebar — top 6 of the combined feed
    popular = []
    combined_popular = []
    for a in Article.objects.filter(is_published=True).order_by(
        "-published_date", "-created_at"
    )[:6]:
        combined_popular.append({
            "title": a.title,
            "date": a.published_date or a.created_at.date(),
            "url": a.get_absolute_url(),
        })
    for r in Resource.objects.filter(published=True).order_by("-created_at")[:6]:
        combined_popular.append({
            "title": r.title,
            "date": r.created_at.date(),
            "url": r.link or "#",
        })
    combined_popular.sort(key=lambda item: item["date"], reverse=True)
    popular = combined_popular[:6]

    selected_category_name = None
    if selected_category:
        cat = Category.objects.filter(slug=selected_category).first()
        if cat:
            selected_category_name = cat.name

    context = {
        "categories": categories,
        "items": items,
        "popular": popular,
        "selected_type": selected_type,
        "selected_category": selected_category,
        "selected_category_name": selected_category_name,
    }

    return render(request, "website/insights.html", context)


# ---------------------------
# Knowledge Center — merged into Stories; keep the old URL as a redirect
# ---------------------------
def knowledge_center(request):
    """
    Legacy route. Services / Knowledge Center content was merged into the
    unified Stories page; keep /knowledge/ working by redirecting to it.
    """
    return redirect("website:insights")


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


def loops_detail(request):
    """
    The four loops — Material, Edible, Strategic, Cultural — as a public
    hub page. Renders the loop selector cards linking to each loop's
    dedicated landing page.
    """
    return render(request, "website/loops.html", {"loops": LOOPS})


def loop_detail(request, slug):
    """
    A single loop landing page. Reuses the same rich content shape as the
    directory's Material/Edible modules (lede, pathways, ecosystem, action
    hub) plus a live feed of relevant, approved activity.
    """
    loop = next((l for l in LOOPS if l["slug"] == slug), None)
    if loop is None:
        raise Http404("Loop not found")

    feed_label = ""
    feed_items = []

    if loop["live_feed"] == "surplus":
        feed_label = "Recently Listed"
        feed_items = [
            {"name": s.company, "detail": s.get_material_type_display()}
            for s in SurplusListing.objects.filter(approved=True).order_by("-created_on")[:5]
        ]
    elif loop["live_feed"] == "demand":
        feed_label = "Recently Requested"
        feed_items = [
            {"name": d.organisation or "Anonymous", "detail": d.get_material_wanted_display()}
            for d in DemandListing.objects.filter(approved=True).order_by("-created_on")[:5]
        ]
    elif loop["live_feed"] == "resources":
        feed_label = "Recent Services"
        feed_items = [
            {"name": r.title, "detail": r.get_resource_type_display()}
            for r in Resource.objects.filter(published=True).order_by("-created_at")[:5]
        ]
    elif loop["live_feed"] == "collaborations":
        feed_label = "The Forest"
        feed_items = [
            {"name": c.name, "detail": f"Stage {c.growth_stage} — {c.get_growth_stage_display()}"}
            for c in Collaboration.objects.filter(is_active=True).order_by("-planted_date")[:5]
        ]

    other_loops = [l for l in LOOPS if l["slug"] != slug]

    context = {
        "loop": loop,
        "other_loops": other_loops,
        "feed_label": feed_label,
        "feed_items": feed_items,
    }
    return render(request, "website/loop_detail.html", context)


def city(request):
    """
    "Make the city a partner." Public network page showing the live circular
    economy as a city: locations as nodes, materials flowing between surplus
    and demand, and matched routes. Everything is derived from approved data.
    """
    from collections import OrderedDict

    surpluses = SurplusListing.objects.filter(approved=True)
    demands = DemandListing.objects.filter(approved=True)

    # ---- Resource flow: which materials are circulating? ----
    choices = SurplusListing.MATERIAL_CHOICES
    flow = []
    for value, label in choices:
        s = surpluses.filter(material_type=value).count()
        d = demands.filter(material_wanted=value).count()
        if s or d:
            flow.append({"value": value, "label": label, "surplus": s, "demand": d})

    # ---- City nodes: every location with activity ----
    node_map = OrderedDict()

    def add(location, key):
        loc = location.strip() or "Unlisted"
        node = node_map.setdefault(
            loc,
            {"name": loc, "surplus": 0, "demand": 0, "count": 0, "materials": set()},
        )
        node[key] += 1
        node["count"] += 1

    for s in surpluses:
        add(s.location, "surplus")
        node_map[s.location.strip() or "Unlisted"]["materials"].add(s.get_material_type_display())
    for d in demands:
        add(d.location, "demand")
        node_map[d.location.strip() or "Unlisted"]["materials"].add(d.get_material_wanted_display())

    nodes = []
    for node in node_map.values():
        node["materials"] = sorted(node["materials"])
        nodes.append(node)
    nodes.sort(key=lambda n: n["count"], reverse=True)

    total_surplus = surpluses.count()
    total_demand = demands.count()
    total_matches = Match.objects.count()

    # Deterministic scatter positions for the map canvas (stable per name)
    import hashlib

    def scatter(name, i):
        digest = hashlib.md5(name.encode()).digest()
        x = 8 + (digest[0] % 84)
        y = 10 + (digest[1] % 74)
        return x, y

    for i, node in enumerate(nodes):
        node["x"], node["y"] = scatter(node["name"], i)
        node["radius"] = 5 + min(14, node["count"])

    context = {
        "flow": flow,
        "nodes": nodes,
        "total_surplus": total_surplus,
        "total_demand": total_demand,
        "total_matches": total_matches,
        "total_nodes": len(nodes),
    }
    return render(request, "website/city.html", context)

@login_required(login_url=settings.LOGIN_URL)
def tiers(request):
    tiers_info = [
        {"title": "Creator", "description": "Access to circular community resources.", "price": "Free / $10"},
        {"title": "Business", "description": "Full directory access + features.", "price": "$50"},
        {"title": "Sponsor", "description": "Support the network & gain visibility.", "price": "$100"},
    ]
    return render(request, 'directory/tiers.html', {'tiers': tiers_info})
