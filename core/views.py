from django.shortcuts import render

def home(request):
    """Vista principal del dashboard ejecutivo."""
    context = {
        'page_title': 'Dashboard',
        'kpis': [
            {'title': 'Total Incidentes', 'value': '1,245', 'change': '+12%', 'icon': 'fa-calendar-alt', 'color': 'blue'},
            {'title': 'Graves Hoy', 'value': '5', 'change': '-2', 'icon': 'fa-exclamation-triangle', 'color': 'red'},
            {'title': 'Velocidad Promedio', 'value': '42 km/h', 'change': '+5%', 'icon': 'fa-tachometer-alt', 'color': 'green'},
        ]
    }
    return render(request, 'core/home.html', context)
