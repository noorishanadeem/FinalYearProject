from django.db import models
from django.conf import settings

# Create your models here.
class Review(models.Model):
    booking = models.OneToOneField(
        'bookings.Booking',  # <-- string reference, no import
        on_delete=models.CASCADE,
        related_name='review'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_reviews'
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking} by {self.instructor}"