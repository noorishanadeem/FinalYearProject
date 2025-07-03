# sends an automated email when the status of a lesson changes (e.g., when a lesson is rescheduled or cancelled), WITHOUT repeating the send logic in every view.

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@receiver(post_save, sender=Booking)
def send_status_notification(sender, instance, created, **kwargs):
    """Send an email when a booking changes (cancelled/rescheduled)."""
    if not created:
        student_email = instance.student.email
        instructor_email = instance.instructor.email

        if instance.status == 'cancelled':
            subject = "Lesson Cancelled"
            student_message = render_to_string('email/lesson_cancelled.html', {
                'user': instance.student,
                'booking': instance,
            })
            instructor_message = render_to_string('email/instructor_lesson_cancelled.html', {
                'user': instance.instructor,
                'booking': instance,
            })

            # student email cancel
            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [student_email],
                fail_silently=False,
                html_message=student_message,
            )

            # instructor email cancel
            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [instructor_email],
                fail_silently=False,
                html_message=instructor_message,
            )

        elif instance.status == 'rescheduled':
            subject = "Lesson Rescheduled"

            student_message = render_to_string('email/lesson_rescheduled.html', {
                'user': instance.student,
                'booking': instance,
            })
            instructor_message = render_to_string('email/instructor_lesson_reschedue.html', {
                'user': instance.instructor,
                'booking': instance,
            })

            # student email reschedule
            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [student_email],
                fail_silently=False,
                html_message=student_message,
            )

            # instructor email reschedule
            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [instructor_email],
                fail_silently=False,
                html_message=instructor_message,
            )