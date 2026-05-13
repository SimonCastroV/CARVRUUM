from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("mark-read/", views.mark_notifications_read, name="mark_read"),
    path("unread-count/", views.unread_count, name="unread_count"),
    path("unread/", views.unread_notifications, name="unread_notifications"),
]