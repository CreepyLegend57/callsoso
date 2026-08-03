from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import SurplusListing, DemandListing, Match
from .forms import SurplusListingForm, DemandListingForm
from django.core.mail import send_mail
from django.conf import settings

# ===============================
# Directory Homepage
# ===============================
@login_required
def index(request):
    """
    Directory landing page.
    Shows counts for Material & Edible Loops, latest listings,
    and suggested matches for the logged-in user.
    """
    surplus_count = SurplusListing.objects.count()
    demand_count = DemandListing.objects.count()
    latest_surpluses = SurplusListing.objects.order_by('-created_on')[:5]
    latest_demands = DemandListing.objects.order_by('-created_on')[:5]

    # Strategic + Cultural loop telemetry for the dashboard modules
    from website.models import Collaboration, Resource
    active_collaborations = Collaboration.objects.filter(is_active=True).count()
    featured_services = Resource.objects.filter(published=True, is_featured=True).count()

    # ---- Unique to the directory: the member's own exchange ----
    my_surpluses = SurplusListing.objects.filter(user=request.user)[:6]
    my_demands = DemandListing.objects.filter(user=request.user)[:6]

    my_listing_ids = (
        list(SurplusListing.objects.filter(user=request.user).values_list('id', flat=True))
        + list(DemandListing.objects.filter(user=request.user).values_list('id', flat=True))
    )
    my_matches = (
        Match.objects.filter(
            Q(surplus_id__in=my_listing_ids) | Q(demand_id__in=my_listing_ids)
        )[:5]
        if my_listing_ids
        else Match.objects.none()
    )

    # Suggested matches: pair the user's surplus with approved demands that
    # want that material, and the user's demands with approved surpluses
    # offering that material. Skip pairs that are already a Match.
    candidates = []
    seen = set()

    user_surpluses = list(
        SurplusListing.objects.filter(user=request.user).only('id', 'material_type')
    )
    user_demands = list(
        DemandListing.objects.filter(user=request.user).only('id', 'material_wanted')
    )

    if user_surpluses:
        wanted_types = {s.material_type for s in user_surpluses}
        for d in (
            DemandListing.objects.filter(
                approved=True,
                material_wanted__in=wanted_types,
            )
            .exclude(user=request.user)
            .only('id', 'material_wanted')
        ):
            for s in (s for s in user_surpluses if s.material_type == d.material_wanted):
                candidates.append({'surplus': s, 'demand': d})

    if user_demands:
        offered_types = {d.material_wanted for d in user_demands}
        for s in (
            SurplusListing.objects.filter(
                approved=True,
                material_type__in=offered_types,
            )
            .exclude(user=request.user)
            .only('id', 'material_type')
        ):
            for d in (d for d in user_demands if d.material_wanted == s.material_type):
                candidates.append({'surplus': s, 'demand': d})

    match_suggestions = []
    for c in candidates:
        key = (c['surplus'].id, c['demand'].id)
        if key in seen:
            continue
        seen.add(key)
        if Match.objects.filter(surplus=c['surplus'], demand=c['demand']).exists():
            continue
        match_suggestions.append(c)

    return render(request, 'directory/index.html', {
        'surplus_count': surplus_count,
        'demand_count': demand_count,
        'latest_surpluses': latest_surpluses,
        'latest_demands': latest_demands,
        'match_suggestions': match_suggestions,
        'active_collaborations': active_collaborations,
        'featured_services': featured_services,
        'my_surpluses': my_surpluses,
        'my_demands': my_demands,
        'my_matches': my_matches,
    })


# ===============================
# Surplus Listings & Create
# ===============================
@login_required
def surplus_list(request):
    """
    List the logged-in user's surplus listings with search & filters.
    """
    query = request.GET.get('q', '')
    material_type = request.GET.get('material_type', '')
    location = request.GET.get('location', '')

    listings = SurplusListing.objects.filter(user=request.user)

    if query:
        listings = listings.filter(
            Q(company__icontains=query) |
            Q(material_type__icontains=query)
        )
    if material_type:
        listings = listings.filter(material_type=material_type)
    if location:
        listings = listings.filter(location__icontains=location)

    return render(request, 'directory/surplus_list.html', {
        'surpluses': listings,
        'query': query,
        'material_type': material_type,
        'location': location,
    })


@login_required
def surplus_create(request):
    """
    Create a new surplus listing.
    """
    if request.method == 'POST':
        form = SurplusListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return redirect('directory:surplus_list')  # FIXED: was missing the 'directory:' namespace
    else:
        form = SurplusListingForm()
    return render(request, 'directory/surplus_form.html', {'form': form})


# ===============================
# Demand Listings & Create
# ===============================
@login_required
def demand_list(request):
    """
    List the logged-in user's demand listings with search & filters.
    """
    query = request.GET.get('q', '')
    material_wanted = request.GET.get('material_wanted', '')
    location = request.GET.get('location', '')

    listings = DemandListing.objects.filter(user=request.user)

    if query:
        listings = listings.filter(
            Q(organisation__icontains=query) |  # FIXED: model field is 'organisation', not 'org'
            Q(material_wanted__icontains=query)
        )
    if material_wanted:
        listings = listings.filter(material_wanted=material_wanted)
    if location:
        listings = listings.filter(location__icontains=location)

    return render(request, 'directory/demand_list.html', {
        'demands': listings,
        'query': query,
        'material_wanted': material_wanted,
        'location': location,
    })


@login_required
def demand_create(request):
    """
    Create a new demand listing.
    """
    if request.method == 'POST':
        form = DemandListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return redirect('directory:demand_list')  # FIXED: was missing the 'directory:' namespace
    else:
        form = DemandListingForm()
    return render(request, 'directory/demand_form.html', {'form': form})


# ===============================
# Matches
# ===============================
@login_required
def suggest_match(request, surplus_id, demand_id):
    """
    Suggest a match between a surplus and a demand.
    Sends notification emails.
    """
    surplus = get_object_or_404(SurplusListing, pk=surplus_id)
    demand = get_object_or_404(DemandListing, pk=demand_id)
    match, created = Match.objects.get_or_create(
        surplus=surplus,
        demand=demand,
        defaults={'suggested_by': request.user},
    )
    if not created:
        messages.info(request, "That match was already suggested.")
        return redirect('directory:match_list')

    # Send notification emails (silent fail)
    send_mail(
        subject="Call Soso: Potential Match Found!",
        message=f"A match has been suggested between surplus from {surplus.company} and demand from {demand.organisation}.",  # FIXED: was demand.org
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[surplus.contact_email, demand.user.email],
        fail_silently=True,
    )
    return redirect('directory:match_list')  # FIXED: was missing the 'directory:' namespace


@login_required
def match_list(request):
    """
    List matches visible to the user.
    Admins see all matches.
    """
    if request.user.is_staff:
        matches = Match.objects.all()
    else:
        matches = Match.objects.filter(
            Q(surplus__user=request.user)
            | Q(demand__user=request.user)
            | Q(surplus__approved=True)
            | Q(demand__approved=True)
        )
    matches = matches.select_related('surplus', 'demand', 'suggested_by')
    return render(request, 'directory/match_list.html', {'matches': matches})