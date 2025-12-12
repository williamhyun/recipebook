from django.db import transaction
from django.db.models import Count, Avg, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Recipe, RecipeIngredient, Cuisine
from .forms import RecipeForm, RecipeIngredientFormSet

class RecipeListView(ListView):
    model = Recipe
    template_name = "recipebook/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("cuisine").prefetch_related("recipe_ingredients__ingredient")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(notes__icontains=q))
        return qs


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipebook/recipe_detail.html"
    context_object_name = "recipe"

    def get_queryset(self):
        return super().get_queryset().select_related("cuisine").prefetch_related("recipe_ingredients__ingredient")


class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipebook/recipe_form.html"
    success_url = reverse_lazy("recipe_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = RecipeIngredientFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = RecipeIngredientFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        formset = RecipeIngredientFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            return response
        # if inline invalid, render the page again with errors
        return render(self.request, self.template_name, {"form": form, "formset": formset})


class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipebook/recipe_form.html"
    success_url = reverse_lazy("recipe_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = RecipeIngredientFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = RecipeIngredientFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        formset = RecipeIngredientFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            return response
        return render(self.request, self.template_name, {"form": form, "formset": formset})


class RecipeDeleteView(DeleteView):
    model = Recipe
    template_name = "recipebook/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipe_list")

def report(request):
    cuisine_id = request.GET.get("cuisine")
    max_minutes = request.GET.get("max_minutes")
    difficulty = request.GET.get("difficulty")

    base_qs = Recipe.objects.select_related("cuisine").all()
    if cuisine_id:
        base_qs = base_qs.filter(cuisine_id=cuisine_id)
    if max_minutes:
        try:
            base_qs = base_qs.filter(minutes__lte=int(max_minutes))
        except ValueError:
            pass
    if difficulty in {"easy", "medium", "hard"}:
        base_qs = base_qs.filter(difficulty=difficulty)

    # aggregate computed from base_qs
    avg_minutes_per_cuisine = (
        base_qs.values("cuisine__id", "cuisine__name")
               .annotate(avg_minutes=Avg("minutes"))
               .order_by("cuisine__name")
    )
    recipe_count_by_difficulty = (
        base_qs.values("difficulty")
               .annotate(count=Count("id"))  # distinct by construction
               .order_by("difficulty")
    )

    # table queryset with ingredient_count
    recipes = (
        base_qs.annotate(ingredient_count=Count("recipe_ingredients", distinct=True))
               .order_by("name")
    )

    context = {
        "cuisines": Cuisine.objects.order_by("name"),
        "recipes": recipes,
        "avg_minutes_per_cuisine": avg_minutes_per_cuisine,
        "recipe_count_by_difficulty": recipe_count_by_difficulty,
        "selected": {
            "cuisine": int(cuisine_id) if cuisine_id and cuisine_id.isdigit() else None,
            "max_minutes": max_minutes or "",
            "difficulty": difficulty or "",
        },
    }
    return render(request, "recipebook/report.html", context)
