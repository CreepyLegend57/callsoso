from django.db import models
from django.contrib.auth.models import User


# ================================
# Surplus Listings (Materials / Food)
# ================================
class SurplusListing(models.Model):
    MATERIAL_CHOICES = [
        ("wood", "Wood"),
        ("metal", "Metal"),
        ("textiles", "Textiles"),
        ("plastic", "Plastic"),
        ("foam", "Foam"),
        ("cardboard", "Cardboard"),
        ("food", "Food"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="surplus_listings"
    )

    company = models.CharField(max_length=150)
    location = models.CharField(max_length=150)

    material_type = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    description = models.TextField(blank=True, help_text="Optional details about the material (condition, packaging, etc.)")
    monthly_volume = models.DecimalField(max_digits=10, decimal_places=2, help_text="Estimated monthly surplus volume")
    is_food_safe = models.BooleanField(default=False, help_text="Only required if material type is food")
    contact_email = models.EmailField()

    approved = models.BooleanField(default=False, help_text="Admin approval before appearing publicly")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Surplus Listing"
        verbose_name_plural = "Surplus Listings"

    def __str__(self):
        return f"{self.company} – {self.material_type}"


# ================================
# Demand Listings (Requests / Use Cases)
# ================================
class DemandListing(models.Model):
    MATERIAL_CHOICES = SurplusListing.MATERIAL_CHOICES

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="demand_listings"
    )

    organisation = models.CharField(max_length=150, blank=True, null=True, help_text="Organisation or individual requesting material")
    location = models.CharField(max_length=150)

    material_wanted = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    quantity_needed = models.DecimalField(max_digits=10, decimal_places=2)
    intended_use = models.TextField(blank=True, null=True, help_text="Describe how the material will be used")
    approved = models.BooleanField(default=False, help_text="Admin approval before appearing publicly")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Demand Listing"
        verbose_name_plural = "Demand Listings"

    def __str__(self):
        return f"{self.organisation or 'Anonymous'} needs {self.material_wanted}"


# ================================
# Matches (Surplus ↔ Demand)
# ================================
class Match(models.Model):
    surplus = models.ForeignKey(SurplusListing, on_delete=models.CASCADE, related_name="matches")
    demand = models.ForeignKey(DemandListing, on_delete=models.CASCADE, related_name="matches")
    suggested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Admin or system user who suggested the match")
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about this match")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("surplus", "demand")
        ordering = ["-created_on"]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.surplus.company} → {self.demand.organisation or 'Requester'}"
