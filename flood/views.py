from django.shortcuts import render, get_object_or_404
import json 
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Location, FloodRecord, FloodAlert
from .forms import LocationFilterForm

@login_required
def dashboard(request):
    locations = Location.objects.all()

    risk_counts = {
        'low': locations.filter(current_risk_level=Location.RISK_LOW).count(),
        'medium': locations.filter(current_risk_level=Location.RISK_MEDIUM).count(),
        'high': locations.filter(current_risk_level=Location.RISK_HIGH).count()
    }

    recent_alerts = FloodAlert.objects.filter(is_active=True).select_related("location")[:8]
    recent_records = FloodRecord.objects.select_related("location").order_by("-date")[:8]
    high_risk_locations = locations.filter(current_risk_level=Location.RISK_HIGH)[:6]

    district_counts = (
        locations.values('district').annotate(total=Count('id')).order_by('-total')[:8]
    )

    context = {
        "total_locations": locations.count(),
        "risk_counts": risk_counts,
        "recent_alerts": recent_alerts,
        "recent_records": recent_records,
        "high_risk_locations": high_risk_locations,
        "district_counts": district_counts,
    }

    return render(request, "flood/dashboard.html", context)

@login_required
def locations(request):
    form = LocationFilterForm(request.GET or None)
    queryset = Location.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        district = form.cleaned_data.get('district')
        risk_level = form.cleaned_data.get('risk_level')
        urban_rural = form.cleaned_data.get('urban_rural')

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(district__icontains=q))
        if district:
            queryset = queryset.filter(district=district)
        if risk_level:
            queryset = queryset.filter(current_risk_level=risk_level)
        if urban_rural:
            queryset = queryset.filter(urban_rural=urban_rural)

    queryset = queryset.annotate(record_count=Count('records'))[':500']

    context = {
        'form': form,
        'locations': queryset
    }
    return render(request, 'flood/locations.html', context)

@login_required
def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    records = location.records.all()[:30]
    alerts = location.alerts.filter(is_active=True)

    chart_labels = [r.date.strftime("%Y-%m-%d") for r in reversed(records)]
    chart_rainfall = [r.monthly_rainfall_mm for r in reversed(records)]
    chart_risk_score = [r.flood_risk_score for r in reversed(records)]

    context = {
        'location': location,
        'records': records,
        'alerts': alerts,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_rainfall_json': json.dumps(chart_rainfall),
        'chart_risk_score_json': json.dumps(chart_risk_score),
    }
    return render(request, 'flood/location_detail.html', context)