from django import forms
from .models import Booking
from accounts.models import CustomUser

from django.core.exceptions import ValidationError
from datetime import datetime

from bookings.models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['instructor', 'date', 'time']
        widgets = {
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        self.fields['instructor'].queryset = CustomUser.objects.filter(role='instructor')

    def clean(self):
        cleaned_data = super().clean()
        instructor = cleaned_data.get('instructor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if not (instructor and date and time):
            return
        
        # for excluding current booking instance for rescheduling
        qs = Booking.objects.exclude(id=self.instance.id if self.instance else None)
        
        if not self.student:
            raise ValidationError("Student not set on BookingForm.")

        #checks if student already has booking for that time
        if Booking.objects.filter(student=self.student, date=date, time=time, status='booked').exists():
            raise ValidationError("You already have a lesson booked at this time.")
        
        if Booking.objects.filter(instructor=instructor, date=date, time=time, status='booked').exists():
            raise ValidationError(f"{instructor.username} is already booked at this time.")
        