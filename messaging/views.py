from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from cars.models import Car
from .forms import MessageForm
from .models import Conversation, Message


@login_required
def start_conversation(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    if request.user == car.owner:
        return redirect("cars:car_detail", car_id=car.id)

    conversation, _ = Conversation.objects.get_or_create(
        car=car,
        buyer=request.user,
        seller=car.owner,
    )

    return redirect("messaging:conversation_detail", conversation_id=conversation.id)


@login_required
def conversation_list(request):
    conversations = (
        Conversation.objects
        .filter(Q(buyer=request.user) | Q(seller=request.user))
        .select_related("car", "buyer", "seller")
        .order_by("-updated_at")
    )

    return render(
        request,
        "messaging/conversation_list.html",
        {"conversations": conversations},
    )


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("car", "buyer", "seller"),
        pk=conversation_id,
    )

    if request.user not in [conversation.buyer, conversation.seller]:
        return HttpResponseForbidden("No autorizado.")

    messages = conversation.messages.select_related("sender").all()
    form = MessageForm()

    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    return render(
        request,
        "messaging/conversation_detail.html",
        {
            "conversation": conversation,
            "messages": messages,
            "form": form,
        },
    )


@login_required
@require_POST
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)

    if request.user not in [conversation.buyer, conversation.seller]:
        return HttpResponseForbidden("No autorizado.")

    form = MessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"ok": False, "errors": form.errors},
            status=400,
        )

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=form.cleaned_data["text"],
    )

    conversation.save(update_fields=["updated_at"])

    return JsonResponse(
        {
            "ok": True,
            "message": {
                "id": message.id,
                "text": message.text,
                "sender": message.sender.username,
                "sender_id": message.sender.id,
                "created_at": message.created_at.strftime("%H:%M"),
            },
        }
    )


@login_required
@require_GET
def fetch_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)

    if request.user not in [conversation.buyer, conversation.seller]:
        return HttpResponseForbidden("No autorizado.")

    messages = (
        conversation.messages
        .select_related("sender")
        .all()
    )

    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    data = [
        {
            "id": msg.id,
            "text": msg.text,
            "sender": msg.sender.username,
            "sender_id": msg.sender.id,
            "created_at": msg.created_at.strftime("%H:%M"),
        }
        for msg in messages
    ]

    return JsonResponse({"messages": data})