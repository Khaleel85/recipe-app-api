"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from drf_spectacular.utils import extend_schema_field


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    title = serializers.SerializerMethodField()
    time_minutes = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    def get_title(self, obj) -> str:
        if self.context['request'].LANGUAGE_CODE == 'ar':
            return obj.title_ar
        else:
            return obj.title_en

    def get_time_minutes(self, obj) -> int:
        if self.context['request'].LANGUAGE_CODE == 'ar':
            return obj.time_minutes_ar
        else:
            return obj.time_minutes_en

    @extend_schema_field(
        serializers.DecimalField(max_digits=5, decimal_places=2),
        )
    def get_price(self, obj):
        if self.context['request'].LANGUAGE_CODE == 'ar':
            return obj.price_ar
        else:
            return obj.price_en

    def get_link(self, obj) -> str:
        if self.context['request'].LANGUAGE_CODE == 'ar':
            return obj.link_ar
        else:
            return obj.link_en

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients', 'image',
        ]
        read_only_fields = ['id']

    def _get_and_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_and_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_and_create_tags(tags, recipe)
        self._get_and_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_and_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_and_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    description = serializers.SerializerMethodField()

    def get_description(self, obj) -> str:
        if self.context['request'].LANGUAGE_CODE == 'ar':
            return obj.description_ar
        else:
            return obj.description_en

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
