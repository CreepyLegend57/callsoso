from django.contrib import admin
from .models import SurplusListing, DemandListing, Match


@admin.register(SurplusListing)
class SurplusListingAdmin(admin.ModelAdmin):
    list_display = ("company", "material_type", "monthly_volume", "location", "approved", "created_on")
    list_display_links = ("company",)
    list_editable = ("approved",)
    list_filter = ("material_type", "approved", "is_food_safe")
    search_fields = ("company", "location", "contact_email")
    date_hierarchy = "created_on"


@admin.register(DemandListing)
class DemandListingAdmin(admin.ModelAdmin):
    list_display = ("organisation", "material_wanted", "quantity_needed", "location", "approved", "created_on")
    list_display_links = ("organisation",)
    list_editable = ("approved",)
    list_filter = ("material_wanted", "approved")
    search_fields = ("organisation", "location")
    date_hierarchy = "created_on"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("surplus", "demand", "suggested_by", "created_on")
    search_fields = ("surplus__company", "demand__organisation")
    date_hierarchy = "created_on"