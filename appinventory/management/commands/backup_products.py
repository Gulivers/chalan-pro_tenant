from django.core.management.base import BaseCommand
from django.db import transaction
from appinventory.models import Product, ProductBrand
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Create backup of products before unification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-file',
            type=str,
            default=None,
            help='Output file for backup (default: auto-generated)'
        )

    def handle(self, *args, **options):
        output_file = options['output_file']
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'product_backup_{timestamp}.json'
        
        self.stdout.write(self.style.SUCCESS(f'[INFO] Creating backup to {output_file}...'))
        
        # Obtener todos los productos activos
        products = Product.objects.filter(is_active=True)
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'total_products': products.count(),
            'products': []
        }
        
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category_id': product.category.id if product.category else None,
                'category_name': product.category.name if product.category else None,
                'brands': [
                    {
                        'id': brand.id,
                        'name': brand.name,
                        'is_default': brand.is_default
                    }
                    for brand in product.brands.all()
                ],
                'reorder_level': float(product.reorder_level),
                'unit_default_id': product.unit_default.id if product.unit_default else None,
                'unit_default_name': product.unit_default.name if product.unit_default else None,
                'created_at': product.created_at.isoformat(),
                'is_active': product.is_active
            }
            backup_data['products'].append(product_data)
        
        # Guardar backup
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Backup created successfully!'))
        self.stdout.write(f'[INFO] File: {output_file}')
        self.stdout.write(f'[INFO] Products backed up: {backup_data["total_products"]}')
        self.stdout.write(f'[INFO] Timestamp: {backup_data["timestamp"]}')
