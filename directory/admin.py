from django.contrib import admin
from .models import SurplusListing, DemandListing, Match

admin.site.register(SurplusListing)
admin.site.register(DemandListing)
admin.site.register(Match)
