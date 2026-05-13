from django.urls import reverse

def notifications(request):

    if request.user.is_authenticated:

        unread_qs = request.user.notifications.filter(
            is_read=False
        ).order_by("-created_at")[:10]

        notifications_list = []
        for n in unread_qs:
            if "|" in n.title:
                text, conv_id = n.title.rsplit("|", 1)
                url = reverse("messaging:conversation_detail", args=[conv_id])
            else:
                text = n.title
                url = "#"

            notifications_list.append({
                "sender": n.sender,
                "title": text,
                "url": url,
                "created_at": n.created_at,
            })

        return {
            "navbar_notifications": notifications_list,
            "navbar_notifications_count": len(notifications_list),
        }

    return {}