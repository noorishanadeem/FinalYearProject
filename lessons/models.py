from django.db import models
from bookings.models import Booking

class Lesson(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Lesson: {self.booking}"
