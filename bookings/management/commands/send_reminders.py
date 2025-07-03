from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = "Send lesson reminder emails 24 hours before lesson"

    def handle (self, *args, **options):
        now = timezone.now()
        target_time = now + timedelta(hours=24)

        bookings = Booking.objects.filter(date=target_time.date(), time__hour=target_time.hour, status='booked')
        for booking in bookings:
            subject = "Lesson Reminder"
            message = (
                f"Hi {booking.student.username},\n\n"
                f"This is a reminder for your lesson with {booking. instructor.username} "
                f"on {booking.date} at {booking.time}.\n\n"
                "Thank you for choosing us!\n"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.student.email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Sent reminder for booking id {booking.id}"))