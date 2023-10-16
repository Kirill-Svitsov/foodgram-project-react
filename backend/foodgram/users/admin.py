from django.contrib import admin

from users.models import Follow, CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = ("username",)
    list_filter = ("username", "email")


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
