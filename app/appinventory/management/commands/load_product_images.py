# -*- coding: utf-8 -*-
"""
Comando para cargar imágenes de productos desde un directorio local,
emparejando productos de la BD con el CSV de códigos/descripciones
y creando registros ProductImage por cada asignación producto-marca.
"""
import csv
import os
import re
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction
from django_tenants.utils import schema_context

from appinventory.models import Product, ProductImage, ProductBrandAssignment


def normalize_text(text):
    """Normaliza texto para comparación: minúsculas, espacios colapsados, sin comillas extra."""
    if not text:
        return ""
    t = text.strip().lower()
    t = re.sub(r'\s+', ' ', t)
    t = t.replace('"', "'")
    return t.strip()


def load_csv_codes(csv_path):
    """
    Carga el CSV con columnas id (código) y description.
    Retorna: (all_codes, code_by_description).
    - all_codes: set de todos los códigos (id del CSV = código del producto).
    - code_by_description: mapa descripción normalizada/exacta -> código.
    """
    code_by_description = {}
    all_codes = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get('id') or '').strip()
            desc = (row.get('description') or '').strip()
            if not code:
                continue
            all_codes.add(code)
            norm = normalize_text(desc)
            if norm and norm not in code_by_description:
                code_by_description[norm] = code
            if desc and desc not in code_by_description:
                code_by_description[desc] = code
    return all_codes, code_by_description


def find_code_for_product(product, all_codes, code_by_description):
    """
    Obtiene el código del producto buscando por NOMBRE en el CSV (columna description).
    No se usa SKU. Coincidencia tipo LIKE: nombre en descripción o descripción en nombre.
    1) Exacta: nombre (o normalizado) == descripción.
    2) LIKE %%: descripción contiene nombre (description LIKE %product_name%).
    3) LIKE %%: nombre contiene descripción (product_name LIKE %description%).
    Si hay varias coincidencias parciales, se prefiere la descripción más larga (más específica).
    """
    name = (product.name or '').strip()
    if not name:
        return None
    norm_name = normalize_text(name)
    # Exacta
    if name in code_by_description:
        return code_by_description[name]
    if norm_name in code_by_description:
        return code_by_description[norm_name]
    # Coincidencia parcial tipo LIKE: nombre en descripción o descripción en nombre
    # Evitar matches demasiado cortos (ej. "green" solo)
    min_len = 4
    if len(norm_name) < min_len:
        return None
    candidates = []
    for desc_key, code in code_by_description.items():
        if len(desc_key) < min_len:
            continue
        if norm_name in desc_key:
            # description LIKE %product_name%
            candidates.append((code, len(desc_key), True))
        elif desc_key in norm_name:
            # product_name LIKE %description%
            candidates.append((code, len(desc_key), False))
    if not candidates:
        return None
    # Preferir: exact match (norm_name == desc_key ya devuelto arriba), luego descripción más larga
    candidates.sort(key=lambda x: (-x[1], not x[2]))
    return candidates[0][0]


def find_image_path(images_dir, code):
    """Busca archivo de imagen por código: code.jpg o code.jpeg (case-insensitive)."""
    if not code or not images_dir or not os.path.isdir(images_dir):
        return None
    base = os.path.join(images_dir, code)
    for ext in ('.jpg', '.jpeg', '.JPG', '.JPEG'):
        path = base + ext
        if os.path.isfile(path):
            return path
    return None


class Command(BaseCommand):
    help = (
        'Carga imágenes de productos desde un directorio local usando un CSV de códigos/descripciones. '
        'Empareja por NOMBRE del producto (appinventory_product.name) en la columna description del CSV, '
        'con coincidencia tipo LIKE (%%), y copia la imagen a media por cada asignación producto-marca.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='/home/oliver/Downloads/List of cleaned products.csv',
            help='Ruta al CSV con columnas id (código) y description',
        )
        parser.add_argument(
            '--images-dir',
            type=str,
            default='/home/oliver/Downloads/JPGfull-01/full-01',
            help='Directorio donde están las imágenes (nombre = código.jpg)',
        )
        parser.add_argument(
            '--schema',
            type=str,
            default=None,
            help='Schema del tenant (ej: test_dominio_local). Si no se indica, se usa el schema actual.',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=1,
            help='ID del usuario para uploaded_by (default: 1)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría, sin escribir en BD ni copiar archivos',
        )
        parser.add_argument(
            '--list-missing',
            action='store_true',
            help='Solo listar productos con código en CSV pero sin archivo de imagen en el directorio',
        )
        parser.add_argument(
            '--output-missing',
            type=str,
            default=None,
            help='Ruta de archivo donde guardar la lista de productos sin imagen (ej: missing_images.txt)',
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        images_dir = options['images_dir']
        schema = options['schema']
        user_id = options['user_id']
        dry_run = options['dry_run']
        list_missing = options.get('list_missing', False)
        output_missing = options.get('output_missing')

        if not os.path.isfile(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV no encontrado: {csv_path}'))
            return
        if not os.path.isdir(images_dir):
            self.stdout.write(self.style.ERROR(f'Directorio de imágenes no encontrado: {images_dir}'))
            return

        self.stdout.write('Cargando CSV...')
        all_codes, code_by_description = load_csv_codes(csv_path)
        self.stdout.write(self.style.SUCCESS(f'  Códigos en CSV: {len(all_codes)}'))

        def run_in_schema():
            User = __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model()
            try:
                upload_user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                upload_user = None
                self.stdout.write(self.style.WARNING(f'Usuario id={user_id} no existe; uploaded_by quedará NULL'))

            products = Product.objects.filter(is_active=True).prefetch_related('brand_assignments__brand')
            if list_missing:
                self.stdout.write(self.style.SUCCESS('Productos con código en CSV pero sin archivo de imagen en el directorio:'))
            created_count = 0
            skipped_no_code = 0
            skipped_no_image = 0
            skipped_has_image = 0
            errors = []
            missing_list = []  # (product_id, name, sku, code) sin archivo de imagen

            for product in products:
                code = find_code_for_product(product, all_codes, code_by_description)
                if not code:
                    skipped_no_code += 1
                    continue
                image_path = find_image_path(images_dir, code)
                if not image_path:
                    skipped_no_image += 1
                    missing_list.append((product.id, product.name, product.sku, code))
                    if list_missing:
                        self.stdout.write(
                            f'  Sin imagen: id={product.id} sku={product.sku!r} name={product.name!r} → código={code!r}'
                        )
                    continue
                assignments = list(product.brand_assignments.select_related('brand').all())
                if not assignments:
                    errors.append(f'Producto id={product.id} sin asignaciones de marca')
                    continue
                # Una imagen por asignación (marca), marcada como primary si es la única
                for assignment in assignments:
                    if dry_run:
                        self.stdout.write(
                            f'  [DRY-RUN] Crearía ProductImage: product_id={product.id} '
                            f'assignment_id={assignment.id} code={code} is_primary=True'
                        )
                        created_count += 1
                        continue
                    # Evitar duplicar si ya hay imagen para esta asignación
                    if ProductImage.objects.filter(assignment=assignment).exists():
                        skipped_has_image += 1
                        continue
                    try:
                        with open(image_path, 'rb') as f:
                            content = f.read()
                        filename = os.path.basename(image_path)
                        if not filename.lower().endswith(('.jpg', '.jpeg')):
                            filename = code + '.jpg'
                        pi = ProductImage(
                            product=product,
                            assignment=assignment,
                            is_primary=True,
                            uploaded_by=upload_user,
                            description=code or '',
                        )
                        pi.image.save(filename, ContentFile(content), save=False)
                        pi.save()
                        created_count += 1
                    except Exception as e:
                        errors.append(f'Product {product.id} assignment {assignment.id}: {e}')

            self.stdout.write(self.style.SUCCESS(f'Imágenes creadas: {created_count}'))
            if skipped_no_code:
                self.stdout.write(self.style.WARNING(f'Sin código en CSV: {skipped_no_code} productos'))
            if skipped_no_image:
                self.stdout.write(self.style.WARNING(f'Sin archivo de imagen: {skipped_no_image} productos'))
            if output_missing and missing_list:
                out_path = output_missing
                with open(out_path, 'w', encoding='utf-8') as out:
                    out.write('product_id\tname\tsku\tcodigo_esperado\n')
                    for pid, name, sku, code in sorted(missing_list, key=lambda x: (x[3], x[0])):
                        out.write(f'{pid}\t{name}\t{sku}\t{code}\n')
                self.stdout.write(self.style.SUCCESS(f'Lista guardada en: {out_path}'))
            if skipped_has_image:
                self.stdout.write(self.style.WARNING(f'Assignment ya tenía imagen (omitidos): {skipped_has_image}'))
            for err in errors:
                self.stdout.write(self.style.ERROR(err))

        if schema:
            with schema_context(schema):
                self.stdout.write(self.style.SUCCESS(f'Ejecutando en schema: {schema}'))
                run_in_schema()
        else:
            self.stdout.write(self.style.WARNING('Ejecutando en el schema actual (usa --schema para un tenant concreto).'))
            run_in_schema()
