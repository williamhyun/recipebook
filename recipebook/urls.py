# DO NOT set app_name here for this option
from django.urls import path
from .views import (
    RecipeListView, RecipeDetailView, RecipeCreateView,
    RecipeUpdateView, RecipeDeleteView, report
)

urlpatterns = [
    path('', RecipeListView.as_view(), name='recipe_list'),
    path('recipes/new/', RecipeCreateView.as_view(), name='recipe_create'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipes/<int:pk>/edit/', RecipeUpdateView.as_view(), name='recipe_edit'),
    path('recipes/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),
    path('reports/', report, name='report'),
]

