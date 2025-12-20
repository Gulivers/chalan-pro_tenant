"""
Este módulo contiene la función de validación para las unidades de producto.

La función validate_units_of_measure revisa todas las relaciones UnitOfMeasure en la base de datos y detecta posibles errores o inconsistencias, como:
- Factores de conversión desproporcionados (mayores a 1000 o menores a 0.01)
- Detecta factores desproporcionados
- Detecta múltiples unidades base en una misma categoría
- Verifica si hay más de una unidad base por categoría

Devuelve un JsonResponse con una lista de advertencias o errores encontrados, ayudando a mantener la integridad de los datos de inventario.
"""
from django.http import JsonResponse
from .models import UnitOfMeasure

def validate_units_of_measure(request):
    errors = []

    categories = {}

    for unit in UnitOfMeasure.objects.select_related('category'):
        cat_name = unit.category.name
        unit_code = unit.code
        factor = unit.conversion_factor
        sign = unit.conversion_sign

        # Detecta factores desproporcionados
        if factor > 1000 or factor < 0.01:
            errors.append({
                "unit": unit_code,
                "category": cat_name,
                "issue": f"⚠️ El factor de conversión {factor:.4f} parece desproporcionado."
            })

        # Detecta múltiples unidades base en una misma categoría
        if sign == 'ref':
            categories.setdefault(cat_name, []).append(unit_code)

    # Verifica si hay más de una unidad base por categoría
    for cat_name, ref_units in categories.items():
        if len(ref_units) > 1:
            errors.append({
                "category": cat_name,
                "issue": f"❗ Hay múltiples unidades base (ref) en esta categoría: {', '.join(ref_units)}"
            })

    return JsonResponse(errors, safe=False)
