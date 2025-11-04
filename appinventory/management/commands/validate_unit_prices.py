from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import csv
import os

from appinventory.models import Product, ProductPrice
from appinventory.helpers import convert_to_reference_unit


def _parse_tolerance(raw: str) -> Decimal:
    """
    Acepta '0.02' o '2%' y lo devuelve como Decimal (0.02).
    """
    raw = (raw or "").strip()
    if raw.endswith("%"):
        try:
            return (Decimal(raw[:-1]) / Decimal("100")).quantize(Decimal("0.0001"))
        except InvalidOperation:
            return Decimal("0.02")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0.02")


def price_per_reference_unit(product, unit, price: Decimal):
    """
    Convierte el precio por 'unit' a precio por unidad de referencia.
    Si 1 unit = X unidades de referencia, entonces:
        price_per_ref = price / X
    """
    ref_qty = convert_to_reference_unit(product, unit, Decimal("1"))
    if not ref_qty:
        return None
    return (Decimal(price) / Decimal(ref_qty)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = (
        "Audita proporcionalidad de ProductPrice contra la unidad de referencia por producto "
        "y exporta inconsistencias a CSV."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default="validate_unit_prices_report.csv",
            help="Ruta de salida CSV (por defecto: ./validate_unit_prices_report.csv)",
        )
        parser.add_argument(
            "--tolerance",
            dest="tolerance",
            default="0.02",
            help="Tolerancia como decimal (0.02) o porcentaje (2%). Default: 0.02",
        )
        parser.add_argument(
            "--per-price-type",
            action="store_true",
            dest="per_price_type",
            help="Reinicia baseline por cada price_type (útil si manejas listas de precios distintas).",
        )
        parser.add_argument(
            "--include-inactive",
            action="store_true",
            dest="include_inactive",
            help="Incluye ProductPrice inactivos en la auditoría.",
        )

    def handle(self, *args, **opts):
        csv_path = opts["csv_path"]
        tol = _parse_tolerance(opts["tolerance"])
        per_price_type = opts["per_price_type"]
        include_inactive = opts["include_inactive"]

        self.stdout.write(self.style.NOTICE(
            f"🔍 Iniciando validación (tolerancia={tol} {'(por price_type)' if per_price_type else '(global por producto)'})."
        ))

        price_qs = ProductPrice.objects.select_related("unit", "price_type")
        if not include_inactive:
            price_qs = price_qs.filter(is_active=True)

        products = Product.objects.prefetch_related(
            Prefetch("prices", queryset=price_qs)
        ).all()

        inconsistencies = []
        total_compared = 0

        for product in products:
            prices = list(product.prices)
            if len(prices) < 2:
                continue  # nada que comparar

            # Agrupación: una sola clave (global) o por price_type
            if per_price_type:
                groups = {}
                for pp in prices:
                    key = pp.price_type_id or 0
                    groups.setdefault(key, []).append(pp)
                groups_lists = groups.values()
            else:
                groups_lists = [prices]

            for group in groups_lists:
                if len(group) < 2:
                    continue

                # Calcula precio/ref de cada fila
                ref_prices = []
                for pp in group:
                    try:
                        ppr = price_per_reference_unit(product, pp.unit, pp.price)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"⚠️ {product.name}: error convirtiendo {pp.unit} → ref: {e}"
                        ))
                        ppr = None
                    if ppr is None:
                        self.stdout.write(self.style.WARNING(
                            f"⚠️ {product.name}: no se pudo converter 1 {pp.unit.code} a unidad ref."
                        ))
                        continue
                    ref_prices.append((pp, ppr))

                if len(ref_prices) < 2:
                    continue

                # Baseline: el marcado como default o primero
                baseline_pp, baseline_ppr = next(
                    ((pp, ppr) for (pp, ppr) in ref_prices if pp.is_default),
                    ref_prices[0]
                )

                for (pp, ppr) in ref_prices:
                    total_compared += 1
                    if not baseline_ppr or baseline_ppr == 0:
                        continue
                    diff_ratio = abs((ppr - baseline_ppr) / baseline_ppr)

                    if diff_ratio > tol:
                        inconsistencies.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "sku": product.sku,
                            "price_type": getattr(pp.price_type, "name", "") if pp.price_type_id else "",
                            "unit": pp.unit.code,
                            "price": str(pp.price),
                            "price_per_ref": str(ppr),
                            "baseline_unit": baseline_pp.unit.code,
                            "baseline_price_type": getattr(baseline_pp.price_type, "name", "") if baseline_pp.price_type_id else "",
                            "baseline_price_per_ref": str(baseline_ppr),
                            "diff_percent": f"{(diff_ratio * Decimal('100')).quantize(Decimal('0.01'))}%",
                            "is_default": "Y" if pp.is_default else "N",
                            "is_sale": "Y" if pp.is_sale else "N",
                            "is_purchase": "Y" if pp.is_purchase else "N",
                        })

        # Export CSV
        if inconsistencies:
            # Asegurar carpeta
            os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "product_id", "product_name", "sku",
                    "price_type", "unit", "price",
                    "price_per_ref",
                    "baseline_price_per_ref", "baseline_unit", "baseline_price_type",
                    "diff_percent",
                    "is_default", "is_sale", "is_purchase",
                ])
                writer.writeheader()
                for row in inconsistencies:
                    writer.writerow(row)

            self.stdout.write(self.style.ERROR(
                f"🚨 Se encontraron {len(inconsistencies)} inconsistencias. (Comparados: {total_compared})"
            ))
            self.stdout.write(self.style.WARNING(
                f"📄 Reporte CSV generado en: {os.path.abspath(csv_path)}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Sin inconsistencias. (Comparados: {total_compared})"))
