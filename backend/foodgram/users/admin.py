from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


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
        return obj.followers.count()

    get_followers_count.short_description = "Кол-во подписчиков"


class SubscriptionAdmin(BaseUserAdmin):
    list_display = ("user", "author")
