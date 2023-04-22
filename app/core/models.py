"""
Database models.
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.utils.translation import gettext_lazy as _


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Managers for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    title_en = models.CharField(
        _('title (English)'),
        max_length=255,
        null=True,
        blank=True,
        default=None,
        )
    title_ar = models.CharField(
        _('اسم الوصفة (Arabic)'),
        max_length=255,
        null=True,
        blank=True,
        default=None,
    )
    description_en = models.TextField(_('description (English)'), blank=True)
    description_ar = models.TextField(_('الوصف (Arabic)'), blank=True)
    time_minutes_en = models.IntegerField(
        _('time_minutes (English)'),
        null=True,
        blank=True,
        default=None,
    )
    time_minutes_ar = models.IntegerField(
        _('الوقت بالدقائق(Arabic)'),
        null=True,
        blank=True,
        default=None,
    )
    price_en = models.DecimalField(
        _('price (English)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
    )
    price_ar = models.DecimalField(
        _('التكلفة (Arabic)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
    )
    link_en = models.CharField(
        _('link (English)'),
        max_length=255,
        blank=True,
    )
    link_ar = models.CharField(
        _('الرابط (Arabic)'),
        max_length=255,
        blank=True,
    )
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(
        _('الصورة'),
        null=True,
        upload_to=recipe_image_file_path,
    )

    class Meta:
        verbose_name = 'الوصفة'
        verbose_name_plural = 'الوصفات'

    def __str__(self):
        return self.title_en


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
