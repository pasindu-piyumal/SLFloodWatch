from django import forms
from .models import Location

class LocationFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search", widget=forms.TextInput( attrs={"class": "form-control", "placeholder": "Search by name or district"}),)

    district = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-select"}),)

    risk_level = forms.ChoiceField(required=False, choices=[("", "Any risk level")] + Location.RISK_CHOICES, widget=forms.Select(attrs={"class": "form-select"}),)

    urban_rural = forms.ChoiceField(required=False, choices=[("", "Urban & Rural")] + Location.URBAN_RURAL_CHOICES, widget=forms.Select(attrs={"class": "form-select"}),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        districts = (Location.objects.order_by("district").values_list("district", flat=True).distinct())
        self.fields["district"].choices = [("", "All districts")] + [(d, d) for d in districts]