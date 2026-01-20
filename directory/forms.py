from django import forms
from .models import SurplusListing, DemandListing

class SurplusListingForm(forms.ModelForm):
    class Meta:
        model = SurplusListing
        exclude = ['user']

class DemandListingForm(forms.ModelForm):
    class Meta:
        model = DemandListing
        exclude = ['user']
