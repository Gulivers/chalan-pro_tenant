from django.db import models
from django.utils.text import slugify

class ManualCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Categoría de Manual"
        verbose_name_plural = "Categorías de Manual"

    def __str__(self):
        return self.name

class ManualEntry(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    module = models.CharField(max_length=100, help_text="Ej: Inventario, ERP, Contratos")
    summary = models.TextField(blank=True, help_text="Resumen corto para vista previa o meta descripción.")
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        ManualCategory,
        on_delete=models.PROTECT,
        related_name="manuals",
        verbose_name="Categoría"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Manual Entry"
        verbose_name_plural = "Manual Entries"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.module})"
