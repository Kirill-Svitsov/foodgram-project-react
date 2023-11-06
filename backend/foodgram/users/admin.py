from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Follow


class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_recipe_count",
        "get_followers_count"
    )
    search_fields = ("username",)
    list_filter = ("username", "email")

    def get_recipe_count(self, obj):
        return obj.recipes.count()

    get_recipe_count.short_description = "Кол-во рецептов"

    def get_followers_count(self, obj):
        return obj.follower.count()

    get_followers_count.short_description = "Кол-во подписчиков"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
