from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "buyer", "seller", "updated_at")
    search_fields = ("car__make", "car__model", "buyer__username", "seller__username")
    list_filter = ("created_at", "updated_at")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at", "is_read")
    search_fields = ("sender__username", "text")
    list_filter = ("created_at", "is_read")