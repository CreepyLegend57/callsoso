from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
    Shows counts for Material & Edible Loops.
    """
    surplus_count = SurplusListing.objects.count()
    demand_count = DemandListing.objects.count()
    # Optionally preview latest items
    latest_surpluses = SurplusListing.objects.order_by('-created_on')[:5]
    latest_demands = DemandListing.objects.order_by('-created_on')[:5]

    return render(request, 'directory/index.html', {
        'surplus_count': surplus_count,
        'demand_count': demand_count,
        'latest_surpluses': latest_surpluses,
        'latest_demands': latest_demands,
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
            return redirect('surplus_list')
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
            Q(org__icontains=query) |
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
            return redirect('demand_list')
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
    Match.objects.create(surplus=surplus, demand=demand, suggested_by=request.user)

    # Send notification emails (silent fail)
    send_mail(
        subject="Call Soso: Potential Match Found!",
        message=f"A match has been suggested between surplus from {surplus.company} and demand from {demand.org}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[surplus.contact_email, demand.user.email],
        fail_silently=True,
    )
    return redirect('match_list')


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
            Q(surplus__user=request.user) | Q(demand__user=request.user)
        )
    return render(request, 'directory/match_list.html', {'matches': matches})
