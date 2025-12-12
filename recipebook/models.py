from django.db import models
from django.core.validators import MinValueValidator

class Cuisine(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    name = models.CharField(max_length=160, unique=True)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT, related_name="recipes")
    minutes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)

    # Many-to-many via a through table to store quantity
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["cuisine", "minutes"]),
            models.Index(fields=["difficulty"]),
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Junction with payload: quantity per ingredient per recipe
    """
    class Unit(models.TextChoices):
        # Keep the set small; you can expand later.
        GRAM = "g", "g"
        KILOGRAM = "kg", "kg"
        MILLILITER = "ml", "ml"
        LITER = "l", "l"
        TEASPOON = "tsp", "tsp"
        TABLESPOON = "tbsp", "tbsp"
        CUP = "cup", "cup"
        PIECE = "pc", "piece"

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="ingredient_recipes")

    # optional
    quantity = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=8, choices=Unit.choices, blank=True)
    preparation = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["ingredient__name"]
        # Prevent duplicate ingredient rows for the same recipe.
        constraints = [
            models.UniqueConstraint(fields=["recipe", "ingredient"], name="uniq_recipe_ingredient")
        ]
        indexes = [
            models.Index(fields=["recipe"]),
            models.Index(fields=["ingredient"]),
        ]

    def __str__(self):
        base = f"{self.ingredient.name}"
        if self.quantity is not None:
            if self.unit:
                return f"{base} ({self.quantity} {self.unit})"
            return f"{base} ({self.quantity})"
        return base

