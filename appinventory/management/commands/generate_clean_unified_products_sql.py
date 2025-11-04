from django.core.management.base import BaseCommand
from django.db import connection
from appinventory.models import Product, ProductBrand
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Generate clean MySQL INSERT statements for unified products (without commented deactivation)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-file',
            type=str,
            default='db/insert_unified_products_clean.sql',
            help='Output file for clean SQL statements'
        )

    def handle(self, *args, **options):
        output_file = options['output_file']
        
        self.stdout.write(self.style.SUCCESS(f'[INFO] Generating clean MySQL INSERT statements...'))
        
        # Obtener productos unificados (IDs altos, creados recientemente)
        unified_products = Product.objects.filter(
            is_active=True,
            id__gte=880  # Los productos unificados tienen IDs altos
        ).order_by('id')
        
        self.stdout.write(f'[INFO] Found {unified_products.count()} unified products')
        
        sql_statements = []
        sql_statements.append('-- MySQL INSERT statements for unified products (CLEAN VERSION)')
        sql_statements.append(f'-- Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        sql_statements.append('-- Total unified products: {}'.format(unified_products.count()))
        sql_statements.append('-- Original products have been permanently deleted')
        sql_statements.append('')
        
        # Insertar productos
        sql_statements.append('-- Insert unified products')
        sql_statements.append('INSERT INTO appinventory_product (id, name, sku, category_id, reorder_level, unit_default_id, created_at, is_active) VALUES')
        
        product_values = []
        for product in unified_products:
            category_id = product.category.id if product.category else 'NULL'
            unit_default_id = product.unit_default.id if product.unit_default else 'NULL'
            created_at = product.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # Escapar comillas simples en nombres
            escaped_name = product.name.replace("'", "''")
            escaped_sku = product.sku.replace("'", "''")
            
            product_values.append(
                f"({product.id}, '{escaped_name}', '{escaped_sku}', {category_id}, {product.reorder_level}, {unit_default_id}, '{created_at}', {1 if product.is_active else 0})"
            )
        
        sql_statements.append(',\n'.join(product_values) + ';')
        sql_statements.append('')
        
        # Insertar relaciones producto-marca
        sql_statements.append('-- Insert product-brand relationships')
        sql_statements.append('INSERT INTO appinventory_product_brands (product_id, productbrand_id) VALUES')
        
        brand_relations = []
        for product in unified_products:
            for brand in product.brands.all():
                brand_relations.append(f'({product.id}, {brand.id})')
        
        sql_statements.append(',\n'.join(brand_relations) + ';')
        sql_statements.append('')
        
        # Actualizar marcas predeterminadas
        sql_statements.append('-- Update default brands')
        default_brands = []
        for product in unified_products:
            default_brand = product.get_default_brand()
            if default_brand:
                default_brands.append(f"UPDATE appinventory_productbrand SET is_default = 1 WHERE id = {default_brand.id};")
        
        sql_statements.extend(default_brands)
        sql_statements.append('')
        
        sql_statements.append('-- NOTE: Original products with brand prefixes have been permanently deleted')
        sql_statements.append('-- This script only contains the unified products with clean names')
        
        # Guardar archivo SQL
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_statements))
        
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Clean SQL file created successfully!'))
        self.stdout.write(f'[INFO] File: {output_file}')
        self.stdout.write(f'[INFO] Products: {unified_products.count()}')
        self.stdout.write(f'[INFO] Brand relations: {len(brand_relations)}')
        self.stdout.write(f'[INFO] Default brands: {len(default_brands)}')
