from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from bookings.models import Booking
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Send daily lesson alerts to instructors.'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)

        instructors = CustomUser.objects.filter(role='instructor')
        for instructor in instructors:
            bookings = Booking.objects.filter(instructor, date= tomorrow, status='booked')

            if bookings.exists():
                subject = "Your Lessons for Tomorrow"
                message = render_to_string('email/daily_instructor_alert.html', {
                    'instructor': instructor,
                    'bookings': bookings,
                    'date': tomorrow,
                })

                send_mail(
                    subject,
                    '',
                    settings.EMAIL_HOST_USER,
                    [instructor.email],
                    fail_silently=False,
                    html_message=message,
                )

                self.stdout.write(f"Sent daily alert to {instructor.username}")