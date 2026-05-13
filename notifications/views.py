from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince
from django.utils import timezone
from .models import Notification

@login_required
def mark_notifications_read(request):
    if request.method == "POST":
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"count": count})

@login_required
def mark_notifications_read(request):
    if request.method == "POST":
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"count": count})


@login_required
def unread_notifications(request):
    notifications = request.user.notifications.filter(
        is_read=False
    ).order_by("-created_at")[:10]

    data = []
    for n in notifications:
        if "|" in n.title:
            text, conv_id = n.title.rsplit("|", 1)
            from django.urls import reverse
            url = reverse("messaging:conversation_detail", args=[conv_id])
        else:
            text = n.title
            url = "#"

        data.append({
            "sender": n.sender.username,
            "title": text,
            "url": url,
            "time_ago": timesince(n.created_at, timezone.now()),
        })

    return JsonResponse({"notifications": data})