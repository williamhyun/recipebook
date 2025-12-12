from django.contrib import admin
from .models import Cuisine, Ingredient, Recipe, RecipeIngredient

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "cuisine", "minutes", "difficulty")
    list_filter = ("cuisine", "difficulty")
    search_fields = ("name",)
    inlines = [RecipeIngredientInline]

admin.site.register(Cuisine)
admin.site.register(Ingredient)
