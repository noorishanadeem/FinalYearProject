from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def student_dashboard(request):
    return HttpResponse("Student Dashboard")

@login_required
def instructor_dashboard(request):
    return HttpResponse("Instructor Dashboard")

@login_required
def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")
