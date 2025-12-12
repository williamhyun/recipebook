from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Recipe, RecipeIngredient

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "cuisine", "minutes", "difficulty", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "cuisine": forms.Select(attrs={"class": "form-select"}),
            "minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "difficulty": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit", "preparation"]
        widgets = {
            "ingredient": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "unit": forms.Select(attrs={"class": "form-select"}),
            "preparation": forms.TextInput(attrs={"class": "form-control"}),
        }

class AtLeastOneIngredientInlineFormSet(BaseInlineFormSet):
    """
    Require at least one non-deleted ingredient row
    """
    def clean(self):
        super().clean()
        non_deleted = 0
        for form in self.forms:
            if getattr(form, "cleaned_data", None) and not form.cleaned_data.get("DELETE", False):
                # Count only rows that actually select an ingredient
                ing = form.cleaned_data.get("ingredient")
                if ing:
                    non_deleted += 1
        if non_deleted == 0:
            raise forms.ValidationError("Please add at least one ingredient.")

RecipeIngredientFormSet = inlineformset_factory(
    parent_model=Recipe,
    model=RecipeIngredient,
    form=RecipeIngredientForm,
    formset=AtLeastOneIngredientInlineFormSet,
    fields=["ingredient", "quantity", "unit", "preparation"],
    extra=3,
    can_delete=True,
)

