from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from bookings.models import Booking
from django.utils import timezone

from django.http import HttpResponseRedirect
from django.urls import reverse

from bookings.forms import BookingForm

from django.http import JsonResponse
from django.core.serializers import serialize
from bookings.models import Booking, InstructorAvailability

from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

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
            "status": booking.status,
        })

    # available slots across instructors + skips booked ones
    availability = InstructorAvailability.objects.all()
    
    for slot in availability:
        is_taken = Booking.objects.filter(
            instructor=slot.instructor,
            date=slot.date,
            time=slot.time,
            status='booked'
        ).exists()

        if not is_taken:
            events.append({
                "title": f"Available: {slot.instructor.username}",
                "start": f"{slot.date}T{slot.time}",
                "color": "#007bff",
                "description": f"{slot.instructor.username} is available on {slot.date} at {slot.time}",
            })

    return JsonResponse(events, safe=False)


@login_required
def book_lesson(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, student=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            booking.status = 'booked'
            booking.save()
            messages.success(request, 'Lesson booked successfully!')

            # SEND CONFIRMATION EMAIL
            html_body = render_to_string('email/lesson_confirmation.html', {
                'username': request.user.username,
                'instructor': booking.instructor.username,
                'date': booking.date,
                'time': booking.time,
            })
            subject = 'Lesson Booking Confirmation'
            from_email = settings.EMAIL_HOST_USER
            to_email = request.user.email

            email = EmailMultiAlternatives(subject, '', from_email, [to_email])
            email.attach_alternative(html_body, "text/html")
            email.send()

            return redirect('student_dashboard')
    else:
        initial_data = {}

        instructor_username = request.GET.get('instructor')
        if instructor_username:
            from accounts.models import CustomUser
            try:
                instructor = CustomUser.objects.get(username=instructor_username, role='instructor')
                initial_data['instructor'] = instructor.id
            except CustomUser.DoesNotExist:
                pass

        date = request.GET.get('date')
        time = request.GET.get('time')
        if date:
            initial_data['date'] = date
        if time:
            initial_data['time'] = time

        form = BookingForm(initial=initial_data)

    return render(request, 'dashboard/book_lesson.html', {'form': form})



def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Lesson cancelled successfully.")
        
        # send email
        subject = "Lesson Cancelled"
        message = render_to_string('email/lesson_cancelled.html', {
            'user': request.user,
            'booking': booking,
        })
        send_mail(
            subject,
            '',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=False,
            html_message=message,
        )

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

            # send email
            subject = "Lesson Rescheduled"
            message = render_to_string('email/lesson_rescheduled.html', {
                'user': request.user,
                'booking': booking,
            })
            send_mail(
                subject,
                '',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=False,
                html_message=message,
            )
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
def instructor_calendar_view(request):
    return render(request, 'dashboard/instructor_calendar.html')

@login_required
def instructor_calendar_data(request):
    instructor = request.user
    if request.user.role != 'instructor':
        return JsonResponse([], safe=False)
    
    bookings = Booking.objects.filter(instructor=request.user)
    events = []

    for booking in bookings:
        events.append({
            "title": f"Lesson with {booking.student.username}",
            "start":f"{booking.date}T{booking.time}",
            "color": "green" if booking.status == "booked" else "red",
            "status": booking.status,
            "booking_id": booking.id,
        })
        
    return JsonResponse(events, safe=False)

@staff_member_required
def admin_dashboard(request):
    from bookings.models import Booking
    from accounts.models import CustomUser

    total_students = CustomUser.objects.filter(role='student').count()
    total_instructors = CustomUser.objects.filter(role='instructor').count()
    total_bookings = Booking.objects.count()

    upcoming = Booking.objects.filter(date__gte=timezone.now().date()).order_by('date', 'time')[:5]
    bookings = Booking.objects.all().order_by('-date', '-time')

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_bookings': total_bookings,
        'upcoming': upcoming,
        'bookings': bookings,
    })

@staff_member_required
def admin_calendar_data(request):
    bookings = Booking.objects.all()
    events = []

    for booking in bookings:
        if booking.status =="booked":
            color = "orange"
        elif booking.status =="completed":
            color = "green"
        elif booking.status =="cancelled":
            color = "red"
        else:
            color = "grey"

        events.append({
            "title": f"{booking.student.username} with {booking.instructor.username}",#
            "start": f"{booking.date}T{booking.time}",
            "color": color,
            "description": f"{booking.status.capitalize()} lesson",
            "status": booking.status.capitalize(),
        })

    return JsonResponse(events, safe=False)

@staff_member_required
def admin_calendar_view(request):
    return render(request, 'dashboard/admin_calendar.html')

@staff_member_required
@require_POST
def admin_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'cancelled' 
    booking.save()
    messages.success(request, "Booking Cancelled.")
    return redirect('admin_dashboard')

@staff_member_required
@require_POST
def admin_complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'completed' 
    booking.save()
    messages.success(request, f"Marked booking #{booking.id} as Completed.")
    return redirect('admin_dashboard')

@staff_member_required
@require_POST
def admin_delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, "Booking Deleted.")
    return redirect('admin_dashboard')

@login_required
def dashboard_home_redirect(request):
    return redirect('dashboard_redirect')