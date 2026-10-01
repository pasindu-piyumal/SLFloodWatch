from django.shortcuts import render
from .riverwatch import save_riverwatch_readings

def river_levels(request):
    readings = save_riverwatch_readings()
    return render(request, 'river_monitor/river_levels.html', {
        'readings': readings
    })
