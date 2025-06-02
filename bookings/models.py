from django.db import models
from accounts.models import CustomUser

class Booking(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_bookings')
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='instructor_bookings')
    date = models.DateField()
    time = models.TimeField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(Self):
        return f"lesson with {Self.instructor.username} on {Self.date} at {Self.time}" 