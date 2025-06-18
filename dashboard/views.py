from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from bookings.models import Booking
from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from bookings.forms import BookingForm

from django.http import JsonResponse
from django.core.serializers import serialize
from bookings.models import Booking

from django.contrib import messages

@login_required 
def calendar_view(request):
    return render(request, 'dashboard/calendar.html')

@login_required
def booking_events_json(request):
    student = request.user
    bookings = Booking.objects.filter(student=student)
    events = []

    for booking in bookings:
        color = 'green' if booking.status == 'booked' else 'red'
        start_time = f"{booking.date}T{booking.time}"


        events.append({
            "title": f"Lesson with {booking.instructor.username}",
            "start": f"{booking.date}T{booking.time}",
            "color": color,
            "description": f"{booking.status.capitalize()} lesson on {booking.date} at {booking.time}",
            "booking_id": booking.id,
        })
    
    return JsonResponse(events, safe=False)

@login_required
def book_lesson(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, student=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            booking.save()
            messages.success(request, "Lesson booked successfully!")
            return redirect('student_dashboard')
    else:
        form = BookingForm(student=request.user)
    return render(request, 'dashboard/book_lesson.html', {'form': form})


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    booking.status= 'cancelled'
    booking.save()
    return HttpResponseRedirect(reverse('student_dashboard'))

@login_required
def student_dashboard(request):
    user = request.user
    today = timezone.now().date()

    upcoming = Booking.objects.filter(student=user, date__gte=today, status='booked').order_by('date')
    past = Booking.objects.filter(student=user, date__lt=today).order_by('-date')

    return render(request, 'dashboard/student_dashboard.html', {
        'upcoming': upcoming,
        'past': past,
    })

@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, student=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson rescheduled successfully.")
            return redirect('student_dashboard')
    else:
        form = BookingForm(instance=booking, student=request.user)

    return render(request, 'dashboard/reschedule_lesson.html', {'form': form, 'booking': booking})


@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return render(request, '403.html')
    
    return render(request, 'dashboard/instructor_dashboard.html')

@login_required
def instructor_calendar(request):
    if request.user.role != 'instructor':
        return render(request, '403.html')
    return render(request, 'dashboard/instructor_calendar.html')

@login_required
def instructor_calendar_data(request):
    if request.user.role != 'instructor':
        return JsonResponse([], safe=False)
    
    bookings = Booking.objects.filter(instructor=request.user)
    events = []

    for booking in bookings:
        events.appent({
            "title": f"Lesson with {booking.student.username}",
            "start":f"{booking.date}T{booking.time}",
            "color": "green" if booking.status == "booked" else "red",
            "status": booking.status,
            "booking_id": booking.id,
        })
        
    return JsonResponse(events, safe=False)

@login_required
def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")


@login_required
def dashboard_home_redirect(request):
    return redirect('dashboard_redirect')