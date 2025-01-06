from django.shortcuts import render
from dashboard.utils import role_required

@role_required(['distributor'])
def distributor_dashboard(request):
    return render(request, 'distributor_dashboard/dashboard.html')



def pin_entry(request):
    """
    View for managing PIN entry.
    """
    return render(request, 'admin_dashboard/pin_entry.html')
