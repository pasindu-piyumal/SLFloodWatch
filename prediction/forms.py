from django import forms

class FloodPredictionForm(forms.Form):
    rainfall_7d_mm = forms.FloatField(
        label="7-Day Rainfall (mm)", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    monthly_rainfall_mm = forms.FloatField(
        label="Monthly Rainfall (mm)", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    elevation_m = forms.FloatField(
        label="Elevation (meters)", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    distance_to_river_m = forms.FloatField(
        label="Distance to River (meters)", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    drainage_index = forms.FloatField(
        label="Drainage Index (0.0 to 1.0)", 
        min_value=0.0, 
        max_value=1.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'})
    )
    historical_flood_count = forms.IntegerField(
        label="Historical Flood Count", 
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )