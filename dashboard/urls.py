from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/calendar/', views.admin_calendar_view, name='admin_calendar_view'),
    path('admin/calendar/data/', views.admin_calendar_data, name='admin_calendar_data'),
    path('admin/complete-booking/<int:booking_id>/', views.admin_complete_booking, name='admin_complete_booking'),
    path('admin/delete-booking/<int:booking_id>/', views.admin_delete_booking, name='admin_delete_booking'),
    path('admin/cancel-booking/<int:booking_id>/', views.admin_cancel_booking, name='admin_cancel_booking'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('book-lesson/', views.book_lesson, name='book_lesson'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/data/', views.booking_events_json, name='booking_events_json'),
    path('reschedule/<int:booking_id>/', views.reschedule_booking, name='reschedule_booking'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('instructor/calendar/', views.instructor_calendar, name='instructor_calendar'),
    path('instructor/calendar/data/', views.instructor_calendar_data, name='instructor_calendar_data'),
    path('', views.dashboard_home_redirect),

]